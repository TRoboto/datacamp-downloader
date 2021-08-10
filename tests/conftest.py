import pytest


def pytest_addoption(parser):
    parser.addoption("--username", action="store", default=None)
    parser.addoption("--password", action="store", default=None)
    parser.addoption("--token", action="store", default=None)


@pytest.fixture()
def username(pytestconfig):
    return pytestconfig.getoption("username")


@pytest.fixture()
def password(pytestconfig):
    return pytestconfig.getoption("password")


@pytest.fixture()
def token(pytestconfig):
    return pytestconfig.getoption("token")
