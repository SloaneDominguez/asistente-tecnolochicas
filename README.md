# 🤖 Ada - Asistente Virtual y Pedagógica para TECNOLOchicas

**Ada** es un chatbot inteligente y mentora virtual diseñado para apoyar a las instructoras de **TECNOLOchicas** en la preparación e impartición de clases sobre Scratch, Python, lógica de programación, chatbots e Inteligencia Artificial para niñas y jóvenes.

---

## 🚀 1. Arquitectura e Integración con IA

La solución combina una interfaz web ligera con la infraestructura en la nube de Azure y los modelos de lenguaje de OpenAI.

### Componentes Principales
* **Frontend / Backend:** Desarrollado en **Python con Flask**, encargado de la interfaz de chat y el manejo de rutas HTTP.
* **Orquestación de IA:** Integración con **Azure AI Foundry (Projects SDK)** y el **OpenAI SDK**, permitiendo mantener contexto conversacional mediante hilos de chat (`conversation_id`).
* **Seguridad y Autenticación:** Uso de **Managed Identity (Identidad Administrada)** en Azure con asignación del rol *Azure AI Developer*, garantizando una conexión segura sin exponer credenciales en el código.
* **Modelo de Lenguaje:** Conexión con agentes personalizados hospedados en Azure AI Foundry, parametrizados para responder con un enfoque pedagógico, inclusivo y didáctico.

---

## 📄 2. Descripción de la Integración con IA

El desarrollo de este proyecto integró Inteligencia Artificial en dos niveles:

1. **Uso de IA como Asistente de Desarrollo (VibeCoding / Copilot):**
   * Apoyo de herramientas de IA generativa para la estructuración de la API en Flask, manejo de excepciones y configuración de SDKs de Azure.

2. **Agente Pedagógico Virtual (Ada):**
   * Configuración de un agente conversacional provisto con un *system prompt* especializado en metodologías de enseñanza STEM para mujeres jóvenes.
   * Manejo dinámico de versiones de API (`2024-05-01-preview`) y endpoints dinámicos gestionados por variables de entorno.

---

## 🛠️ 3. Guía de Despliegue en Azure (Azure App Service)

### Prerrequisitos
* Suscripción activa a Microsoft Azure (Azure for Students).
* Recurso de **Azure AI Projects / Azure AI Foundry** configurado con un agente creado.
* Repositorio en GitHub sincronizado con el código del proyecto.

### Pasos de Despliegue

1. **Creación del App Service:**
   * Crear un nuevo servicio de aplicaciones en Azure con Stack de **Python 3.10+** (Linux).
   * Asignar el plan de tarifas **Free (F1)** o **Basic (B1)** según los requerimientos de cómputo.

2. **Configuración de Variables de Entorno (App Settings):**
   En la sección *Configuración > Variables de entorno* del App Service, agregar:
   * `FOUNDRY_ENDPOINT`: URI de conexión a tu proyecto de Azure AI Foundry.
   * `AGENT_NAME`: Nombre del agente configurado (ej. `Ada-Tecnolochicas`).
   * `API_VERSION`: Versión de API (ej. `2024-05-01-preview`).

3. **Configuración de Identidad Administrada y Permisos RBAC:**
   * En el menú *Identidad* del App Service, activar la **Identidad asignada por el sistema**.
   * Ir al recurso de Azure AI Foundry / Azure AI Services, acceder al control de acceso (**IAM**) y asignar el rol **Azure AI Developer** a la Identidad Administrada de la aplicación.

4. **Despliegue Continuo:**
   * Conectar el repositorio de GitHub (rama `desarrollo`) a través del *Centro de Despliegue (Deployment Center)* para automatizar el build con GitHub Actions / Oryx.

---

## 🧪 4. Guía de Pruebas

Para verificar el correcto funcionamiento del sistema en entorno local o en producción:

### Prueba 1: Diagnóstico de Salud (Health Check)
Acceder a la ruta `/health` desde el navegador o mediante `curl`:
```bash
GET https://asistente-tecnolochicas-527634d2-eqbbaufvgndxc2bv.westus-01.azurewebsites.net/health
