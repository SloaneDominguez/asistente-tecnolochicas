import os
import traceback
from flask import Flask, render_template, request, jsonify
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

app = Flask(__name__)

# ---------- Configuración ----------
FOUNDRY_ENDPOINT = os.getenv(
    "FOUNDRY_ENDPOINT",
    "https://fdb2330910-ia-1710-resource.services.ai.azure.com/api/projects/fdb2330910-ia-1710"
)
AGENT_NAME = os.getenv("AGENT_NAME", "Ada-Tecnolochicas")

credential = DefaultAzureCredential()

# ---------- Cliente Azure AI Project ----------
project_client = None
try:
    project_client = AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential)
except Exception as e:
    print(f"Advertencia al inicializar Foundry: {e}")


# ---------- Lógica del Agente Ada ----------
def _ejecutar_agente(mensaje, conversation_id=None):
    """Envía un mensaje al agente Ada (mentora de TECNOLOchicas)."""
    openai_client = project_client.get_openai_client(agent_name=AGENT_NAME)
    
    if not conversation_id:
        conversation_id = openai_client.conversations.create().id

    # Contexto pedagógico para Ada
    prompt_con_contexto = (
        "Eres Ada, la mentora virtual y asistente pedagógica de TECNOLOchicas.\n"
        "Tu misión es apoyar a las instructoras en la preparación e impartición de sus clases "
        "de Scratch, Python, lógica de programación, chatbots e Inteligencia Artificial para niñas y jóvenes.\n"
        "Ofrece explicaciones didácticas, ideas de dinámicas, soluciones a problemas técnicos y "
        "estrategias pedagógicas inclusivas e inspiradoras.\n\n"
        f"Consulta de la instructora: {mensaje}"
    )

    response = openai_client.responses.create(
        conversation=conversation_id,
        input=[{"role": "user", "content": prompt_con_contexto}]
    )
    return response.output_text, conversation_id


# ---------- Rutas ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    conversation_id = data.get("conversation_id")

    if not user_message:
        return jsonify({"error": "El mensaje no puede estar vacío"}), 400

    if project_client is None:
        return jsonify({"error": "El cliente de Azure no se inicializó correctamente"}), 500

    try:
        reply, conversation_id = _ejecutar_agente(user_message, conversation_id)
        return jsonify({"reply": reply, "conversation_id": conversation_id})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Error al comunicar con Ada: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
