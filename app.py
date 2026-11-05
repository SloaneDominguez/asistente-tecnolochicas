import os
import logging
from flask import Flask, render_template, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import PermissionDeniedError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------- Configuración ----------
FOUNDRY_ENDPOINT = os.environ.get("FOUNDRY_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME", "Ada-Tecnolochicas")

CONTEXTO_ADA = (
    "Eres Ada, la mentora virtual y asistente pedagógica de TECNOLOchicas.\n"
    "Tu misión es apoyar a las instructoras en la preparación e impartición de sus clases "
    "de Scratch, Python, lógica de programación, chatbots e Inteligencia Artificial "
    "para niñas y jóvenes.\n"
    "Ofrece explicaciones didácticas, ideas de dinámicas, soluciones a problemas técnicos y "
    "estrategias pedagógicas inclusivas e inspiradoras.\n\n"
)

# ---------- Cliente Azure AI Project ----------
project_client = None
openai_client = None
try:
    if not FOUNDRY_ENDPOINT:
        raise ValueError("Falta la variable de entorno FOUNDRY_ENDPOINT")
    project_client = AIProjectClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    openai_client = project_client.get_openai_client(agent_name=AGENT_NAME)
except Exception:
    logger.exception("Error al inicializar el cliente de Foundry")


# ---------- Lógica del Agente Ada ----------
def _ejecutar_agente(mensaje, conversation_id=None):
    """Envía un mensaje al agente Ada y devuelve (respuesta, conversation_id)."""
    es_nueva = not conversation_id
    if es_nueva:
        conversation_id = openai_client.conversations.create().id

    # El contexto solo se envía en el primer turno de la conversación
    contenido = f"{CONTEXTO_ADA}Consulta de la instructora: {mensaje}" if es_nueva else mensaje

    response = openai_client.responses.create(
        conversation=conversation_id,
        input=[{"role": "user", "content": contenido}],
    )
    return response.output_text, conversation_id


# ---------- Rutas ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "foundry_ready": openai_client is not None})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    conversation_id = data.get("conversation_id")

    if not user_message:
        return jsonify({"error": "El mensaje no puede estar vacío"}), 400

    if openai_client is None:
        return jsonify({"error": "El servicio de IA no está disponible en este momento"}), 503

    try:
        reply, conversation_id = _ejecutar_agente(user_message, conversation_id)
        return jsonify({"reply": reply, "conversation_id": conversation_id})

    except PermissionDeniedError:
        logger.exception("403 al llamar a Foundry (revisar RBAC)")
        return jsonify({"error": "La aplicación no tiene permisos para usar el agente."}), 502

    except Exception:
        logger.exception("Error al comunicar con Ada")
        return jsonify({"error": "Ocurrió un error al comunicar con Ada. Intenta de nuevo."}), 500


if __name__ == "__main__":
    app.run(port=5000)
