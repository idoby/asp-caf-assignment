from pathlib import Path

from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_tags_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # initial commit
    (temp_repo.working_dir / 'test.txt').write_text('test')
    temp_repo.commit_working_dir('Author', 'Initial commit')
    
    tags = ['v1.0.0', 'v2.0.0', 'stable']

    for tag in tags:
        cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name=tag, commit_hash='HEAD')

    capsys.readouterr()

    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0

    output = capsys.readouterr().out
    lines = output.splitlines()
    
    # parse tag names from "tag_name -> commit_hash" format
    tag_names: list[str] = []
    for line in lines:
        tag_name = line.strip().split(' -> ')[0]
        tag_names.append(tag_name)

    assert len(tag_names) == len(tags)
    assert set(tag_names) == set(tags)

def test_tags_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.tags(working_dir_path=temp_repo_dir) == -1
    assert 'No repository found' in capsys.readouterr().err


def test_tags_no_tags(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    assert 'No tags found' in capsys.readouterr().out
