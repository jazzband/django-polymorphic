set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set unstable := true
set script-interpreter := ['uv', 'run', '--script']

export PYTHONPATH := source_directory()

[private]
default:
    @just --list --list-submodules

# run the django admin
[script]
manage *COMMAND:
    import os
    import sys
    from django.core import management
    sys.path.append(os.getcwd())
    os.environ["DJANGO_SETTINGS_MODULE"] = "polymorphic.tests.debug"
    os.environ["SQLITE_DATABASES"] = "test1.db,test2.db"
    management.execute_from_command_line(sys.argv + "{{ COMMAND }}".split(" "))

# install the uv package manager
[linux]
[macos]
install_uv:
    curl -LsSf https://astral.sh/uv/install.sh | sh

# install the uv package manager
[windows]
install_uv:
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# setup the venv, pre-commit hooks and playwright dependencies
setup python="python":
    uv venv -p {{ python }}
    @just install-precommit

# install git pre-commit hooks
install-precommit:
    @just run --no-default-groups --group precommit --exact pre-commit install

# update and install development dependencies
install *OPTS:
    uv sync {{ OPTS }}
    @just install-precommit

# install playwright dependencies
install-playwright:
    @just run --no-default-groups --group test playwright install chromium

# run static type checking with mypy
check-types-mypy *RUN_ARGS:
    @just run --no-default-groups --all-extras --group integrations --group typing {{ RUN_ARGS }} mypy src/polymorphic

# run static type checking with pyright
check-types-pyright *RUN_ARGS:
    @just run --no-default-groups --all-extras --group integrations --group typing {{ RUN_ARGS }} pyright src/polymorphic
    @just run --no-default-groups --all-extras --group integrations --group typing {{ RUN_ARGS }} pyright --project src/polymorphic/tests/examples/type_hints/pyright.json

# run all static type checking
check-types: check-types-mypy check-types-pyright

# run all static type checking in an isolated environment
check-types-isolated:
    @just check-types-mypy --exact --isolated
    @just check-types-pyright --exact --isolated

# run package checks
check-package:
    @just run --no-default-groups pip check
    uv pip check

# remove doc build artifacts-
[script]
clean-docs:
    import shutil
    shutil.rmtree('./docs/_build', ignore_errors=True)

# remove the virtual environment
[script]
clean-env:
    import shutil
    import sys
    shutil.rmtree(".venv", ignore_errors=True)

# remove all git ignored files
clean-git-ignored:
    git clean -fdX

# remove all non repository artifacts
clean: clean-docs clean-env clean-git-ignored

# build html documentation
build-docs-html:
    @just run --group docs --group integrations sphinx-build --fresh-env --builder html --doctree-dir ./docs/_build/doctrees ./docs/ ./docs/_build/html

# build pdf documentation
build-docs-pdf:
    @just run --group docs --group integrations sphinx-build --fresh-env --builder latex --doctree-dir ./docs/_build/doctrees ./docs/ ./docs/_build/pdf
    cd docs/_build/pdf && make

# build the docs
build-docs: build-docs-html

# build docs and package
build: build-docs-html
    @just manage compilemessages --ignore ".venv/*"
    uv build

# regenerate test migrations using the lowest version of Django
remake-test-migrations:
    - rm src/polymorphic/tests/migrations/00*.py
    - rm src/polymorphic/tests/deletion/migrations/00*.py
    - rm src/polymorphic/tests/other/migrations/00*.py
    - rm src/polymorphic/tests/examples/**/migrations/00*.py
    - rm src/polymorphic/tests/examples/integrations/**/migrations/00*.py
    uv run --no-default-groups  --exact --isolated --resolution lowest-direct --group integrations --script ./manage.py makemigrations

# open the html documentation
[script]
open-docs:
    import os
    import webbrowser
    webbrowser.open(f'file://{os.getcwd()}/docs/_build/html/index.html')

# build and open the documentation
docs: build-docs-html open-docs

# serve the documentation, with auto-reload
docs-live:
    @just run --no-default-groups --group docs --group integrations sphinx-autobuild docs docs/_build --open-browser --watch src --port 8000 --delay 1

_link_check:
    -uv run --no-default-groups --group docs sphinx-build -b linkcheck -Q -D linkcheck_timeout=10 ./docs/ ./docs/_build

# check the documentation links for broken links
[script]
check-docs-links: _link_check
    import os
    import sys
    import json
    from pathlib import Path
    # The json output isn't valid, so we have to fix it before we can process.
    data = json.loads(f"[{','.join((Path(os.getcwd()) / 'docs/_build/output.json').read_text().splitlines())}]")
    broken_links = [link for link in data if link["status"] not in {"working", "redirected", "unchecked", "ignored"}]
    if broken_links:
        for link in broken_links:
            print(f"[{link['status']}] {link['filename']}:{link['lineno']} -> {link['uri']}", file=sys.stderr)
        sys.exit(1)

# lint the documentation
check-docs:
    @just run --no-default-groups --group lint doc8 --ignore-path ./docs/_build --max-line-length 100 -q ./docs

# lint the code
check-lint:
    @just run --no-default-groups --group lint ruff check --select I
    @just run --no-default-groups --group lint ruff check

# check if the code needs formatting
check-format:
    @just run --no-default-groups --group lint ruff format --check
    @just run --no-default-groups --group lint ruff format --line-length 80 --check src/polymorphic/tests/examples

# check that the readme renders
check-readme:
    @just run --no-default-groups --group lint -m readme_renderer ./README.md -o /tmp/README.html

_check-readme-quiet:
    @just --quiet check-readme

# sort the python imports
sort-imports:
    @just run --no-default-groups --group lint ruff check --fix --select I

# format the code and sort imports
format: sort-imports
    just --fmt --unstable
    @just run --no-default-groups --group lint ruff format
    @just run --no-default-groups --group lint ruff format --line-length 80 src/polymorphic/tests/examples

# sort the imports and fix linting issues
lint: sort-imports
    @just run --no-default-groups --group lint ruff check --fix

# fix formatting, linting issues and import sorting
fix: lint format

# run all static checks
check: check-lint check-format check-types check-docs _check-readme-quiet check-package

# run all checks including documentation link checking (slow)
check-all: check check-docs-links

[script]
_lock-python:
    import tomlkit
    import sys
    f='pyproject.toml'
    d=tomlkit.parse(open(f).read())
    d['project']['requires-python']='=={}'.format(sys.version.split()[0])
    open(f,'w').write(tomlkit.dumps(d))

# lock to specific python and versions of given dependencies
test-lock +PACKAGES: _lock-python
    uv add --no-sync {{ PACKAGES }}

# run tests
test *TESTS:
    @just run --no-default-groups --exact --group test --isolated pytest {{ TESTS }} --cov 

# test against the specified database backend
test-db DB_CLIENT="dev" *TESTS:
    # No Optional Dependency Unit Tests
    # todo clean this up, rerunning a lot of tests
    @just run --no-default-groups --exact --group test --isolated --group {{ DB_CLIENT }} pytest {{ TESTS }} --cov 

# test django-revision integration
test-reversion *TESTS:
    @just run --no-default-groups --group reversion --group test --exact --isolated pytest -m integration src/polymorphic/tests/examples/integrations/reversion {{ TESTS }}

# test django extra views integration
test-extra-views *TESTS:
    @just run --no-default-groups --group extra-views --group test --exact --isolated pytest -m integration src/polymorphic/tests/examples/integrations/extra_views {{ TESTS }}

# test django rest framework integration
test-drf *TESTS:
    @just run --no-default-groups --no-default-groups --group drf --group test --exact --isolated pytest -m integration src/polymorphic/tests/examples/integrations/drf {{ TESTS }}

# test guardian integration
test-guardian *TESTS:
    @just run --no-default-groups --group guardian --group test --exact --isolated pytest -m integration src/polymorphic/tests/examples/integrations/guardian {{ TESTS }}

# run all third party integration tests
test-integrations DB_CLIENT="dev":
    # Integration Tests
    @just run --no-default-groups --group {{ DB_CLIENT }} --group integrations --group guardian --group reversion --group test --exact --isolated pytest -m integration --cov --cov-append

# debug an test
debug-test *TESTS:
    @just run pytest \
      -o addopts='-ra -q' \
      -s --trace --pdbcls=IPython.terminal.debugger:Pdb \
      --headed {{ TESTS }}

# run the pre-commit checks
precommit:
    @just run pre-commit

# generate the test coverage report
coverage:
    @just run --no-default-groups--group coverage coverage combine --keep *.coverage
    @just run --no-default-groups --group coverage coverage report
    @just run --no-default-groups --group coverage coverage xml

_install-docs:
    uv sync --no-default-groups --group docs --all-extras

# get the intersphinx references for the given library
[script]
fetch-refs LIB: _install-docs
    import os
    from pathlib import Path
    import logging as _logging
    import sys
    import runpy
    from sphinx.ext.intersphinx import inspect_main
    _logging.basicConfig()

    libs = runpy.run_path(Path(os.getcwd()) / "docs/conf.py").get("intersphinx_mapping")
    url = libs.get("{{ LIB }}", None)
    if not url:
        sys.exit(f"Unrecognized {{ LIB }}, must be one of: {', '.join(libs.keys())}")
    if url[1] is None:
        url = f"{url[0].rstrip('/')}/objects.inv"
    else:
        url = url[1]

    raise SystemExit(inspect_main([url]))

# run the command in the virtual environment
run +ARGS:
    uv run {{ ARGS }}

# validate the given version string against the lib version
[script]
validate_version VERSION:
    import re
    import tomllib
    import polymorphic
    version = re.match(r"v?(\d+[.]\d+[.]\w+)", "{{ VERSION }}").groups()[0]
    assert version == tomllib.load(open('pyproject.toml', 'rb'))['project']['version']
    assert version == polymorphic.__version__
    print(version)

# issue a release for the given semver string (e.g. 2.1.0)
release VERSION: install check-all
    @just validate_version v{{ VERSION }}
    git tag -s v{{ VERSION }} -m "{{ VERSION }} Release"
    git push upstream v{{ VERSION }}
