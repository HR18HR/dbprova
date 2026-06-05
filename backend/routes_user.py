import base64
import datetime
import jwt
import bcrypt
from flask import Blueprint, request, jsonify, current_app

from model import db, Utente, Istituto, Pratica, TranscriptOfRecords, LearningAgreement, Esame

utenti_bp = Blueprint("users", __name__)


# decodifica il JWT e restituisce l'id utente ────────────────────
def _get_id_from_token():
    """Restituisce l'id utente dal JWT, oppure None."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload["id"]
    except jwt.PyJWTError:
        return None


# ── POST /registrazione ─────────────────────────────────────────────────────
@utenti_bp.route("/registrazione", methods=["POST"])
def registrazione():
    data = request.get_json()
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(data["password"].encode(), salt).decode()

    dat = Utente(
        nome=data["nome"],
        cognome=data["cognome"],
        email=data["email"],
        password_hash=password_hash,
        salt=salt.decode(),
        ruolo=data["ruolo"],
        data_nascita=data["data_nascita"]
    )
    try:
        db.session.add(dat)
        db.session.commit()
        return {"msg": "Utente creato"}, 201
    except Exception as e:
        db.session.rollback()
        return {"errore": str(e.orig)}, 400


## ── POST /login ─────────────────────────────────────────────────────────────
@utenti_bp.route("/login", methods=["POST"])
def login():

    # 1. estrai email e password in chiaro dall'header Basic
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Basic "):
        return {"errore": "Credenziali mancanti nell'header"}, 401
    try:
        email, password = auth.split(" ", 1)[1].split(":", 1)
    except Exception:
        return {"errore": "Header Basic non valido"}, 401

    # 2. estrai l'utente dal DB tramite email
    utente = db.session.query(Utente).filter_by(email=email.strip()).first()
    if utente is None:
        return {"errore": "Credenziali non valide"}, 401

    # 3. codifica password + salt e confronta con l'hash salvato
    password_check = bcrypt.hashpw(
        (password + utente.salt).encode(),
        utente.salt.encode()
    )
    if password_check.decode() != utente.password_hash:
        return {"errore": "Credenziali non valide"}, 401

    # 4. genera JWT
    payload = {
        "id":    utente.id,
        "email": utente.email,
        "ruolo": utente.ruolo,
        "exp":   datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return {"token": token}, 200

# ── PUT /utente/me ───────────────────────────────────────────────────────────
@utenti_bp.route("/modifica", methods=["PUT"])
def aggiorna_utente():

    # 1. estrai l'id dal JWT
    utente_id = _get_id_from_token()
    if utente_id is None:
        return {"errore": "Non autenticato"}, 401

    # 2. estrai l'utente dal DB tramite l'id
    utente = db.session.query(Utente).filter_by(id=utente_id).first()
    if utente is None:
        return {"errore": "Utente non trovato"}, 404

    data = request.get_json()

    # 3. modifica i campi presenti nel body
    if "nome" in data:
        utente.nome = data["nome"]

    if "cognome" in data:
        utente.cognome = data["cognome"]

    if "email" in data:
        utente.email = data["email"]

    if "password" in data:
        password_hash=bcrypt.hashpw(data["password"].encode(), utente.salt).decode()

    try:
        db.session.commit()
        return {"msg": "Dati aggiornati"}, 200
    except Exception as e:
        db.session.rollback()
        return {"errore": str(e)}, 400
