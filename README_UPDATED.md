# Discord Message Listener - Versión Mejorada con Notion

## 🚀 Nuevas Funcionalidades

### Manejo de Respuestas (Replies)
- **Detección automática**: El bot detecta cuando un mensaje es una respuesta
- **Relaciones en Notion**: Crea automáticamente relaciones entre mensajes
- **Búsqueda inteligente**: Busca mensajes originales en la base de datos
- **Fallback robusto**: Guarda mensajes aunque no encuentre el original

### Propiedades Completas en Notion
- **ID del mensaje**: Identificador único de Discord
- **Información del autor**: Nombre del usuario
- **Metadatos temporales**: Fecha y hora del mensaje
- **Contexto**: Servidor y canal
- **Contenido completo**: Texto, URLs y archivos adjuntos
- **Enlaces directos**: URL al mensaje original en Discord
- **Relaciones**: Conexión con mensajes respondidos

## 📋 Configuración Requerida

### Variables de Entorno (.env)
```env
# Discord
DISCORD_TOKEN=tu_token_aqui
MONITORING_SERVER_ID=123456789012345678
MONITORING_CHANNEL_IDS=123456789012345678,987654321098765432

# Notion
NOTION_TOKEN=secret_notion_token
NOTION_DATABASE_ID=database_id_aqui

# Opcional
LOG_FILE=./logs/messages.txt
```

### Base de Datos de Notion
Tu base de datos debe tener estas propiedades:

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| ID | Rich Text | ID del mensaje de Discord |
| Autor | Title | Nombre del autor |
| Fecha | Date | Fecha del mensaje |
| Servidor | Select | Nombre del servidor |
| Canal | Select | Nombre del canal |
| Contenido | Rich Text | Texto del mensaje |
| URL adjunta | URL | Primera URL encontrada |
| Archivo Adjunto | Files | Archivos adjuntos |
| URL del mensaje | URL | Enlace al mensaje original |
| Replied message | Relation | Relación con mensaje respondido |

## 🔧 Instalación y Configuración

### 1. Clonar e Instalar Dependencias
```bash
git clone <tu-repo>
cd DiscordSelfBotting
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus tokens y IDs
```

### 3. Verificar Base de Datos de Notion
```bash
python setup_notion_database.py
```

### 4. Probar la Integración
```bash
python test_notion_integration.py
```

### 5. Ejecutar el Bot
```bash
python simple_message_listener.py
# o usar el script
./start_simple_listener.sh
```

## 📝 Uso

### Modo Básico
El bot se ejecuta automáticamente y:
1. Conecta a Discord con tu token
2. Escucha mensajes del servidor configurado
3. Guarda cada mensaje en Notion
4. Crea relaciones automáticamente para respuestas

### Respuestas (Replies)
Cuando alguien responde a un mensaje:
1. El bot detecta que es una respuesta
2. Busca el mensaje original en Notion
3. Crea una relación en la propiedad "Replied message"
4. Guarda el mensaje con toda la información

### Ejemplo de Flujo
```
Usuario A: "¿Alguien sabe sobre Python?"
→ Se guarda en Notion con ID: 123456789

Usuario B: "Sí, ¿qué necesitas?" (respuesta a mensaje 123456789)
→ Se guarda en Notion con relación al mensaje 123456789
```

## 🛠️ Scripts Auxiliares

### `setup_notion_database.py`
- Verifica la configuración de tu base de datos
- Lista propiedades existentes
- Identifica propiedades faltantes
- Genera archivo JSON con estructura de ejemplo

### `test_notion_integration.py`
- Prueba la conexión con Notion
- Verifica la configuración del bot
- Testea búsquedas básicas

## 🔍 Debugging y Logs

### Logs en Consola
```
✅ Mensaje guardado en Notion: @usuario en #canal
🔗 Mensaje es respuesta a: 123456789
⚠️  Mensaje original no encontrado en Notion: 123456789
```

### Archivo de Backup
Si Notion falla, el bot guarda en archivo de texto:
```
[2024-01-15T10:30:45] Servidor > #canal | @usuario: mensaje aquí
```

## 🚨 Troubleshooting

### Error: "Cliente de Notion no inicializado"
- Verifica `NOTION_TOKEN` en .env
- Verifica `NOTION_DATABASE_ID` en .env
- Comprueba permisos de la integración

### Error: "Propiedades faltantes"
- Ejecuta `python setup_notion_database.py`
- Agrega propiedades faltantes en Notion
- Verifica tipos de propiedades

### Error: "Mensaje original no encontrado"
- Normal para mensajes antiguos
- El bot guarda el mensaje sin la relación
- No afecta la funcionalidad

### Error: "Rate limit exceeded"
- Notion tiene límites de API
- El bot reintenta automáticamente
- Considera espaciar las requests

## 🔒 Seguridad

### Tokens
- Nunca compartas tu `DISCORD_TOKEN`
- Nunca compartas tu `NOTION_TOKEN`
- Usa archivos `.env` locales
- Agrega `.env` a `.gitignore`

### Permisos
- El bot solo necesita permisos de lectura en Discord
- La integración de Notion necesita acceso a la base de datos
- Revisa permisos periódicamente

## 📊 Monitoreo

### Métricas
- Mensajes guardados exitosamente
- Relaciones creadas
- Errores de conexión
- Uso de backup

### Salud del Sistema
- Conexión a Discord: ✅/❌
- Conexión a Notion: ✅/❌
- Espacio en disco: Disponible
- Memoria: Normal

## 🔄 Actualizaciones

### Versión Actual: 2.0
- ✅ Manejo de respuestas
- ✅ Propiedades completas
- ✅ Búsqueda inteligente
- ✅ Fallback robusto

### Próximas Mejoras
- [ ] Interfaz web para monitoreo
- [ ] Análisis de conversaciones
- [ ] Exportación de datos
- [ ] Alertas personalizadas

## 🤝 Contribuciones

¿Encontraste un bug? ¿Tienes una mejora?
1. Crea un issue describiendo el problema
2. Fork el repositorio
3. Crea una branch con tu mejora
4. Envía un pull request

## 📄 Licencia

Este proyecto es para uso personal y educativo.
