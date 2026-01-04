import pytest
from pathlib import Path
from libcaf.repository import RepositoryNotFoundError,Repository, RepositoryError, TagError


#create test
def test_create_tag(temp_repo, parse_commit_hash):
    f = temp_repo.working_dir / "test_file.txt"
    f.write_text("file for tag check")

    commit_hash = temp_repo.commit_working_dir(
        author="Tag Tester",
        message="Creating a commit for the tester to check"
    )

    temp_repo.create_tag("Tag", commit_hash)
    
    tag_path = temp_repo.tags_dir() / "Tag"

    assert tag_path.exists()


def test_create_tags_same_name(temp_repo, parse_commit_hash):
    f = temp_repo.working_dir / "test_file.txt"
    f.write_text("file for tag check")

    commit_hash = temp_repo.commit_working_dir(
        author="Tag Tester",
        message="Creating a commit for the tester to check"
    )

    temp_repo.create_tag("Tag", commit_hash)
    

    with pytest.raises(TagError): temp_repo.create_tag("Tag", commit_hash)



def test_create_tag_no_name(temp_repo,parse_commit_hash):
    f = temp_repo.working_dir / "test_file.txt"
    f.write_text("file for tag check")

    commit_hash = temp_repo.commit_working_dir(
        author="Tag Tester",
        message="Creating a commit for the tester to check"
    )
    
    with pytest.raises(ValueError): temp_repo.create_tag("" ,commit_hash)
    


def test_create_tag_no_commit(temp_repo):
  
    with pytest.raises(RepositoryError): temp_repo.create_tag("Tag")


def test_create_tag_without_no_hash_and_commit(temp_repo):
    with pytest.raises(RepositoryError): temp_repo.create_tag("Tag", commit_hash="FAKE HASH")


def test_create_tag_without_hash(temp_repo):
    f = temp_repo.working_dir / "test_file.txt"
    f.write_text("file for tag check")

    commit_hash = temp_repo.commit_working_dir(
        author="Tag Tester",
        message="Creating a commit for the tester to check"
    )
    #without hash
    temp_repo.create_tag("Tag_Tester")
    assert "Tag_Tester" in temp_repo.list_tags()

def test_create_tag_no_repo(temp_repo_dir: Path):
    repo = Repository(temp_repo_dir)  
    with pytest.raises(RepositoryNotFoundError): repo.create_tag("Tag", "There is no commit")



#delete test

def test_delete_tag(temp_repo, parse_commit_hash):
    f = temp_repo.working_dir / "test_file.txt"
    f.write_text("file for tag check")

    commit_hash = temp_repo.commit_working_dir(
        author="Tag Tester",
        message="Creating a commit for the tester to check"
    
    )

    temp_repo.create_tag("Tag", commit_hash)

    
    assert "Tag" in temp_repo.list_tags()

    temp_repo.delete_tag("Tag")

    assert "Tag" not in temp_repo.list_tags()


def test_delete_tag_not_exist(temp_repo):
   
    with pytest.raises(RepositoryError): temp_repo.delete_tag("FAKE TAG")

def test_delete_tag_no_repo(temp_repo_dir):
    repo = Repository(temp_repo_dir)
    with pytest.raises(RepositoryNotFoundError):repo.delete_tag("Tag")

def test_delete_tag_no_name(temp_repo):
    with pytest.raises(ValueError): temp_repo.delete_tag("")


#list tag


def test_list_tags(temp_repo, parse_commit_hash):
    f = temp_repo.working_dir / "test_file.txt"
    f.write_text("file for tag check")

    commit_hash = temp_repo.commit_working_dir(
        author="Tag Tester",
        message="Creating a commit for the tester to check"
    
    )

    temp_repo.create_tag("Tag_1", commit_hash)
    temp_repo.create_tag("Tag_2", commit_hash)
    temp_repo.create_tag("Tag_3", commit_hash)
    temp_repo.create_tag("Tag_4", commit_hash)


    tags = temp_repo.list_tags()
    assert set(tags) == {"Tag_1", "Tag_2", "Tag_3","Tag_4"}


def test_list_tags_no_tags(temp_repo):
   
    assert temp_repo.list_tags() == []

def test_list_tags_empty_dir(temp_repo):
    
    temp_repo.tags_dir().mkdir(parents=True, exist_ok=True)
    assert temp_repo.list_tags() == []


def test_list_tags_no_repo(temp_repo_dir: Path):
    repo = Repository(temp_repo_dir)  
    with pytest.raises(RepositoryNotFoundError):  repo.list_tags()
