import pytest
from src.mongo.crud.crud_usuario import UsuarioCrud
from src.mongo.crud.crud_estudante import EstudanteCrud

usuarios, crud = UsuarioCrud(), EstudanteCrud()
CPF, MAT = "11122233344", "2026001"


@pytest.mark.order(1)
def test_insert_fk_violation():
    assert crud.insert(MAT, CPF, 7, 2026) is None  # usuário ainda não existe


@pytest.mark.order(2)
def test_insert():
    usuarios.insert(CPF, "Aluno", None, [], [], "aluno1", "s")
    assert crud.insert(MAT, CPF, 7, 2026)["_id"] == MAT


@pytest.mark.order(3)
def test_check_mc_rejected():
    assert crud.insert("2026002", None, 150, 2026) is None  # mc fora do limite


@pytest.mark.order(4)
def test_read():
    assert crud.read(MAT)[0]["cpf"] == CPF


@pytest.mark.order(5)
def test_update():
    assert crud.update(MAT, mc=8)["mc"] == 8


@pytest.mark.order(6)
def test_delete_usuario_sets_null():
    usuarios.delete(CPF)
    assert crud.read(MAT)[0]["cpf"] is None


@pytest.mark.order(7)
def test_delete():
    assert crud.delete(MAT)["_id"] == MAT
