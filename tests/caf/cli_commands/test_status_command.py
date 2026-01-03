from __future__ import annotations

from typing import Callable

from pytest import CaptureFixture

from caf import cli_commands
from libcaf.repository import Repository


def _assert_contains_all(haystack: str, *needles: str) -> None:
    for n in needles:
        assert n in haystack, f"Expected to find {n!r} in output, but it was not present. Output was:\n{haystack}"


def test_status_no_head_commit(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    rc = cli_commands.status(working_dir_path=str(temp_repo.working_dir), repo_dir=str(temp_repo.repo_dir))
    assert rc == 0

    out = capsys.readouterr().out
    assert 'No HEAD commit' in out


def test_status_clean_working_dir(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')
    temp_repo.commit_working_dir('Tester', 'Init')

    rc = cli_commands.status(working_dir_path=str(temp_repo.working_dir), repo_dir=str(temp_repo.repo_dir))
    assert rc == 0

    out = capsys.readouterr().out
    assert 'Working directory clean.' in out


def test_status_shows_added_removed_and_nested_modified(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    d = temp_repo.working_dir / 'dir'
    d.mkdir()
    (d / 'x.txt').write_text('v1')
    (temp_repo.working_dir / 'root_keep.txt').write_text('keep')
    temp_repo.commit_working_dir('Tester', 'Init')

    # Working directory changes:
    # - modify nested file
    (d / 'x.txt').write_text('v2')
    # - add file
    (temp_repo.working_dir / 'added.txt').write_text('new')
    # - remove file
    (temp_repo.working_dir / 'root_keep.txt').unlink()

    rc = cli_commands.status(working_dir_path=str(temp_repo.working_dir), repo_dir=str(temp_repo.repo_dir))
    assert rc == 0

    out = capsys.readouterr().out

    _assert_contains_all(out, 'Diff:', 'Added: added.txt', 'Removed: root_keep.txt', 'Modified: dir')

    # Nested child should appear indented under the directory diff
    lines = out.splitlines()
    found_dir = False
    found_child = False

    for i, line in enumerate(lines):
        if 'Modified: dir' in line:
            found_dir = True
            # children are printed with indent +3, so look in the next few lines
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].startswith(' ' * 3) and 'Modified: x.txt' in lines[j]:
                    found_child = True
                    break
            break

    assert found_dir, 'Directory modification should be detected'
    assert found_child, 'Nested file diff should be indented and shown'


def test_status_shows_moved_file(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / 'file1.txt').write_text('move-me')
    temp_repo.commit_working_dir('Tester', 'Init')

    (temp_repo.working_dir / 'file1.txt').rename(temp_repo.working_dir / 'moved_file.txt')

    rc = cli_commands.status(working_dir_path=str(temp_repo.working_dir), repo_dir=str(temp_repo.repo_dir))
    assert rc == 0

    out = capsys.readouterr().out

    # Depending on how you print moves, you might print either:
    #   "Moved: file1.txt -> moved_file.txt"  (MovedToDiff)
    # or:
    #   "Moved: file1.txt -> moved_file.txt" via MovedFromDiff formatting.
    # We assert the key pieces are present.
    assert 'Diff:' in out
    assert 'Moved:' in out
    _assert_contains_all(out, 'file1.txt', 'moved_file.txt')