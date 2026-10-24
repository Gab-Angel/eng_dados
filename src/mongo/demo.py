"""
Demonstração para o relatório/apresentação: executa cada método dos 4 CRUDs
e imprime o estado da coleção antes e depois (efeito no banco).
Uso: uv run python -m src.mongo.demo
"""
from pprint import pprint

from src.mongo.conn import get_db
from src.mongo.crud.crud_usuario import UsuarioCrud
from src.mongo.crud.crud_estudante import EstudanteCrud
from src.mongo.crud.crud_curso import CursoCrud
from src.mongo.crud.crud_vinculo import VinculoCrud


def estado(colecao, titulo):
    print(f"\n--- {titulo} [{colecao}] ---")
    pprint(list(get_db()[colecao].find()), width=100)


def passo(titulo, colecao, fn):
    estado(colecao, f"ANTES: {titulo}")
    resultado = fn()
    print(f">>> retorno: {resultado}")
    estado(colecao, f"DEPOIS: {titulo}")


if __name__ == "__main__":
    u, e, c, v = UsuarioCrud(), EstudanteCrud(), CursoCrud(), VinculoCrud()

    passo("usuario.insert", "usuario", lambda: u.insert(
        "12345678901", "Maria Silva", "2003-05-10", ["maria@ufs.br"], ["79999990000"], "maria", "s3nh4"))
    passo("usuario.update", "usuario", lambda: u.update("12345678901", nome="Maria S. Souza"))

    passo("curso.insert", "curso", lambda: c.insert(
        "Sistemas de Informação", "Noturno", "Bacharelado", "São Cristóvão", "Graduação"))
    id_curso = c.read()[-1]["_id"]
    passo("curso.update", "curso", lambda: c.update(id_curso, turno="Matutino"))

    passo("estudante.insert", "estudante", lambda: e.insert("2026001", "12345678901", 8, 2026))
    passo("estudante.update", "estudante", lambda: e.update("2026001", mc=9))

    passo("vinculo.insert", "vinculo", lambda: v.insert("2026001", id_curso, "2026-03-01", "Ativo"))
    id_vinc = v.read()[-1]["_id"]
    passo("vinculo.update", "vinculo", lambda: v.update(id_vinc, status="Formando"))

    # Restrições: FK violada e domínio violado
    print("\n=== Violações de restrição ===")
    v.insert("inexistente", id_curso, "2026-03-01", "Ativo")
    v.insert("2026001", id_curso, "2026-03-01", "StatusInvalido")

    # Cascatas
    passo("curso.delete (vinculo.curso -> null)", "vinculo", lambda: c.delete(id_curso))
    passo("usuario.delete (estudante.cpf -> null)", "estudante", lambda: u.delete("12345678901"))
    passo("vinculo.delete", "vinculo", lambda: v.delete(id_vinc))
    passo("estudante.delete", "estudante", lambda: e.delete("2026001"))
