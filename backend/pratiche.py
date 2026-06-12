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
def _get_email_from_token():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return None

    token = auth.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        return payload.get("email")

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
            Esame.nome_esame_estero == EsameEstero.nome
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
        return jsonify({"errore": "Non autenticato"}), 401

    id_pratica = request.form.get("id_pratica")
    email_studente = request.form.get("email_studente")
    email_docente = request.form.get("email_docente")
    nome_istituto = request.form.get("nome_istituto")

    data_partenza = request.form.get("data_partenza")
    data_rientro = request.form.get("data_rientro")

    esami_json = request.form.get("esami")
    file = request.files.get("agreement")

    if not id_pratica:
        return jsonify({"errore": "ID pratica mancante"}), 400

    if not email_studente:
        return jsonify({"errore": "Email studente mancante"}), 400

    if not data_partenza:
        return jsonify({"errore": "Data partenza mancante"}), 400

    try:
        data_inizio = datetime.strptime(data_partenza, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"errore": "Formato data partenza non valido"}), 400

    data_fine = None

    if data_rientro:
        try:
            data_fine = datetime.strptime(data_rientro, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"errore": "Formato data rientro non valido"}), 400

    try:
        esami = json.loads(esami_json) if esami_json else []
    except Exception:
        return jsonify({"errore": "Formato esami non valido"}), 400

    if Pratica.query.get(id_pratica):
        return jsonify({"errore": "Pratica già esistente"}), 409

    try:
        nuova_pratica = Pratica(
            id=id_pratica,
            studente_email=email_studente,
            docente_email=email_docente if email_docente else None,
            nome_istituto=nome_istituto if nome_istituto else None,
            data_inizio=data_inizio,
            data_fine=data_fine,
            stato="ATT_APPROVAZIONE"
        )

        db.session.add(nuova_pratica)

        for e in esami:
            esame_locale_nome = e.get("esame_locale_nome")
            esame_estero_nome = e.get("esame_estero_nome")

            if not esame_locale_nome or not esame_estero_nome:
                db.session.rollback()
                return jsonify({
                    "errore": "Ogni esame deve avere esame_locale_nome ed esame_estero_nome"
                }), 400

            nuovo_esame = EsamePratica(
                pratica_id=id_pratica,
                esame_locale_nome=esame_locale_nome,
                esame_estero_nome=esame_estero_nome
            )

            db.session.add(nuovo_esame)

        if file:
            cartella_studente = os.path.join(
                "uploads",
                secure_filename(email_studente.replace("@", "_"))
            )

            os.makedirs(cartella_studente, exist_ok=True)

            nome_file = secure_filename(file.filename)

            percorso_file = os.path.join(
                cartella_studente,
                nome_file
            )

            file.save(percorso_file)

        db.session.commit()

        return jsonify({
            "message": "Pratica creata correttamente"
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "errore": "Errore durante la creazione",
            "dettaglio": str(e)
        }), 500




@pratiche_bp.route("/pratiche", methods=["GET"])
def get_pratiche_utente():

    id = _get_email_from_token()

    if id is None:
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    pratiche = Pratica.query.filter_by(
        studente_email=id
    ).all()

    return jsonify([
        {
            "id": pratica.id,
            "studente_email": pratica.studente_email,
            "docente_email": pratica.docente_email,
            "nome_istituto": pratica.nome_istituto,
            "stato": pratica.stato,
            "data_inizio": pratica.data_inizio.isoformat(),
            "data_fine": pratica.data_fine.isoformat() if pratica.data_fine else None,
            "data_creazione": pratica.data_creazione.isoformat(),
            "motivazione": pratica.motivazione
        }
        for pratica in pratiche
    ]), 200




@pratiche_bp.route("/eliminapratiche/<id_pratica>", methods=["DELETE"])
def elimina_pratica(id_pratica):

    email = _get_email_from_token()

    if email is None:
        return jsonify({
            "errore": "Non autenticato"
        }), 401

    pratica = Pratica.query.filter_by(
        id=id_pratica
    ).first()

    if pratica is None:
        return jsonify({
            "errore": "Pratica non trovata"
        }), 404

    if pratica.studente_email != email:
        return jsonify({
            "errore": "Non autorizzato"
        }), 403

    try:

        db.session.delete(pratica)
        db.session.commit()

        return jsonify({
            "messaggio": "Pratica eliminata con successo"
        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "errore": str(e)
        }), 400
