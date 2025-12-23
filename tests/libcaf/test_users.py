from libcaf.repository import Repository, RepositoryError
from pytest import raises


def test_users_initially_empty(temp_repo: Repository) -> None:
    assert temp_repo.users() == []


def test_add_user_and_list(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")

    assert "alice" in temp_repo.users()


def test_add_user_twice_is_idempotent(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")
    temp_repo.add_user("alice")  # should be a no-op

    assert "alice" in temp_repo.users()
    assert (temp_repo.users_dir() / "alice").exists()


def test_add_user_empty_raises_value_error(temp_repo: Repository) -> None:
    with raises(ValueError, match="Username is required"):
        temp_repo.add_user("")


def test_add_user_invalid_name_raises_value_error(temp_repo: Repository) -> None:
    with raises(ValueError):
        temp_repo.add_user("a/b")


def test_set_current_user_success(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")
    temp_repo.set_current_user("alice")

    assert temp_repo.current_user() == "alice"
    assert temp_repo.current_user_file().read_text(encoding="utf-8").strip() == "alice"


def test_set_current_user_missing_user_raises(temp_repo: Repository) -> None:
    with raises(RepositoryError, match='User "alice" does not exist'):
        temp_repo.set_current_user("alice")


def test_unset_current_user(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")
    temp_repo.set_current_user("alice")
    temp_repo.unset_current_user()

    assert temp_repo.current_user() is None


def test_delete_user_success(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")
    temp_repo.delete_user("alice")

    assert "alice" not in temp_repo.users()
    assert not (temp_repo.users_dir() / "alice").exists()


def test_delete_nonexistent_user_raises(temp_repo: Repository) -> None:
    with raises(RepositoryError, match='User "alice" does not exist'):
        temp_repo.delete_user("alice")


def test_delete_user_unsets_if_current(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")
    temp_repo.set_current_user("alice")

    temp_repo.delete_user("alice")

    assert temp_repo.current_user() is None
    assert not temp_repo.current_user_file().exists()


def test_current_user_auto_unsets_if_stale(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")
    temp_repo.set_current_user("alice")

    # simulate external deletion (concurrency / manual)
    (temp_repo.users_dir() / "alice").unlink()

    assert temp_repo.current_user() is None
    assert not temp_repo.current_user_file().exists()
    
    
def test_multiple_users_and_switch_current(temp_repo: Repository) -> None:
    temp_repo.add_user("alice")
    temp_repo.add_user("bob")

    users = temp_repo.users()
    assert "alice" in users
    assert "bob" in users

    temp_repo.set_current_user("alice")
    assert temp_repo.current_user() == "alice"

    temp_repo.set_current_user("bob")
    assert temp_repo.current_user() == "bob"
