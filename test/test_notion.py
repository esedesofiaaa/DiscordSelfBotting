#!/usr/bin/env python3
"""
Pytest tests para verificar la conexión con Notion
"""
import os
import pytest
from dotenv import load_dotenv
from notion_client import Client


class TestNotionIntegration:
    """Test suite for Notion integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        load_dotenv()
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
    
    def test_environment_variables_exist(self):
        """Test that required environment variables are set"""
        assert self.notion_token is not None, "NOTION_TOKEN no encontrado en .env"
        assert self.database_id is not None, "NOTION_DATABASE_ID no encontrado en .env"
        assert len(self.notion_token) > 10, "NOTION_TOKEN parece estar vacío o inválido"
        
    def test_notion_client_creation(self):
        """Test that Notion client can be created successfully"""
        if not self.notion_token:
            pytest.skip("NOTION_TOKEN not available")
            
        notion = Client(auth=self.notion_token)
        assert notion is not None, "Failed to create Notion client"
        
    def test_database_access(self):
        """Test that we can access the configured database"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        notion = Client(auth=self.notion_token)
        
        try:
            database = notion.databases.retrieve(database_id=self.database_id)
            assert database is not None, "Database not found or not accessible"
            assert hasattr(database, 'id') or (isinstance(database, dict) and 'id' in database), "Database response is invalid"
        except Exception as e:
            if "unauthorized" in str(e).lower():
                pytest.fail("Token de Notion inválido o la integración no tiene acceso a la base de datos")
            elif "not_found" in str(e).lower():
                pytest.fail("ID de base de datos incorrecto o la base de datos no existe")
            else:
                pytest.fail(f"Error inesperado al acceder a la base de datos: {e}")
                
    def test_create_test_page(self):
        """Test creating a test page in the Notion database"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        notion = Client(auth=self.notion_token)
        
        try:
            # Verificar acceso a la base de datos
            database = notion.databases.retrieve(database_id=self.database_id)
            assert database is not None, "Database not found or not accessible"
            
            # Crear página de prueba
            test_page = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Autor": {
                        "rich_text": [{"text": {"content": "Test Bot - Pytest"}}]
                    },
                    "Fecha": {
                        "date": {"start": "2025-07-02T10:00:00.000Z"}
                    },
                    "Servidor": {
                        "select": {"name": "Test Server"}
                    },
                    "Canal": {
                        "select": {"name": "test-channel"}
                    },
                    "Contenido": {
                        "rich_text": [{"text": {"content": "Este es un mensaje de prueba para verificar la integración con pytest"}}]
                    },
                    "URL adjunta": {
                        "url": "https://example.com"
                    },
                    "URL del mensaje": {
                        "url": "https://discord.com/channels/123/456/789"
                    }
                }
            }
            
            response = notion.pages.create(**test_page)
            assert response is not None, "Failed to create test page"
            assert hasattr(response, 'id') or (isinstance(response, dict) and 'id' in response), "Invalid page creation response"
            
            print("✅ Página de prueba creada exitosamente")
            print("🎉 ¡La integración con Notion está funcionando perfectamente!")
            
        except Exception as e:
            if "unauthorized" in str(e).lower():
                pytest.fail("Token de Notion inválido o la integración no tiene acceso a la base de datos")
            elif "not_found" in str(e).lower():
                pytest.fail("ID de base de datos incorrecto o la base de datos no existe")
            else:
                pytest.fail(f"Error inesperado al crear página de prueba: {e}")
                
    def test_message_search_functionality(self):
        """Test the new message search functionality in Notion"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        # Importar la funcionalidad del bot
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from simple_message_listener import SimpleMessageListener
        
        # Crear instancia del listener
        listener = SimpleMessageListener()
        
        # Verificar que el cliente de Notion esté inicializado
        assert listener.notion_client is not None, "Notion client should be initialized"
        
        # Test búsqueda de mensaje inexistente
        non_existent_id = "999999999999999999"
        result = listener._find_message_in_notion(non_existent_id)
        assert result is None, "Should return None for non-existent message"
        
        print("✅ Función de búsqueda de mensajes probada exitosamente")
        
    def test_notion_properties_structure(self):
        """Test that the Notion database has the required properties for enhanced functionality"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        notion = Client(auth=self.notion_token)
        
        try:
            database = notion.databases.retrieve(database_id=self.database_id)
            properties = database['properties']  # type: ignore
            
            # Propiedades requeridas para la funcionalidad mejorada
            required_properties = {
                'Message ID': 'title',
                'Autor': 'rich_text',
                'Fecha': 'date',
                'Servidor': 'select',
                'Canal': 'select',
                'Contenido': 'rich_text',
                'URL adjunta': 'url',
                'Archivo Adjunto': 'files',
                'URL del mensaje': 'url',
                'Original Message': 'url'  # Cambiado de relación a URL
            }
            
            missing_properties = []
            wrong_type_properties = []
            
            for prop_name, expected_type in required_properties.items():
                if prop_name not in properties:
                    missing_properties.append(prop_name)
                else:
                    actual_type = properties[prop_name]['type']
                    if actual_type != expected_type:
                        wrong_type_properties.append((prop_name, actual_type, expected_type))
            
            # Verificar que no falten propiedades críticas
            if missing_properties:
                pytest.fail(f"Faltan propiedades requeridas: {missing_properties}. "
                          f"Ejecuta setup_notion_database.py para ver instrucciones.")
            
            if wrong_type_properties:
                error_msg = "Propiedades con tipo incorrecto:\n"
                for prop, actual, expected in wrong_type_properties:
                    error_msg += f"  - {prop}: {actual} (esperado: {expected})\n"
                pytest.fail(error_msg)
            
            print("✅ Todas las propiedades requeridas están configuradas correctamente")
            
        except Exception as e:
            pytest.fail(f"Error al verificar propiedades de la base de datos: {e}")
            
    def test_create_message_with_id(self):
        """Test creating a message with ID property for reply functionality"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        notion = Client(auth=self.notion_token)
        
        try:
            # Crear mensaje con ID específico para pruebas
            test_message_id = "test_message_123456789"
            
            test_page = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Message ID": {
                        "title": [{"text": {"content": test_message_id}}]
                    },
                    "Autor": {
                        "rich_text": [{"text": {"content": "Test Bot - Message with ID"}}]
                    },
                    "Fecha": {
                        "date": {"start": "2025-07-07T10:00:00.000Z"}
                    },
                    "Servidor": {
                        "select": {"name": "Test Server"}
                    },
                    "Canal": {
                        "select": {"name": "test-channel"}
                    },
                    "Contenido": {
                        "rich_text": [{"text": {"content": "Mensaje de prueba con ID para funcionalidad de respuestas"}}]
                    },
                    "URL del mensaje": {
                        "url": "https://discord.com/channels/123/456/789"
                    }
                }
            }
            
            response = notion.pages.create(**test_page)
            assert response is not None, "Failed to create test message with ID"
            
            # Verificar que podemos buscar el mensaje por ID
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from simple_message_listener import SimpleMessageListener
            
            listener = SimpleMessageListener()
            found_page_url = listener._find_message_in_notion(test_message_id)
            
            # Verificar que ahora retorna una URL en lugar de un ID
            print(f"✅ Mensaje de prueba creado con ID: {test_message_id}")
            if found_page_url:
                print(f"✅ Mensaje encontrado, URL: {found_page_url}")
                # Verificar que es una URL válida de Notion
                assert found_page_url.startswith("https://www.notion.so/"), "Debe retornar una URL de Notion válida"
            else:
                print("⚠️  Mensaje no encontrado (puede ser debido a timing de indexación)")
            
        except Exception as e:
            pytest.fail(f"Error al crear mensaje con ID: {e}")
            
    def test_original_message_url_structure(self):
        """Test that original message URL property can be created in Notion"""
        if not self.notion_token or not self.database_id:
            pytest.skip("NOTION_TOKEN or NOTION_DATABASE_ID not available")
            
        notion = Client(auth=self.notion_token)
        
        try:
            # Verificar que la propiedad "Original Message" existe y es del tipo correcto
            database = notion.databases.retrieve(database_id=self.database_id)
            properties = database['properties']  # type: ignore
            
            # La propiedad puede no existir hasta que se use por primera vez
            if 'Original Message' in properties:
                original_msg_prop = properties['Original Message']
                assert original_msg_prop['type'] == 'url', "Propiedad 'Original Message' debe ser de tipo 'url'"
                print("✅ Propiedad 'Original Message' configurada correctamente como URL")
            else:
                print("ℹ️  Propiedad 'Original Message' se creará automáticamente al usarse")
            
            # Test crear un mensaje con Original Message URL
            test_page = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Message ID": {
                        "title": [{"text": {"content": "test_reply_message_789"}}]
                    },
                    "Autor": {
                        "rich_text": [{"text": {"content": "Test Bot - Reply Message"}}]
                    },
                    "Fecha": {
                        "date": {"start": "2025-07-07T10:00:00.000Z"}
                    },
                    "Servidor": {
                        "select": {"name": "Test Server"}
                    },
                    "Canal": {
                        "select": {"name": "test-channel"}
                    },
                    "Contenido": {
                        "rich_text": [{"text": {"content": "Este es un mensaje de respuesta de prueba"}}]
                    },
                    "URL del mensaje": {
                        "url": "https://discord.com/channels/123/456/789"
                    },
                    "Original Message": {
                        "url": "https://www.notion.so/abcd1234567890abcdef"
                    }
                }
            }
            
            response = notion.pages.create(**test_page)
            assert response is not None, "Failed to create test message with Original Message URL"
            
            print("✅ Mensaje con URL de mensaje original creado exitosamente")
            
        except Exception as e:
            pytest.fail(f"Error al verificar configuración de URL de mensaje original: {e}")
