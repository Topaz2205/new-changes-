from flask import Blueprint, request, jsonify
from app.ai.rag_service import RAGService

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")
rag = None

@ai_bp.before_app_first_request
def _init():
    global rag
    if rag is None:
        rag = RAGService()

@ai_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True) or {}
    q = data.get("query", "").strip()
    if not q:
        return jsonify({"error":"missing query"}), 400
    try:
        out = rag.ask(q)
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    