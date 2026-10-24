from pymongo import ReturnDocument

from src.mongo.conn import get_db, to_date, as_list
from src.postgres.crud.crud_base import BaseCrud


class UsuarioCrud(BaseCrud):
    """Coleção `usuario` (_id = cpf). email/telefone são arrays (VARCHAR[])."""

    def insert(self, cpf, nome, data_nascimento, email, telefone, login, senha):
        try:
            doc = {
                "_id": str(cpf),
                "nome": nome,
                "data_nascimento": to_date(data_nascimento),
                "email": as_list(email),
                "telefone": as_list(telefone),
                "login": login,
                "senha": senha,
            }
            get_db().usuario.insert_one(doc)
            return doc
        except Exception as e:
            print(f"Erro ao inserir na coleção usuario: {e}")
            return None

    def read(self, cpf=None):
        try:
            filtro = {"_id": str(cpf)} if cpf is not None else {}
            return list(get_db().usuario.find(filtro))
        except Exception as e:
            print(f"Erro ao ler coleção usuario: {e}")
            return []

    def update(self, cpf, **campos):
        """Atualiza campos do usuário. A chave (_id/cpf) é imutável no MongoDB."""
        if not campos:
            return None
        try:
            if "data_nascimento" in campos:
                campos["data_nascimento"] = to_date(campos["data_nascimento"])
            for k in ("email", "telefone"):
                if k in campos:
                    campos[k] = as_list(campos[k])
            return get_db().usuario.find_one_and_update(
                {"_id": str(cpf)}, {"$set": campos}, return_document=ReturnDocument.AFTER
            )
        except Exception as e:
            print(f"Erro ao atualizar coleção usuario: {e}")
            return None

    def delete(self, cpf):
        """ON DELETE SET NULL: estudante.cpf e professor.cpf passam a null."""
        try:
            db = get_db()
            doc = db.usuario.find_one_and_delete({"_id": str(cpf)})
            if doc:
                db.estudante.update_many({"cpf": str(cpf)}, {"$set": {"cpf": None}})
                db.professor.update_many({"cpf": str(cpf)}, {"$set": {"cpf": None}})
            return doc
        except Exception as e:
            print(f"Erro ao deletar da coleção usuario: {e}")
            return None
