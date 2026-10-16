import pytest
from psycopg2.extras import RealDictRow
from src.postgres.crud.crud_usuario import UsuarioCrud

usuarioCrud = UsuarioCrud()

@pytest.mark.order(1)
def test_insert():
    call = usuarioCrud.insert(
        cpf="12345678901",
        nome="userA",
        data_nascimento="2007-11-22",
        email="userA@gmail.com",
        telefone="79999999999",
        login="489u23fh7",
        senha="43y9hu"
    )

    assert isinstance(call, RealDictRow) is True

@pytest.mark.order(2)
def test_read():
    call = usuarioCrud.read()

    assert isinstance(call, list) is True

@pytest.mark.order(3)
def test_update():
    nome_esperado = "userX"
    call = usuarioCrud.update(
        senha="43y9hu",
        nome=nome_esperado
    )

    assert isinstance(call, RealDictRow) is True
    assert call["nome"] == nome_esperado

@pytest.mark.order(4)
def test_delete():
    call = usuarioCrud.delete(cpf="12345678901")

    assert isinstance(call, RealDictRow) is True