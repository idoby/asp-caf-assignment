from libcaf.repository import Repository
from libcaf.diff import (AddedDiff, Diff, ModifiedDiff, MovedFromDiff, MovedToDiff, RemovedDiff)
from collections.abc import Sequence

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

def test_status_no_commits_reports_added_files(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')

    diffs = temp_repo.status()
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diffs)

    assert len(added) == 1
    assert added[0].record.name == 'a.txt'
    assert len(modified) == 0
    assert len(removed) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0

def test_status_no_commits_empty_dir_is_clean(temp_repo: Repository) -> None:
    diffs = temp_repo.status()
    assert len(diffs) == 0

def test_status_clean_after_commit(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'file.txt').write_text('Same content')
    temp_repo.commit_working_dir('Tester', 'Initial commit')

    diffs = temp_repo.status()
    assert len(diffs) == 0

def test_status_modified_file_since_head(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('Old')
    temp_repo.commit_working_dir('Tester', 'Commit old')

    (temp_repo.working_dir / 'a.txt').write_text('New')

    diffs = temp_repo.status()
    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diffs)

    assert len(modified) == 1
    assert modified[0].record.name == 'a.txt'
    assert len(added) == 0
    assert len(removed) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0

def test_status_ignores_repo_dir_changes(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')
    temp_repo.commit_working_dir('Tester', 'Commit A')

    internal = temp_repo.repo_path() / 'INTERNAL.txt'
    internal.write_text('ignore me')

    diffs = temp_repo.status()
    assert len(diffs) == 0