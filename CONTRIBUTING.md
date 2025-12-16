# Contributing

[![Jazzband](https://jazzband.co/static/img/badge.svg)](https://jazzband.co/)

This is a [Jazzband](https://jazzband.co) project. By contributing you agree to abide by the [Contributor Code of Conduct](https://jazzband.co/about/conduct) and follow the [guidelines](https://jazzband.co/about/guidelines).

Contributions are encouraged! Please use the issue page to submit feature requests or bug reports. Issues with attached PRs will be given priority and have a much higher likelihood of acceptance.

We are actively seeking additional maintainers. If you're interested, [contact me](https://github.com/bckohan).

## Installation

### Install Just

We provide a platform independent justfile with recipes for all the development tasks. You should [install just](https://just.systems/man/en/) if it is not on your system already.

[django-polymorphic](https://pypi.python.org/pypi/django-polymorphic) uses [uv](https://docs.astral.sh/uv) for environment, package, and dependency management. ``just setup`` will install the necessary build tooling if you do not already have it:

 ```bash
just setup
```

Setup also may take a python version:

```bash
just setup 3.12
```

If you already have uv and python installed running install will just install the development dependencies:

 ```bash
just install
```

**To run pre-commit checks you will have to install just.**

## Documentation

`django-polymorphic` documentation is generated using [Sphinx](https://www.sphinx-doc.org) with the [furo](https://github.com/pradyunsg/furo) theme. Any new feature PRs must provide updated documentation for the features added. To build the docs run doc8 to check for formatting issues then run Sphinx:

```bash
just install-docs # install the doc dependencies
just docs  # builds docs
just check-docs  # lint the docs
just check-docs-links  # check for broken links in the docs
```

Run the docs with auto rebuild using:

```bash
just docs-live
```

## Static Analysis

`django-polymorphic` uses [ruff](https://docs.astral.sh/ruff/) for Python linting, header import standardization and code formatting. Before any PR is accepted the following must be run, and static analysis tools should not produce any errors or warnings. Disabling certain errors or warnings where justified is acceptable:

To fix formatting and linting problems that are fixable run:

```bash
just fix
```

To run all static analysis without automated fixing you can run:

```bash
just check
```

To format source files you can run:

```bash
just format
```

## Running Tests

`django-polymorphic` is set up to use [pytest](https://docs.pytest.org) to run unit tests. All the tests are housed in `src/polymorphic/tests`. Before a PR is accepted, all tests must be passing and the code coverage must be at 100%. A small number of exempted error handling branches are acceptable.

To run the full suite:

 ```bash
just test
```

To run a single test, or group of tests in a class:

 ```bash
just test <path_to_tests_file>::ClassName::FunctionName
```

For instance, to run all admin tests, and then just the test_admin_registration test you would do:

 ```bash
just test src/polymorphic/tests/test_admin.py
just test src/polymorphic/tests/test_admin.py::PolymorphicAdminTests::test_admin_registration
```

### Running UI Tests

Make sure you have playwright installed:

```bash
just install-playwright
```

If you want to see the test step through the UI actions you can run the test like so:

```bash
just debug-test -k <test_name>
```

This will open a browser and the debugger at the start of the test, you can then ``next`` through and see the UI actions happen.

## Versioning

[django-polymorphic](https://pypi.python.org/pypi/django-polymorphic) strictly adheres to [semantic versioning](https://semver.org).

## Issuing Releases

The release workflow is triggered by tag creation. You must have [git tag signing enabled](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits). Our justfile has a release shortcut:

```bash
just release x.x.x
```

## Just Recipes

```bash
build                          # build docs and package
build-docs                     # build the docs
build-docs-html                # build html documentation
build-docs-pdf                 # build pdf documentation
check                          # run all static checks
check-docs                     # lint the documentation
check-docs-links               # check the documentation links for broken links
check-format                   # check if the code needs formatting
check-lint                     # lint the code
check-package                  # run package checks
check-readme                   # check that the readme renders
check-types                    # run static type checking
clean                          # remove all non repository artifacts
clean-docs                     # remove doc build artifacts-
clean-env                      # remove the virtual environment
clean-git-ignored              # remove all git ignored files
coverage                       # generate the test coverage report
debug-test *TESTS              # debug a test - (break at test start/run in headed mode)
docs                           # build and open the documentation
docs-live                      # serve the documentation, with auto-reload
fetch-refs LIB
fix                            # fix formatting, linting issues and import sorting
format                         # format the code and sort imports
install *OPTS                  # update and install development dependencies
install-docs                   # install documentation dependencies
install-precommit              # install git pre-commit hooks
install_uv                     # install the uv package manager
lint                           # sort the imports and fix linting issues
make-test-migrations           # regenerate test migrations using the lowest version of Django
manage *COMMAND                # run the django admin
open-docs                      # open the html documentation
precommit                      # run the pre-commit checks
release VERSION                # issue a release for the given semver string (e.g. 2.1.0)
run +ARGS                      # run the command in the virtual environment
setup python="python"          # setup the venv, pre-commit hooks and playwright dependencies
sort-imports                   # sort the python imports
test *TESTS                    # run tests
test-db DB_CLIENT="dev" *TESTS
test-lock +PACKAGES            # lock to specific python and versions of given dependencies
validate_version VERSION       # validate the given version string against the lib version
```
