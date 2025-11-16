# Task 1 – Project Catalog

## Root Documentation & Metadata
1. `README.md`
   - **Functionality:** Plain-language tour of CAF’s goals, commands, and layout.
   - **Purpose:** First stop for any student who needs setup or usage instructions.
   - **Relationships:** Mentions every major directory so readers know where to look next.
   - **Insight:** I reused its outline to confirm my own catalog is complete.
2. `LICENSE`
   - **Functionality:** States the project is MIT licensed.
   - **Purpose:** Lets students share or reuse pieces of the repo without legal doubt.
   - **Relationships:** Referenced by packaging metadata that ships with each module.
   - **Insight:** A permissive license fits the “learn by tinkering” spirit of the course.
3. `pyproject.toml` (root)
   - **Functionality:** Workspace-level config for metadata, pytest options, and Ruff rules.
   - **Purpose:** Keeps tooling consistent even though multiple Python packages live here.
   - **Relationships:** Pytest and Ruff read these defaults no matter which subpackage is under test.
   - **Insight:** By leaving `packages = []`, it clearly signals that packaging happens in subfolders.
4. `.envrc`
   - **Functionality:** Sets `ENABLE_COVERAGE` when `direnv` enters the repo.
   - **Purpose:** Gives the Makefile and Docker scripts a single toggle for coverage runs.
   - **Relationships:** Targets in the Makefile read the same variable to decide whether to collect coverage.
   - **Insight:** Editing one line flips coverage everywhere, so no one has to export vars manually.

## Tooling & Automation
5. `Makefile`
   - **Functionality:** Single entry point for building/running the Docker container, deploying both packages, toggling coverage, testing, and cleaning artifacts.
   - **Purpose:** Ensures every environment (local, CI, grading) runs the exact same commands.
   - **Relationships:** Calls the Dockerfile to build images, installs `libcaf` before `caf`, and forwards `ENABLE_COVERAGE` from `.envrc`.
   - **Insight:** It is the real “source of truth” for how to build and verify the hybrid Python/C++ stack.
6. `.github/workflows/tests.yml`
   - **Functionality:** GitHub Actions workflow that builds the Docker image, deploys the project with coverage, runs `make test`, and uploads results.
   - **Purpose:** Automates grading checks so reviewers trust pull requests and forks.
   - **Relationships:** Runs the same Make targets students use locally, so failures match what they would see.
   - **Insight:** Because CI rebuilds the container, there are no hidden host dependencies.
7. `deployment/Dockerfile`
   - **Functionality:** Produces the “caf-dev” image with compilers, CMake, pybind11, pytest/coverage, Ruff, and a ready-to-use virtualenv.
   - **Purpose:** Removes “works on my machine” issues when compiling `_libcaf` or running coverage-heavy tests.
   - **Relationships:** Invoked by `make build-container` and CI; its shell bootstrap copies `.envrc` so coverage flags are respected inside the container.
   - **Insight:** With every dependency pre-installed, students can go straight to `make run` instead of fighting local toolchains.

## Assignment Materials
8. `assignment/asp26-assignment1.tex`
   - **Functionality:** LaTeX source for the official assignment handout.
   - **Purpose:** Lets staff regenerate the PDF and track wording changes.
   - **Relationships:** Pulls imagery from `assignment/assets/` and produces the PDF below.
   - **Insight:** Keeping the instructions version-controlled documents the educational goals beside the code.
9. `assignment/artifacts/asp26-assignment1.pdf`
   - **Functionality:** Prebuilt PDF of the assignment.
   - **Purpose:** Students can read the brief without installing LaTeX.
   - **Relationships:** Matches the `.tex` file so anyone can diff wording vs. code changes.
   - **Insight:** Shipping both source and artifact underlines the reproducibility theme of the course.

## Python CLI Package (`caf/`)
10. `caf/pyproject.toml`
    - **Functionality:** Declares the CLI package, console entry point, and optional test extras.
    - **Purpose:** Allows `pip install -e caf` so the `caf` command is globally available.
    - **Relationships:** Called by the Makefile after `libcaf` is built to ensure bindings resolve.
    - **Insight:** Separate packaging lets the CLI evolve independently from the core library.
11. `caf/caf/__main__.py`
    - **Functionality:** Tiny bridge that simply calls `cli()` when `python -m caf` or the `caf` script runs.
    - **Purpose:** Gives Python a predictable entry point without duplicating logic.
    - **Relationships:** Imports `cli` from `caf/cli.py`; setuptools points the console script here.
    - **Insight:** Because it only forwards calls, the real behavior (and tests) stay in `cli.py`.
12. `caf/caf/cli.py`
    - **Functionality:** Builds the `argparse` command tree, registers handlers, and exits with each command’s return code.
    - **Purpose:** Centralizes user interaction so every CLI verb works the same way.
    - **Relationships:** Pulls defaults from `libcaf.constants` and calls functions in `cli_commands`.
    - **Insight:** Friendly help text and emojis show that UX matters even in a systems class.
13. `caf/caf/cli_commands.py`
    - **Functionality:** Implements each CLI verb (init, commit, branch, diff, etc.), prints user-facing messages, and returns status codes.
    - **Purpose:** Turns user actions into repository operations while keeping errors readable.
    - **Relationships:** Heavily uses `libcaf.repository.Repository`, `libcaf.plumbing`, and `libcaf.ref`.
    - **Insight:** Doing the work here keeps the CLI layer thin and easy to extend.

## Python Library Layer (`libcaf/libcaf`)
14. `libcaf/pyproject.toml`
    - **Functionality:** Configures scikit-build-core so `pip install -e libcaf` compiles the C++ sources.
    - **Purpose:** Packages the native module plus its Python glue in one command.
    - **Relationships:** The Makefile passes `CMAKE_ARGS` through this file to toggle coverage.
    - **Insight:** Using scikit-build keeps the packaging story close to standard Python tooling.
15. `libcaf/CMakeLists.txt`
    - **Functionality:** Describes how to build `_libcaf` (sources, warnings-as-errors, optional coverage flags).
    - **Purpose:** Guarantees a consistent native build whether you run pip locally or in CI.
    - **Relationships:** Reads the `ENABLE_COVERAGE` option set by the Makefile/Docker image.
    - **Insight:** Treating the extension as a MODULE drops the `.so` right next to the Python package for easy imports.
16. `_libcaf.cpython-*.so` and `_libcaf.pyi`
    - **Functionality:** Compiled pybind11 extension plus matching type stubs.
    - **Purpose:** Provide fast hashing, IO, and data structures that Python code imports.
    - **Relationships:** Re-exported by `libcaf/__init__.py` and wrapped by `plumbing.py`.
    - **Insight:** Shipping stubs with the binary keeps IDEs lint-friendly even for native code.
17. `libcaf/libcaf/__init__.py`
    - **Functionality:** Re-exports Blob/Tree/Commit classes from `_libcaf`.
    - **Purpose:** Lets other modules import from `libcaf` without reaching into the private extension.
    - **Relationships:** Used by every other Python file in `libcaf`.
    - **Insight:** Thin facades like this make renaming the extension painless later.
18. `libcaf/libcaf/constants.py`
    - **Functionality:** Stores repo-wide constants (e.g., `.caf`, `objects`, `HEAD`) and queries `_libcaf` for hash length.
    - **Purpose:** Keeps directory names and hash metadata consistent.
    - **Relationships:** Read by CLI defaults, repository paths, and ref utilities.
    - **Insight:** Having one source for names avoids magic strings across the codebase.
19. `libcaf/libcaf/plumbing.py`
    - **Functionality:** Python-friendly wrappers around `_libcaf` for hashing, saving blobs/trees/commits, and opening file descriptors.
    - **Purpose:** Shields higher layers from low-level file-handle juggling.
    - **Relationships:** Called by `Repository`, CLI commands, and tests that need direct object IO.
    - **Insight:** Normalizing `Path` vs. `str` handling here prevents subtle bugs elsewhere.
20. `libcaf/libcaf/ref.py`
    - **Functionality:** Defines `HashRef`, `SymRef`, parser/writer helpers, and validation logic.
    - **Purpose:** Encapsulates Git-style reference handling.
    - **Relationships:** Used across `Repository` and CLI branch commands.
    - **Insight:** Lightweight classes inherited from `str` stay ergonomic while still type-checked.
21. `libcaf/libcaf/repository.py`
    - **Functionality:** High-level API for repos: init, branch management, commits, logs, diffs, and helper dataclasses.
    - **Purpose:** Serves as the “porcelain” layer every other component calls.
    - **Relationships:** Depends on constants, plumbing, refs, and the `_libcaf` data types.
    - **Insight:** The `requires_repo` decorator is a great guardrail against using an uninitialized repo.

## Native Core (`libcaf/src`)
22. `caf.h` / `caf.cpp`
    - **Functionality:** Implement hashing, blob storage layout, file locking, and content read/write operations using OpenSSL and POSIX calls.
    - **Purpose:** Provide the high-speed, race-safe foundation for content-addressable storage.
    - **Relationships:** Wrapped by pybind11 so Python can call these routines, and used by `object_io`.
    - **Insight:** Directory sharding by hash prefix mirrors Git and keeps filesystem performance stable.
23. `hash_types.h` / `hash_types.cpp`
    - **Functionality:** Define overloaded `hash_object` helpers for blobs, trees, and commits.
    - **Purpose:** Ensure every object type has a consistent hashing recipe.
    - **Relationships:** Called by `object_io` and exposed to Python via `_libcaf`.
    - **Insight:** Hashing tree records deterministically is key for accurate diffs.
24. `object_io.h` / `object_io.cpp`
    - **Functionality:** Serialize and deserialize commits and trees with length-prefixed binary formats and strict locking.
    - **Purpose:** Turn rich objects into bytes stored under their hash and back again.
    - **Relationships:** Use the file helpers from `caf.cpp` and hashing from `hash_types.cpp`.
    - **Insight:** The `MAX_LENGTH` guardrails defend against corrupt inputs—important in a student repo.
25. `blob.h`, `commit.h`, `tree_record.h`, `tree.h`
    - **Functionality:** Define the in-memory C++ data structures used across the native core.
    - **Purpose:** Provide strong typing for pybind11 and internal helpers.
    - **Relationships:** Included by almost every native file and mirrored on the Python side.
    - **Insight:** Immutable members (const fields) emphasize that repository objects never mutate.
26. `bind.cpp`
    - **Functionality:** Pybind11 module that exposes hashing, IO helpers, and the data classes to Python.
    - **Purpose:** Acts as the bridge between C++ speed and Python ergonomics.
    - **Relationships:** Depends on every header above and compiles into `_libcaf`.
    - **Insight:** Keeping bindings small means most logic stays testable from Python.
27. `libcaf/build/`
    - **Functionality:** CMake build output folder created when compiling `_libcaf`.
    - **Purpose:** Stores intermediate objects and caches; safe to delete between builds.
    - **Relationships:** Referenced indirectly by Makefile clean targets.
    - **Insight:** Its presence reminds us to rebuild whenever dependencies change.

## Test Suite
28. `tests/conftest.py`
    - **Functionality:** Pytest fixtures for temp repos, random files, and CLI output parsing.
    - **Purpose:** Gives every test an isolated workspace without repeated setup code.
    - **Relationships:** Shared by both CLI and library tests.
    - **Insight:** The `parse_commit_hash` helper codifies CLI output format, so regressions are caught quickly.
29. `tests/libcaf/*.py`
    - **Functionality:** Unit tests for repository internals (hashing, refs, diffs, object IO, etc.).
    - **Purpose:** Prove the Python layer around the native module behaves correctly.
    - **Relationships:** Hit `repository.py`, `ref.py`, `plumbing.py`, and the pybind11 classes directly.
    - **Insight:** These tests double as executable documentation for tricky repo edge cases.
30. `tests/caf/cli_commands/*.py`
    - **Functionality:** Tests for each CLI verb that assert outputs, exit codes, and repo effects.
    - **Purpose:** Ensure the user-facing commands stay stable and friendly.
    - **Relationships:** Depend on the fixtures above and call into CLI command functions.
    - **Insight:** One-file-per-command layout makes it obvious where to add new coverage.

## Deliverables
31. `task1.md`
    - **Functionality:** Holds this structured catalog for Task 1.
    - **Purpose:** Demonstrates codebase understanding as required by the assignment.
    - **Relationships:** References everything above so later tasks can link back here.
    - **Insight:** Writing it forced me to trace data flow end-to-end, which will help with future debugging.
32. `stupidprogex.md`
    - **Functionality:** Kid-friendly story that explains CAF using the “librarian and robot” analogy.
    - **Purpose:** Helps non-programmers grasp why the project mixes Python and C++.
    - **Relationships:** Distills the same concepts found in README and this catalog into simpler words.
    - **Insight:** Translating ideas for kids is a good test that I actually understand them myself.
