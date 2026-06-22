from datetime import datetime
from datetime import date
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
CORS(app, origins=["http://localhost:4200"],supports_credentials=True)
db.init_app(app)
 # prova
with app.app_context():
    db.drop_all()
    db.create_all()
    salt = bcrypt.gensalt().decode()

    utente = Utente(
    nome="user",
    cognome="user_1",
    email="user@unive.it",
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

    esami = [
        Esame("Algoritmi e Strutture Dati", 6, "Introduction to Algorithms"),
        Esame("Basi di Dati", 6, "Database Systems"),
        Esame("Ingegneria del Software", 9, "Software Engineering"),
        Esame("Reti di Calcolatori", 6, "Computer Networks"),
        Esame("Intelligenza Artificiale", 9, "Artificial Intelligence"),
        Esame("Sistemi Operativi", 6, "Operating Systems"),
        Esame("Architettura degli Elaboratori", 6, "Computer Architecture"),
        Esame("Apprendimento Automatico", 9, "Machine Learning"),
        Esame("Sicurezza Informatica", 6, "Cyber Security"),
        Esame("Tecnologie Web", 6, "Web Development"),
    ]

    esami_esteri = [
        EsameEstero(nome="Introduction to Algorithms", crediti=6),
        EsameEstero(nome="Database Systems", crediti=6),
        EsameEstero(nome="Software Engineering", crediti=9),
        EsameEstero(nome="Computer Networks", crediti=6),
        EsameEstero(nome="Artificial Intelligence", crediti=9),
        EsameEstero(nome="Operating Systems", crediti=6),
        EsameEstero(nome="Computer Architecture", crediti=6),
        EsameEstero(nome="Machine Learning", crediti=9),
        EsameEstero(nome="Cyber Security", crediti=6),
        EsameEstero(nome="Web Development", crediti=6),
        EsameEstero(nome="Human Computer Interaction", crediti=6),
        EsameEstero(nome="Distributed Systems", crediti=6),
        EsameEstero(nome="Data Mining", crediti=6),
        EsameEstero(nome="Mobile Application Development", crediti=6),
        EsameEstero(nome="Cloud Computing", crediti=6),
    ]




    salt_1 = bcrypt.gensalt().decode()

    docente = Utente(
        nome="docente",
        cognome="docente_1",
        email="docente@unive.it",
        password_hash=bcrypt.hashpw(
            "123".encode(),
            salt_1.encode()
        ).decode(),
        salt=salt_1,
        ruolo="D",
        data_nascita=datetime.strptime(
            "12/12/2000",
            "%d/%m/%Y"
        )
)
    uff = Utente(
        nome="uff",
        cognome="uff_1",
        email="ffff@unive.it",
        password_hash=bcrypt.hashpw(
            "123".encode(),
            salt_1.encode()
        ).decode(),
        salt=salt_1,
        ruolo="U",
        data_nascita=datetime.strptime(
            "12/12/2000",
            "%d/%m/%Y"
        )
    )
    db.session.add(docente)
    db.session.commit()
    db.session.add(uff)
    db.session.commit()

    db.session.add_all(esami_esteri)
    db.session.commit()

    db.session.add_all(esami)
    db.session.commit()
    db.session.add_all(istituti)
    db.session.commit()

    db.session.add(utente)
    db.session.commit()
    print("0k")



if __name__ == "__main__":
      app.run(debug=True)
