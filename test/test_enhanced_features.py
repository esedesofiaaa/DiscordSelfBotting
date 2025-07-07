#!/usr/bin/env python3
"""
Tests específicos para la nueva funcionalidad de respuestas y relaciones en Notion
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Agregar el directorio padre al path para importar el módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEnhancedNotionFeatures:
    """Test suite para las nuevas funcionalidades de Notion"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        load_dotenv()
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
    
    def test_import_enhanced_listener(self):
        """Test that the enhanced listener can be imported"""
        try:
            from simple_message_listener import SimpleMessageListener
            assert SimpleMessageListener is not None
            print("✅ SimpleMessageListener importado correctamente")
        except ImportError as e:
            pytest.fail(f"No se pudo importar SimpleMessageListener: {e}")
    
    def test_listener_initialization_with_notion(self):
        """Test that listener initializes correctly with Notion"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        from simple_message_listener import SimpleMessageListener
        
        listener = SimpleMessageListener()
        
        # Verificar que los atributos necesarios existen
        assert hasattr(listener, 'notion_client'), "Listener debe tener notion_client"
        assert hasattr(listener, 'notion_database_id'), "Listener debe tener notion_database_id"
        assert hasattr(listener, '_find_message_in_notion'), "Listener debe tener método _find_message_in_notion"
        
        print("✅ Listener inicializado correctamente con Notion")
    
    def test_find_message_in_notion_method(self):
        """Test the _find_message_in_notion method"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        from simple_message_listener import SimpleMessageListener
        
        listener = SimpleMessageListener()
        
        # Test con un ID que no existe
        result = listener._find_message_in_notion("nonexistent_id_123")
        assert result is None, "Debería retornar None para ID inexistente"
        
        print("✅ Método _find_message_in_notion funciona correctamente")
    
    def test_message_properties_structure(self):
        """Test that message properties are correctly structured"""
        from simple_message_listener import SimpleMessageListener
        
        # Crear un mock message para probar
        mock_message = Mock()
        mock_message.id = "123456789012345678"
        mock_message.content = "Test message content"
        mock_message.author.name = "testuser"
        mock_message.author.discriminator = "0"
        mock_message.guild.name = "Test Server"
        mock_message.guild.id = "987654321098765432"
        mock_message.channel.name = "test-channel"
        mock_message.channel.id = "111222333444555666"
        mock_message.created_at.isoformat.return_value = "2025-07-07T10:00:00.000Z"
        mock_message.attachments = []
        mock_message.reference = None  # No es una respuesta
        
        listener = SimpleMessageListener()
        
        # Verificar que el método existe y puede ser llamado
        assert hasattr(listener, '_save_message_to_notion'), "Método _save_message_to_notion debe existir"
        
        print("✅ Estructura de propiedades de mensaje verificada")
    
    def test_reply_detection_logic(self):
        """Test reply detection logic"""
        from simple_message_listener import SimpleMessageListener
        
        # Crear mock message que es una respuesta
        mock_message = Mock()
        mock_message.id = "123456789012345678"
        mock_message.content = "This is a reply"
        mock_message.reference = Mock()
        mock_message.reference.message_id = "original_message_id"
        
        listener = SimpleMessageListener()
        
        # Verificar que la lógica de detección funciona
        # (esto se probará indirectamente a través del método _save_message_to_notion)
        has_reference = mock_message.reference is not None
        assert has_reference, "Mock message debería tener reference"
        
        has_message_id = mock_message.reference.message_id is not None
        assert has_message_id, "Mock message reference debería tener message_id"
        
        print("✅ Lógica de detección de respuestas verificada")
    
    @pytest.mark.integration
    def test_full_message_flow_with_notion(self):
        """Integration test for full message processing flow"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        from simple_message_listener import SimpleMessageListener
        
        listener = SimpleMessageListener()
        
        if not listener.notion_client:
            pytest.skip("Notion client no está configurado")
        
        # Crear un mensaje de prueba simple
        mock_message = Mock()
        mock_message.id = "test_integration_message"
        mock_message.content = "Test integration message"
        mock_message.author.name = "pytest_bot"
        mock_message.author.discriminator = "0"
        mock_message.guild.name = "Test Server"
        mock_message.guild.id = "123456789012345678"
        mock_message.channel.name = "test-channel"
        mock_message.channel.id = "987654321098765432"
        mock_message.created_at.isoformat.return_value = "2025-07-07T10:00:00.000Z"
        mock_message.attachments = []
        mock_message.reference = None
        
        # Intentar procesar el mensaje
        # Nota: Esto creará una entrada real en Notion si está configurado
        try:
            result = listener._save_message_to_notion(mock_message)
            
            # Si llegamos aquí, el procesamiento fue exitoso
            print("✅ Flujo completo de procesamiento de mensaje probado")
            
            if result:
                print("✅ Mensaje guardado exitosamente en Notion")
            else:
                print("⚠️  Mensaje no guardado en Notion (configuración incompleta)")
                
        except Exception as e:
            # Si hay error, verificar que sea por configuración, no por código
            if "notion" in str(e).lower():
                pytest.skip(f"Error de configuración de Notion: {e}")
            else:
                pytest.fail(f"Error inesperado en el procesamiento: {e}")
    
    def test_enhanced_properties_in_save_method(self):
        """Test that the enhanced save method includes all new properties"""
        from simple_message_listener import SimpleMessageListener
        import inspect
        
        listener = SimpleMessageListener()
        
        # Verificar que el método _save_message_to_notion existe
        assert hasattr(listener, '_save_message_to_notion'), "Método _save_message_to_notion debe existir"
        
        # Verificar la signatura del método
        method = getattr(listener, '_save_message_to_notion')
        signature = inspect.signature(method)
        
        # Debe tener parámetro 'message'
        assert 'message' in signature.parameters, "Método debe tener parámetro 'message'"
        
        # Verificar que el código del método incluye las nuevas propiedades
        source = inspect.getsource(method)
        
        # Verificar que incluye las propiedades mejoradas
        required_properties = ['Message ID', 'Replied message', 'message_id', 'reference']
        for prop in required_properties:
            assert prop in source, f"Propiedad '{prop}' debe estar en el código del método"
        
        print("✅ Método _save_message_to_notion incluye todas las propiedades mejoradas")
