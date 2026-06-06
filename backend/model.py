from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Utente(db.Model):
    __tablename__ = "utenti"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    salt = db.Column(db.Text, nullable=False)
    ruolo = db.Column(db.String(1), nullable=False)
    data_nascita = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.CheckConstraint("ruolo IN ('S', 'D', 'U')", name="check_ruolo"),
        db.CheckConstraint(
            "data_nascita <= CURRENT_DATE - INTERVAL '18 years'",
            name="check_eta_18"
        ),
        db.CheckConstraint("email  LIKE '____%@unive.it'",name="check_email")
    )

    pratiche_studente = db.relationship(
        "Pratica",
        foreign_keys="Pratica.studente_id",
        back_populates="studente"
    )

    pratiche_docente = db.relationship(
        "Pratica",
        foreign_keys="Pratica.docente_id",
        back_populates="docente"
    )

    def __init__(self, nome, cognome, email, password_hash, salt, ruolo, data_nascita):
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.password_hash = password_hash
        self.salt = salt
        self.ruolo = ruolo
        self.data_nascita = data_nascita


class Istituto(db.Model):
    __tablename__ = "istituti"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    citta = db.Column(db.String(100))
    paese = db.Column(db.String(100), nullable=False)

    pratiche = db.relationship("Pratica", back_populates="istituto")

    def __init__(self, nome, citta, paese):
        self.nome = nome
        self.citta = citta
        self.paese = paese


class Pratica(db.Model):
    __tablename__ = "pratiche"

    id = db.Column(db.Integer, primary_key=True)

    studente_id = db.Column(
        db.Integer,
        db.ForeignKey("utenti.id", ondelete="RESTRICT"),
        nullable=False
    )

    docente_id = db.Column(
        db.Integer,
        db.ForeignKey("utenti.id", ondelete="RESTRICT"),
        nullable=False
    )

    istituto_id = db.Column(
        db.Integer,
        db.ForeignKey("istituti.id", ondelete="RESTRICT"),
        nullable=False
    )

    anno_accademico = db.Column(db.String(9), nullable=False)
    periodo = db.Column(db.String(20), nullable=False)
    stato = db.Column(db.String(5), nullable=False, default="CRE")
    data_creazione = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)
    approvato = db.Column(db.Boolean)
    motivazione = db.Column(db.Text)

    __table_args__ = (
        db.CheckConstraint(
            "stato IN ('CRE', 'ALA', 'PPC', 'MC', 'IRE', 'CHI')",
            name="check_stato_pratica"
        ),
    )

    studente = db.relationship(
        "Utente",
        foreign_keys=[studente_id],
        back_populates="pratiche_studente"
    )

    docente = db.relationship(
        "Utente",
        foreign_keys=[docente_id],
        back_populates="pratiche_docente"
    )

    istituto = db.relationship(
        "Istituto",
        back_populates="pratiche"
    )

    esami = db.relationship(
        "Esame",
        back_populates="pratica",
        cascade="all, delete-orphan"
    )

    learning_agreements = db.relationship(
        "LearningAgreement",
        back_populates="pratica",
        cascade="all, delete-orphan"
    )

    transcripts = db.relationship(
        "TranscriptOfRecords",
        back_populates="pratica",
        cascade="all, delete-orphan"
    )

    def __init__(self, studente_id, docente_id, istituto_id, anno_accademico,
                 periodo, stato="CRE", data_inizio=None, data_fine=None,
                 approvato=None, motivazione=None):
        self.studente_id = studente_id
        self.docente_id = docente_id
        self.istituto_id = istituto_id
        self.anno_accademico = anno_accademico
        self.periodo = periodo
        self.stato = stato
        self.data_inizio = data_inizio
        self.data_fine = data_fine
        self.approvato = approvato
        self.motivazione = motivazione


class Esame(db.Model):
    __tablename__ = "esami"

    id = db.Column(db.Integer, primary_key=True)

    pratica_id = db.Column(
        db.Integer,
        db.ForeignKey("pratiche.id", ondelete="CASCADE"),
        nullable=False
    )

    nome = db.Column(db.String(150), nullable=False)
    crediti = db.Column(db.Integer, nullable=False)

    id_esame_estero = db.Column(
        db.Integer,
        db.ForeignKey("esami.id", ondelete="SET NULL"),
        nullable=True
    )

    __table_args__ = (
        db.CheckConstraint("crediti > 0", name="check_crediti_positivi"),
    )

    pratica = db.relationship("Pratica", back_populates="esami")

    esame_estero = db.relationship(
        "Esame",
        remote_side="Esame.id",
        foreign_keys=[id_esame_estero]
    )

    def __init__(self, pratica_id, nome, crediti, id_esame_estero=None):
        self.pratica_id = pratica_id
        self.nome = nome
        self.crediti = crediti
        self.id_esame_estero = id_esame_estero


class LearningAgreement(db.Model):
    __tablename__ = "learning_agreement"

    id = db.Column(db.Integer, primary_key=True)

    pratica_id = db.Column(
        db.Integer,
        db.ForeignKey("pratiche.id", ondelete="CASCADE"),
        nullable=False
    )

    path_f = db.Column(db.Text, nullable=False)
    versione = db.Column(db.Integer, nullable=False, default=1)
    data_upload = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_decisione = db.Column(db.DateTime)
    approvato = db.Column(db.Boolean)
    motivazione = db.Column(db.Text)

    pratica = db.relationship("Pratica", back_populates="learning_agreements")

    def __init__(self, pratica_id, path_f, versione=1, data_upload=None,
                 data_decisione=None, approvato=None, motivazione=None):
        self.pratica_id = pratica_id
        self.path_f = path_f
        self.versione = versione
        self.data_upload = data_upload
        self.data_decisione = data_decisione
        self.approvato = approvato
        self.motivazione = motivazione


class TranscriptOfRecords(db.Model):
    __tablename__ = "transcript_of_records"

    id = db.Column(db.Integer, primary_key=True)

    pratica_id = db.Column(
        db.Integer,
        db.ForeignKey("pratiche.id", ondelete="CASCADE"),
        nullable=False
    )

    path_f = db.Column(db.Text, nullable=False)
    versione = db.Column(db.Integer, nullable=False, default=1)
    data_upload = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_decisione = db.Column(db.DateTime)
    approvato = db.Column(db.Boolean)
    motivazione = db.Column(db.Text)

    pratica = db.relationship("Pratica", back_populates="transcripts")

    def __init__(self, pratica_id, path_f, versione=1, data_upload=None,
                 data_decisione=None, approvato=None, motivazione=None):
        self.pratica_id = pratica_id
        self.path_f = path_f
        self.versione = versione
        self.data_upload = data_upload
        self.data_decisione = data_decisione
        self.approvato = approvato
        self.motivazione = motivazione