# Contributing

[![Jazzband](https://jazzband.co/static/img/badge.svg)](https://jazzband.co/)

This is a [Jazzband](https://jazzband.co) project. By contributing you agree to abide by the [Contributor Code of Conduct](https://jazzband.co/about/conduct) and follow the [guidelines](https://jazzband.co/about/guidelines).

Contributions are encouraged! Please use the issue page to submit feature requests or bug reports. Issues with attached PRs will be given priority and have a much higher likelihood of acceptance.

We are actively seeking additional maintainers. If you're interested, [contact me](https://github.com/bckohan).

## Installation

### Install Just

We provide a platform independent justfile with recipes for all the development tasks. You should [install just](https://just.systems/man/en/installation.html) if it is not on your system already.

`[django-polymorphic](https://pypi.python.org/pypi/django-polymorphic)` uses [uv](https://docs.astral.sh/uv) for environment, package, and dependency management. ``just setup`` will install the necessary build tooling if you do not already have it:

```shell
just setup
```

## Documentation

TODO

## Static Analysis

TODO

## Running Tests

TODO

## Versioning

[django-polymorphic](https://pypi.python.org/pypi/django-polymorphic) strictly adheres to [semantic versioning](https://semver.org).

## Issuing Releases

The release workflow is triggered by tag creation. You must have [git tag signing enabled](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits). Our justfile has a release shortcut:

```bash
just release x.x.x
```

## Just Recipes

```bash

```
