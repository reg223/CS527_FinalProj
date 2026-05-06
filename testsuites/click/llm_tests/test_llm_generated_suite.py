import pytest
from click import Context, Command, Option, Argument, BadParameter, UsageError
from click.decorators import command, option, argument
from click.exceptions import ClickException
from click.testing import CliRunner
import click

@pytest.fixture
def runner():
    return CliRunner()

def test_command_execution(runner):
    @command()
    def cli():
        click.echo("Hello, World!")

    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "Hello, World!" in result.output

def test_option_with_default(runner):
    @command()
    @option('--name', default='World')
    def cli(name):
        click.echo(f"Hello, {name}!")

    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "Hello, World!" in result.output

def test_option_with_value(runner):
    @command()
    @option('--name', default='World')
    def cli(name):
        click.echo(f"Hello, {name}!")

    result = runner.invoke(cli, ['--name', 'Alice'])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output

def test_argument(runner):
    @command()
    @argument('name')
    def cli(name):
        click.echo(f"Hello, {name}!")

    result = runner.invoke(cli, ['Alice'])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output

def test_missing_required_option(runner):
    @command()
    @option('--name', required=True)
    def cli(name):
        click.echo(f"Hello, {name}!")

    result = runner.invoke(cli)
    assert result.exit_code != 0
    assert isinstance(result.exception, SystemExit)

def test_bad_parameter(runner):
    @command()
    @argument('age', type=int)
    def cli(age):
        click.echo(f"Your age is {age}.")

    result = runner.invoke(cli, ['not_a_number'])
    assert result.exit_code != 0
    assert isinstance(result.exception, SystemExit)

def test_custom_exception(runner):
    class CustomClickException(ClickException):
        def __init__(self):
            super().__init__("This is a custom error message.")

    @command()
    def cli():
        raise CustomClickException()

    result = runner.invoke(cli)
    assert result.exit_code != 0
    assert "This is a custom error message." in result.output

def test_command_with_context(runner):
    @command()
    @option('--name', default='World')
    def cli(name):
        ctx = click.get_current_context()
        click.echo(f"Hello, {name}! Context: {ctx}")

    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "Hello, World!" in result.output

def test_command_with_choices(runner):
    @command()
    @option('--color', type=click.Choice(['red', 'green', 'blue']), default='red')
    def cli(color):
        click.echo(f"Color selected: {color}")

    result = runner.invoke(cli, ['--color', 'green'])
    assert result.exit_code == 0
    assert "Color selected: green" in result.output

def test_command_with_invalid_choice(runner):
    @command()
    @option('--color', type=click.Choice(['red', 'green', 'blue']), default='red')
    def cli(color):
        click.echo(f"Color selected: {color}")

    result = runner.invoke(cli, ['--color', 'yellow'])
    assert result.exit_code != 0
    assert isinstance(result.exception, SystemExit)
