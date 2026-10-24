from pymongo import ReturnDocument

from src.mongo.conn import get_db, next_id
from src.postgres.crud.crud_base import BaseCrud


class CursoCrud(BaseCrud):
    """Coleção `curso` (_id = idCurso, gerado por contador)."""

    def insert(self, nome, turno, grau=None, campus=None, nivel=None):
        try:
            doc = {
                "_id": next_id("curso"),
                "nome": nome,
                "grau": grau,
                "turno": turno,
                "campus": campus,
                "nivel": nivel,
            }
            get_db().curso.insert_one(doc)
            return doc
        except Exception as e:
            print(f"Erro ao inserir na coleção curso: {e}")
            return None

    def read(self, id_curso=None):
        try:
            filtro = {"_id": id_curso} if id_curso is not None else {}
            return list(get_db().curso.find(filtro))
        except Exception as e:
            print(f"Erro ao ler coleção curso: {e}")
            return []

    def update(self, id_curso, **campos):
        if not campos:
            return None
        try:
            return get_db().curso.find_one_and_update(
                {"_id": id_curso}, {"$set": campos}, return_document=ReturnDocument.AFTER
            )
        except Exception as e:
            print(f"Erro ao atualizar coleção curso: {e}")
            return None

    def delete(self, id_curso):
        """ON DELETE SET NULL: vinculo.curso passa a null."""
        try:
            db = get_db()
            doc = db.curso.find_one_and_delete({"_id": id_curso})
            if doc:
                db.vinculo.update_many({"curso": id_curso}, {"$set": {"curso": None}})
            return doc
        except Exception as e:
            print(f"Erro ao deletar da coleção curso: {e}")
            return None
