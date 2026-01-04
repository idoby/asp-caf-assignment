from pathlib import Path
from libcaf.repository import Repository
from caf import cli_commands
from libcaf.constants import DEFAULT_REPO_DIR, REFS_DIR, TAGS_DIR
import shutil


def test_List_tags(temp_repo: Repository , parse_commit_hash, capsys):
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check'
    ) == 0

    commit_hash = parse_commit_hash()


    assert cli_commands.create_tag(
        tag_name='Tag_1',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to check'
    ) == 0

    assert cli_commands.create_tag(
        tag_name='Tag_2',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to check'
    ) == 0

    assert cli_commands.create_tag(
        tag_name='Tag_3',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to check'
    ) == 0

    assert cli_commands.create_tag(
        tag_name='Tag_4',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to check') == 0

    assert cli_commands.list_tags(working_dir_path=temp_repo.working_dir) == 0
    
    output: str = capsys.readouterr().out
    assert "Tag_1" in output
    assert "Tag_2" in output
    assert "Tag_3" in output
    assert "Tag_4" in output



    
def test_List_tags_no_tag(temp_repo: Repository , capsys):
    assert cli_commands.list_tags(working_dir_path=temp_repo.working_dir
                                  ) == 0
    output = capsys.readouterr().out
    assert "No tags found." in output
        
        
def test_List_tags_no_repo(temp_repo_dir: Path, capsys):
    
    assert cli_commands.list_tags(working_dir_path=temp_repo_dir) == -1
    
    err = capsys.readouterr().err
    expected =temp_repo_dir / ".caf"
    assert f"No repository found at {expected}" in err





def test_List_tags_delete(temp_repo: Repository , parse_commit_hash, capsys):
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check'
    ) == 0

    commit_hash = parse_commit_hash()


    assert cli_commands.create_tag(
        tag_name='Tag_1',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to check'
        ) == 0

    assert cli_commands.create_tag(
        tag_name='Tag_2',
        commit_hash=commit_hash,
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a tag for the tester to chec'
    ) == 0

    assert cli_commands.list_tags(working_dir_path=temp_repo.working_dir
                                  ) == 0
    
    output: str = capsys.readouterr().out
    assert "Tag_1" in output
    assert "Tag_2" in output


    assert cli_commands.delete_tag(
    tag_name='Tag_2',
    working_dir_path=temp_repo.working_dir
    ) == 0

    assert cli_commands.list_tags(working_dir_path=temp_repo.working_dir
                                  ) == 0
    
    output: str = capsys.readouterr().out
    assert "Tag_1" in output

    assert cli_commands.delete_tag(
    tag_name='Tag_1',
    working_dir_path=temp_repo.working_dir
    ) == 0

    assert cli_commands.list_tags(working_dir_path=temp_repo.working_dir
                                  ) == 0
    
    
    output = capsys.readouterr().out
    assert "No tags found." in output

