from datacamp_downloader.downloader import app
from typer.testing import CliRunner

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Commands" in result.stdout


def test_login(username, password):
    result = runner.invoke(app, ["login", "-u", username, "-p", password])
    assert result.exit_code == 0
    assert "Hi" in result.stdout


def test_set_token(token):
    result = runner.invoke(app, ["set-token", token])
    assert result.exit_code == 0
    assert "Hi" in result.stdout
