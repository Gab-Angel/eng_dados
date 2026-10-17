import pytest
from psycopg2.extras import RealDictRow
from src.postgres.crud.crud_turma import TurmaCrud

turmaCrud = TurmaCrud()


@pytest.mark.order(1)
def test_insert():
    call = turmaCrud.insert(
        id_turma=1,
        cod_disc="MAT0064",
        numero=1,
        ano=2026,
        semestre=2
    )

    assert isinstance(call, RealDictRow) is True
    assert call["id_turma"] == 1


@pytest.mark.order(2)
def test_read():
    call = turmaCrud.read()

    assert isinstance(call, list) is True


@pytest.mark.order(3)
def test_update():
    ano_esperado = 2017
    call = turmaCrud.update(
        ano=ano_esperado,
        id_turma=1
    )

    assert isinstance(call, RealDictRow) is True
    assert call["ano"] == ano_esperado


@pytest.mark.order(4)
def test_delete():
    call = turmaCrud.delete(
        id_turma=1
    )

    assert isinstance(call, RealDictRow) is True
    assert call["id_turma"] == 1