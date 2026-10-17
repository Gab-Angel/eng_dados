from src.postgres.conn import get_conn
from src.postgres.crud.crud_base import BaseCrud

class TurmaCrud(BaseCrud):
    def insert(
            self,
            id_turma, cod_disc,
            numero, ano, semestre
    ):
        with get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO turma (
                            id_turma, cod_disc,
                            numero, ano, semestre
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id_turma;
                    """,
                    (id_turma, cod_disc, numero, ano, semestre)
                    )

                    result = cur.fetchone()
                    conn.commit()
                    return result


                except Exception as e:
                    conn.rollback()
                    print(f"Erro ao inserir na tabela turma: {e}")
                    return []

    def read(self):
        with get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("SELECT * FROM turma;")

                    result = cur.fetchall()
                    conn.commit()
                    return result


                except Exception as e:
                    conn.rollback()
                    print(f"Erro ao ler na tabela turma: {e}")
                    return []

    def update(self, ano, id_turma):
        with get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        UPDATE turma
                        SET ano = %s
                        WHERE id_turma = %s
                        RETURNING ano;
                    """,
                    (ano, id_turma)
                    )

                    result = cur.fetchone()
                    conn.commit()
                    return result


                except Exception as e:
                    conn.rollback()
                    print(f"Erro ao atualizar na tabela turma: {e}")
                    return []
    
    def delete(self, id_turma):
        with get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        DELETE FROM turma
                        WHERE id_turma = %s
                        RETURNING id_turma;
                    """,
                    (id_turma,)
                    )

                    result = cur.fetchone()
                    conn.commit()
                    return result


                except Exception as e:
                    conn.rollback()
                    print(f"Erro ao deletar na tabela turma: {e}")
                    return []
    