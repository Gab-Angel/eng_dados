from datetime import date, datetime

from decouple import config
from pymongo import MongoClient, ReturnDocument

_client = None


class IntegrityError(Exception):
    """Violação de restrição (integridade referencial) verificada pela aplicação."""


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(config("MONGO_URI"), serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    return get_client()[config("MONGO_DB", default="universidade")]


def next_id(name: str) -> int:
    """Substitui SERIAL / SEQUENCE do PostgreSQL (incremento atômico)."""
    doc = get_db().counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["seq"]


def to_date(value):
    """Aceita 'YYYY-MM-DD', date ou datetime e devolve datetime (BSON date)."""
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    return datetime.strptime(value, "%Y-%m-%d")


def as_list(value):
    """Atributo multivalorado: str -> [str]; None -> []."""
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)
