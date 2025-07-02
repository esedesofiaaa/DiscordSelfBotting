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
                        "title": [{"text": {"content": "Test Bot - Pytest"}}]
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
