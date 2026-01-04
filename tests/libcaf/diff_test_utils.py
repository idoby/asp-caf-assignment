from collections.abc import Sequence
from libcaf.diff import AddedDiff, Diff, ModifiedDiff, MovedFromDiff, MovedToDiff, RemovedDiff


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
