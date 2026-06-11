from datetime import datetime

import bcrypt
from  bcrypt  import hashpw
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.sqltypes import NULLTYPE
from werkzeug.security import generate_password_hash
from config import Config
from model import db
from routes_user import utenti_bp
from model import Utente,Istituto,Pratica,EsamePratica,Esame,EsameEstero
from routes_user import utenti_bp
from pratiche import pratiche_bp


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(utenti_bp)
app.register_blueprint(pratiche_bp)
CORS(app, origins=["http://localhost:4200"])
db.init_app(app)
 # prova
with app.app_context():
    db.drop_all()
    db.create_all()
    salt = bcrypt.gensalt().decode()

    utente = Utente(
    nome="Hamza",
    cognome="Rofi",
    email="hamza.rofi@unive.it",
    password_hash=bcrypt.hashpw(
        "123".encode(),
        salt.encode()
    ).decode(),
    salt=salt,
    ruolo="S",
    data_nascita=datetime.strptime("12/12/2000","%d/%m/%Y")
    )


    istituti = [
    Istituto(nome="Université Paris-Saclay",              paese="Francia",      citta="Paris",      indirizzo="Bâtiment Bréguet, 3 Rue Joliot Curie, 91190 Gif-sur-Yvette"),
    Istituto(nome="Technische Universität München",        paese="Germania",     citta="München",    indirizzo="Arcisstraße 21, 80333 München"),
    Istituto(nome="Universidad Complutense de Madrid",     paese="Spagna",       citta="Madrid",     indirizzo="Av. Séneca, 2, 28040 Madrid"),
    Istituto(nome="Universiteit van Amsterdam",            paese="Paesi Bassi",  citta="Amsterdam",  indirizzo="Spui 21, 1012 WX Amsterdam"),
    Istituto(nome="KU Leuven",                             paese="Belgio",       citta="Leuven",     indirizzo="Oude Markt 13, 3000 Leuven"),
    Istituto(nome="KTH Royal Institute of Technology",     paese="Svezia",       citta="Stockholm",  indirizzo="Brinellvägen 8, 114 28 Stockholm"),
    Istituto(nome="Universität Wien",                      paese="Austria",      citta="Wien",       indirizzo="Universitätsring 1, 1010 Wien"),
    Istituto(nome="Charles University Prague",             paese="Rep. Ceca",    citta="Praha",      indirizzo="Ovocný trh 560/5, 116 36 Praha 1"),
]

    esami_esteri = [
        EsameEstero(id="EE001", nome="Introduction to Algorithms", crediti=6),
        EsameEstero(id="EE002", nome="Database Systems",           crediti=6),
        EsameEstero(id="EE003", nome="Software Engineering",       crediti=9),
        EsameEstero(id="EE004", nome="Computer Networks",          crediti=6),
        EsameEstero(id="EE005", nome="Artificial Intelligence",    crediti=9),
    ]

    esami = [
        Esame(nome="Algoritmi e Strutture Dati", crediti=6, id_esame_estero="EE001"),
        Esame(nome="Basi di Dati",               crediti=6, id_esame_estero="EE002"),
        Esame(nome="Ingegneria del Software",    crediti=9, id_esame_estero="EE003"),
        Esame(nome="Reti di Calcolatori",        crediti=6, id_esame_estero="EE004"),
        Esame(nome="Intelligenza Artificiale",   crediti=9, id_esame_estero="EE005"),
        Esame(nome="Analisi Matematica",         crediti=9),
        Esame(nome="Fisica",                     crediti=6),
    ]


    from datetime import date

    docente = Utente(
        nome="Mario",
        cognome="Rossi",
        email="mario.rossi@unive.it",
        password_hash="hash",
        salt="salt",
        ruolo="D",
        data_nascita=date(1980, 5, 10)
    )

    db.session.add(docente)
    db.session.commit()

    db.session.add_all(esami_esteri)
    db.session.flush()
    db.session.add_all(esami)
    db.session.commit()

    db.session.add_all(istituti)
    db.session.commit()

    db.session.add(utente)
    db.session.commit()
    print("0k")



if __name__ == "__main__":
      app.run(debug=True)
