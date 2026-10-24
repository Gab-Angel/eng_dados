# Parte 2 — Projeto Lógico NoSQL (MongoDB)

## 1. Pesquisa e estudo de SGBDs NoSQL

| Família | Exemplos | Modelo de representação | Bom para | Limitação para este domínio |
|---|---|---|---|---|
| Chave-valor | Redis, DynamoDB | par chave → valor opaco | cache, sessões | sem consultas por atributos / junções |
| **Documento** | **MongoDB**, CouchDB | documentos JSON/BSON em coleções | dados semiestruturados, entidades com atributos multivalorados e aninhamento | sem FK nativa; junções limitadas (`$lookup`) |
| Colunar (famílias de colunas) | Cassandra, HBase | linhas com famílias de colunas, modeladas por consulta | escrita massiva, séries temporais | modelagem orientada a consultas, pouca flexibilidade |
| Grafos | Neo4j | nós e arestas | relacionamentos profundos | o domínio é pouco "navegacional" |

**Escolha: MongoDB** (exigido pelo enunciado e adequado ao domínio): atributos multivalorados do
modelo relacional (`email[]`, `telefone[]`) viram arrays nativos; relacionamentos N:N pequenos
(`leciona`) e entidades fracas (`alocacao`) podem ser embutidos; e há validação declarativa
(`$jsonSchema`) e índices únicos para impor restrições.

## 2. Método de mapeamento

Regras adotadas (guia de modelagem de relacionamentos do MongoDB — *embed vs. reference*):

1. **Entidade com ciclo de vida próprio → coleção própria**, chave primária → `_id` (chave natural) ou índice único composto.
2. **Atributo multivalorado → array** dentro do documento (`usuario.email`, `usuario.telefone`).
3. **Relacionamento N:N sem atributos próprios e limitado → array de referências no lado que o consulta** (`leciona` → `turma.professores`).
4. **Entidade fraca / 1:N limitado e sempre lido junto → subdocumentos embutidos** (`alocacao` → `turma.alocacoes`).
5. **Relacionamento 1:N ilimitado ou com atributos próprios → coleção separada com referência** (`vinculo`, `cursa`, `plano`).
6. **SERIAL / SEQUENCE → coleção `counters`** com `findOneAndUpdate($inc)` (atômico).

## 3. Mapeamento das 16 tabelas

| Tabela relacional | Estrutura MongoDB | Chave | Observação |
|---|---|---|---|
| usuario | coleção `usuario` | `_id` = cpf (string) | `email[]`, `telefone[]` como arrays; cpf como string preserva zeros à esquerda |
| professor | coleção `professor` | `_id` = mat_professor | `cpf` (ref. usuario, único parcial), `departamento` (ref.) |
| departamento | coleção `departamento` | `_id` = cod_depto | `chefe` (ref. professor) |
| curso | coleção `curso` | `_id` = idCurso (contador) | índice único `(nome, turno, campus, nivel)` |
| estudante | coleção `estudante` | `_id` = mat_estudante | `cpf` único parcial (ref. usuario) |
| vinculo | coleção `vinculo` | `_id` = idVinculo (contador) | refs. `mat_estudante` e `curso`; cresce sem limite → não embutido |
| projeto | coleção `projeto` | `_id` = id_projeto | |
| plano | coleção `plano` | índice único `(mat_estudante, ano)` | refs. projeto, professor, estudante |
| disciplina | coleção `disciplina` | `_id` = cod_disc | `pre_req` (auto-ref.), `depto_responsavel` (ref.) |
| semestre | coleção `semestre` | índice único `(ano, semestre)` | `data_fom` do script → `data_fim` |
| sala | coleção `sala` | `_id` = id_sala | |
| horario | coleção `horario` | `_id` = id_horario | |
| turma | coleção `turma` | `_id` = id_turma (contador) | **absorve leciona e alocacao** |
| leciona | `turma.professores: [mat_professor]` | — | N:N sem atributos; `uniqueItems` evita duplicata |
| alocacao | `turma.alocacoes: [{id_horario, id_sala}]` | — | índice único multikey `(id_horario, id_sala)` entre turmas |
| cursa | coleção `cursa` | índice único `(mat_estudante, id_turma)` | tem atributo `nota`; volume alto → não embutido |

Exemplo de documento `turma`:

```json
{ "_id": 1, "cod_disc": "MAT0064", "numero": 1, "ano": 2026, "semestre": 2,
  "professores": ["1234567"],
  "alocacoes": [ { "id_horario": 3, "id_sala": 7 } ] }
```

## 4. Como as restrições são garantidas

| Restrição (SQL) | Mecanismo no MongoDB | Onde |
|---|---|---|
| Chave primária | `_id` natural / índice único composto | `schema.py` |
| UNIQUE | índice único; **parcial** (`$type: string`) quando a coluna aceita NULL, para múltiplos NULL | `schema.py` |
| NOT NULL | `required` + `bsonType` sem `"null"` | `$jsonSchema` |
| Domínio (ENUM, tipo, tamanho) | `enum`, `bsonType`, `maxLength`, `pattern` | `$jsonSchema` |
| CHECK | `minimum`, `maximum`, `exclusiveMinimum` (ex.: `creditos` 1..11, `orcamento > 0`) | `$jsonSchema` |
| Campos inesperados | `additionalProperties: false` | `$jsonSchema` |
| **FOREIGN KEY** | **não existe no MongoDB** → verificada antes de inserir/atualizar (`IntegrityError`) | `crud_*.py` |
| ON DELETE SET NULL | `update_many` zerando a referência após o delete | `crud_*.py` |
| ON DELETE CASCADE | `delete_many` nos documentos dependentes | `crud_estudante.py` |
| ON UPDATE CASCADE | **não suportado**: `_id` é imutável. Chaves não são alteradas pelo CRUD | limitação documentada |

Validação com `validationLevel: strict` e `validationAction: error`: documentos inválidos são **rejeitados** pelo servidor.

### Limitações conhecidas (para discutir na apresentação)
- Integridade referencial é **por convenção da aplicação**; escrita direta no banco (fora do CRUD) pode violá-la.
- Sem transações multi-documento em instância standalone; cascatas são *best effort* (ordem: operação principal, depois dependentes). Em *replica set* poderiam usar `start_session().with_transaction()`.
- Índice único no MongoDB trata `null`/ausente como valor igual; em `uq_curso` dois cursos idênticos com `campus` nulo são rejeitados (no SQL seriam aceitos).
- `estudante.mc` era `DECIMAL(2)` (0–99); mantido o limite 0–99.

## 5. Hospedagem na AWS

O enunciado exige **MongoDB** hospedado na AWS. Atenção: **Amazon DocumentDB não serve** — é compatível
com a API do MongoDB mas **não suporta `$jsonSchema`**, o que invalidaria a validação de restrições. Opções:

1. **EC2 + MongoDB Community** (ex.: `docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=... -e MONGO_INITDB_ROOT_PASSWORD=... -v mongo:/data/db mongo:7`), liberando a porta 27017 no *Security Group* apenas para os IPs do grupo.
2. **MongoDB Atlas** com cluster na região AWS.

Depois, preencher `MONGO_URI` no `.env` (ver `.env.example`).

## 6. Como executar

```bash
uv sync
cp .env.example .env            # preencher MONGO_URI / MONGO_DB
uv run python -m src.mongo.schema   # cria coleções, validadores, índices e dados iniciais
uv run python -m src.mongo.demo     # executa cada método mostrando ANTES/DEPOIS (para o relatório)
uv run pytest tests/mongo -v        # testes (usam o database `universidade_test`)
```

## 7. Roteiro do relatório
1. Pesquisa NoSQL e justificativa (seção 1) · 2. Método de mapeamento (2) · 3. Tabela de mapeamento (3)
· 4. Restrições (4) · 5. Saída do `demo.py` (efeito de cada método) · 6. Link do GitHub.
