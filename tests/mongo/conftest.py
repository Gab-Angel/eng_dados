import os

os.environ["MONGO_DB"] = "eng_dados"

import pytest
from src.mongo.conn import get_client
from src.mongo.schema import create_collections, seed


@pytest.fixture(scope="session", autouse=True)
def banco_de_teste():
    get_client().drop_database("eng_dados")
    create_collections()
    seed()
    yield
    get_client().drop_database("eng_dados")
