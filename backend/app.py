from datetime import datetime

import bcrypt
from  bcrypt  import hashpw
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.sqltypes import NULLTYPE
from werkzeug.security import generate_password_hash

from config import Config
from model import db
from routes_user import utenti_bp
from model import Utente,Istituto,Pratica,Mobilita
from routes_user import utenti_bp


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(utenti_bp)
db.init_app(app)
 # prova
with app.app_context():
    db.drop_all()
    db.create_all()
    with app.app_context():
     salt=bcrypt.gensalt();
     studente = Utente(
        "Hamza",
        "Rofi",
        "hamza.rofi@gmail.com",
        hashpw(b"ciao",salt),
         salt,
        "S",
        datetime.strptime("12/05/2000", "%d/%m/%Y").date()

    )
    salt_1=bcrypt.gensalt()
    docente = Utente(
        "Mario",
        "Rossi",
        "mario@gmail.com",
        bcrypt.hashpw(b"ciao1",salt_1),
        salt_1,
        "D",
        datetime.strptime("12/05/1980", "%d/%m/%Y").date()
    )

    db.session.add(studente)
    db.session.add(docente)
    db.session.commit()



    istituto = Istituto(
        "Universidad de Granada",
        "Via Centrale 10",
        "Granada",
        "Spagna"
    )

    db.session.add(istituto)
    db.session.commit()


    s = db.session.query(Utente).filter_by(
        email="hamza.rofi@gmail.com"
    ).one()

    d = db.session.query(Utente).filter_by(
        email="mario@gmail.com"
    ).one()

    i = db.session.query(Istituto).filter_by(
        nome="Universidad de Granada"
    ).one()



    pratica = Pratica(
        studente_id=s.id,
        docente_id=d.id,
        stato="ATT",
        motivazione="Erasmus"
    )

    db.session.add(pratica)
    db.session.commit()


    p = db.session.query(Pratica).filter_by(
        studente_id=s.id
    ).one()



    mobilita = Mobilita(
        pratica_id=p.id,
        istituto_id=i.id,
        data_inizio=datetime.strptime("01/09/2026", "%d/%m/%Y").date(),
        data_fine=datetime.strptime("31/01/2027", "%d/%m/%Y").date(),
        semestre="1"
    )

    db.session.add(mobilita)
    db.session.commit()

    print("Creato tutto")


if __name__ == "__main__":
      app.run(debug=True)
