CREATE TABLE utenti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cognome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    ruolo CHAR(1) NOT NULL
        CHECK (ruolo IN ('S', 'D', 'U')),
    data_nascita DATE NOT NULL,
    CONSTRAINT chk_eta_18
        CHECK (
            data_nascita <= CURRENT_DATE - INTERVAL '18 years'
        )
);

CREATE TABLE istituti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    indirizzo TEXT,
    citta VARCHAR(100),
    paese VARCHAR(100) NOT NULL
);

CREATE TABLE pratiche (
    id SERIAL PRIMARY KEY,

    studente_id INTEGER NOT NULL,
    docente_id INTEGER NOT NULL,
    id_istituto INTEGER NOT NULL,

    stato VARCHAR(10) NOT NULL DEFAULT 'ATT'
        CHECK (stato IN ('ATT', 'PPC', 'MC', 'C')),

    data_creazione TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivazione TEXT,
    data_inizio DATE NOT NULL,
    data_fine DATE,

    CONSTRAINT fk_pratica_studente
        FOREIGN KEY (studente_id)
        REFERENCES utenti(id),

    CONSTRAINT fk_pratica_docente
        FOREIGN KEY (docente_id)
        REFERENCES utenti(id),

    CONSTRAINT fk_pratica_istituto
        FOREIGN KEY (id_istituto)
        REFERENCES istituti(id)
);

CREATE TABLE esami (
    id_esame SERIAL PRIMARY KEY,
    pratica_id INTEGER NOT NULL,
    nome_esame VARCHAR(150) NOT NULL,
    crediti INTEGER NOT NULL CHECK (crediti > 0),
    id_esame_estero INTEGER,

    CONSTRAINT fk_esame_pratica
        FOREIGN KEY (pratica_id)
        REFERENCES pratiche(id),

    CONSTRAINT fk_esame_equivalente
        FOREIGN KEY (id_esame_estero)
        REFERENCES esami(id_esame),

    CONSTRAINT uq_pratica_esame
        UNIQUE (pratica_id, nome_esame)
);

CREATE TABLE learning_agreement (
    id SERIAL PRIMARY KEY,
    pratica_id INTEGER NOT NULL UNIQUE,
    data_upload TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_pdf BYTEA,

    CONSTRAINT fk_learning_pratica
        FOREIGN KEY (pratica_id)
        REFERENCES pratiche(id)
);

CREATE TABLE transcript_of_records (
    id SERIAL PRIMARY KEY,
    pratica_id INTEGER NOT NULL UNIQUE,
    data_upload TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_pdf BYTEA,

    CONSTRAINT fk_transcript_pratica
        FOREIGN KEY (pratica_id)
        REFERENCES pratiche(id)
);