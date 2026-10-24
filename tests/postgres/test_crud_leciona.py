import pytest
from psycopg2.extras import RealDictRow
from src.postgres.conn import get_conn
from src.postgres.crud.crud_leciona import LecionaCrud

crud = LecionaCrud()

CPF_TESTE = 99911122233
CPF_TESTE_2 = 99911122234
MAT_PROF_TESTE = "P999901"
MAT_PROF_TESTE_2 = "P999902"
DEPTO_TESTE = "DCOMP"
COD_DISC_TESTE = "COMP0001"
ANO_TESTE = 2026
SEMESTRE_TESTE = 1
ID_TURMA_TESTE = 99999


@pytest.fixture(scope="module", autouse=True)
def setup_dependencias_leciona():
    conn = None
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # 1. Usuários
                cur.execute(
                    """
                    INSERT INTO usuario (cpf, nome, login, senha)
                    VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
                    ON CONFLICT (cpf) DO NOTHING;
                    """,
                    (
                        CPF_TESTE, "Prof Leciona 1", "user_leciona_1", "123456",
                        CPF_TESTE_2, "Prof Leciona 2", "user_leciona_2", "123456"
                    )
                )

                # 2. Departamento
                cur.execute(
                    """
                    INSERT INTO departamento (cod_depto, nome, orcamento)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cod_depto) DO NOTHING;
                    """,
                    (DEPTO_TESTE, "Dept Computacao Teste", 10000.0)
                )

                # 3. Professores
                cur.execute(
                    """
                    INSERT INTO professor (mat_professor, cpf, departamento, formacao, tipo_jornada_trabalho, salario)
                    VALUES 
                        (%s, %s, %s, 'Doutorado', 'DE', 8000.0),
                        (%s, %s, %s, 'Mestrado', '40h', 6000.0)
                    ON CONFLICT (mat_professor) DO NOTHING;
                    """,
                    (MAT_PROF_TESTE, CPF_TESTE, DEPTO_TESTE, MAT_PROF_TESTE_2, CPF_TESTE_2, DEPTO_TESTE)
                )

                # 4. Disciplina
                cur.execute(
                    """
                    INSERT INTO disciplina (cod_disc, nome, creditos, depto_responsavel)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (cod_disc) DO NOTHING;
                    """,
                    (COD_DISC_TESTE, "Banco de Dados I", 4, DEPTO_TESTE)
                )

                # 5. Semestre
                cur.execute(
                    """
                    INSERT INTO semestre (ano, semestre, data_inicio, data_fom)
                    VALUES (%s, %s, '2026-03-01', '2026-07-15')
                    ON CONFLICT (ano, semestre) DO NOTHING;
                    """,
                    (ANO_TESTE, SEMESTRE_TESTE)
                )

                # 6. Turma
                cur.execute(
                    """
                    INSERT INTO turma (id_turma, cod_disc, numero, ano, semestre)
                    VALUES (%s, %s, 1, %s, %s)
                    ON CONFLICT (id_turma) DO NOTHING;
                    """,
                    (ID_TURMA_TESTE, COD_DISC_TESTE, ANO_TESTE, SEMESTRE_TESTE)
                )

                conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e

    yield

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM leciona WHERE id_turma = %s;", (ID_TURMA_TESTE,))
                cur.execute("DELETE FROM turma WHERE id_turma = %s;", (ID_TURMA_TESTE,))
                cur.execute("DELETE FROM semestre WHERE ano = %s AND semestre = %s;", (ANO_TESTE, SEMESTRE_TESTE))
                cur.execute("DELETE FROM disciplina WHERE cod_disc = %s;", (COD_DISC_TESTE,))
                cur.execute("DELETE FROM professor WHERE mat_professor IN (%s, %s);", (MAT_PROF_TESTE, MAT_PROF_TESTE_2))
                cur.execute("DELETE FROM departamento WHERE cod_depto = %s;", (DEPTO_TESTE,))
                cur.execute("DELETE FROM usuario WHERE cpf IN (%s, %s);", (CPF_TESTE, CPF_TESTE_2))
                conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro na limpeza de dependencias leciona: {e}")


@pytest.mark.order(1)
def test_insert():
    call = crud.insert(id_turma=ID_TURMA_TESTE, mat_professor=MAT_PROF_TESTE)

    assert isinstance(call, RealDictRow) is True
    assert call["id_turma"] == ID_TURMA_TESTE
    assert call["mat_professor"] == MAT_PROF_TESTE


@pytest.mark.order(2)
def test_read():
    call = crud.read()

    assert isinstance(call, list) is True
    assert any(
        reg["id_turma"] == ID_TURMA_TESTE and reg["mat_professor"] == MAT_PROF_TESTE
        for reg in call
    )


@pytest.mark.order(3)
def test_update():
    call = crud.update(
        id_turma=ID_TURMA_TESTE,
        mat_professor_antiga=MAT_PROF_TESTE,
        novo_mat_professor=MAT_PROF_TESTE_2
    )

    assert isinstance(call, RealDictRow) is True
    assert call["id_turma"] == ID_TURMA_TESTE
    assert call["mat_professor"] == MAT_PROF_TESTE_2


@pytest.mark.order(4)
def test_delete():
    # Remove a vinculação atualizada com o segundo professor
    call = crud.delete(id_turma=ID_TURMA_TESTE, mat_professor=MAT_PROF_TESTE_2)

    assert isinstance(call, RealDictRow) is True
    assert call["id_turma"] == ID_TURMA_TESTE
    assert call["mat_professor"] == MAT_PROF_TESTE_2