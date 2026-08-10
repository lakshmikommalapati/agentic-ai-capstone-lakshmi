from flask import Flask, render_template, request, redirect, url_for
from src.agent import RelationshipManagerCopilot
from src.approval_store import record_decision, decisions_for

app = Flask(__name__)
copilot = RelationshipManagerCopilot()


@app.route("/")
def index():
    clients = copilot.list_clients()
    return render_template("index.html", clients=clients)


@app.route("/client/<client_id>")
def client_detail(client_id):
    result = copilot.run_scan(client_id)
    decisions = decisions_for(client_id)
    return render_template("client.html", result=result, decisions=decisions)


@app.route("/approve/<client_id>", methods=["POST"])
def approve(client_id):
    decision = request.form.get("decision", "Rejected")
    reviewer = request.form.get("reviewer", "Lakshmi Kommalapati")
    comment = request.form.get("comment", "")
    record_decision(client_id, decision, reviewer, comment)
    return redirect(url_for("client_detail", client_id=client_id))


if __name__ == "__main__":
    app.run(debug=True)
