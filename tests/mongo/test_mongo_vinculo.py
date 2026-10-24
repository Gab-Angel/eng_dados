import pytest
from src.mongo.crud.crud_curso import CursoCrud
from src.mongo.crud.crud_estudante import EstudanteCrud
from src.mongo.crud.crud_vinculo import VinculoCrud

cursos, estudantes, crud = CursoCrud(), EstudanteCrud(), VinculoCrud()
MAT = "2026010"
estado = {}


@pytest.mark.order(1)
def test_setup():
    estudantes.insert(MAT, None, 6, 2026)
    estado["curso"] = cursos.insert("Matemática", "Vespertino", "Licenciatura Plena", "Campus", "Graduação")["_id"]


@pytest.mark.order(2)
def test_insert():
    r = crud.insert(MAT, estado["curso"], "2026-03-01", "Ativo")
    assert isinstance(r["_id"], int)
    estado["id"] = r["_id"]


@pytest.mark.order(3)
def test_fk_and_domain_rejected():
    assert crud.insert("naoexiste", estado["curso"], "2026-03-01", "Ativo") is None
    assert crud.insert(MAT, 99999, "2026-03-01", "Ativo") is None
    assert crud.insert(MAT, estado["curso"], "2026-03-01", "Trancado") is None


@pytest.mark.order(4)
def test_read():
    assert len(crud.find_by_estudante(MAT)) == 1
    assert crud.read(estado["id"])[0]["status"] == "Ativo"


@pytest.mark.order(5)
def test_update():
    assert crud.update(estado["id"], status="Graduado", data_saida="2030-12-01")["status"] == "Graduado"


@pytest.mark.order(6)
def test_delete_curso_sets_null():
    cursos.delete(estado["curso"])
    assert crud.read(estado["id"])[0]["curso"] is None


@pytest.mark.order(7)
def test_delete():
    assert crud.delete(estado["id"])["_id"] == estado["id"]
    estudantes.delete(MAT)
