import pytest
from src.mongo.crud.crud_usuario import UsuarioCrud

crud = UsuarioCrud()
CPF = "12345678901"


@pytest.mark.order(1)
def test_insert():
    r = crud.insert(CPF, "userA", "2007-11-22", "userA@gmail.com", "79999999999", "login1", "senha1")
    assert r["_id"] == CPF
    assert r["email"] == ["userA@gmail.com"]


@pytest.mark.order(2)
def test_insert_duplicate_key_rejected():
    assert crud.insert(CPF, "outro", None, [], [], "login2", "x") is None


@pytest.mark.order(3)
def test_unique_login_rejected():
    assert crud.insert("999", "outro", None, [], [], "login1", "x") is None


@pytest.mark.order(4)
def test_not_null_rejected():
    assert crud.insert("888", None, None, [], [], "login3", "x") is None


@pytest.mark.order(5)
def test_domain_rejected():
    assert crud.insert("abc", "nome", None, [], [], "login4", "x") is None  # cpf não numérico


@pytest.mark.order(6)
def test_read():
    assert len(crud.read()) == 1
    assert crud.read(CPF)[0]["nome"] == "userA"


@pytest.mark.order(7)
def test_update():
    assert crud.update(CPF, nome="userX")["nome"] == "userX"


@pytest.mark.order(8)
def test_delete():
    assert crud.delete(CPF)["_id"] == CPF
    assert crud.read() == []
