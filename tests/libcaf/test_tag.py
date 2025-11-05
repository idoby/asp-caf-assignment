from pathlib import Path
import pytest
from libcaf.ref import HashRef
from libcaf.constants import HASH_LENGTH
from libcaf.tag import (Tag, TagError, TagNotInTagsDirError, TagAlreadyExistsError, write_tag)

@pytest.fixture
def tags_dir(tmp_path: Path) -> Path:
    """Creates a 'tags' directory for testing."""
    tags_path = tmp_path / 'tags'
    tags_path.mkdir()
    return tags_path

@pytest.fixture
def valid_tag_file(tags_dir: Path) -> Path:
    """Provides a path to a valid tag file."""
    return tags_dir / 'v1.0'

@pytest.fixture
def dummy_tag() -> Tag:
    """Returns a dummy tag (HashRef)."""
    return Tag('a' * HASH_LENGTH)

def test_write_tag_success(valid_tag_file: Path, dummy_tag: Tag):
    """Tests that write_tag successfully writes a tag file."""
    write_tag(valid_tag_file, dummy_tag)
    assert valid_tag_file.read_text() == dummy_tag

def test_write_tag_already_exists(valid_tag_file: Path, dummy_tag: Tag):
    """Tests that write_tag fails if the tag file already exists."""
    write_tag(valid_tag_file, dummy_tag)  # Write it once
    
    with pytest.raises(TagAlreadyExistsError):
        write_tag(valid_tag_file, dummy_tag)  # Try to write it again

def test_write_tag_not_in_tags_dir(tmp_path: Path, dummy_tag: Tag):
    """Tests that write_tag fails if the path is not in a 'tags' directory."""
    invalid_file = tmp_path / 'v1.0'
    
    with pytest.raises(TagNotInTagsDirError):
        write_tag(invalid_file, dummy_tag)