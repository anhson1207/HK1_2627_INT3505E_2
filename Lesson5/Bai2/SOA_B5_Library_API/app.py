"""Library SOA homework; create tables automatically for a zero-setup SQLite demo."""
import os
from flask import Flask, jsonify
from sqlalchemy import event
from extensions import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///library.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.getenv("SECRET_KEY", "CHANGE-ME-IN-PRODUCTION"),
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    from routes.books import bp as books_bp
    from routes.authors import bp as authors_bp
    from routes.members import bp as members_bp
    from routes.loans import bp as loans_bp
    from routes.genres import bp as genres_bp
    for blueprint in (books_bp, authors_bp, members_bp, loans_bp, genres_bp):
        app.register_blueprint(blueprint, url_prefix="/api/v1")

    for code in (400, 404, 405, 409):
        app.register_error_handler(code, lambda err: (jsonify({"error": err.name.lower().replace(" ", "_"), "message": err.description}), err.code))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    with app.app_context():
        # SQLite FK constraints need to be explicitly enabled on each connection.
        if db.engine.dialect.name == "sqlite":
            @event.listens_for(db.engine, "connect")
            def _sqlite_fk(conn, record):
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        db.create_all()
    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="127.0.0.1", port=5000)
