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
    @just run pre-commit install
    @just run playwright install

# install git pre-commit hooks
install-precommit:
    @just run pre-commit install

# update and install development dependencies
install *OPTS:
    uv sync {{ OPTS }}
    @just run pre-commit install

# install playwright dependencies
install-playwright:
    @just run playwright install

# install documentation dependencies
install-docs:
    uv sync --group docs --all-extras

# run static type checking
check-types:
    #TODO @just run mypy src/polymorphic

# run package checks
check-package:
    @just run pip check

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
build-docs-html: install-docs
    @just run sphinx-build --fresh-env --builder html --doctree-dir ./docs/_build/doctrees ./docs/ ./docs/_build/html

# build pdf documentation
build-docs-pdf: install-docs
    @just run sphinx-build --fresh-env --builder latex --doctree-dir ./docs/_build/doctrees ./docs/ ./docs/_build/pdf
    cd docs/_build/pdf && make

# build the docs
build-docs: build-docs-html

# build docs and package
build: build-docs-html
    @just manage compilemessages --ignore ".venv/*"
    uv build

# regenerate test migrations using the lowest version of Django
make-test-migrations:
    - rm src/polymorphic/tests/migrations/00*.py
    - rm src/polymorphic/tests/deletion/migrations/00*.py
    - rm src/polymorphic/tests/examples/**/migrations/00*.py
    uv run --isolated --resolution lowest-direct --script ./manage.py makemigrations

# open the html documentation
[script]
open-docs:
    import os
    import webbrowser
    webbrowser.open(f'file://{os.getcwd()}/docs/_build/html/index.html')

# build and open the documentation
docs: build-docs-html open-docs

# serve the documentation, with auto-reload
docs-live: install-docs
    @just run sphinx-autobuild docs docs/_build --open-browser --watch src --port 8000 --delay 1

_link_check:
    -uv run sphinx-build -b linkcheck -Q -D linkcheck_timeout=10 ./docs/ ./docs/_build

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
    @just run doc8 --ignore-path ./docs/_build --max-line-length 100 -q ./docs

# lint the code
check-lint:
    @just run ruff check --select I
    @just run ruff check

# check if the code needs formatting
check-format:
    @just run ruff format --check

# check that the readme renders
check-readme:
    @just run -m readme_renderer ./README.md -o /tmp/README.html

_check-readme-quiet:
    @just --quiet check-readme

# sort the python imports
sort-imports:
    @just run ruff check --fix --select I

# format the code and sort imports
format: sort-imports
    just --fmt --unstable
    @just run ruff format

# sort the imports and fix linting issues
lint: sort-imports
    @just run ruff check --fix

# fix formatting, linting issues and import sorting
fix: lint format

# run all static checks
check: check-lint check-format check-types check-package check-docs check-docs-links _check-readme-quiet

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
    uv add {{ PACKAGES }}

# run tests
test *TESTS: install-playwright
    @just run pytest {{ TESTS }} --cov 

test-db DB_CLIENT="dev" *TESTS: install-playwright
    # No Optional Dependency Unit Tests
    # todo clean this up, rerunning a lot of tests
    uv sync --group {{ DB_CLIENT }}
    @just run pytest {{ TESTS }} --cov 

# debug a test - (break at test start/run in headed mode)
debug-test *TESTS:
    @just run pytest -s --trace --pdbcls=IPython.terminal.debugger:Pdb --headed {{ TESTS }}

# run the pre-commit checks
precommit:
    @just run pre-commit

# generate the test coverage report
coverage:
    @just run coverage combine --keep *.coverage
    @just run coverage report
    @just run coverage xml

[script]
fetch-refs LIB: install-docs
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
release VERSION:
    @just validate_version v{{ VERSION }}
    git tag -s v{{ VERSION }} -m "{{ VERSION }} Release"
    git push upstream v{{ VERSION }}
