from pymongo import ReturnDocument

from src.mongo.conn import get_db, next_id, to_date, IntegrityError
from src.postgres.crud.crud_base import BaseCrud


def _check_fks(mat_estudante, curso):
    db = get_db()
    if mat_estudante is not None and db.estudante.count_documents({"_id": mat_estudante}, limit=1) == 0:
        raise IntegrityError(f"FK violada: estudante {mat_estudante} não existe")
    if curso is not None and db.curso.count_documents({"_id": curso}, limit=1) == 0:
        raise IntegrityError(f"FK violada: curso {curso} não existe")


class VinculoCrud(BaseCrud):
    """Coleção `vinculo` (_id = idVinculo). Referencia estudante e curso."""

    def insert(self, mat_estudante, curso, data_entrada, status, data_saida=None):
        try:
            _check_fks(mat_estudante, curso)
            doc = {
                "_id": next_id("vinculo"),
                "mat_estudante": mat_estudante,
                "curso": curso,
                "data_entrada": to_date(data_entrada),
                "status": status,
                "data_saida": to_date(data_saida),
            }
            get_db().vinculo.insert_one(doc)
            return doc
        except Exception as e:
            print(f"Erro ao inserir na coleção vinculo: {e}")
            return None

    def read(self, id_vinculo=None):
        try:
            filtro = {"_id": id_vinculo} if id_vinculo is not None else {}
            return list(get_db().vinculo.find(filtro))
        except Exception as e:
            print(f"Erro ao ler coleção vinculo: {e}")
            return []

    def find_by_estudante(self, mat_estudante):
        try:
            return list(get_db().vinculo.find({"mat_estudante": mat_estudante}))
        except Exception as e:
            print(f"Erro ao buscar vínculos do estudante: {e}")
            return []

    def update(self, id_vinculo, **campos):
        if not campos:
            return None
        try:
            _check_fks(campos.get("mat_estudante"), campos.get("curso"))
            for k in ("data_entrada", "data_saida"):
                if k in campos:
                    campos[k] = to_date(campos[k])
            return get_db().vinculo.find_one_and_update(
                {"_id": id_vinculo}, {"$set": campos}, return_document=ReturnDocument.AFTER
            )
        except Exception as e:
            print(f"Erro ao atualizar coleção vinculo: {e}")
            return None

    def delete(self, id_vinculo):
        try:
            return get_db().vinculo.find_one_and_delete({"_id": id_vinculo})
        except Exception as e:
            print(f"Erro ao deletar da coleção vinculo: {e}")
            return None
