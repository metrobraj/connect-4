"""Flask backend: holds game state, validates moves, runs the AI."""
import uuid
from flask import Flask, jsonify, request, send_from_directory
from game import Game, HUMAN

app = Flask(__name__, static_folder="static")
GAMES = {}


@app.after_request
def cors(resp):  # lets the page work even if served from another origin/port
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.errorhandler(Exception)
def json_errors(e):  # API errors always come back as JSON, never an HTML page
    from werkzeug.exceptions import HTTPException
    code = e.code if isinstance(e, HTTPException) else 500
    if request.path.startswith("/api/"):
        return jsonify(error=f"{code}: {getattr(e, 'description', str(e))}"), code
    return e if isinstance(e, HTTPException) else ("Server error", 500)


@app.route("/api/<path:_>", methods=["OPTIONS"])
def preflight(_):
    return "", 204


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.post("/api/new")
def new_game():
    d = request.get_json(silent=True) or {}
    g = Game(ai_first=bool(d.get("ai_first")), depth=4)
    gid = uuid.uuid4().hex
    GAMES[gid] = g
    if g.turn != HUMAN:
        g.ai_move()
    return jsonify(id=gid, **g.to_dict())


@app.post("/api/move")
def move():
    d = request.get_json(silent=True) or {}
    g = GAMES.get(d.get("id"))
    if not g:
        return jsonify(error="unknown game"), 404
    try:
        g.play(int(d.get("col", -1)), HUMAN)
        if g.status == "playing":
            g.ai_move()
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(**g.to_dict())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
