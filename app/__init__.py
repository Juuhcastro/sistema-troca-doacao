from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # ✅ importado

db = SQLAlchemy()
migrate = Migrate()  # ✅ criado

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'segredo_seguro'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:novasenha123@localhost/troca_doacao'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)  # ✅ inicializado

    from .routes import main
    app.register_blueprint(main)

    return app

__all__ = ['create_app', 'db']
