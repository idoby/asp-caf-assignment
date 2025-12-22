from datetime import datetime
from libcaf.repository import Repository, RepositoryError
from libcaf.plumbing import save_commit, save_tree
from libcaf.ref import write_ref
from pytest import raises

def test_common_ancestor_same_commit(temp_repo: Repository) -> None:
    temp_repo.init()
    temp_file = temp_repo.working_dir / 'file.txt'
    temp_file.write_text('content')
    c1 = temp_repo.commit_working_dir('Author', 'Commit 1')
    
    assert temp_repo.get_common_ancestor(c1, c1) == c1

def test_common_ancestor_parent_child(temp_repo: Repository) -> None:
    temp_repo.init()
    temp_file = temp_repo.working_dir / 'file.txt'
    
    temp_file.write_text('v1')
    c1 = temp_repo.commit_working_dir('Author', 'Commit 1')
    
    temp_file.write_text('v2')
    c2 = temp_repo.commit_working_dir('Author', 'Commit 2')
    
    assert temp_repo.get_common_ancestor(c1, c2) == c1
    assert temp_repo.get_common_ancestor(c2, c1) == c1

def test_common_ancestor_diverged(temp_repo: Repository) -> None:
    temp_repo.init()
    temp_file = temp_repo.working_dir / 'file.txt'
    
    # Base
    temp_file.write_text('base')
    base = temp_repo.commit_working_dir('Author', 'Base')
    
    # Branch 1
    # Update master ref to base (it is already there, but just to be sure/explicit if we moved it)
    # Actually commit_working_dir advances HEAD.
    
    # Create Branch 1
    temp_file.write_text('b1')
    c1 = temp_repo.commit_working_dir('Author', 'Branch 1')
    
    # Reset HEAD to base to create Branch 2 from base
    write_ref(temp_repo.heads_dir() / 'master', base)
    
    # Create Branch 2
    temp_file.write_text('b2')
    c2 = temp_repo.commit_working_dir('Author', 'Branch 2')
    
    assert temp_repo.get_common_ancestor(c1, c2) == base

def test_common_ancestor_criss_cross(temp_repo: Repository) -> None:
    temp_repo.init()
    objects_dir = temp_repo.objects_dir()
    
    # Create a dummy tree
    tree_hash = save_tree(objects_dir, [])
    
    # A
    c_a = save_commit(objects_dir, tree_hash, [], 'Author', 'A', datetime.now())
    
    # B (parent A)
    c_b = save_commit(objects_dir, tree_hash, [c_a], 'Author', 'B', datetime.now())
    
    # C (parent A)
    c_c = save_commit(objects_dir, tree_hash, [c_a], 'Author', 'C', datetime.now())
    
    # D (parents B, C) - Merge commit
    c_d = save_commit(objects_dir, tree_hash, [c_b, c_c], 'Author', 'D', datetime.now())
    
    # E (parent D)
    c_e = save_commit(objects_dir, tree_hash, [c_d], 'Author', 'E', datetime.now())
    
    # Now find ancestor of B and C -> A
    assert temp_repo.get_common_ancestor(c_b, c_c) == c_a
    
    # Ancestor of D and A -> A
    assert temp_repo.get_common_ancestor(c_d, c_a) == c_a
    
    # Ancestor of E and B -> B (since B is ancestor of D which is ancestor of E)
    assert temp_repo.get_common_ancestor(c_e, c_b) == c_b

def test_common_ancestor_no_common(temp_repo: Repository) -> None:
    temp_repo.init()
    objects_dir = temp_repo.objects_dir()
    tree_hash = save_tree(objects_dir, [])
    
    c1 = save_commit(objects_dir, tree_hash, [], 'Author', '1', datetime.now())
    c2 = save_commit(objects_dir, tree_hash, [], 'Author', '2', datetime.now())
    
    assert temp_repo.get_common_ancestor(c1, c2) is None

def test_common_ancestor_error(temp_repo: Repository) -> None:
    temp_repo.init()
    with raises(RepositoryError):
        temp_repo.get_common_ancestor('1' * 40, '2' * 40)
