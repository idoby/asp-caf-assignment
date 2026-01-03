from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, REFS_DIR, TAGS_DIR
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_delete_tag_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # initial commit
    (temp_repo.working_dir / 'test.txt').write_text('test')
    temp_repo.commit_working_dir('Author', 'Initial commit')
    
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='v1.0.0', commit_hash='HEAD') == 0
    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir, tag_name='v1.0.0') == 0

    tag_path = temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR / 'v1.0.0'
    assert not tag_path.exists()

    assert 'Tag "v1.0.0" deleted' in capsys.readouterr().out


def test_delete_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(working_dir_path=temp_repo_dir, tag_name='v1.0.0') == -1
    assert 'No repository found' in capsys.readouterr().err


def test_delete_tag_empty(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir, tag_name='') == -1
    assert 'Tag name is required' in capsys.readouterr().err


def test_delete_tag_does_not_exist(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir, tag_name='nonexistent') == -1
    assert 'does not exist' in capsys.readouterr().err
