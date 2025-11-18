from _pytest.config import Config as PytestConfig
from _pytest.config.argparsing import Parser
import pytest
import dotenv

dotenv.load_dotenv()


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default="http://localhost",
        help="Base URL for web tests",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig: PytestConfig) -> str:
    return pytestconfig.getoption("--base-url")
