from src.postgres.conn import get_conn
from src.postgres.crud.crud_base import BaseCrud

class ProfessorCrud(BaseCrud):
    def insert(
        self,
        cpf,
        mat_professor,
        departamento,
        formacao,
        data_admissao,
        tipo_jornada_trabalho,
        salario
    ):
        conn = None
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO professor (
                            cpf, mat_professor, departamento,
                            formacao, data_admissao,
                            tipo_jornada_trabalho, salario
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *;
                    """
                    valores = (
                        cpf,
                        mat_professor,
                        departamento,
                        formacao,
                        data_admissao,
                        tipo_jornada_trabalho,
                        salario
                    )
                    cur.execute(query, valores)
                    result = cur.fetchone()
                    conn.commit()
                    return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao inserir na tabela professor: {e}")
            return None

    def read(self):
        conn = None
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM professor;")
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao consultar professores: {e}")
            return []

    def update(self, mat_professor, **kwargs):
        conn = None
        if not kwargs:
            return None
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    colunas = [f"{chave} = %s" for chave in kwargs.keys()]
                    valores = list(kwargs.values())
                    valores.append(mat_professor)

                    query = f"""
                        UPDATE professor
                        SET {', '.join(colunas)}
                        WHERE mat_professor = %s
                        RETURNING *;
                    """
                    cur.execute(query, tuple(valores))
                    result = cur.fetchone()
                    conn.commit()
                    return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao atualizar professor: {e}")
            return None

    def delete(self, mat_professor):
        conn = None
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = """
                        DELETE FROM professor
                        WHERE mat_professor = %s
                        RETURNING *;
                    """
                    cur.execute(query, (mat_professor,))
                    result = cur.fetchone()
                    conn.commit()
                    return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao deletar professor: {e}")
            return None