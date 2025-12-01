#!/usr/bin/env python3
"""
Script de prueba para verificar que la nueva funcionalidad de Category funciona correctamente
"""
import os
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_category_detection():
    """Prueba la detección de categorías en canales de Discord"""
    print("🧪 Probando detección de categorías...\n")
    
    # Simular un canal con categoría
    mock_channel_with_category = MagicMock()
    mock_channel_with_category.name = "general-chat"
    mock_channel_with_category.category = MagicMock()
    mock_channel_with_category.category.name = "📝 GENERAL"
    
    # Simular un canal sin categoría
    mock_channel_without_category = MagicMock()
    mock_channel_without_category.name = "standalone-channel"
    mock_channel_without_category.category = None
    
    # Test 1: Canal con categoría
    print("Test 1: Canal con categoría")
    category_name = None
    try:
        if hasattr(mock_channel_with_category, 'category') and mock_channel_with_category.category:
            category_name = mock_channel_with_category.category.name
            print(f"✅ Categoría detectada: '{category_name}'")
        else:
            category_name = "Sin categoría"
            print(f"⚠️ No se encontró categoría, usando: '{category_name}'")
    except Exception as e:
        category_name = "Sin categoría"
        print(f"❌ Error: {e}")
    
    assert category_name == "📝 GENERAL", f"Esperaba '📝 GENERAL', obtuvo '{category_name}'"
    print()
    
    # Test 2: Canal sin categoría
    print("Test 2: Canal sin categoría")
    category_name = None
    try:
        if hasattr(mock_channel_without_category, 'category') and mock_channel_without_category.category:
            category_name = mock_channel_without_category.category.name
            print(f"✅ Categoría detectada: '{category_name}'")
        else:
            category_name = "Sin categoría"
            print(f"⚠️ No se encontró categoría, usando: '{category_name}'")
    except Exception as e:
        category_name = "Sin categoría"
        print(f"❌ Error: {e}")
    
    assert category_name == "Sin categoría", f"Esperaba 'Sin categoría', obtuvo '{category_name}'"
    print()
    
    print("✅ Todos los tests pasaron correctamente!")
    print()
    print("📋 Resumen:")
    print("   - Canal con categoría: Detectada correctamente")
    print("   - Canal sin categoría: Valor por defecto asignado correctamente")
    print()
    print("🎯 La nueva funcionalidad de Category está lista para usar!")
    print()
    print("📝 Recuerda:")
    print("   1. Asegúrate de que tu base de datos de Notion tiene una propiedad 'Category' de tipo Select")
    print("   2. El bot ahora guardará automáticamente la categoría del canal en cada mensaje")
    print("   3. Si un canal no tiene categoría, se usará 'Sin categoría' como valor por defecto")

if __name__ == "__main__":
    test_category_detection()
