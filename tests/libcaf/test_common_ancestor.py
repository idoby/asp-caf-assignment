from datetime import datetime
from libcaf.repository import Repository, RepositoryError
from libcaf.plumbing import save_commit, save_tree, load_commit
from libcaf.ref import write_ref
from pytest import raises
from pathlib import Path



def test_common_ancestor_same_commit(temp_repo: Repository) -> None:
    # if temp_repo.exists():
    #     temp_repo.delete_repo()
    # temp_repo.init()
    temp_file = temp_repo.working_dir / 'file.txt'
    temp_file.write_text('content')
    c1 = temp_repo.commit_working_dir('Author', 'Commit 1')
    
    assert temp_repo.get_common_ancestor(c1, c1) == c1

def test_common_ancestor_parent_child(temp_repo: Repository) -> None:
    # if temp_repo.exists():
    #     temp_repo.delete_repo()
    # temp_repo.init()
    temp_file = temp_repo.working_dir / 'file.txt'
    
    temp_file.write_text('v1')
    c1 = temp_repo.commit_working_dir('Author', 'Commit 1')
    
    temp_file.write_text('v2')
    c2 = temp_repo.commit_working_dir('Author', 'Commit 2')
    
    assert temp_repo.get_common_ancestor(c1, c2) == c1
    assert temp_repo.get_common_ancestor(c2, c1) == c1

def test_common_ancestor_diverged(temp_repo: Repository) -> None:
    # if temp_repo.exists():
    #     temp_repo.delete_repo()
    # temp_repo.init()
    temp_file = temp_repo.working_dir / 'file.txt'

    temp_file.write_text('base')
    base = temp_repo.commit_working_dir('Author', 'Base')

    temp_file.write_text('b1')
    c1 = temp_repo.commit_working_dir('Author', 'Branch 1')

    write_ref(temp_repo.repo_path() / "HEAD", base)

    temp_file.write_text('b2')
    c2 = temp_repo.commit_working_dir('Author', 'Branch 2')
    
    assert temp_repo.get_common_ancestor(c1, c2) == base

def test_common_ancestor_no_common(temp_repo: Repository) -> None:
    # if temp_repo.exists():
    #     temp_repo.delete_repo()
    # temp_repo.init()

    (temp_repo.working_dir / "a.txt").write_text("a")
    c1 = temp_repo.commit_working_dir("Author", "1")

    (temp_repo.repo_path() / "HEAD").write_text("ref: heads/isolated\n")
    isolated_ref: Path = temp_repo.refs_dir() / "heads" / "isolated"
    isolated_ref.parent.mkdir(parents=True, exist_ok=True)
    isolated_ref.write_text("")

    (temp_repo.working_dir / "b.txt").write_text("b")
    c2 = temp_repo.commit_working_dir("Author", "2")

    assert temp_repo.get_common_ancestor(c1, c2) is None

def test_common_ancestor_error(temp_repo: Repository) -> None:
    if temp_repo.exists():
        temp_repo.delete_repo()
    temp_repo.init()
    with raises(RuntimeError):
        temp_repo.get_common_ancestor('1' * 40, '2' * 40)
