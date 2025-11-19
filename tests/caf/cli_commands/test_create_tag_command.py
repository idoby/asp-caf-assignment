
from libcaf.repository import Repository
from caf import cli_commands
from collections.abc import Callable 







def test_create_tag(temp_repo: Repository ,parse_commit_hash : Callable[[],str]) -> None:

    file = temp_repo.working_dir / "test_file.txt"
    file.write_text("file for tag check")

    assert cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author='Log Tester',
        message='first commit'
    ) == 0
    commit_hash1 = parse_commit_hash()

    assert cli_commands.create_tag('first try',commit_hash,
                               author='Log Tester', message='first try') == 0
    
    assert cli_commands.create_tag('secound try',commit_hash,
                               author='', message='secound try') == 0

    assert cli_commands.create_tag('third try',commit_hash,
                               author='Log Tester', message='') == 0


# def test_create_tag_no_commit(temp_repo: Repository) -> None:
#     assert cli_commands.create_tag('first try',commit_hash,
#                                author='Log Tester', message='first try') == 0
    

# def test_create_tag_no_repo(temp_repo_dir: Path) -> None:
#     assert cli_commands.create_command("try",working_dir_path=temp_repo.working_dir,
#                                author='Log Tester', message="try without repo") == 0








# def test_create_command_no_commit(temp_repo: Repository) -> None:


#     assert cli_commands.add_branch(working_dir_path=temp_repo.working_dir) == -1
#     assert 'Branch name is required' in capsys.readouterr().err


# def test_add_branch_twice(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
#     assert cli_commands.add_branch(working_dir_path=temp_repo.working_dir, branch_name='feature') == 0
#     assert cli_commands.add_branch(working_dir_path=temp_repo.working_dir, branch_name='feature') == -1

#     assert 'Branch "feature" already exists' in capsys.readouterr().err


