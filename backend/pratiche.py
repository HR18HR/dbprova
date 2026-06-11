import base64
import datetime
import jwt
import bcrypt
from flask import Blueprint, request, jsonify, current_app

from model import db, Utente, Istituto, Pratica,Esame,EsameEstero,EsamePratica
import os
import json

from datetime import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename

pratiche_bp = Blueprint("pratiche", __name__)

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


@pratiche_bp.route("/istituti", methods=["GET"])
def get_istituti():
    # --- 1. Valida il token ---
    utente_id = _get_id_from_token()

    if utente_id is None:
        return {"errore": "Non autenticato"}, 401

    # --- 2. Restituisci gli istituti ---
    istituti = Istituto.query.order_by(Istituto.paese, Istituto.nome).all()

    return jsonify([
        {
            "nome":      i.nome,
            "paese":     i.paese,
            "citta":     i.citta,
            "indirizzo": i.indirizzo,
        }
        for i in istituti
    ]), 200

@pratiche_bp.route("/esami", methods=["GET"])
def get_esami():

    utente_id = _get_id_from_token()
    if utente_id is None:
        return {"errore": "Non autenticato"}, 401


    esami = (
        db.session.query(Esame, EsameEstero.nome.label("nome_estero"))
        .outerjoin(
            EsameEstero,
            Esame.id_esame_estero == EsameEstero.id
        )
        .all()
    )

    return jsonify([
        {
            "nome": esame.nome,
            "crediti": esame.crediti,
            "nome_esame_estero": nome_estero
        }
        for esame, nome_estero in esami
    ]), 200


@pratiche_bp.route("/pratica", methods=["POST"])
def crea_pratica():

    utente_id = _get_id_from_token()

    if utente_id is None:
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    id_pratica = request.form.get("id_pratica")
    email_studente = request.form.get("email_studente")
    email_docente = request.form.get("email_docente")
    nome_istituto = request.form.get("nome_istituto")

    data_partenza = request.form.get("data_partenza")
    data_rientro = request.form.get("data_rientro")

    semestre = request.form.get("semestre")

    esami_json = request.form.get("esami")

    file = request.files.get("agreement")

    if not id_pratica:
        return jsonify({
            "errore": "ID pratica mancante"
        }), 400

    if not email_studente:
        return jsonify({
            "errore": "Email studente mancante"
        }), 400

    if not data_partenza:
        return jsonify({
            "errore": "Data partenza mancante"
        }), 400

    try:

        data_inizio = datetime.strptime(
            data_partenza,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return jsonify({
            "errore": "Formato data partenza non valido"
        }), 400

    data_fine = None

    if data_rientro:

        try:

            data_fine = datetime.strptime(
                data_rientro,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            return jsonify({
                "errore": "Formato data rientro non valido"
            }), 400

    try:

        esami = json.loads(
            esami_json if esami_json else "[]"
        )

    except Exception:

        return jsonify({
            "errore": "Formato esami non valido"
        }), 400

    pratica_esistente = Pratica.query.get(
        id_pratica
    )

    if pratica_esistente:

        return jsonify({
            "errore": "Pratica già esistente"
        }), 409

    try:

        percorso_file = None

        if file:

            cartella_studente = os.path.join(
                "uploads",
                secure_filename(
                    email_studente.replace("@", "_")
                )
            )

            os.makedirs(
                cartella_studente,
                exist_ok=True
            )

            nome_file = secure_filename(
                file.filename
            )

            percorso_file = os.path.join(
                cartella_studente,
                nome_file
            )

            file.save(
                percorso_file
            )

        nuova_pratica = Pratica(
            id=id_pratica,
            studente_email=email_studente,
            docente_email=email_docente if email_docente else None,
            nome_istituto=nome_istituto if nome_istituto else None,
            data_inizio=data_inizio,
            data_fine=data_fine,
            stato="CREATA"
        )

        db.session.add(
            nuova_pratica
        )

        for e in esami:

            nuovo_esame = EsamePratica(
                pratica_id=id_pratica,
                esame_locale_nome=e["esame_locale_nome"],
                esame_estero_id=e["esame_estero_id"]
            )

            db.session.add(
                nuovo_esame
            )

        db.session.commit()

        return jsonify({
            "message":
                "Pratica creata correttamente"
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "errore":
                "Errore durante la creazione",
            "dettaglio":
                print(str(e))
        }), 500
