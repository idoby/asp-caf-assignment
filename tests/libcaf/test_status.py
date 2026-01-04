from libcaf.repository import Repository
from libcaf.diff import (AddedDiff, Diff, ModifiedDiff, MovedFromDiff, MovedToDiff, RemovedDiff)
from collections.abc import Sequence
from diff_test_utils import split_diffs_by_type

def test_status_no_commits_reports_added_files(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')

    diffs = temp_repo.status()
    assert diffs is None

def test_status_no_commits_empty_dir_is_clean(temp_repo: Repository) -> None:
    diffs = temp_repo.status()
    assert diffs is None

def test_status_clean_after_commit(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'file.txt').write_text('Same content')
    temp_repo.commit_working_dir('Tester', 'Initial commit')

    diffs = temp_repo.status()
    assert diffs is not None
    assert len(diffs) == 0

def test_status_modified_file_since_head(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('Old')
    temp_repo.commit_working_dir('Tester', 'Commit old')

    (temp_repo.working_dir / 'a.txt').write_text('New')

    diffs = temp_repo.status()
    assert diffs is not None
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
    assert diffs is not None
    assert len(diffs) == 0
    
def test_status_added_file_since_head(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')
    temp_repo.commit_working_dir('Tester', 'Commit A')

    (temp_repo.working_dir / 'b.txt').write_text('B')

    diffs = temp_repo.status()
    assert diffs is not None

    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diffs)

    assert len(added) == 1
    assert added[0].record.name == 'b.txt'

    assert len(modified) == 0
    assert len(removed) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0


def test_status_removed_file_since_head(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')
    temp_repo.commit_working_dir('Tester', 'Commit A')

    (temp_repo.working_dir / 'a.txt').unlink()

    diffs = temp_repo.status()
    assert diffs is not None

    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diffs)

    assert len(removed) == 1
    assert removed[0].record.name == 'a.txt'

    assert len(added) == 0
    assert len(modified) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0


def test_status_move_detection_at_root(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'original.txt').write_text('Moving Content')
    temp_repo.commit_working_dir('Tester', 'Commit original')

    (temp_repo.working_dir / 'original.txt').rename(temp_repo.working_dir / 'renamed.txt')

    diffs = temp_repo.status()
    assert diffs is not None

    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diffs)

    # Renames should be detected as a move pair, not add/remove
    assert len(added) == 0
    assert len(removed) == 0
    assert len(modified) == 0

    assert len(moved_to) == 1
    assert moved_to[0].record.name == 'original.txt'

    assert len(moved_from) == 1
    assert moved_from[0].record.name == 'renamed.txt'

    # Cross-link sanity (these attributes are on the Diff objects)
    assert moved_to[0].moved_to is not None
    assert moved_to[0].moved_to.record.name == 'renamed.txt'

    assert moved_from[0].moved_from is not None
    assert moved_from[0].moved_from.record.name == 'original.txt'


def test_status_nested_recursive_diffs(temp_repo: Repository) -> None:
    subdir = temp_repo.working_dir / 'subdir'
    subdir.mkdir()

    (subdir / 'keep.txt').write_text('keep')
    (subdir / 'mod.txt').write_text('v1')
    temp_repo.commit_working_dir('Tester', 'Commit nested')

    # Added
    (subdir / 'add.txt').write_text('new')
    # Modified
    (subdir / 'mod.txt').write_text('v2')
    # Removed
    (subdir / 'keep.txt').unlink()

    diffs = temp_repo.status()
    assert diffs is not None

    added, modified, moved_to, moved_from, removed = split_diffs_by_type(diffs)

    # Expect one top-level modified directory
    assert len(modified) == 1
    assert modified[0].record.name == 'subdir'

    # Children should include Added/Modified/Removed
    child_added = [c for c in modified[0].children if isinstance(c, AddedDiff)]
    child_modified = [c for c in modified[0].children if isinstance(c, ModifiedDiff)]
    child_removed = [c for c in modified[0].children if isinstance(c, RemovedDiff)]

    assert any(c.record.name == 'add.txt' for c in child_added)
    assert any(c.record.name == 'mod.txt' for c in child_modified)
    assert any(c.record.name == 'keep.txt' for c in child_removed)

    # No moves in this scenario
    assert len(moved_to) == 0
    assert len(moved_from) == 0

    # At top-level, we don't expect added/removed; they should be inside subdir
    assert len(added) == 0
    assert len(removed) == 0