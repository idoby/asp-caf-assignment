import pytest
from pathlib import Path

from libcaf.repository import Repository, RepositoryError
from libcaf.ref import HashRef, read_ref
from libcaf.constants import HASH_LENGTH


""""  --------------------------- create_tag_tests ---------------------------  """

def test_create_tag_creates_ref_for_existing_commit(tmp_path: Path) -> None:
    """ create_tag should creat a tag ref file pointing to an existing commit. """

    # Arrange: initialize a new repository in a temporary working directory
    repo = Repository(working_dir=tmp_path)
    repo.init()

    # Create a file so that commit_working_dir has some content to commit
    work_file = tmp_path / "file.txt"
    work_file.write_text("hello from test create_tag")

    # Create a real commit in the repository
    commit_ref = repo.commit_working_dir(author="tester", message="initial commit")

    tag_name = "v1.0"

    # Act: create a tag that points to this commit
    repo.create_tag(tag_name, str(commit_ref))

    # Assert: a ref file was created under refs/tags/<tag_name>
    tag_path = repo.tags_dir() / tag_name
    assert tag_path.exists(), "Tag ref file was not created"

    # The tag file should contain a HashRef wuth the same commit hash
    stored_ref = read_ref(tag_path)
    assert isinstance(stored_ref, HashRef)
    assert stored_ref == commit_ref


def test_create_tag_fails_when_tag_already_exists(tmp_path: Path) -> None:
    """ create_tag should raise RepositoryError if the tag name already exists. """
    repo = Repository(working_dir=tmp_path)
    repo.init()

    work_file = tmp_path / "file.txt"
    work_file.write_text("content")

    commit_ref = repo.commit_working_dir(author="tester", message="initial commit")
    tag_name = "v1.0"

    # First creation should succeed
    repo.create_tag(tag_name, str(commit_ref))

    # Second creation with the same name should fail
    with pytest.raises(RepositoryError) as excinfo:
        repo.create_tag(tag_name, str(commit_ref))

    assert 'already exists' in str(excinfo.value)


def test_create_tag_fails_when_tag_already_exists(tmp_path: Path) -> None:
    """create_tag should raise RepositoryError if the tag name already exists."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    work_file = tmp_path / "file.txt"
    work_file.write_text("content")

    commit_ref = repo.commit_working_dir(author="tester", message="initial commit")
    tag_name = "v1.0"

    # First creation should succeed
    repo.create_tag(tag_name, str(commit_ref))

    # Second creation with the same name should fail
    with pytest.raises(RepositoryError) as excinfo:
        repo.create_tag(tag_name, str(commit_ref))

    assert 'already exists' in str(excinfo.value)


def test_create_tag_fails_for_non_existing_commit(tmp_path: Path) -> None:
    """create_tag should raise RepositoryError if the commit hash does not exist."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    tag_name = "v1.0"
    # Construct a dummy hash with the correct length, but with no object stored for it
    invalid_hash = "a" * HASH_LENGTH

    with pytest.raises(RepositoryError) as excinfo:
        repo.create_tag(tag_name, invalid_hash)

    assert 'does not exist' in str(excinfo.value)



def test_create_tag_requires_non_empty_name(tmp_path: Path) -> None:
    """create_tag should raise ValueError when called with an empty tag name."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    # We do not care about the commit hash in this test,
    # because the validation should fail earlier on the empty name.
    some_hash = "a" * HASH_LENGTH

    with pytest.raises(ValueError) as excinfo:
        repo.create_tag("", some_hash)

    assert 'Tag name is required' in str(excinfo.value)

""""  --------------------------- create_tag_tests ---------------------------  """


""""  --------------------------- delete_tag_tests ---------------------------  """

def test_delete_tag_removes_existing_tag(tmp_path: Path) -> None:
    """delete_tag should remove an existing tag ref file."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    work_file = tmp_path / "file.txt"
    work_file.write_text("content for delete_tag test")

    commit_ref = repo.commit_working_dir(author="tester", message="commit for tag")
    tag_name = "v1.0"

    # Create the tag
    repo.create_tag(tag_name, str(commit_ref))

    tag_path = repo.tags_dir() / tag_name
    assert tag_path.exists(), "Precondition: tag ref file should exist before deletion"

    # Act: delete the tag
    repo.delete_tag(tag_name)

    # Assert: tag ref file is removed
    assert not tag_path.exists(), "Tag ref file was not deleted"


def test_delete_tag_fails_when_tag_does_not_exist(tmp_path: Path) -> None:
    """delete_tag should raise RepositoryError if the tag does not exist."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    tag_name = "non-existent-tag"

    with pytest.raises(RepositoryError) as excinfo:
        repo.delete_tag(tag_name)

    assert 'does not exist' in str(excinfo.value)


def test_delete_tag_requires_non_empty_name(tmp_path: Path) -> None:
    """delete_tag should raise ValueError when called with an empty tag name."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    with pytest.raises(ValueError) as excinfo:
        repo.delete_tag("")

    assert 'Tag name is required' in str(excinfo.value)

""""  --------------------------- delete_tag_tests ---------------------------  """




