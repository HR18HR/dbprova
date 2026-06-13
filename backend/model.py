from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Utente(db.Model):
    __tablename__ = "utenti"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    salt = db.Column(db.Text, nullable=False)
    ruolo = db.Column(db.String(1), nullable=False)
    data_nascita = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.CheckConstraint("ruolo IN ('S', 'D', 'U')", name="chk_ruolo"),
        db.CheckConstraint(
            "data_nascita <= CURRENT_DATE - INTERVAL '18 years'",
            name="chk_eta_18"
        ),
    )

    pratiche_studente = db.relationship(
        "Pratica",
        foreign_keys="Pratica.studente_email",
        back_populates="studente"
    )

    pratiche_docente = db.relationship(
        "Pratica",
        foreign_keys="Pratica.docente_email",
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

    nome = db.Column(db.String(150), primary_key=True)
    indirizzo = db.Column(db.Text)
    citta = db.Column(db.String(100))
    paese = db.Column(db.String(100), nullable=False)

    pratiche = db.relationship("Pratica", back_populates="istituto")

    def __init__(self, nome, indirizzo=None, citta=None, paese=None):
        self.nome = nome
        self.indirizzo = indirizzo
        self.citta = citta
        self.paese = paese


class Pratica(db.Model):
    __tablename__ = "pratiche"

    id = db.Column(db.Text, primary_key=True)

    studente_email = db.Column(
        db.String(150),
        db.ForeignKey("utenti.email", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    docente_email = db.Column(
        db.String(150),
        db.ForeignKey("utenti.email", ondelete="SET NULL", onupdate="CASCADE")
    )

    nome_istituto = db.Column(
        db.String(150),
        db.ForeignKey("istituti.nome", ondelete="SET NULL", onupdate="CASCADE")
    )

    stato = db.Column(db.String(30), nullable=False, default="ATT_APPROVAZIONE")

    data_creazione = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    motivazione = db.Column(db.Text)

    data_inizio = db.Column(db.Date, nullable=False)
    data_fine = db.Column(db.Date)
    semestre =db.Column(db.String(250),nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            """
            stato IN (
                'CREATA',
                'ATT_APPROVAZIONE',
                'APPROVATA_DOCENTE',
                'APPROVATA_UFFICIO',
                'MOBILITA_IN_CORSO',
                'APPROVATO_TRANSCRIPT',
                'CHIUSA'
            )
            """,
            name="chk_stato"
        ),
        db.CheckConstraint(
            """
            semestre IN(
            'PRIMO','SECONDO','ANNO'
        )
        """
    )
    )

    studente = db.relationship(
        "Utente",
        foreign_keys=[studente_email],
        back_populates="pratiche_studente"
    )

    docente = db.relationship(
        "Utente",
        foreign_keys=[docente_email],
        back_populates="pratiche_docente"
    )

    istituto = db.relationship("Istituto", back_populates="pratiche")

    esami_pratica = db.relationship(
        "EsamePratica",
        back_populates="pratica",
        cascade="all, delete-orphan"
    )

    def __init__(
            self,
            id,
            studente_email,
            data_inizio,
            semestre,
            docente_email=None,
            nome_istituto=None,
            stato="CREATA",
            data_fine=None,
            motivazione=None
    ):
        self.id = id
        self.studente_email = studente_email
        self.docente_email = docente_email
        self.nome_istituto = nome_istituto
        self.stato = stato
        self.semestre =semestre
        self.data_inizio = data_inizio
        self.data_fine = data_fine
        self.motivazione = motivazione


class EsameEstero(db.Model):
    __tablename__ = "esami_esteri"

    nome = db.Column(db.String(250), primary_key=True)
    crediti = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.CheckConstraint("crediti > 0", name="chk_crediti_estero"),
    )

    esami_locali = db.relationship(
        "Esame",
        back_populates="esame_estero"
    )

    esami_pratica = db.relationship(
        "EsamePratica",
        back_populates="esame_estero"
    )

    def __init__(self, nome, crediti):
        self.nome = nome
        self.crediti = crediti


class Esame(db.Model):
    __tablename__ = "esami"

    nome = db.Column(db.String(250), primary_key=True)
    crediti = db.Column(db.Integer, nullable=False)

    nome_esame_estero = db.Column(
        db.String(250),
        db.ForeignKey("esami_esteri.nome", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True
    )

    __table_args__ = (
        db.CheckConstraint("crediti > 0", name="chk_crediti"),
    )

    esame_estero = db.relationship(
        "EsameEstero",
        back_populates="esami_locali"
    )

    esami_pratica = db.relationship(
        "EsamePratica",
        back_populates="esame_locale"
    )

    def __init__(self, nome, crediti, nome_esame_estero=None):
        self.nome = nome
        self.crediti = crediti
        self.nome_esame_estero = nome_esame_estero


class EsamePratica(db.Model):
    __tablename__ = "esami_pratica"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    pratica_id = db.Column(
        db.Text,
        db.ForeignKey("pratiche.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    esame_locale_nome = db.Column(
        db.String(250),
        db.ForeignKey("esami.nome", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False
    )

    esame_estero_nome = db.Column(
        db.String(250),
        db.ForeignKey("esami_esteri.nome", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "pratica_id",
            "esame_locale_nome",
            name="uq_pratica_esame_locale"
        ),
        db.UniqueConstraint(
            "pratica_id",
            "esame_estero_nome",
            name="uq_pratica_esame_estero"
        ),
    )

    pratica = db.relationship(
        "Pratica",
        back_populates="esami_pratica"
    )

    esame_locale = db.relationship(
        "Esame",
        back_populates="esami_pratica"
    )

    esame_estero = db.relationship(
        "EsameEstero",
        back_populates="esami_pratica"
    )

    def __init__(self, pratica_id, esame_locale_nome, esame_estero_nome):
        self.pratica_id = pratica_id
        self.esame_locale_nome = esame_locale_nome
        self.esame_estero_nome = esame_estero_nome