import pytest
from psycopg2.extras import RealDictRow
from src.postgres.conn import get_conn
from src.postgres.crud.crud_professor import ProfessorCrud

crud = ProfessorCrud()

CPF_TESTE = 123144325346
MATRICULA_TESTE = "P202601"
DEPTO_TESTE = "Dcomp"


@pytest.fixture(scope="module", autouse=True)
def setup_dependencias():
    """Garante a existência prévia de usuario e departamento no banco."""
    conn = None
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # 1. Cria usuário base caso não exista
                cur.execute(
                    """
                    INSERT INTO usuario (cpf, nome, login, senha)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (cpf) DO NOTHING;
                    """,
                    (CPF_TESTE, "Professor Teste", "prof_teste", "123456")
                )

                # 2. Cria departamento base caso não exista
                cur.execute(
                    """
                    INSERT INTO departamento (cod_depto, nome, orcamento)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cod_depto) DO NOTHING;
                    """,
                    (DEPTO_TESTE, "Departamento de Computacao", 50000.0)
                )
                conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e

    yield

    # Limpeza após os testes do módulo executarem
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Remove o professor caso ainda exista
                cur.execute("DELETE FROM professor WHERE mat_professor = %s;", (MATRICULA_TESTE,))
                # Remove as dependências criadas para o teste
                cur.execute("DELETE FROM departamento WHERE cod_depto = %s;", (DEPTO_TESTE,))
                cur.execute("DELETE FROM usuario WHERE cpf = %s;", (CPF_TESTE,))
                conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro na limpeza do banco: {e}")


@pytest.mark.order(1)
def test_insert():
    call = crud.insert(
        cpf=CPF_TESTE,
        mat_professor=MATRICULA_TESTE,
        departamento=DEPTO_TESTE,
        formacao="Mestrado",
        data_admissao="2006-07-23",
        tipo_jornada_trabalho="20h",
        salario=4000.00
    )

    assert isinstance(call, RealDictRow) is True
    assert call["mat_professor"] == MATRICULA_TESTE


@pytest.mark.order(2)
def test_read():
    call = crud.read()

    assert isinstance(call, list) is True
    assert any(p["mat_professor"] == MATRICULA_TESTE for p in call)


@pytest.mark.order(3)
def test_update():
    novo_salario = 6500.00
    call = crud.update(
        mat_professor=MATRICULA_TESTE,
        salario=novo_salario,
        formacao="Doutorado"
    )

    assert isinstance(call, RealDictRow) is True
    assert float(call["salario"]) == novo_salario
    assert call["formacao"] == "Doutorado"


@pytest.mark.order(4)
def test_delete():
    call = crud.delete(mat_professor=MATRICULA_TESTE)

    assert isinstance(call, RealDictRow) is True
    assert call["mat_professor"] == MATRICULA_TESTE