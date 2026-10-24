from pymongo import ReturnDocument

from src.mongo.conn import get_db, IntegrityError
from src.postgres.crud.crud_base import BaseCrud


def _check_usuario(cpf):
    if cpf is not None and get_db().usuario.count_documents({"_id": str(cpf)}, limit=1) == 0:
        raise IntegrityError(f"FK violada: usuario cpf={cpf} não existe")


class EstudanteCrud(BaseCrud):
    """Coleção `estudante` (_id = mat_estudante; cpf referencia usuario)."""

    def insert(self, mat_estudante, cpf, mc=None, ano_ingresso=None):
        try:
            cpf = str(cpf) if cpf is not None else None
            _check_usuario(cpf)
            doc = {"_id": mat_estudante, "cpf": cpf, "mc": mc, "ano_ingresso": ano_ingresso}
            get_db().estudante.insert_one(doc)
            return doc
        except Exception as e:
            print(f"Erro ao inserir na coleção estudante: {e}")
            return None

    def read(self, mat_estudante=None):
        try:
            filtro = {"_id": mat_estudante} if mat_estudante is not None else {}
            return list(get_db().estudante.find(filtro))
        except Exception as e:
            print(f"Erro ao ler coleção estudante: {e}")
            return []

    def update(self, mat_estudante, **campos):
        if not campos:
            return None
        try:
            if campos.get("cpf") is not None:
                campos["cpf"] = str(campos["cpf"])
                _check_usuario(campos["cpf"])
            return get_db().estudante.find_one_and_update(
                {"_id": mat_estudante}, {"$set": campos}, return_document=ReturnDocument.AFTER
            )
        except Exception as e:
            print(f"Erro ao atualizar coleção estudante: {e}")
            return None

    def delete(self, mat_estudante):
        """vinculo e plano: SET NULL; cursa: CASCADE."""
        try:
            db = get_db()
            doc = db.estudante.find_one_and_delete({"_id": mat_estudante})
            if doc:
                db.vinculo.update_many({"mat_estudante": mat_estudante}, {"$set": {"mat_estudante": None}})
                db.plano.update_many({"mat_estudante": mat_estudante}, {"$set": {"mat_estudante": None}})
                db.cursa.delete_many({"mat_estudante": mat_estudante})
            return doc
        except Exception as e:
            print(f"Erro ao deletar da coleção estudante: {e}")
            return None
