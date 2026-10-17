CREATE TYPE tipo_jornada AS ENUM ('20h', '40h', 'DE');

CREATE TYPE tipo_formacao AS ENUM (
    'Graduação', 'Especialização', 'Mestrado', 'Doutorado'
);

CREATE TYPE tipo_grau AS ENUM (
    'Bacharelado', 'Licenciatura Plena'
);

CREATE TYPE tipo_nivel AS ENUM (
    'Graduação', 'Mestrado', 'Doutorado', 'Lato'
);

CREATE TYPE tipo_turno AS ENUM (
    'Matutino', 'Vespertino', 'Noturno', 'Turno Indefinido'
);

CREATE TYPE status_estudante AS ENUM (
    'Ativo', 'Cancelada', 'Formando', 'Graduado'
);

CREATE TABLE usuario (
    cpf NUMERIC(13),
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE,
    email VARCHAR[],
    telefone VARCHAR[],
    login VARCHAR(45) UNIQUE,
    senha VARCHAR(32),
    CONSTRAINT pk_usuario PRIMARY KEY (cpf)
);

CREATE TABLE professor (
    mat_professor VARCHAR(7),
    cpf NUMERIC(13) UNIQUE,
    departamento VARCHAR(5),
    formacao tipo_formacao,
    data_admissao DATE,
    tipo_jornada_trabalho tipo_jornada,
    salario FLOAT,
    CONSTRAINT pk_professor PRIMARY KEY (mat_professor),
    CONSTRAINT fk_usuario FOREIGN KEY (cpf) REFERENCES usuario(cpf)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE departamento (
    cod_depto VARCHAR(5),
    nome VARCHAR(50) NOT NULL,
    chefe VARCHAR(7),
    orcamento REAL CHECK (orcamento > 0),
    comissal FLOAT,
    CONSTRAINT pk_departamento PRIMARY KEY (cod_depto)
);

ALTER TABLE professor
ADD CONSTRAINT fk_alocacao
FOREIGN KEY (departamento) REFERENCES departamento(cod_depto)
ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE departamento
ADD CONSTRAINT fk_chefia
FOREIGN KEY (chefe) REFERENCES professor(mat_professor)
ON DELETE SET NULL ON UPDATE CASCADE;

CREATE TABLE curso (
    idCurso SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    grau tipo_grau,
    turno tipo_turno NOT NULL,
    campus VARCHAR(100),
    nivel tipo_nivel,
    CONSTRAINT uq_curso UNIQUE (nome, turno, campus, nivel)
);

CREATE TABLE estudante (
    mat_estudante VARCHAR(7),
    cpf NUMERIC(13),
    MC DECIMAL(2),
    ano_ingresso INT,
    CONSTRAINT pk_estudante PRIMARY KEY (mat_estudante),
    CONSTRAINT fk_usuario FOREIGN KEY (cpf) REFERENCES usuario(cpf)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT uq_cpf UNIQUE (cpf)
);

CREATE TABLE vinculo (
    idVinculo SERIAL PRIMARY KEY,
    mat_estudante VARCHAR(7),
    curso INT,
    data_entrada DATE,
    status status_estudante,
    data_saida DATE,
    CONSTRAINT fk_curso FOREIGN KEY (curso) REFERENCES curso(idCurso)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_estudante FOREIGN KEY (mat_estudante)
        REFERENCES estudante(mat_estudante)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE projeto (
    id_projeto INT,
    descricao VARCHAR,
    CONSTRAINT pk_projeto PRIMARY KEY (id_projeto)
);

CREATE TABLE plano (
    id_projeto INT,
    mat_professor VARCHAR(7),
    mat_estudante VARCHAR(7),
    ano INT,
    CONSTRAINT pk_plano PRIMARY KEY (mat_estudante, ano),
    CONSTRAINT fk_projeto FOREIGN KEY (id_projeto)
        REFERENCES projeto(id_projeto)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_professor FOREIGN KEY (mat_professor)
        REFERENCES professor(mat_professor)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_mat_estudante FOREIGN KEY (mat_estudante)
        REFERENCES estudante(mat_estudante)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE disciplina (
    cod_disc VARCHAR(8),
    nome VARCHAR(40) NOT NULL,
    pre_req VARCHAR(8),
    creditos SMALLINT CHECK (1 <= creditos AND creditos < 12),
    depto_responsavel VARCHAR(5),
    CONSTRAINT pk_disciplina PRIMARY KEY (cod_disc),
    CONSTRAINT fk_pre_req FOREIGN KEY (pre_req)
        REFERENCES disciplina(cod_disc)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_responsavel FOREIGN KEY (depto_responsavel)
        REFERENCES departamento(cod_depto)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE SEQUENCE seq_turma INCREMENT 1 START 1;

CREATE TABLE semestre (
    ano SMALLINT,
    semestre SMALLINT,
    data_inicio DATE,
    data_fom DATE,
    CONSTRAINT pk_semestre PRIMARY KEY (ano, semestre)
);

CREATE TABLE sala (
    id_sala SERIAL,
    descricao VARCHAR,
    CONSTRAINT pk_sala PRIMARY KEY (id_sala)
);

CREATE TABLE horario (
    id_horario SERIAL,
    dia VARCHAR(15) NOT NULL,
    slot SMALLINT NOT NULL,
    CONSTRAINT pk_horario PRIMARY KEY (id_horario)
);

CREATE TABLE turma (
    id_turma INT DEFAULT nextval('seq_turma'),
    cod_disc VARCHAR(8) NOT NULL,
    numero INT,
    ano SMALLINT,
    semestre SMALLINT,
    CONSTRAINT pk_turma PRIMARY KEY (id_turma),
    CONSTRAINT uq_turma UNIQUE (cod_disc, numero, semestre, ano),
    CONSTRAINT fk_disciplina FOREIGN KEY (cod_disc)
        REFERENCES disciplina(cod_disc)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_semestre FOREIGN KEY (ano, semestre)
        REFERENCES semestre(ano, semestre)
        ON DELETE NO ACTION ON UPDATE CASCADE
);

CREATE TABLE leciona (
    id_turma INT NOT NULL,
    mat_professor VARCHAR(7) NOT NULL,
    CONSTRAINT pk_leciona PRIMARY KEY (id_turma, mat_professor),
    CONSTRAINT fk_turma FOREIGN KEY (id_turma)
        REFERENCES turma(id_turma)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_professor FOREIGN KEY (mat_professor)
        REFERENCES professor(mat_professor)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE alocacao (
    id_turma INT,
    id_horario INT,
    id_sala INT,
    CONSTRAINT pk_alocacao PRIMARY KEY (id_turma, id_horario),
    CONSTRAINT uq_alocacao UNIQUE (id_horario, id_sala)
);

CREATE TABLE cursa (
    mat_estudante VARCHAR(7),
    id_turma INT,
    nota REAL,
    CONSTRAINT pk_cursa PRIMARY KEY (mat_estudante, id_turma),
    CONSTRAINT fk_turma FOREIGN KEY (id_turma)
        REFERENCES turma(id_turma)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_estudante FOREIGN KEY (mat_estudante)
        REFERENCES estudante(mat_estudante)
        ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO semestre VALUES (2026,2,NULL, NULL);
INSERT INTO departamento VALUES ('DMA', 'Departamento de Matemática', NULL, 20000,1000);
INSERT INTO disciplina VALUES ('MAT0064', 'Cálculo I', NULL, 6, 'DMA');
