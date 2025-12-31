from collections.abc import Sequence
from pathlib import Path

from libcaf.repository import (Repository)
from libcaf.diff import (AddedDiff, Diff, ModifiedDiff, MovedFromDiff, MovedToDiff, RemovedDiff)


def snapshot_objects(temp_repo: Repository) -> set[str]:
    objects_dir = temp_repo.objects_dir()
    if not objects_dir.exists():
        return set()
    return {p.name for p in objects_dir.iterdir() if p.is_file()}


def flatten_diffs(diffs: Sequence[Diff]) -> list[Diff]:
    out: list[Diff] = []

    def walk(d: Diff) -> None:
        out.append(d)
        for c in d.children:
            walk(c)

    for d in diffs:
        walk(d)
    return out

def split_diffs_by_type(diffs: Sequence[Diff]) -> \
        tuple[list[AddedDiff],
        list[ModifiedDiff],
        list[MovedToDiff],
        list[MovedFromDiff],
        list[RemovedDiff]]:
    added = [d for d in diffs if isinstance(d, AddedDiff)]
    moved_to = [d for d in diffs if isinstance(d, MovedToDiff)]
    moved_from = [d for d in diffs if isinstance(d, MovedFromDiff)]
    removed = [d for d in diffs if isinstance(d, RemovedDiff)]
    modified = [d for d in diffs if isinstance(d, ModifiedDiff)]

    return added, modified, moved_to, moved_from, removed


def test_diff_head(temp_repo: Repository) -> None:
    file_path = temp_repo.working_dir / 'file.txt'
    file_path.write_text('Same content')

    temp_repo.commit_working_dir('Tester', 'Initial commit')
    diff_result = temp_repo.diff()

    assert len(diff_result) == 0


def test_diff_identical_commits(temp_repo: Repository) -> None:
    file_path = temp_repo.working_dir / 'file.txt'
    file_path.write_text('Same content')

    commit_hash = temp_repo.commit_working_dir('Tester', 'Initial commit')
    diff_result = temp_repo.diff(commit_hash, 'HEAD')

    assert len(diff_result) == 0


def test_diff_added_file(temp_repo: Repository) -> None:
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Content 1')
    commit1_hash = temp_repo.commit_working_dir('Tester', 'Initial commit')

    file2 = temp_repo.working_dir / 'file2.txt'
    file2.write_text('Content 2')
    temp_repo.commit_working_dir('Tester', 'Added file2')

    diff_result = temp_repo.diff(commit1_hash)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 1
    assert added[0].record.name == 'file2.txt'

    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0
    assert len(modified) == 0


def test_diff_removed_file(temp_repo: Repository) -> None:
    file1 = temp_repo.working_dir / 'file.txt'
    file1.write_text('Content')
    commit1_hash = temp_repo.commit_working_dir('Tester', 'File created')

    file1.unlink()  # Delete the file.
    temp_repo.commit_working_dir('Tester', 'File deleted')

    diff_result = temp_repo.diff(commit1_hash)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(modified) == 0

    assert len(removed) == 1
    assert removed[0].record.name == 'file.txt'


def test_diff_modified_file(temp_repo: Repository) -> None:
    file1 = temp_repo.working_dir / 'file.txt'
    file1.write_text('Old content')
    commit1 = temp_repo.commit_working_dir('Tester', 'Original commit')

    file1.write_text('New content')
    commit2 = temp_repo.commit_working_dir('Tester', 'Modified file')

    diff_result = temp_repo.diff(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 1
    assert modified[0].record.name == 'file.txt'


def test_diff_nested_directory(temp_repo: Repository) -> None:
    subdir = temp_repo.working_dir / 'subdir'
    subdir.mkdir()
    nested_file = subdir / 'file.txt'
    nested_file.write_text('Initial')
    commit1 = temp_repo.commit_working_dir('Tester', 'Commit with subdir')

    nested_file.write_text('Modified')
    commit2 = temp_repo.commit_working_dir('Tester', 'Modified nested file')

    diff_result = temp_repo.diff(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 1
    assert modified[0].record.name == 'subdir'
    assert len(modified[0].children) == 1
    assert modified[0].children[0].record.name == 'file.txt'


def test_diff_nested_trees(temp_repo: Repository) -> None:
    dir1 = temp_repo.working_dir / 'dir1'
    dir1.mkdir()
    file_a = dir1 / 'file_a.txt'
    file_a.write_text('A1')

    dir2 = temp_repo.working_dir / 'dir2'
    dir2.mkdir()
    file_b = dir2 / 'file_b.txt'
    file_b.write_text('B1')

    commit1 = temp_repo.commit_working_dir('Tester', 'Initial nested commit')

    file_a.write_text('A2')
    file_b.unlink()
    file_c = dir2 / 'file_c.txt'
    file_c.write_text('C1')

    commit2 = temp_repo.commit_working_dir('Tester', 'Updated nested commit')

    diff_result = temp_repo.diff(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 2

    assert modified[0].record.name == 'dir1'
    assert len(modified[0].children) == 1
    assert modified[0].children[0].record.name == 'file_a.txt'
    assert isinstance(modified[0].children[0], ModifiedDiff)

    assert modified[1].record.name == 'dir2'
    assert len(modified[1].children) == 2
    assert modified[1].children[0].record.name == 'file_b.txt'
    assert isinstance(modified[1].children[0], RemovedDiff)
    assert modified[1].children[1].record.name == 'file_c.txt'
    assert isinstance(modified[1].children[1], AddedDiff)


def test_diff_moved_file_added_first(temp_repo: Repository) -> None:
    dir1 = temp_repo.working_dir / 'dir1'
    dir1.mkdir()
    file_a = dir1 / 'file_a.txt'
    file_a.write_text('A1')

    dir2 = temp_repo.working_dir / 'dir2'
    dir2.mkdir()
    file_b = dir2 / 'file_b.txt'
    file_b.write_text('B1')

    commit1 = temp_repo.commit_working_dir('Tester', 'Initial nested commit')

    file_a.rename(dir2 / 'file_c.txt')

    commit2 = temp_repo.commit_working_dir('Tester', 'Updated nested commit')

    diff_result = temp_repo.diff(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 2

    assert modified[0].record.name == 'dir1'
    assert len(modified[0].children) == 1

    modified_child = modified[0].children[0]
    assert isinstance(modified_child, MovedToDiff)
    assert modified_child.record.name == 'file_a.txt'

    assert isinstance(modified_child.moved_to, MovedFromDiff)
    assert modified_child.moved_to.parent is not None
    assert modified_child.moved_to.parent.record.name == 'dir2'
    assert len(modified_child.moved_to.parent.children) == 1
    assert modified_child.moved_to.record.name == 'file_c.txt'

    assert modified[1].record.name == 'dir2'
    assert len(modified[1].children) == 1

    modified_child = modified[1].children[0]
    assert isinstance(modified_child, MovedFromDiff)
    assert modified_child.record.name == 'file_c.txt'

    assert isinstance(modified_child.moved_from, MovedToDiff)
    assert modified_child.moved_from.parent is not None
    assert modified_child.moved_from.parent.record.name == 'dir1'
    assert len(modified_child.moved_from.parent.children) == 1
    assert modified_child.moved_from.record.name == 'file_a.txt'


def test_diff_moved_file_removed_first(temp_repo: Repository) -> None:
    dir1 = temp_repo.working_dir / 'dir1'
    dir1.mkdir()
    file_a = dir1 / 'file_a.txt'
    file_a.write_text('A1')

    dir2 = temp_repo.working_dir / 'dir2'
    dir2.mkdir()
    file_b = dir2 / 'file_b.txt'
    file_b.write_text('B1')

    commit1 = temp_repo.commit_working_dir('Tester', 'Initial nested commit')

    file_b.rename(dir1 / 'file_c.txt')

    commit2 = temp_repo.commit_working_dir('Tester', 'Updated nested commit')

    diff_result = temp_repo.diff(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 2

    assert modified[0].record.name == 'dir1'
    assert len(modified[0].children) == 1

    modified_child = modified[0].children[0]
    assert isinstance(modified_child, MovedFromDiff)
    assert modified_child.record.name == 'file_c.txt'

    assert isinstance(modified_child.moved_from, MovedToDiff)
    assert modified_child.moved_from.parent is not None
    assert modified_child.moved_from.parent.record.name == 'dir2'
    assert len(modified_child.moved_from.parent.children) == 1
    assert modified_child.moved_from.record.name == 'file_b.txt'

    assert modified[1].record.name == 'dir2'
    assert len(modified[1].children) == 1

    modified_child = modified[1].children[0]
    assert isinstance(modified_child, MovedToDiff)
    assert modified_child.record.name == 'file_b.txt'

    assert isinstance(modified_child.moved_to, MovedFromDiff)
    assert modified_child.moved_to.parent is not None
    assert len(modified_child.moved_to.parent.children) == 1
    assert modified_child.moved_to.parent.record.name == 'dir1'
    assert modified_child.moved_to.record.name == 'file_c.txt'

def test_diff_commit_dir_no_changes(temp_repo: Repository) -> None:
    file_path = temp_repo.working_dir / 'file.txt'
    file_path.write_text('Same content')

    commit_hash = temp_repo.commit_working_dir('Tester', 'Initial commit')

    diff_result = temp_repo.diff(commit_hash, temp_repo.working_dir)
    assert len(diff_result) == 0
    
def test_diff_commit_dir_added_file(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')
    commit_hash = temp_repo.commit_working_dir('Tester', 'Commit A')

    (temp_repo.working_dir / 'b.txt').write_text('B')

    diff_result = temp_repo.diff(commit_hash, temp_repo.working_dir)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    assert len(added) == 1
    assert added[0].record.name == 'b.txt'
    assert len(modified) == 0
    assert len(removed) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    
def test_diff_commit_dir_removed_file(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')
    commit_hash = temp_repo.commit_working_dir('Tester', 'Commit A')

    (temp_repo.working_dir / 'a.txt').unlink()

    diff_result = temp_repo.diff(commit_hash, temp_repo.working_dir)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    assert len(removed) == 1
    assert removed[0].record.name == 'a.txt'
    assert len(added) == 0
    assert len(modified) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0

def test_diff_commit_dir_modified_file(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('Old')
    commit_hash = temp_repo.commit_working_dir('Tester', 'Commit old')

    (temp_repo.working_dir / 'a.txt').write_text('New')

    diff_result = temp_repo.diff(commit_hash, temp_repo.working_dir)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    assert len(modified) == 1
    assert modified[0].record.name == 'a.txt'
    assert len(added) == 0
    assert len(removed) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0

def test_diff_commit_dir_nested_changes(temp_repo: Repository) -> None:
    subdir = temp_repo.working_dir / 'subdir'
    subdir.mkdir()
    (subdir / 'file.txt').write_text('Initial')
    commit_hash = temp_repo.commit_working_dir('Tester', 'Commit nested')

    (subdir / 'file.txt').write_text('Modified')
    (subdir / 'new.txt').write_text('New file')

    diff_result = temp_repo.diff(commit_hash, temp_repo.working_dir)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    # Expect the directory to be modified, with children diffs
    assert len(modified) == 1
    assert modified[0].record.name == 'subdir'

    child_types = [type(c) for c in modified[0].children]
    child_names = [c.record.name for c in modified[0].children]

    assert 'file.txt' in child_names
    assert 'new.txt' in child_names
    assert any(isinstance(c, ModifiedDiff) and c.record.name == 'file.txt' for c in modified[0].children)
    assert any(isinstance(c, AddedDiff) and c.record.name == 'new.txt' for c in modified[0].children)

def test_diff_commit_dir_ignores_repo_dir(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')
    commit_hash = temp_repo.commit_working_dir('Tester', 'Commit A')

    # Create internal file inside .caf
    internal = temp_repo.repo_dir / 'INTERNAL.txt'
    internal.write_text('ignore me')

    diff_result = temp_repo.diff(commit_hash, temp_repo.working_dir)
    flat = flatten_diffs(diff_result)

    assert not any(d.record.name == 'INTERNAL.txt' for d in flat)

def test_diff_path_vs_path_detects_changes(temp_repo: Repository) -> None:
    dir1 = temp_repo.working_dir / 'dir1_any'
    dir2 = temp_repo.working_dir / 'dir2_any'
    dir1.mkdir()
    dir2.mkdir()

    # Same filename, different content => Modified
    (dir1 / 'same.txt').write_text('v1')
    (dir2 / 'same.txt').write_text('v2')

    # Present only in dir1 => Removed
    (dir1 / 'only1.txt').write_text('only in 1')

    # Present only in dir2 => Added
    (dir2 / 'only2.txt').write_text('only in 2')

    diffs = temp_repo.diff(dir1, dir2)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diffs)

    assert [d.record.name for d in added] == ['only2.txt']
    assert [d.record.name for d in removed] == ['only1.txt']
    assert [d.record.name for d in modified] == ['same.txt']
    assert len(moved_to) == 0
    assert len(moved_from) == 0

def test_diff_fs_vs_commit_reversed(temp_repo: Repository) -> None:
    # 1. Setup Commit A with file.txt = "v1"
    file_path = temp_repo.working_dir / 'file.txt'
    file_path.write_text('v1')
    commit_hash = temp_repo.commit_working_dir('Tester', 'Commit v1')

    # 2. Modify file.txt to "v2" and create new.txt in Working Directory
    file_path.write_text('v2')
    (temp_repo.working_dir / 'new.txt').write_text('new content')

    # 3. Diff Working Directory -> Commit
    # Note: Logic is "How to transform Spec1 (WD) into Spec2 (Commit)"
    diff_result = temp_repo.diff(temp_repo.working_dir, commit_hash)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    # Expect 'new.txt' to be REMOVED (it exists in WD, but not in Commit)
    assert len(removed) == 1
    assert removed[0].record.name == 'new.txt'

    # Expect 'file.txt' to be MODIFIED (v2 -> v1)
    assert len(modified) == 1
    assert modified[0].record.name == 'file.txt'

    # Ensure no additions (nothing in Commit that isn't in WD, except the content change)
    assert len(added) == 0

def test_diff_arbitrary_fs_dirs_modified(temp_repo: Repository) -> None:
    dir_a = temp_repo.working_dir / 'folder_a'
    dir_b = temp_repo.working_dir / 'folder_b'
    dir_a.mkdir()
    dir_b.mkdir()

    # Same file, different content
    (dir_a / 'common.txt').write_text('Content A')
    (dir_b / 'common.txt').write_text('Content B')

    # File only in A
    (dir_a / 'only_a.txt').write_text('A')

    # File only in B
    (dir_b / 'only_b.txt').write_text('B')

    diff_result = temp_repo.diff(dir_a, dir_b)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    assert len(modified) == 1
    assert modified[0].record.name == 'common.txt'

    assert len(removed) == 1
    assert removed[0].record.name == 'only_a.txt'

    assert len(added) == 1
    assert added[0].record.name == 'only_b.txt'

def test_diff_arbitrary_fs_dirs_move_detection(temp_repo: Repository) -> None:
    dir_a = temp_repo.working_dir / 'start_state'
    dir_b = temp_repo.working_dir / 'end_state'
    dir_a.mkdir()
    dir_b.mkdir()

    # Create content in A
    (dir_a / 'original.txt').write_text('Moving Content')

    # Create same content in B but renamed
    (dir_b / 'renamed.txt').write_text('Moving Content')

    diff_result = temp_repo.diff(dir_a, dir_b)
    
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(removed) == 0
    
    # Corrected Assertions:
    
    # 1. MovedToDiff represents the OLD file (the source)
    assert len(moved_to) == 1
    assert moved_to[0].record.name == 'original.txt'  # Was 'renamed.txt'
    
    # It points to the NEW file
    assert isinstance(moved_to[0].moved_to, MovedFromDiff)
    assert moved_to[0].moved_to.record.name == 'renamed.txt'

    # 2. MovedFromDiff represents the NEW file (the destination)
    assert len(moved_from) == 1
    assert moved_from[0].record.name == 'renamed.txt' # Was 'original.txt'
    
    # It points back to the OLD file
    assert isinstance(moved_from[0].moved_from, MovedToDiff)
    # Note: Depending on recursion/linking, the parent might be None or populated, 
    # but the record name should definitively be the source.
    assert moved_from[0].moved_from.record.name == 'original.txt'

def test_diff_commit_vs_fs_deep_nested_changes(temp_repo: Repository) -> None:
    # Setup complex directory structure
    src = temp_repo.working_dir / 'src'
    src.mkdir()
    utils = src / 'utils'
    utils.mkdir()
    
    (utils / 'helper.py').write_text('print("help")')
    (src / 'main.py').write_text('print("main")')
    
    commit_hash = temp_repo.commit_working_dir('Tester', 'Structure')

    # Modify deep file in FS
    (utils / 'helper.py').write_text('print("help v2")')
    
    # Diff Commit -> FS
    diff_result = temp_repo.diff(commit_hash, temp_repo.working_dir)
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

    # Top level should be 'src' (Modified)
    assert len(modified) == 1
    assert modified[0].record.name == 'src'
    
    # Inside src, 'utils' should be Modified
    src_children = modified[0].children
    utils_diff = next(c for c in src_children if c.record.name == 'utils')
    assert isinstance(utils_diff, ModifiedDiff)
    
    # Inside utils, 'helper.py' should be Modified
    utils_children = utils_diff.children
    helper_diff = next(c for c in utils_children if c.record.name == 'helper.py')
    assert isinstance(helper_diff, ModifiedDiff)

def test_diff_absolute_paths(temp_repo: Repository) -> None:
    abs_dir_1 = (temp_repo.working_dir / 'abs_1').resolve()
    abs_dir_2 = (temp_repo.working_dir / 'abs_2').resolve()
    
    abs_dir_1.mkdir()
    abs_dir_2.mkdir()
    
    (abs_dir_1 / 'test.txt').write_text('A')
    (abs_dir_2 / 'test.txt').write_text('B')
    
    # Pass string representation of absolute paths
    diff_result = temp_repo.diff(str(abs_dir_1), str(abs_dir_2))
    
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)
    assert len(modified) == 1
    assert modified[0].record.name == 'test.txt'