import sys
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--app-path",
        required=True,
        help="Path to the directory containing app.py (e.g. ../module-04/winner)",
    )


@pytest.fixture(scope="session")
def notes_app(pytestconfig):
    app_path = pytestconfig.getoption("--app-path")
    sys.path.insert(0, str(app_path))
    import app as _app
    return _app
