import pytest
from src.mongo.crud.crud_curso import CursoCrud

crud = CursoCrud()
estado = {}


@pytest.mark.order(1)
def test_insert():
    r = crud.insert("Sistemas de Informação", "Noturno", "Bacharelado", "São Cristóvão", "Graduação")
    assert isinstance(r["_id"], int)
    estado["id"] = r["_id"]


@pytest.mark.order(2)
def test_unique_rejected():
    assert crud.insert("Sistemas de Informação", "Noturno", "Bacharelado", "São Cristóvão", "Graduação") is None


@pytest.mark.order(3)
def test_domain_rejected():
    assert crud.insert("Curso X", "Madrugada") is None 


@pytest.mark.order(4)
def test_read():
    assert crud.read(estado["id"])[0]["turno"] == "Noturno"


@pytest.mark.order(5)
def test_update():
    assert crud.update(estado["id"], turno="Matutino")["turno"] == "Matutino"


@pytest.mark.order(6)
def test_delete():
    assert crud.delete(estado["id"])["_id"] == estado["id"]
    assert crud.read(estado["id"]) == []
