from .ref import HashRef

class TagError(Exception):
    """Base class for all tag-related errors."""

class TagNotFound(TagError):
    """Exception raised when a tag file is not located in a 'tags' directory."""

    def __init__(self, tag_file: str) -> None:
        super().__init__(f"Tag '{tag_file}' was not found in 'tags' directory")

class TagExistsError(TagError):
    """Exception raised when attempting to create a tag that already exists."""

    def __init__(self, tag_file: str) -> None:
        super().__init__(f"Tag '{tag_file}' Already Exists")

class UnknownHashError(TagError):
    """Exception raised when a provided hash is unknown(does not exist)."""

    def __init__(self, hash_str: str) -> None:
        super().__init__(f"Unknown commit hash: '{hash_str}'")

# A tag is basically just a hash reference
class Tag(HashRef):
    """Represents a tag in the version control system."""
    pass