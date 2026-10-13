
from flask import Blueprint, jsonify, render_template

main = Blueprint("main", __name__)


@main.get("/")
def dashboard():
    return render_template("dashboard.html")


@main.get("/health")
def health():
    return jsonify({"status": "healthy"})
