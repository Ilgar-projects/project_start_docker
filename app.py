from hashlib import md5

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

app = Flask("app")
app.config.from_pyfile("default_config.py")
app.config.from_envvar("APP_SETTINGS", silent=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))


@app.route("/")
def index():
    users = User.query.all()
    response = {
        "total": len(users),
        "users": [{"username": user.username, "id": user.id} for user in users],
    }
    return jsonify(response)


@app.route("/api/register", methods=["POST"])
def register():
    user_data = request.json
    if not user_data or "username" not in user_data or "password" not in user_data:
        return jsonify({"error": "invalid_request"}), 400

    try:
        user = User(
            username=user_data["username"],
            password=md5(user_data["password"].encode()).hexdigest(),
        )
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        return jsonify({"error": "имя пользователя уже существует"}), 400

    return jsonify({"username": user.username}), 200


@app.route("/api/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"ошибка": "пользователь с таким id не найден"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"сообщение": "пользователь с таким id удалён"}), 200
