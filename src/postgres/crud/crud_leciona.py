from src.postgres.conn import get_conn
from src.postgres.crud.crud_base import BaseCrud

class LecionaCrud(BaseCrud):
    def insert(self, id_turma: int, mat_professor: str):
        conn = None
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO leciona (id_turma, mat_professor)
                        VALUES (%s, %s)
                        RETURNING id_turma, mat_professor;
                    """
                    cur.execute(query, (id_turma, mat_professor))
                    result = cur.fetchone()
                    conn.commit()
                    return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao inserir na tabela leciona: {e}")
            return None

    def read(self):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = "SELECT * FROM leciona;"
                    cur.execute(query)
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao listar leciona: {e}")
            return []

    def update(self, id_turma: int, mat_professor_antiga: str, novo_mat_professor: str):
        """Substitui o professor alocado em uma turma específica."""
        conn = None
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = """
                        UPDATE leciona
                        SET mat_professor = %s
                        WHERE id_turma = %s AND mat_professor = %s
                        RETURNING id_turma, mat_professor;
                    """
                    cur.execute(query, (novo_mat_professor, id_turma, mat_professor_antiga))
                    result = cur.fetchone()
                    conn.commit()
                    return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao atualizar leciona: {e}")
            return None

    def find_by_professor(self, mat_professor: str):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = "SELECT * FROM leciona WHERE mat_professor = %s;"
                    cur.execute(query, (mat_professor,))
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao buscar turmas do professor: {e}")
            return []

    def find_by_turma(self, id_turma: int):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = "SELECT * FROM leciona WHERE id_turma = %s;"
                    cur.execute(query, (id_turma,))
                    return cur.fetchall()
        except Exception as e:
            print(f"Erro ao buscar professores da turma: {e}")
            return []

    def delete(self, id_turma: int, mat_professor: str):
        conn = None
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    query = """
                        DELETE FROM leciona
                        WHERE id_turma = %s AND mat_professor = %s
                        RETURNING id_turma, mat_professor;
                    """
                    cur.execute(query, (id_turma, mat_professor))
                    result = cur.fetchone()
                    conn.commit()
                    return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao remover vínculo em leciona: {e}")
            return None