from __future__ import annotations

import pathlib
import pytest

INTEGRATION_DIR = pathlib.Path(__file__).resolve().parent / "examples" / "integrations"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        # item.path is pathlib.Path on modern pytest; fall back for older
        p = pathlib.Path(str(getattr(item, "path", item.fspath))).resolve()
        if INTEGRATION_DIR in p.parents:
            item.add_marker(pytest.mark.integration)
