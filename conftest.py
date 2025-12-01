def pytest_configure(config):
    # stash it somewhere global-ish
    from polymorphic import tests

    tests.HEADLESS = not config.getoption("--headed")
