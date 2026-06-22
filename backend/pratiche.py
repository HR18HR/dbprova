import jwt
import os
import json

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename

from model import db, Istituto, Pratica, Esame, EsameEstero, EsamePratica


pratiche_bp = Blueprint("pratiche", __name__)


# =========================
# TOKEN / RUOLI
# =========================

def _get_payload_from_token():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return None

    token = auth.split(" ", 1)[1]

    try:
        return jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        return None


def _get_id_from_token():
    payload = _get_payload_from_token()
    return payload.get("id") if payload else None


def _get_email_from_token():
    payload = _get_payload_from_token()
    return payload.get("email") if payload else None


def _get_ruolo_from_token():
    payload = _get_payload_from_token()
    return payload.get("ruolo") if payload else None


def _utente_autenticato():
    payload = _get_payload_from_token()

    if not payload:
        return None, None

    return payload.get("email"), payload.get("ruolo")


def _richiedi_ruolo(ruolo_richiesto):
    email, ruolo = _utente_autenticato()

    if email is None:
        return None, jsonify({"errore": "Non autenticato"}), 401

    if ruolo != ruolo_richiesto:
        return None, jsonify({"errore": "Ruolo non autorizzato"}), 403

    return email, None, None


def _file_pdf_obbligatorio(nome_file):
    file = request.files.get(nome_file)

    if not file:
        return None, jsonify({"errore": "File PDF obbligatorio"}), 400

    if file.filename == "":
        return None, jsonify({"errore": "File PDF obbligatorio"}), 400

    if file.mimetype != "application/pdf":
        return None, jsonify({"errore": "Sono consentiti solo file PDF"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return None, jsonify({"errore": "Il file deve avere estensione .pdf"}), 400

    return file, None, None


def _file_pdf_opzionale(nome_file):
    file = request.files.get(nome_file)

    if not file or file.filename == "":
        return None, None, None

    if file.mimetype != "application/pdf":
        return None, jsonify({"errore": "Sono consentiti solo file PDF"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return None, jsonify({"errore": "Il file deve avere estensione .pdf"}), 400

    return file, None, None


def _cartella_pratica(pratica):
    return os.path.join(
        "uploads",
        secure_filename(pratica.studente_email.replace("@", "_")),
        pratica.id
    )


def _salva_agreement(pratica, file):
    cartella = _cartella_pratica(pratica)
    os.makedirs(cartella, exist_ok=True)

    percorso = os.path.join(cartella, "agreement.pdf")

    if os.path.exists(percorso):
        os.remove(percorso)

    file.save(percorso)


def _percorso_agreement(pratica):
    percorso_nuovo = os.path.join(
        _cartella_pratica(pratica),
        "agreement.pdf"
    )

    if os.path.exists(percorso_nuovo):
        return percorso_nuovo

    percorso_vecchio = os.path.join(
        "uploads",
        secure_filename(pratica.studente_email.replace("@", "_")),
        "agreement.pdf"
    )

    return percorso_vecchio


# =========================
# JSON
# =========================

def esami_pratica_json(pratica_id):
    risultati = (
        db.session.query(EsamePratica, Esame.crediti)
        .join(Esame, EsamePratica.esame_locale_nome == Esame.nome)
        .filter(EsamePratica.pratica_id == pratica_id)
        .all()
    )

    return [
        {
            "id": esame.id,
            "pratica_id": esame.pratica_id,
            "esame_locale_nome": esame.esame_locale_nome,
            "esame_estero_nome": esame.esame_estero_nome,
            "crediti": crediti
        }
        for esame, crediti in risultati
    ]


def pratica_json(pratica):
    return {
        "id": pratica.id,
        "studente_email": pratica.studente_email,
        "docente_email": pratica.docente_email,
        "nome_istituto": pratica.nome_istituto,
        "stato": pratica.stato,
        "data_inizio": str(pratica.data_inizio),
        "data_fine": str(pratica.data_fine) if pratica.data_fine else None,
        "data_creazione": str(pratica.data_creazione) if pratica.data_creazione else None,
        "semestre": pratica.semestre,
        "motivazione": pratica.motivazione,
        "esami": esami_pratica_json(pratica.id)
    }


# =========================
# DATI
# =========================

@pratiche_bp.route("/istituti", methods=["GET"])
def get_istituti():
    utente_id = _get_id_from_token()

    if utente_id is None:
        return jsonify({"errore": "Non autenticato"}), 401

    istituti = Istituto.query.order_by(
        Istituto.paese,
        Istituto.nome
    ).all()

    return jsonify([
        {
            "nome": i.nome,
            "paese": i.paese,
            "citta": i.citta,
            "indirizzo": i.indirizzo
        }
        for i in istituti
    ]), 200


@pratiche_bp.route("/esami", methods=["GET"])
def get_esami():
    utente_id = _get_id_from_token()

    if utente_id is None:
        return jsonify({"errore": "Non autenticato"}), 401

    esami = (
        db.session.query(
            Esame,
            EsameEstero.nome.label("nome_estero")
        )
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


# =========================
# STUDENTE
# =========================

@pratiche_bp.route("/pratica", methods=["POST"])
def crea_pratica():
    email_token, errore, status = _richiedi_ruolo("S")

    if errore:
        return errore, status

    id_pratica = request.form.get("id_pratica")
    email_studente = request.form.get("email_studente")
    email_docente = request.form.get("email_docente")
    nome_istituto = request.form.get("nome_istituto")

    data_partenza = request.form.get("data_partenza")
    data_rientro = request.form.get("data_rientro")
    semestre = request.form.get("semestre")
    esami_json = request.form.get("esami")

    file, errore, status = _file_pdf_obbligatorio("agreement")

    if errore:
        return errore, status

    if email_studente != email_token:
        return jsonify({"errore": "Non puoi creare pratiche per altri studenti"}), 403

    if not id_pratica:
        return jsonify({"errore": "ID pratica mancante"}), 400

    if not email_studente:
        return jsonify({"errore": "Email studente mancante"}), 400

    if not data_partenza:
        return jsonify({"errore": "Data partenza mancante"}), 400

    if not semestre:
        return jsonify({"errore": "Semestre mancante"}), 400

    if semestre not in ["PRIMO", "SECONDO", "ANNO"]:
        return jsonify({"errore": "Semestre non valido"}), 400

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
            data_inizio=data_inizio,
            semestre=semestre,
            docente_email=email_docente if email_docente else None,
            nome_istituto=nome_istituto if nome_istituto else None,
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

        _salva_agreement(nuova_pratica, file)

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
    email, errore, status = _richiedi_ruolo("S")

    if errore:
        return errore, status

    pratiche = Pratica.query.filter_by(
        studente_email=email
    ).all()

    return jsonify([
        pratica_json(pratica)
        for pratica in pratiche
    ]), 200


@pratiche_bp.route("/eliminapratiche/<id_pratica>", methods=["DELETE"])
def elimina_pratica(id_pratica):
    email, errore, status = _richiedi_ruolo("S")

    if errore:
        return errore, status

    pratica = Pratica.query.filter_by(
        id=id_pratica
    ).first()

    if pratica is None:
        return jsonify({"errore": "Pratica non trovata"}), 404

    if pratica.studente_email != email:
        return jsonify({"errore": "Non autorizzato"}), 403

    if pratica.stato not in ["CREATA", "ATT_APPROVAZIONE"]:
        return jsonify({
            "errore": "Puoi eliminare solo pratiche create o in attesa approvazione"
        }), 400

    try:
        db.session.delete(pratica)
        db.session.commit()

        return jsonify({
            "message": "Pratica eliminata con successo"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"errore": str(e)}), 400


@pratiche_bp.route("/modifica_pratica/<id_pratica>", methods=["PUT"])
def modifica_pratica(id_pratica):
    try:
        email_utente, errore, status = _richiedi_ruolo("S")

        if errore:
            return errore, status

        pratica = Pratica.query.filter_by(id=id_pratica).first()

        if not pratica:
            return jsonify({"errore": "Pratica non trovata"}), 404

        if pratica.studente_email != email_utente:
            return jsonify({"errore": "Non puoi modificare questa pratica"}), 403

        if pratica.stato not in ["CREATA", "ATT_APPROVAZIONE", "MOBILITA_IN_CORSO"]:
            return jsonify({
                "errore": "Questa pratica non può essere modificata"
            }), 400

        data = request.form

        if pratica.stato in ["CREATA", "ATT_APPROVAZIONE"]:
            learning_agreement, errore, status = _file_pdf_obbligatorio("agreement")

            if errore:
                return errore, status

            pratica.docente_email = data.get("email_docente")
            pratica.nome_istituto = data.get("nome_istituto")

            data_partenza = data.get("data_partenza")

            if data_partenza:
                pratica.data_inizio = datetime.strptime(
                    data_partenza,
                    "%Y-%m-%d"
                ).date()

            pratica.semestre = data.get("semestre")

            _salva_agreement(pratica, learning_agreement)

        data_rientro = data.get("data_rientro")

        if data_rientro:
            pratica.data_fine = datetime.strptime(
                data_rientro,
                "%Y-%m-%d"
            ).date()
        else:
            pratica.data_fine = None

        EsamePratica.query.filter_by(
            pratica_id=id_pratica
        ).delete()

        esami_json = data.get("esami", "[]")
        esami = json.loads(esami_json)

        for e in esami:
            esame_locale_nome = e.get("esame_locale_nome")
            esame_estero_nome = e.get("esame_estero_nome")

            if not esame_locale_nome or not esame_estero_nome:
                db.session.rollback()
                return jsonify({
                    "errore": "Ogni esame deve avere esame locale ed estero"
                }), 400

            nuovo = EsamePratica(
                pratica_id=id_pratica,
                esame_locale_nome=esame_locale_nome,
                esame_estero_nome=esame_estero_nome
            )

            db.session.add(nuovo)

        if pratica.stato == "CREATA":
            pratica.stato = "ATT_APPROVAZIONE"

        db.session.commit()

        return jsonify({
            "message": "Pratica modificata correttamente",
            "pratica": pratica_json(pratica)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"errore": str(e)}), 500


# =========================
# DOCENTE
# =========================

@pratiche_bp.route("/pratiche_docente", methods=["GET"])
def pratiche_docente():
    try:
        email_docente, errore, status = _richiedi_ruolo("D")

        if errore:
            return errore, status

        pratiche = Pratica.query.filter_by(
            docente_email=email_docente
        ).all()

        return jsonify([
            pratica_json(p)
            for p in pratiche
        ]), 200

    except Exception as e:
        return jsonify({"errore": str(e)}), 500


@pratiche_bp.route("/pratiche_docente/<id_pratica>/accetta", methods=["PUT"])
def accetta_pratica_docente(id_pratica):
    try:
        email_docente, errore, status = _richiedi_ruolo("D")

        if errore:
            return errore, status

        pratica = Pratica.query.filter_by(id=id_pratica).first()

        if not pratica:
            return jsonify({"errore": "Pratica non trovata"}), 404

        if pratica.docente_email != email_docente:
            return jsonify({"errore": "Non autorizzato"}), 403

        if pratica.stato == "ATT_APPROVAZIONE":
            pratica.stato = "APPROVATA_DOCENTE"
            messaggio = "Pratica approvata correttamente"

        elif pratica.stato == "MOBILITA_IN_CORSO":
            pratica.stato = "APPROVATO_TRANSCRIPT"
            messaggio = "Pratica approvata correttamente"

        else:
            return jsonify({
                "errore": "La pratica non può essere accettata in questo stato"
            }), 400

        pratica.motivazione = None

        db.session.commit()

        return jsonify({
            "message": messaggio,
            "pratica": pratica_json(pratica)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"errore": str(e)}), 500

@pratiche_bp.route("/pratiche_docente/<id_pratica>/rifiuta", methods=["PUT"])
def rifiuta_pratica_docente(id_pratica):
    try:
        email_docente, errore, status = _richiedi_ruolo("D")

        if errore:
            return errore, status

        data = request.get_json()

        if not data:
            return jsonify({"errore": "Dati mancanti"}), 400

        motivazione = data.get("motivazione", "")

        if not motivazione or motivazione.strip() == "":
            return jsonify({
                "errore": "La motivazione è obbligatoria"
            }), 400

        pratica = Pratica.query.filter_by(id=id_pratica).first()

        if not pratica:
            return jsonify({"errore": "Pratica non trovata"}), 404

        if pratica.docente_email != email_docente:
            return jsonify({"errore": "Non autorizzato"}), 403

        if pratica.stato == "ATT_APPROVAZIONE":
            pratica.stato = "CREATA"
            messaggio = "Pratica rifiutata correttamente"

        elif pratica.stato == "MOBILITA_IN_CORSO":
            messaggio = "Pratica rifiutata correttamente"

        else:
            return jsonify({
                "errore": "La pratica non può essere rifiutata in questo stato"
            }), 400

        pratica.motivazione = motivazione.strip()

        db.session.commit()

        return jsonify({
            "message": messaggio,
            "pratica": pratica_json(pratica)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"errore": str(e)}), 500


@pratiche_bp.route("/pratiche_docente/<id_pratica>/learning_agreement", methods=["GET"])
def mostra_learning_agreement(id_pratica):
    try:
        email_docente, errore, status = _richiedi_ruolo("D")

        if errore:
            return errore, status

        pratica = Pratica.query.filter_by(id=id_pratica).first()

        if not pratica:
            return jsonify({"errore": "Pratica non trovata"}), 404

        if pratica.docente_email != email_docente:
            return jsonify({"errore": "Non autorizzato"}), 403

        percorso = _percorso_agreement(pratica)

        if not os.path.exists(percorso):
            return jsonify({"errore": "File non trovato"}), 404

        return send_file(
            percorso,
            mimetype="application/pdf",
            as_attachment=False
        )

    except Exception as e:
        return jsonify({"errore": str(e)}), 500



@pratiche_bp.route("/pratiche_docente/<id_pratica>/transcript", methods=["GET"])
def mostra_transcript_docente(id_pratica):
    try:
        email_docente, errore, status = _richiedi_ruolo("D")

        if errore:
            return errore, status

        pratica = Pratica.query.filter_by(id=id_pratica).first()

        if not pratica:
            return jsonify({"errore": "Pratica non trovata"}), 404

        if pratica.docente_email != email_docente:
            return jsonify({"errore": "Non autorizzato"}), 403

        percorso =os.path.join(
                        _cartella_pratica(pratica),
                        "transcript.pdf"
                    )

        if not os.path.exists(percorso):
            return jsonify({"errore": "Transcript non trovato"}), 404

        return send_file(
            percorso,
            mimetype="application/pdf",
            as_attachment=False
        )

    except Exception as e:
        return jsonify({"errore": str(e)}), 500






# =========================
# UFFICIO
# =========================

@pratiche_bp.route("/pratiche_ufficio", methods=["GET"])
def get_tutte_pratiche_ufficio():
    email, errore, status = _richiedi_ruolo("U")

    if errore:
        return errore, status

    pratiche = Pratica.query.order_by(
        Pratica.data_creazione.desc()
    ).all()

    return jsonify([
        pratica_json(p)
        for p in pratiche
    ]), 200


@pratiche_bp.route("/pratiche_ufficio/<id_pratica>/accetta", methods=["PUT"])
def accetta_pratica_ufficio(id_pratica):
    email, errore, status = _richiedi_ruolo("U")

    if errore:
        return errore, status

    pratica = Pratica.query.filter_by(id=id_pratica).first()

    if not pratica:
        return jsonify({"errore": "Pratica non trovata"}), 404

    if pratica.stato == "APPROVATA_DOCENTE":
        pratica.stato = "MOBILITA_IN_CORSO"

    elif pratica.stato == "APPROVATO_TRANSCRIPT":
        pratica.stato = "CHIUSA"

    else:
        return jsonify({
            "errore": "La pratica non può essere accettata in questo stato"
        }), 400

    db.session.commit()

    return jsonify({
        "message": "Pratica accettata correttamente",
        "pratica": pratica_json(pratica)
    }), 200


@pratiche_bp.route("/pratiche_ufficio/<id_pratica>/rifiuta", methods=["PUT"])
def rifiuta_pratica_ufficio(id_pratica):
    email, errore, status = _richiedi_ruolo("U")

    if errore:
        return errore, status

    pratica = Pratica.query.filter_by(id=id_pratica).first()

    if not pratica:
        return jsonify({"errore": "Pratica non trovata"}), 404

    if pratica.stato == "APPROVATA_DOCENTE":
        pratica.stato = "ATT_APPROVAZIONE"

    else:
        return jsonify({
            "errore": "La pratica non può essere rifiutata in questo stato"
        }), 400

    db.session.commit()

    return jsonify({
        "message": "Pratica rifiutata e rimandata al docente",
        "pratica": pratica_json(pratica)
    }), 200


@pratiche_bp.route("/pratiche_ufficio/<id_pratica>/learning_agreement", methods=["GET"])
def learning_agreement_ufficio(id_pratica):
    email, errore, status = _richiedi_ruolo("U")

    if errore:
        return errore, status

    pratica = Pratica.query.filter_by(id=id_pratica).first()

    if not pratica:
        return jsonify({"errore": "Pratica non trovata"}), 404

    percorso = _percorso_agreement(pratica)

    if not os.path.exists(percorso):
        return jsonify({
            "errore": "Learning Agreement non trovato"
        }), 404

    return send_file(
        percorso,
        mimetype="application/pdf",
        as_attachment=False
    )