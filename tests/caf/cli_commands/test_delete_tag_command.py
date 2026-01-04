from pathlib import Path
from libcaf.repository import Repository
from caf import cli_commands


def test_delete_tag(temp_repo: Repository , parse_commit_hash, capsys):
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check'
    ) == 0

    commit_hash = parse_commit_hash()


    assert cli_commands.create_tag(
        tag_name='Tag',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to check'
    ) == 0
    

    assert cli_commands.delete_tag(
        tag_name='Tag',
        working_dir_path=temp_repo.working_dir
    ) == 0


    assert not (temp_repo.tags_dir() / 'Tag').exists()



def test_delete_tag_not_exists(temp_repo: Repository , capsys):
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.delete_tag(
        tag_name='tag',
        working_dir_path=temp_repo.working_dir
    ) == -1

    assert 'A tag with that name does not exist' in capsys.readouterr().err



def test_delete_tag_no_name(temp_repo: Repository , capsys):
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.delete_tag(
        tag_name=None,
        working_dir_path=temp_repo.working_dir
    ) == -1

    assert 'Tag name is required.' in capsys.readouterr().err



def test_delete_tag_no_repo(temp_repo_dir: Path, capsys):
    assert cli_commands.delete_tag(
        tag_name='Tag',
        working_dir_path=temp_repo_dir
    ) == -1

    assert "No repository found at" in capsys.readouterr().err



def test_delete_tag_twice(temp_repo: Repository , parse_commit_hash, capsys):
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check'
    ) == 0
    commit_hash = parse_commit_hash()

    
    assert cli_commands.create_tag(
        tag_name='Tag',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to check'
    ) == 0


    assert cli_commands.delete_tag(
        tag_name='Tag',
        working_dir_path=temp_repo.working_dir
    ) == 0


    assert cli_commands.delete_tag(
        tag_name='Tag',
        working_dir_path=temp_repo.working_dir
    ) == -1

    assert 'A tag with that name does not exist' in capsys.readouterr().err