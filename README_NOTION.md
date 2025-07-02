# Integración con Notion - Discord Message Listener

## Configuración de la Base de Datos en Notion

### 1. Crear la Base de Datos

Tu base de datos de Notion debe tener **exactamente** las siguientes propiedades con estos tipos:

| Nombre de Propiedad | Tipo de Propiedad | Descripción |
|-------------------|------------------|-------------|
| **Autor** | Title | Nombre del autor del mensaje (Propiedad principal) |
| **Fecha** | Date | Fecha y hora cuando se envió el mensaje |
| **Servidor** | Select | Nombre del servidor de Discord |
| **Canal** | Select | Nombre del canal donde se envió el mensaje |
| **Contenido** | Text | Contenido del mensaje (limitado a 2000 caracteres) |
| **URL adjunta** | URL | Primera URL encontrada en el mensaje (si existe) |
| **Archivo Adjunto** | Files & media | Archivos adjuntos del mensaje (solo si existen) |
| **URL del mensaje** | URL | Enlace directo al mensaje en Discord |

### 2. Configurar la Integración

#### Paso 1: Crear la Integración en Notion
1. Ve a [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Haz clic en **"+ New integration"**
3. Ponle un nombre (ej: "Discord Message Listener")
4. Selecciona el workspace donde está tu base de datos
5. Haz clic en **"Submit"**
6. Copia el **"Internal Integration Token"** que aparece

#### Paso 2: Compartir la Base de Datos
1. Ve a tu base de datos en Notion
2. Haz clic en **"Share"** (esquina superior derecha)
3. Haz clic en **"Invite"**
4. Busca el nombre de tu integración y selecciónala
5. Asegúrate de que tenga permisos de **"Can edit"**
6. Haz clic en **"Invite"**

#### Paso 3: Obtener el ID de la Base de Datos
1. Ve a tu base de datos en Notion
2. Copia la URL de la página
3. El ID está en la URL con este formato:
   ```
   https://notion.so/[workspace]/[DATABASE_ID]?v=...
   ```
4. El `DATABASE_ID` es la cadena de caracteres entre las barras después del workspace y antes del `?v=`

### 3. Configurar las Variables de Entorno

Añade estas líneas a tu archivo `.env`:

```env
# Notion Integration
NOTION_TOKEN=secret_tu_integration_token_aquí
NOTION_DATABASE_ID=tu_database_id_aquí
```

### 4. Verificar la Configuración

Cuando inicies el bot, deberías ver:

```
✅ Cliente de Notion inicializado correctamente
✅ Configuración de Notion encontrada. Los mensajes se guardarán en Notion.
```

## Funcionalidades

### Mapeo de Datos

| Campo Discord | Campo Notion | Procesamiento |
|--------------|-------------|---------------|
| `message.author.name` | **Autor** | Se añade @ al principio |
| `message.created_at` | **Fecha** | Formato ISO 8601 |
| `message.guild.name` | **Servidor** | Nombre del servidor, "DM" para mensajes directos |
| `message.channel.name` | **Canal** | Nombre del canal, "DM" para mensajes directos |
| `message.content` | **Contenido** | Limitado a 2000 caracteres, "[Sin contenido de texto]" si está vacío |
| URLs en contenido | **URL adjunta** | Primera URL encontrada usando regex |
| `message.attachments` | **Archivo Adjunto** | Número de archivos adjuntos |
| URL calculada | **URL del mensaje** | `https://discord.com/channels/{guild_id}/{channel_id}/{message_id}` |

### Sistema de Backup

- **Principal**: Los mensajes se guardan en Notion
- **Backup**: Si Notion falla, se guarda en archivo de texto (`./logs/messages.txt`)
- **Logs**: La consola muestra el estado de guardado

### Manejo de Errores

- Si Notion no está configurado: Solo usa archivo de texto
- Si Notion falla: Automáticamente usa archivo de texto como backup
- Si ambos fallan: Muestra error en consola

## Solución de Problemas

### Error: "Notion client not initialized"
- Verifica que `NOTION_TOKEN` y `NOTION_DATABASE_ID` estén configurados
- Asegúrate de que la integración esté compartida con la base de datos

### Error: "Invalid database properties"
- Verifica que los nombres de las propiedades coincidan exactamente
- Asegúrate de que los tipos de propiedades sean correctos

### Los mensajes no aparecen en Notion
- Verifica que la integración tenga permisos de "Can edit"
- Revisa la consola para mensajes de error específicos
- Comprueba que el `DATABASE_ID` sea correcto

### Performance
- Notion tiene límites de velocidad en su API
- El bot maneja automáticamente los errores y usa backup
- Para alto volumen de mensajes, considera usar solo el modo archivo

## Comandos Útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el bot
python simple_message_listener.py

# Verificar logs de backup
tail -f logs/messages.txt
```
