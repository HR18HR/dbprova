class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://admin:123456@localhost:5432/lab"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "chiave"