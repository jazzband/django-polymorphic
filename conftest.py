import inspect
import subprocess
import sys

import pytest


def pytest_configure(config):
    # stash it somewhere global-ish
    from polymorphic import tests

    tests.HEADLESS = not config.getoption("--headed")


def first_breakable_line(obj) -> tuple[str, int]:
    """
    Return the absolute line number of the first executable statement
    in a function or bound method.
    """
    import ast
    import textwrap

    func = obj.__func__ if inspect.ismethod(obj) else obj

    source = inspect.getsource(func)
    source = textwrap.dedent(source)
    filename = inspect.getsourcefile(func)
    assert filename
    _, start_lineno = inspect.getsourcelines(func)

    tree = ast.parse(source)

    for node in tree.body[0].body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue

        return filename, start_lineno + node.lineno - 1

    # fallback: just return the line after the def
    return filename, start_lineno + 1


def pytest_runtest_call(item):
    # --trace cli option does not work for unittest style tests so we implement it here
    test = getattr(item, "obj", None)
    if item.config.option.trace and inspect.ismethod(test):
        from IPython.terminal.debugger import TerminalPdb

        try:
            file = inspect.getsourcefile(test)
            assert file
            dbg = TerminalPdb()
            dbg.set_break(*first_breakable_line(test))
            dbg.cmdqueue.append("continue")
            dbg.set_trace()
        except (OSError, AssertionError):
            pass


def _install_playwright_browsers() -> None:
    cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
    subprocess.run(cmd, check=True)


def _playwright_chromium_installed() -> bool:
    """Quick check if Playwright chromium browsers are already installed."""
    import os

    # Check the default Playwright browsers cache location
    browsers_path = os.environ.get(
        "PLAYWRIGHT_BROWSERS_PATH",
        os.path.join(os.path.expanduser("~"), ".cache", "ms-playwright"),
    )
    return os.path.isdir(browsers_path) and any(
        entry.startswith("chromium") for entry in os.listdir(browsers_path)
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    any_ui = any(item.get_closest_marker("ui") is not None for item in items)

    if any_ui and not getattr(config, "_did_install_playwright", False):
        setattr(config, "_did_install_playwright", True)
        if not _playwright_chromium_installed():
            # Browsers not available: deselect UI tests so the rest of the suite can run.
            # To run UI tests, install Playwright browsers first:
            #   playwright install chromium
            config.hook.pytest_deselected(items=[i for i in items if i.get_closest_marker("ui")])
            items[:] = [i for i in items if i.get_closest_marker("ui") is None]
