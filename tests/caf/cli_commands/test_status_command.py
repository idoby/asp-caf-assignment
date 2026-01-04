from pytest import CaptureFixture

from caf import cli_commands
from libcaf.repository import Repository


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

    (d / 'x.txt').write_text('v2')
    (temp_repo.working_dir / 'added.txt').write_text('new')
    (temp_repo.working_dir / 'root_keep.txt').unlink()

    rc = cli_commands.status(working_dir_path=str(temp_repo.working_dir), repo_dir=str(temp_repo.repo_dir))
    assert rc == 0

    out = capsys.readouterr().out
    assert 'Diff:' in out
    assert 'Added: added.txt' in out
    assert 'Removed: root_keep.txt' in out
    assert 'Modified: dir' in out
    assert 'Modified: x.txt' in out


def test_status_shows_moved_file(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / 'file1.txt').write_text('move-me')
    temp_repo.commit_working_dir('Tester', 'Init')

    (temp_repo.working_dir / 'file1.txt').rename(temp_repo.working_dir / 'moved_file.txt')

    rc = cli_commands.status(working_dir_path=str(temp_repo.working_dir), repo_dir=str(temp_repo.repo_dir))
    assert rc == 0

    out = capsys.readouterr().out
    assert 'Diff:' in out
    assert 'Moved: file1.txt -> moved_file.txt' in out