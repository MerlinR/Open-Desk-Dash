#!/user/bin/python3
from flask import Blueprint, jsonify

api = Blueprint("example", __name__, url_prefix="/example")


@api.route("/ping", methods=["GET"])
def pong():
    return (jsonify("pong"), 200)
