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
from model import Utente,Istituto,Pratica
from routes_user import utenti_bp


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(utenti_bp)
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

    db.session.add(utente)
    db.session.commit()
    print("0k")



if __name__ == "__main__":
      app.run(debug=True)
