from src.postgres.conn import get_conn
from src.postgres.crud.crud_base import BaseCrud

class UsuarioCrud(BaseCrud):
    def insert(
            self,
            cpf, nome, data_nascimento,
            email, telefone, login, senha
    ):
        try: 
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO usuario (
                        cpf, nome, data_nascimento,
                        email, telefone, login, senha
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING cpf, nome, email;
                    """,
                    (cpf, nome, data_nascimento,
                     [email] if isinstance(email, str) else email,
                     [telefone] if isinstance(email, str) else telefone,
                     login, senha)
                    )
                    result = cur.fetchone()
                    conn.commit()
                    return result
                
        except Exception as e:
            conn.rollback()
            print(f"Erro ao inserir na tabela usuario: {e}")
            return []

    def read(self):
        try: 
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM usuario;")
                    result = cur.fetchall()
                    conn.commit()
                    return result
                
        except Exception as e:
            conn.rollback()
            print(f"Erro ao ler tabela usuario: {e}")
            return []

    def update(self, senha, nome):
        try: 
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE usuario
                        SET nome = %s
                        WHERE senha = %s
                        RETURNING nome;
                    """,
                    (nome, senha)
                    )
                    result = cur.fetchone()
                    conn.commit()
                    return result
                
        except Exception as e:
            conn.rollback()
            print(f"Erro em atualizar tabela usuario: {e}")
            return []

    def delete(self, cpf):
        try: 
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE 
                        FROM usuario
                        WHERE cpf = %s
                        RETURNING nome;
                    """,
                    (cpf,)
                    )
                    result = cur.fetchone()
                    conn.commit()
                    return result
                
        except Exception as e:
            conn.rollback()
            print(f"Erro em atualizar tabela usuario: {e}")
            return []