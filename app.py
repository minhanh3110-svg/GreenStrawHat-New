import click
from flask import Flask
from extensions import db, migrate, login_manager
from config import Config
from models import User
from views import register_views
from api_blueprints import register_api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    register_views(app)
    register_api(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.cli.command("init-db")
    def init_db_cmd():
        with app.app_context():
            db.create_all()
        click.echo("✔ Database initialized.")

    @app.cli.command("create-user")
    @click.option("--username", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_user_cmd(username, password):
        from werkzeug.security import generate_password_hash
        with app.app_context():
            if User.query.filter_by(username=username).first():
                click.echo("User already exists.")
                return
            u = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(u)
            db.session.commit()
            click.echo(f"✔ Created user: {username}")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
