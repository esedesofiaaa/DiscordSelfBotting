"""
Script para ayudar a configurar la base de datos de Notion con las propiedades correctas
"""

import os
from dotenv import load_dotenv
from notion_client import Client

def check_notion_database_properties():
    """Verifica y muestra las propiedades de la base de datos de Notion"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    notion_token = os.getenv('NOTION_TOKEN')
    notion_database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not notion_token or not notion_database_id:
        print("❌ Error: NOTION_TOKEN o NOTION_DATABASE_ID no están configurados")
        print("   Configura estas variables en tu archivo .env")
        return False
    
    try:
        # Inicializar cliente de Notion
        client = Client(auth=notion_token)
        print("✅ Cliente de Notion inicializado correctamente")
        
        # Obtener información de la base de datos
        database = client.databases.retrieve(database_id=notion_database_id)
        
        print(f"\n📋 Base de datos: {database['title'][0]['plain_text']}")  # type: ignore
        print(f"🆔 ID: {database['id']}")  # type: ignore
        
        # Obtener propiedades existentes
        properties = database['properties']  # type: ignore
        print(f"\n🔧 Propiedades existentes ({len(properties)}):")
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info['type']
            print(f"   • {prop_name}: {prop_type}")
        
        # Verificar propiedades requeridas
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
            'Replied message': 'relation'
        }
        
        print(f"\n✅ Verificando propiedades requeridas:")
        missing_properties = []
        
        for req_name, req_type in required_properties.items():
            if req_name in properties:
                actual_type = properties[req_name]['type']
                if actual_type == req_type:
                    print(f"   ✅ {req_name}: {actual_type}")
                else:
                    print(f"   ⚠️  {req_name}: {actual_type} (esperado: {req_type})")
            else:
                print(f"   ❌ {req_name}: FALTANTE (tipo: {req_type})")
                missing_properties.append((req_name, req_type))
        
        if missing_properties:
            print(f"\n⚠️  Faltan {len(missing_properties)} propiedades:")
            print("\n📝 Para agregar las propiedades faltantes en Notion:")
            print("   1. Ve a tu base de datos en Notion")
            print("   2. Haz clic en '+' para agregar una nueva propiedad")
            print("   3. Agrega cada una de las siguientes propiedades:")
            
            for prop_name, prop_type in missing_properties:
                notion_type = {
                    'rich_text': 'Rich Text',
                    'title': 'Title',
                    'date': 'Date',
                    'select': 'Select',
                    'url': 'URL',
                    'files': 'Files',
                    'relation': 'Relation'
                }.get(prop_type, prop_type)
                
                print(f"      • Nombre: '{prop_name}' - Tipo: {notion_type}")
                
                if prop_type == 'relation':
                    print(f"        (Para 'Replied message', relacionar con la misma base de datos)")
        else:
            print("\n🎉 ¡Todas las propiedades requeridas están configuradas!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {e}")
        return False

def create_sample_properties_json():
    """Crea un archivo JSON con las propiedades de ejemplo"""
    
    sample_properties = {
        "ID": {
            "type": "rich_text",
            "rich_text": {}
        },
        "Autor": {
            "type": "title",
            "title": {}
        },
        "Fecha": {
            "type": "date",
            "date": {}
        },
        "Servidor": {
            "type": "select",
            "select": {
                "options": []
            }
        },
        "Canal": {
            "type": "select",
            "select": {
                "options": []
            }
        },
        "Contenido": {
            "type": "rich_text",
            "rich_text": {}
        },
        "URL adjunta": {
            "type": "url",
            "url": {}
        },
        "Archivo Adjunto": {
            "type": "files",
            "files": {}
        },
        "URL del mensaje": {
            "type": "url",
            "url": {}
        },
        "Replied message": {
            "type": "relation",
            "relation": {
                "database_id": "TU_DATABASE_ID_AQUI"
            }
        }
    }
    
    import json
    with open('notion_properties_sample.json', 'w', encoding='utf-8') as f:
        json.dump(sample_properties, f, indent=2, ensure_ascii=False)
    
    print("📄 Archivo 'notion_properties_sample.json' creado con propiedades de ejemplo")

if __name__ == "__main__":
    print("🔧 Verificador de Base de Datos de Notion")
    print("=" * 50)
    
    success = check_notion_database_properties()
    
    if success:
        print("\n" + "=" * 50)
        create_sample_properties_json()
        print("\n✅ Verificación completada")
    else:
        print("\n❌ No se pudo completar la verificación")
