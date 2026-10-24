from datetime import datetime

from pymongo.errors import CollectionInvalid

from src.mongo.conn import get_db

INT = ["int", "long"]


def _t(bson, nullable=False, **kw):
    types = list(bson) if isinstance(bson, list) else [bson]
    if nullable:
        types.append("null")
        if "enum" in kw:
            kw["enum"] = kw["enum"] + [None]
    return {"bsonType": types if len(types) > 1 else types[0], **kw}


def _str(max_len=None, nullable=False, **kw):
    if max_len:
        kw["maxLength"] = max_len
    return _t("string", nullable, **kw)


ENUMS = {
    "jornada": ["20h", "40h", "DE"],
    "formacao": ["Graduação", "Especialização", "Mestrado", "Doutorado"],
    "grau": ["Bacharelado", "Licenciatura Plena"],
    "nivel": ["Graduação", "Mestrado", "Doutorado", "Lato"],
    "turno": ["Matutino", "Vespertino", "Noturno", "Turno Indefinido"],
    "status": ["Ativo", "Cancelada", "Formando", "Graduado"],
}

# nome -> (required, properties, indexes)
# indexes: (keys, opções)
COLLECTIONS = {
    "usuario": (
        ["_id", "nome"],
        {
            "_id": _str(13, pattern=r"^[0-9]{1,13}$"),  # cpf (string: preserva zeros à esquerda)
            "nome": _str(100, minLength=1),
            "data_nascimento": _t("date", True),
            "email": {"bsonType": "array", "items": _str()},          # VARCHAR[]
            "telefone": {"bsonType": "array", "items": _str()},       # VARCHAR[]
            "login": _str(45, nullable=True),
            "senha": _str(32, nullable=True),
        },
        [([("login", 1)], {"unique": True, "partialFilterExpression": {"login": {"$type": "string"}}})],
    ),
    "professor": (
        ["_id"],
        {
            "_id": _str(7),  # mat_professor
            "cpf": _str(13, True, pattern=r"^[0-9]{1,13}$"),
            "departamento": _str(5, True),
            "formacao": _t("string", True, enum=ENUMS["formacao"]),
            "data_admissao": _t("date", True),
            "tipo_jornada_trabalho": _t("string", True, enum=ENUMS["jornada"]),
            "salario": _t(["double", "int", "long"], True),
        },
        [([("cpf", 1)], {"unique": True, "partialFilterExpression": {"cpf": {"$type": "string"}}})],
    ),
    "departamento": (
        ["_id", "nome"],
        {
            "_id": _str(5),  # cod_depto
            "nome": _str(50, minLength=1),
            "chefe": _str(7, True),
            "orcamento": _t(["double", "int", "long"], True, minimum=0, exclusiveMinimum=True),
            "comissal": _t(["double", "int", "long"], True),
        },
        [],
    ),
    "curso": (
        ["_id", "nome", "turno"],
        {
            "_id": _t(INT),  # idCurso (contador)
            "nome": _str(100, minLength=1),
            "grau": _t("string", True, enum=ENUMS["grau"]),
            "turno": _t("string", enum=ENUMS["turno"]),
            "campus": _str(100, True),
            "nivel": _t("string", True, enum=ENUMS["nivel"]),
        },
        [([("nome", 1), ("turno", 1), ("campus", 1), ("nivel", 1)], {"unique": True, "name": "uq_curso"})],
    ),
    "estudante": (
        ["_id"],
        {
            "_id": _str(7),  # mat_estudante
            "cpf": _str(13, True, pattern=r"^[0-9]{1,13}$"),
            "mc": _t(["double", "int", "long"], True, minimum=0, maximum=99),  # DECIMAL(2)
            "ano_ingresso": _t(INT, True),
        },
        [([("cpf", 1)], {"unique": True, "partialFilterExpression": {"cpf": {"$type": "string"}}})],
    ),
    "vinculo": (
        ["_id"],
        {
            "_id": _t(INT),  # idVinculo (contador)
            "mat_estudante": _str(7, True),
            "curso": _t(INT, True),
            "data_entrada": _t("date", True),
            "status": _t("string", True, enum=ENUMS["status"]),
            "data_saida": _t("date", True),
        },
        [([("mat_estudante", 1)], {}), ([("curso", 1)], {})],
    ),
    "projeto": (
        ["_id"],
        {"_id": _t(INT), "descricao": _str(nullable=True)},
        [],
    ),
    "plano": (
        ["mat_estudante", "ano"],
        {
            "id_projeto": _t(INT, True),
            "mat_professor": _str(7, True),
            "mat_estudante": _str(7),
            "ano": _t(INT),
        },
        [([("mat_estudante", 1), ("ano", 1)], {"unique": True, "name": "pk_plano"})],
    ),
    "disciplina": (
        ["_id", "nome"],
        {
            "_id": _str(8),  # cod_disc
            "nome": _str(40, minLength=1),
            "pre_req": _str(8, True),
            "creditos": _t(INT, True, minimum=1, maximum=11),  # CHECK 1 <= creditos < 12
            "depto_responsavel": _str(5, True),
        },
        [],
    ),
    "semestre": (
        ["ano", "semestre"],
        {
            "ano": _t(INT),
            "semestre": _t(INT),
            "data_inicio": _t("date", True),
            "data_fim": _t("date", True),  # data_fom no script original
        },
        [([("ano", 1), ("semestre", 1)], {"unique": True, "name": "pk_semestre"})],
    ),
    "sala": (["_id"], {"_id": _t(INT), "descricao": _str(nullable=True)}, []),
    "horario": (
        ["_id", "dia", "slot"],
        {"_id": _t(INT), "dia": _str(15), "slot": _t(INT)},
        [],
    ),
    # turma incorpora LECIONA (N:N -> array de matrículas) e ALOCACAO (1:N -> subdocumentos)
    "turma": (
        ["_id", "cod_disc"],
        {
            "_id": _t(INT),  # id_turma (seq_turma)
            "cod_disc": _str(8),
            "numero": _t(INT, True),
            "ano": _t(INT, True),
            "semestre": _t(INT, True),
            "professores": {"bsonType": "array", "uniqueItems": True, "items": _str(7)},
            "alocacoes": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["id_horario", "id_sala"],
                    "properties": {"id_horario": _t(INT), "id_sala": _t(INT)},
                },
            },
        },
        [
            ([("cod_disc", 1), ("numero", 1), ("semestre", 1), ("ano", 1)], {"unique": True, "name": "uq_turma"}),
            ([("professores", 1)], {}),
            ([("alocacoes.id_horario", 1), ("alocacoes.id_sala", 1)], {"unique": True, "name": "uq_alocacao"}),
        ],
    ),
    "cursa": (
        ["mat_estudante", "id_turma"],
        {"mat_estudante": _str(7), "id_turma": _t(INT), "nota": _t(["double", "int", "long"], True)},
        [([("mat_estudante", 1), ("id_turma", 1)], {"unique": True, "name": "pk_cursa"}), ([("id_turma", 1)], {})],
    ),
}


def _validator(required, props):
    props = {"_id": {"bsonType": "objectId"}, **props}  # _id automático quando não há chave natural
    return {"$jsonSchema": {"bsonType": "object", "required": required,
                            "properties": props, "additionalProperties": False}}


def create_collections():
    db = get_db()
    for name, (required, props, indexes) in COLLECTIONS.items():
        validator = _validator(required, props)
        try:
            db.create_collection(name, validator=validator, validationLevel="strict", validationAction="error")
        except CollectionInvalid:  # já existe: só atualiza o validador
            db.command("collMod", name, validator=validator, validationLevel="strict", validationAction="error")
        for keys, opts in indexes:
            db[name].create_index(keys, **opts)
    print("Coleções, validadores e índices criados com sucesso")


def seed():
    """Linhas originais do script relacional (idempotente)."""
    db = get_db()
    db.semestre.update_one({"ano": 2026, "semestre": 2},
                           {"$setOnInsert": {"data_inicio": None, "data_fim": None}}, upsert=True)
    db.departamento.update_one({"_id": "DMA"}, {"$setOnInsert": {
        "nome": "Departamento de Matemática", "chefe": None, "orcamento": 20000, "comissal": 1000}}, upsert=True)
    db.disciplina.update_one({"_id": "MAT0064"}, {"$setOnInsert": {
        "nome": "Cálculo I", "pre_req": None, "creditos": 6, "depto_responsavel": "DMA"}}, upsert=True)
    print("Dados iniciais (semestre, departamento, disciplina) inseridos")


if __name__ == "__main__":
    create_collections()
    seed()
