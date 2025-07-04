# airregio_mensajes_utilities.py
import os
# Disable LangChain tracing to avoid deprecated handler issues
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_CALLBACKS_MANAGER"] = "false"

from dotenv import load_dotenv
load_dotenv(override=True)

# Set environment variables first
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

# Import langchain components after setting environment variables
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Model configurations
llama_3_2 = "llama-3.2-90b-vision-preview"
llama_3_1 = "llama-3.3-70b-versatile"
gpt = "gpt-4o-mini"

# Initialize LLM with error handling
def get_llm():
    try:
        return ChatOpenAI(model=gpt, temperature=0.2)
    except Exception as e:
        print(f"Error initializing ChatOpenAI: {e}")
        # Fallback to Groq if OpenAI fails
        try:
            return ChatGroq(model=llama_3_1, temperature=0.2)
        except Exception as e2:
            print(f"Error initializing ChatGroq: {e2}")
            raise Exception("Failed to initialize any LLM model")

# Initialize the LLM
llm = get_llm()

def generar_oferta(
    fecha_de_ultimo_servicio, tipo_de_servicio, tipo_de_propiedad, estado_de_garantia
):
    # Define el prompt del sistema
    system_prompt = f"""
    Eres un experto en generar ofertas personalizadas para conseguir la recompra de los cliente de la empresa AIRREGIO.
    AIRREGIO es una empresa experta en Impermeabilización, Aislante térmico, Mantenimiento y Reparación de techos.
    
    El usuario te pasará la siguiente información para que hagas la oferta personalizada:
    - Fecha de último servicio
    - Tipo de Servicio
    - Tipo de Propiedad
    - Estado de Garantía
    La oferta debe estar enfocada en la oportunidad de re-contratar o mejorar el servicio. Algunos ejemplos de ofertas personalizadas son:
    - "Cuando esté listo para renovar, le podemos ofrecer un descuento especial en servicios de Impermeabilización adicional."
    - "Como cliente nuevo, podría beneficiarse de un mantenimiento preventivo gratuito en su primer año."
    - "Recomendar una actualización de Aislante Térmico para sus instalaciones en su propiedad de tipo Industrial, especialmente por el clima en la zona."
    - "Se recomienda un chequeo de mantenimiento antes de la temporada de lluvias para asegurar la durabilidad de su Impermeabilización."
    - "Propuesta de renovación de Mantenimientos con descuento por tiempo limitado."
    Importante: No menciones servicios que no se hayan brindado. NO menciones descuentos de precio como 30 por ciento o a mitad de precio.
    IMPORTANTE: Estás generando ofertas, NO mensajes que se van a enviar.
    Genera la oferta en función de los parámetros dados.
    """
    # Define el prompt del usuario
    user_prompt = f"""
    Genera una oferta con estos datos:
    - Fecha de último servicio: {fecha_de_ultimo_servicio}
    - Tipo de Servicio: {tipo_de_servicio}
    - Tipo de Propiedad: {tipo_de_propiedad}
    - Estado de Garantía: {estado_de_garantia}
    """
    # Crea los mensajes para el modelo
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    # Obtiene la respuesta del modelo
    response = llm.invoke(messages)
    # Retorna la oferta generada
    return response.content

def generar_mensaje(oferta, nombre, fecha_de_ultimo_servicio):
    # Define el prompt del sistema
    system_prompt = f"""
    Eres un experto en generar mensajes cortos para WhatsApp. También eres un experto en persuasión y comunicación.
    El usuario te dará la siguiente información para que puedas generar un mensaje corto de WhatsApp para promover la recompra a clientes pasados de la empresa AIRREGIO. 
    - Oferta
    - Nombre del cliente
    - Fecha de último servicio
    IMPORTANTE: Tu mensaje debe ser corto, ameno, y muy persuasivo para promover la recompra.
    AIRREGIO es una empresa experta en Impermeabilización, Aislante térmico, Mantenimiento y Reparación de techos.
    Genera el mensaje en función de los parámetros dados.
    """
    # Define el prompt del usuario
    user_prompt = f"""
    Genera una mensaje con estos datos:
    - Oferta: {oferta}
    - Nombre del cliente: {nombre}
    - Fecha de último servicio: {fecha_de_ultimo_servicio}
    """
    # Crea los mensajes para el modelo
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    # Obtiene la respuesta del modelo
    response = llm.invoke(messages)
    # Retorna la oferta generada
    return response.content