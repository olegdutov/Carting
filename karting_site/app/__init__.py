import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Генерируем абсолютный путь к папке instance
    instance_path = os.path.join(app.root_path, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)  # создаём папку, если нет

    # Конфигурация
    app.config['SECRET_KEY'] = '95b598a1b374df76a2fac72665c382fc8fb6bed270399d014d29c5b5f31394ee'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'main.login'  # маршрут для редиректа при неавторизованном доступе
    login_manager.login_message_category = 'info'

    # Импорт и регистрация блюпринта
    from app import routes  # или from app.main import routes если структура другая
    app.register_blueprint(routes.main_bp)

    return app
