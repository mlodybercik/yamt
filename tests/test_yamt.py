import pytest
import tempfile
from yamt import create_app, db

@pytest.fixture(scope="module")
def app():
    return create_app({"TESTING": True,
                       "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                       "SQLALCHEMY_TRACK_MODIFICATIONS": False})
