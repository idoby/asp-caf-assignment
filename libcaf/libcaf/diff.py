from collections import deque
from collections.abc import Sequence, Callable
from dataclasses import dataclass
from pathlib import Path

from . import Tree, TreeRecord, TreeRecordType
from .plumbing import hash_file, hash_object, load_tree


class DiffError(Exception):
    """Exception raised for diff-related errors."""


@dataclass
class Diff:
    """A class representing a difference between two tree records."""

    record: TreeRecord
    parent: "Diff | None"
    children: list["Diff"]


@dataclass
class AddedDiff(Diff):
    """An added tree record diff as part of a commit."""


@dataclass
class RemovedDiff(Diff):
    """A removed tree record diff as part of a commit."""


@dataclass
class ModifiedDiff(Diff):
    """A modified tree record diff as part of a commit."""


@dataclass
class MovedToDiff(Diff):
    """A tree record diff that has been moved elsewhere as part of a commit."""

    moved_to: "MovedFromDiff | None"


@dataclass
class MovedFromDiff(Diff):
    """A tree record diff that has been moved from elsewhere as part of a commit."""

    moved_from: MovedToDiff | None


def build_tree_from_fs(path: Path, *, repo_dir_name: str) -> tuple[Tree, str, dict[str, Tree]]:
    """Build an in-memory Tree for the given filesystem directory.

    :param path: The directory path to build the tree from.
    :param repo_dir_name: The repository directory name to ignore (e.g. '.caf').
    :return: A tuple of (root_tree, root_hash, tree_lookup), where tree_lookup maps tree hashes
        to Tree objects for subtrees built from the filesystem.
    :raises NotADirectoryError: If the given path does not exist or is not a directory.
    """
    if not path or not path.is_dir():
        msg = f"{path} is not a directory"
        raise NotADirectoryError(msg)

    dir_hashes: dict[Path, str] = {}
    tree_lookup: dict[str, Tree] = {}
    trees_by_path: dict[Path, Tree] = {}

    stack = deque([path])

    while stack:
        current_path = stack.pop()
        tree_records: dict[str, TreeRecord] = {}

        for item in current_path.iterdir():
            if item.name == repo_dir_name:
                continue

            if item.is_file():
                blob_hash = hash_file(item)
                tree_records[item.name] = TreeRecord(TreeRecordType.BLOB, blob_hash, item.name)

            elif item.is_dir():
                if item in dir_hashes:
                    subtree_hash = dir_hashes[item]
                    tree_records[item.name] = TreeRecord(TreeRecordType.TREE, subtree_hash, item.name)
                else:
                    stack.append(current_path)
                    stack.append(item)
                    break
        else:
            tree = Tree(tree_records)
            tree_hash = hash_object(tree)

            trees_by_path[current_path] = tree
            dir_hashes[current_path] = tree_hash
            tree_lookup[tree_hash] = tree

    root_hash = dir_hashes[path]
    root_tree = trees_by_path[path]
    return root_tree, root_hash, tree_lookup


def diff_trees(tree1: Tree | None, tree2: Tree | None, *, load_tree1: Callable[[str], Tree],
               load_tree2: Callable[[str], Tree]) -> Sequence[Diff]:
    """Generate a diff between two Tree objects.

    :param tree1: The first tree (old side). May be None.
    :param tree2: The second tree (new side). May be None.
    :param load_tree1: Function used to load subtrees for tree1 by hash.
    :param load_tree2: Function used to load subtrees for tree2 by hash.
    :return: A sequence of Diff objects representing the changes.
    :raises DiffError: If a required subtree cannot be loaded.
    """
    top_level_diff = Diff(TreeRecord(TreeRecordType.TREE, "", ""), None, [])
    stack: list[tuple[Tree | None, Tree | None, Diff]] = [(tree1, tree2, top_level_diff)]

    potentially_added: dict[str, Diff] = {}
    potentially_removed: dict[str, Diff] = {}

    while stack:
        current_tree1, current_tree2, parent_diff = stack.pop()
        records1 = current_tree1.records if current_tree1 else {}
        records2 = current_tree2.records if current_tree2 else {}

        for name, record1 in records1.items():
            if name not in records2:
                if record1.hash in potentially_added:
                    added_diff = potentially_added[record1.hash]
                    del potentially_added[record1.hash]

                    local_diff = MovedToDiff(record1, parent_diff, [], None)
                    moved_from_diff = MovedFromDiff(added_diff.record, added_diff.parent, [], local_diff)
                    local_diff.moved_to = moved_from_diff

                    added_diff.parent.children = (
                        [_ if _.record.hash != record1.hash else moved_from_diff for _ in added_diff.parent.children]
                    )
                else:
                    local_diff = RemovedDiff(record1, parent_diff, [])
                    potentially_removed[record1.hash] = local_diff

                parent_diff.children.append(local_diff)
            else:
                record2 = records2[name]

                if record1.hash == record2.hash:
                    continue

                if record1.type == TreeRecordType.TREE and record2.type == TreeRecordType.TREE:
                    subtree_diff = ModifiedDiff(record1, parent_diff, [])

                    try:
                        sub1 = load_tree1(record1.hash)
                        sub2 = load_tree2(record2.hash)
                    except Exception as e:
                        msg = "Error loading subtree for diff"
                        raise DiffError(msg) from e

                    stack.append((sub1, sub2, subtree_diff))
                    parent_diff.children.append(subtree_diff)
                else:
                    parent_diff.children.append(ModifiedDiff(record1, parent_diff, []))

        for name, record2 in records2.items():
            if name not in records1:
                if record2.hash in potentially_removed:
                    removed_diff = potentially_removed[record2.hash]
                    del potentially_removed[record2.hash]

                    local_diff = MovedFromDiff(record2, parent_diff, [], None)
                    moved_to_diff = MovedToDiff(removed_diff.record, removed_diff.parent, [], local_diff)
                    local_diff.moved_from = moved_to_diff

                    removed_diff.parent.children = (
                        [_ if _.record.hash != record2.hash else moved_to_diff for _ in removed_diff.parent.children]
                    )
                else:
                    local_diff = AddedDiff(record2, parent_diff, [])
                    potentially_added[record2.hash] = local_diff

                parent_diff.children.append(local_diff)

    return top_level_diff.children