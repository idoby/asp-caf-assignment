from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, REFS_DIR, TAGS_DIR
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_create_tag_command(temp_repo: Repository) -> None:
    # initial commit
    (temp_repo.working_dir / 'test.txt').write_text('test')
    temp_repo.commit_working_dir('Author', 'Initial commit')
    
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir, 
        tag_name='v1.0.0',
        commit_hash='HEAD'
    ) == 0

    tag_path = temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR / 'v1.0.0'
    assert tag_path.exists()


def test_create_tag_missing_name(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir) == -1
    assert 'Tag name is required' in capsys.readouterr().err


def test_create_tag_twice(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    #  initial commit
    (temp_repo.working_dir / 'test.txt').write_text('test')
    temp_repo.commit_working_dir('Author', 'Initial commit')
    
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='v1.0.0', commit_hash='HEAD') == 0
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='v1.0.0', commit_hash='HEAD') == -1

    assert 'Tag "v1.0.0" already exists' in capsys.readouterr().err


def test_create_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(working_dir_path=temp_repo_dir, tag_name='v1.0.0') == -1
    assert 'No repository found at' in capsys.readouterr().err
