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
    nome VARCHAR(150) PRIMARY KEY,
    indirizzo TEXT,
    citta VARCHAR(100),
    paese VARCHAR(100) NOT NULL
);

CREATE TABLE pratiche (
    id SERIAL PRIMARY KEY,
    studente_email VARCHAR(150) NOT NULL,
    docente_email VARCHAR(150),
    nome_istituto VARCHAR(150),
    stato VARCHAR(30) NOT NULL DEFAULT 'CREATA'
        CHECK (stato IN (
            'CREATA',
            'ATTESA_APPROVAZIONE',
            'APPROVATA_DOCENTE',
            'APPROVATA_UFFICIO',
            'MOBILITA_IN_CORSO',
            'APPROVATO_TRANSCRIPT',
            'CHIUSA'
        )),
    data_creazione TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivazione TEXT,
    data_inizio DATE NOT NULL,
    data_fine DATE,
    CONSTRAINT fk_pratica_studente
        FOREIGN KEY (studente_email)
        REFERENCES utenti(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_pratica_docente
        FOREIGN KEY (docente_email)
        REFERENCES utenti(email)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_pratica_istituto
        FOREIGN KEY (nome_istituto)
        REFERENCES istituti(nome)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE esami (
    nome VARCHAR(150) PRIMARY KEY,
    crediti INTEGER NOT NULL CHECK (crediti > 0)
    esame_estero FOREIGN KEY REFERENCES esami_esteri(nome)
        ON DELETE SET NULL
);

CREATE TABLE esami_esteri (
    nome VARCHAR(150) PRIMARY KEY,
    crediti INTEGER NOT NULL CHECK (crediti > 0)
);

CREATE TABLE esami_pratica (
    id SERIAL PRIMARY KEY,
    pratica_id INTEGER NOT NULL,
    esame_locale_id VARCHAR(20) NOT NULL,
    esame_estero_id VARCHAR(20) NOT NULL,
    CONSTRAINT fk_ep_pratica
        FOREIGN KEY (pratica_id)
        REFERENCES pratiche(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_ep_esame_locale
        FOREIGN KEY (esame_locale_id)
        REFERENCES esami(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_ep_esame_estero
        FOREIGN KEY (esame_estero_id)
        REFERENCES esami_esteri(id)
        ON DELETE RESTRICT,
    CONSTRAINT uq_pratica_esame_locale
        UNIQUE (pratica_id, esame_locale_id),
    CONSTRAINT uq_pratica_esame_estero
        UNIQUE (pratica_id, esame_estero_id)
);

CREATE TABLE learning_agreement (
    id SERIAL PRIMARY KEY,
    pratica_id INTEGER NOT NULL UNIQUE,
    data_upload TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_pdf BYTEA,
    CONSTRAINT fk_learning_pratica
        FOREIGN KEY (pratica_id)
        REFERENCES pratiche(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE transcript_of_records (
    id SERIAL PRIMARY KEY,
    pratica_id INTEGER NOT NULL UNIQUE,
    data_upload TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_pdf BYTEA,
    CONSTRAINT fk_transcript_pratica
        FOREIGN KEY (pratica_id)
        REFERENCES pratiche(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
