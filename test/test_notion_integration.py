import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from dotenv import load_dotenv

# Cargar variables de entorno desde .env.test
load_dotenv(dotenv_path='.env.test')

# Importar la clase a probar
from simple_message_listener import SimpleMessageListener

# --- Fixtures de Pytest (Configuración reutilizable) ---

@pytest.fixture
def listener():
    """Inicializa una instancia de SimpleMessageListener para las pruebas."""
    # Desactivamos el cliente de Discord para no intentar una conexión real
    listener_instance = SimpleMessageListener()
    listener_instance.client = AsyncMock()
    return listener_instance

@pytest.fixture
def mock_message():
    """Crea un objeto de mensaje de Discord simulado (mock)."""
    message = MagicMock()
    message.id = "111111"
    message.guild.name = "Test Server"
    message.channel.name = "test-channel"
    message.author.name = "test-user"
    message.content = "Este es un mensaje de prueba."
    message.created_at.isoformat.return_value = "1900-07-12T12:00:00.000000"
    message.attachments = []
    message.reference = None
    message.guild.id = "123456789"
    message.channel.id = "987654321"
    return message

@pytest.fixture
def mock_reply_message(mock_message):
    """Crea un mensaje de respuesta simulado."""
    reply = MagicMock()
    reply.id = "222222"
    reply.guild.name = "Test Server"
    reply.channel.name = "test-channel"
    reply.author.name = "reply-user"
    reply.content = "Esta es una respuesta al mensaje anterior."
    reply.created_at.isoformat.return_value = "2025-07-12T12:01:00.000000"
    reply.attachments = []
    # Simula la referencia al mensaje original
    reply.reference = MagicMock()
    reply.reference.message_id = mock_message.id
    reply.guild.id = "123456789"
    reply.channel.id = "987654321"
    return reply

# --- Tests ---

## 1. Verificación de Credenciales y Conexión
def test_credentials_and_client_initialization(listener):
    """
    Verifica que las credenciales se carguen y los clientes se inicialicen.
    """
    assert listener.token is not None, "El token de Discord no se cargó."
    assert listener.notion_token is not None, "El token de Notion no se cargó."
    assert listener.notion_database_id is not None, "El ID de la base de datos de Notion no se cargó."
    
    # Verifica que el cliente de Notion se haya inicializado (no sea None)
    assert listener.notion_client is not None, "El cliente de Notion no se pudo inicializar. Revisa el token."
    print("\n✅ Test 1: Credenciales cargadas y cliente de Notion inicializado correctamente.")

## 2. Verificación de la Estructura de la Base de Datos
def test_notion_database_structure(listener):
    """
    Verifica que la base de datos de Notion tenga las propiedades esperadas.
    """
    db_id = listener.notion_database_id
    try:
        db_info = listener.notion_client.databases.retrieve(database_id=db_id)
        properties = db_info['properties'].keys()
        
        # Propiedades que tu bot espera que existan
        expected_properties = [
            "Message ID", "Autor", "Fecha", "Servidor", 
            "Canal", "Contenido", "URL del mensaje", "Original Message"
        ]
        
        for prop in expected_properties:
            assert prop in properties, f"La propiedad '{prop}' no se encontró en la base de datos de Notion."

        print(f"\n✅ Test 2: La estructura de la base de datos '{db_info['title'][0]['text']['content']}' es correcta.")

    except Exception as e:
        pytest.fail(f"No se pudo verificar la base de datos de Notion. Error: {e}")

@pytest.mark.asyncio
async def test_page_creation_and_validation(listener, mock_message, mock_reply_message, mocker):
    """
    Prueba el ciclo completo:
    3. Crea una página de prueba.
    4. Crea una respuesta a esa página.
    5. Valida la información guardada.
    """
    # Mocker para capturar los datos enviados a Notion.pages.create
    mocker.patch.object(listener.notion_client.pages, 'create', wraps=listener.notion_client.pages.create)

    ## 3. Creación de una página de prueba
    print("\n📝 Test 3: Creando página de prueba inicial...")
    # La variable ahora contendrá el objeto de la página creada o None
    created_page = await listener._save_message_to_notion(mock_message)
    assert created_page is not None, "Falló la creación de la página inicial en Notion."
    
    # Obtener el ID directamente del resultado
    created_page_id = created_page['id'] # <-- CAMBIO CLAVE
    print(f"📄 Página inicial creada con ID: {created_page_id}")

    # Captura los argumentos de la llamada para validación posterior
    call_args_initial = listener.notion_client.pages.create.call_args.kwargs

    ## 4. Creación de una página en respuesta
    print("\n📝 Test 4: Creando página de respuesta...")
    reply_page = await listener._save_message_to_notion(mock_reply_message)
    assert reply_page is not None, "Falló la creación de la página de respuesta en Notion."
    
    # Captura los argumentos de la segunda llamada
    call_args_reply = listener.notion_client.pages.create.call_args.kwargs
    print(f"📄 Página de respuesta creada con ID: {reply_page['id']}")

    ## 5. Validación del contenido
    print("\n🕵️ Test 5: Validando contenido de las páginas creadas...")
    
    # Validación de la página inicial
    initial_props = call_args_initial['properties']
    assert initial_props['Message ID']['title'][0]['text']['content'] == mock_message.id
    assert initial_props['Autor']['rich_text'][0]['text']['content'] == f"@{mock_message.author.name}"
    assert initial_props['Contenido']['rich_text'][0]['text']['content'] == mock_message.content
    print("✅ Página inicial validada correctamente.")

    # Validación de la página de respuesta
    reply_props = call_args_reply['properties']
    assert reply_props['Message ID']['title'][0]['text']['content'] == mock_reply_message.id
    assert reply_props['Autor']['rich_text'][0]['text']['content'] == f"@{mock_reply_message.author.name}"
    
    # La validación más importante: verificar el enlace a la página original
    expected_original_url = f"https://www.notion.so/{created_page_id.replace('-', '')}"
    assert reply_props['Original Message']['url'] == expected_original_url
    print("✅ Página de respuesta validada correctamente (incluyendo enlace a la original).")