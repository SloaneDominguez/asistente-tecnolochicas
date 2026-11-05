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

def get_clients():
    global project_client, openai_client
    if openai_client is None:
        if not FOUNDRY_ENDPOINT:
            raise ValueError("Falta la variable de entorno FOUNDRY_ENDPOINT")
        
        project_client = AIProjectClient(
            endpoint=FOUNDRY_ENDPOINT,
            credential=DefaultAzureCredential(),
        )
        # Inicializa el cliente de OpenAI vinculado al proyecto de Foundry
        openai_client = project_client.get_openai_client()
    return openai_client

# ---------- Lógica del Agente Ada ----------
def _ejecutar_agente(mensaje, conversation_id=None):
    client = get_clients()
    es_nueva = not conversation_id
    
    if es_nueva:
        conversation_id = client.conversations.create().id

    contenido = f"{CONTEXTO_ADA}Consulta de la instructora: {mensaje}" if es_nueva else mensaje

    response = client.responses.create(
        conversation=conversation_id,
        input=[{"role": "user", "content": contenido}],
        extra_body={"assistant_id": AGENT_NAME} if AGENT_NAME else None
    )
    return response.output_text, conversation_id

# ---------- Rutas ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    try:
        get_clients()
        ready = True
    except Exception as e:
        logger.error(f"Health check falló al conectar con Foundry: {e}")
        ready = False
    return jsonify({"status": "ok", "foundry_ready": ready})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    conversation_id = data.get("conversation_id")

    if not user_message:
        return jsonify({"error": "El mensaje no puede estar vacío"}), 400

    try:
        reply, conversation_id = _ejecutar_agente(user_message, conversation_id)
        return jsonify({"reply": reply, "conversation_id": conversation_id})

    except PermissionDeniedError as e:
        logger.exception("403 al llamar a Foundry (revisar RBAC)")
        return jsonify({"error": f"Error de permisos (403): {str(e)}"}), 502

    except Exception as e:
        logger.exception("Error al comunicar con Ada")
        return jsonify({"error": f"Error al comunicar con Ada: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000)
