from pathlib import Path

from libcaf.constants import CURRENT_USER_FILE, DEFAULT_REPO_DIR
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_add_user_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.add_user(working_dir_path=temp_repo.working_dir, username="alice") == 0
    out = capsys.readouterr().out
    assert 'User "alice" added.' in out or "added" in out.lower()

    user_path = temp_repo.working_dir / DEFAULT_REPO_DIR / "users" / "alice"
    assert user_path.exists()


def test_users_command_lists_users(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    cli_commands.add_user(working_dir_path=temp_repo.working_dir, username="alice")
    cli_commands.add_user(working_dir_path=temp_repo.working_dir, username="bob")

    assert cli_commands.users(working_dir_path=temp_repo.working_dir) == 0
    out = capsys.readouterr().out
    assert "alice" in out
    assert "bob" in out


def test_set_user_command(temp_repo: Repository) -> None:
    cli_commands.add_user(working_dir_path=temp_repo.working_dir, username="alice")

    assert cli_commands.set_user(working_dir_path=temp_repo.working_dir, username="alice") == 0

    current_path = temp_repo.working_dir / DEFAULT_REPO_DIR / CURRENT_USER_FILE
    assert current_path.exists()
    assert current_path.read_text(encoding="utf-8").strip() == "alice"


def test_set_user_missing_user(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.set_user(working_dir_path=temp_repo.working_dir, username="alice") == -1
    assert "does not exist" in capsys.readouterr().err.lower()


def test_whoami_command_when_set(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    cli_commands.add_user(working_dir_path=temp_repo.working_dir, username="alice")
    cli_commands.set_user(working_dir_path=temp_repo.working_dir, username="alice")

    assert cli_commands.whoami(working_dir_path=temp_repo.working_dir) == 0
    out = capsys.readouterr().out
    assert "alice" in out


def test_whoami_command_when_unset(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # no current user set
    assert cli_commands.whoami(working_dir_path=temp_repo.working_dir) == 0
    out = capsys.readouterr().out.lower()
    # accept either explicit message or empty output, depending on your implementation
    assert ("no current user" in out) or (out.strip() == "")


def test_unset_user_command(temp_repo: Repository) -> None:
    cli_commands.add_user(working_dir_path=temp_repo.working_dir, username="alice")
    cli_commands.set_user(working_dir_path=temp_repo.working_dir, username="alice")

    assert cli_commands.unset_user(working_dir_path=temp_repo.working_dir) == 0

    current_path = temp_repo.working_dir / DEFAULT_REPO_DIR / CURRENT_USER_FILE
    assert not current_path.exists()


def test_delete_user_command(temp_repo: Repository) -> None:
    cli_commands.add_user(working_dir_path=temp_repo.working_dir, username="alice")

    assert cli_commands.delete_user(working_dir_path=temp_repo.working_dir, username="alice") == 0

    user_path = temp_repo.working_dir / DEFAULT_REPO_DIR / "users" / "alice"
    assert not user_path.exists()


def test_delete_user_missing_user(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_user(working_dir_path=temp_repo.working_dir, username="alice") == -1
    assert "does not exist" in capsys.readouterr().err.lower()
