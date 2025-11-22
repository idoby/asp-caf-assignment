from pathlib import Path
from collections.abc import Callable
from pytest import CaptureFixture

from libcaf.repository import Repository
from caf import cli_commands


def test_create_tag(temp_repo: Repository ,parse_commit_hash : Callable[[],str]) -> None:

    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check'
    ) == 0
    commit_hash = parse_commit_hash()

    assert cli_commands.create_tag(
    tag_name='Tag_Tester',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check') == 0


def test_create_tag_no_author(temp_repo: Repository ,parse_commit_hash : Callable[[],str]) -> None:

    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check') == 0
   
    commit_hash = parse_commit_hash()

    assert cli_commands.create_tag(
    tag_name='Tag_Tester_1',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='',
    message='Creating a tag for the tester to check') == 0


    assert cli_commands.create_tag(
    tag_name='Tag_Tester_2',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    message='Creating a tag for the tester to check') == 0
    
def test_create_tag_no_message(temp_repo: Repository ,parse_commit_hash : Callable[[],str]) -> None:
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")
    
    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check') == 0

    commit_hash = parse_commit_hash()

    assert cli_commands.create_tag(
    tag_name='Tag_Tester_1',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='') == 0


    assert cli_commands.create_tag(
    tag_name='Tag_Tester_2',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='Log Tester') == 0
    

    

def test_create_tag_no_name(temp_repo: Repository ,parse_commit_hash : Callable[[],str], capsys) -> None:
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")
    
    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check') == 0

    commit_hash = parse_commit_hash()

    assert cli_commands.create_tag(
    tag_name='',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check') == -1

    assert 'Tag has no name' in capsys.readouterr().err


    assert cli_commands.create_tag(
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check') == -1
    
    assert 'Tag name is required.' in capsys.readouterr().err

  
    

def test_create_tag_no_hash(temp_repo: Repository ,parse_commit_hash : Callable[[],str], capsys) -> None:
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")
    
    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check') == 0

    commit_hash = parse_commit_hash()

    assert cli_commands.create_tag(
    tag_name='Tag_Tester_1',
    commit_hash="",
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check') == -1
    
    assert 'Commit hash is required.' in capsys.readouterr().err
    
    assert cli_commands.create_tag(
    tag_name='Tag_Tester_2',
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check') == -1

    assert 'Commit hash is required.' in capsys.readouterr().err
    
def test_create_tag_no_exists_hash(temp_repo: Repository ,parse_commit_hash : Callable[[],str], capsys) -> None:
    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")
    
    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check') == 0

    commit_hash = parse_commit_hash()
    

    assert cli_commands.create_tag(
    tag_name='Tag_Tester_1',
    commit_hash="Fake Hash",
    working_dir_path=temp_repo.working_dir,
    author='Creating a tag for the tester to check',
    message='') == -1

    assert "Unable to resolve reference 'Fake Hash'." in capsys.readouterr().err





def test_create_tag_no_commit(temp_repo: Repository, capsys) -> None:
    assert cli_commands.create_tag(
    tag_name='Tag_Tester',
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check')  == -1

    assert 'Commit hash is required.' in capsys.readouterr().err

    assert cli_commands.create_tag(
    tag_name='Tag_Tester',
    commit_hash="",
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check')  == -1

    assert 'Commit hash is required.' in capsys.readouterr().err




     
     
def test_create_tag_no_repo(temp_repo_dir: Path, capsys) -> None:
    assert cli_commands.create_tag(tag_name='Tag_Tester',
    commit_hash='fictitious_hash',
    working_dir_path=temp_repo_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check')  == -1
    
    assert "No repository found at" in capsys.readouterr().err


def test_create_tags_same_name(temp_repo: Repository ,parse_commit_hash : Callable[[],str], capsys) -> None:

    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='Creating a commit for the tester to check'
    ) == 0
    commit_hash = parse_commit_hash()

    assert cli_commands.create_tag(
    tag_name='Tag_Tester',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check') == 0

    assert cli_commands.create_tag(
    tag_name='Tag_Tester',
    commit_hash=commit_hash,
    working_dir_path=temp_repo.working_dir,
    author='Log Tester',
    message='Creating a tag for the tester to check') == -1
    
    assert 'Tag "Tag_Tester" already exists and a new one cannot be created .' in capsys.readouterr().err







