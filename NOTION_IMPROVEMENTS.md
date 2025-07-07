# Mejoras en la Integración con Notion - Manejo de Respuestas

## Nuevas Funcionalidades

### 1. Propiedades de Notion Actualizadas

El bot ahora guarda las siguientes propiedades en Notion para cada mensaje:

- **ID**: El ID único del mensaje de Discord (tipo: Rich Text)
- **Autor**: El autor del mensaje (tipo: Title)
- **Fecha**: Fecha y hora del mensaje (tipo: Date)
- **Servidor**: Nombre del servidor (tipo: Select)
- **Canal**: Nombre del canal (tipo: Select)
- **Contenido**: Texto del mensaje (tipo: Rich Text)
- **URL adjunta**: Primera URL encontrada en el mensaje (tipo: URL)
- **Archivo Adjunto**: Archivos adjuntos del mensaje (tipo: Files)
- **URL del mensaje**: Enlace directo al mensaje en Discord (tipo: URL)
- **Replied message**: Relación con el mensaje original si es una respuesta (tipo: Relation)

### 2. Manejo de Respuestas (Replies)

Cuando un mensaje es una respuesta a otro mensaje:

1. El bot detecta automáticamente si el mensaje es una respuesta usando `message.reference`
2. Busca en la base de datos de Notion el mensaje original usando su ID
3. Si encuentra el mensaje original, crea una relación en la propiedad "Replied message"
4. Si no encuentra el mensaje original, guarda el mensaje sin la relación

### 3. Funciones Principales

#### `_find_message_in_notion(message_id: str) -> Optional[str]`
- Busca un mensaje en Notion por su ID de Discord
- Retorna el ID de la página de Notion si lo encuentra
- Retorna None si no lo encuentra

#### `_save_message_to_notion(message: discord.Message)`
- Guarda un mensaje completo en Notion
- Maneja automáticamente las respuestas
- Incluye todas las propiedades requeridas

### 4. Configuración Requerida en Notion

Para que el bot funcione correctamente, tu base de datos de Notion debe tener las siguientes propiedades:

1. **ID** (Rich Text) - Para almacenar el ID del mensaje de Discord
2. **Autor** (Title) - Nombre del autor
3. **Fecha** (Date) - Fecha del mensaje
4. **Servidor** (Select) - Nombre del servidor
5. **Canal** (Select) - Nombre del canal
6. **Contenido** (Rich Text) - Contenido del mensaje
7. **URL adjunta** (URL) - URLs encontradas en el mensaje
8. **Archivo Adjunto** (Files) - Archivos adjuntos
9. **URL del mensaje** (URL) - Enlace al mensaje original
10. **Replied message** (Relation) - Relación a la misma base de datos

### 5. Ejemplo de Uso

```python
# El bot funciona automáticamente
# Cuando detecta un mensaje que es respuesta:
# 1. Extrae el ID del mensaje original
# 2. Busca ese mensaje en Notion
# 3. Crea la relación si lo encuentra
# 4. Guarda el mensaje con toda la información
```

### 6. Manejo de Errores

El bot es robusto y maneja los siguientes casos:

- **Mensaje original no encontrado**: Guarda el mensaje sin la relación
- **Error en Notion**: Usa el archivo de texto como backup
- **Propiedades faltantes**: Continúa con las propiedades disponibles
- **Errores de red**: Reintenta o usa backup

### 7. Logging Mejorado

El bot ahora proporciona información detallada sobre:

- Búsquedas de mensajes en Notion
- Creación de relaciones entre mensajes
- Errores específicos de Notion
- Estados de las respuestas

### 8. Pruebas

Ejecuta el archivo `test_notion_integration.py` para verificar que todo funcione correctamente:

```bash
python test_notion_integration.py
```

### 9. Consideraciones Importantes

- **Orden de mensajes**: Los mensajes deben guardarse en orden cronológico para que las relaciones funcionen correctamente
- **Mensajes antiguos**: Si el mensaje original no está en Notion, la relación no se creará
- **Rendimiento**: La búsqueda en Notion puede ser lenta para bases de datos grandes
- **Límites de API**: Notion tiene límites de rate limiting que el bot respeta

### 10. Troubleshooting

Si encuentras problemas:

1. **Verifica la configuración**: Asegúrate de que todas las propiedades existan en Notion
2. **Revisa los logs**: El bot proporciona información detallada de errores
3. **Prueba la conexión**: Usa el script de prueba para verificar la conectividad
4. **Verifica las variables de entorno**: NOTION_TOKEN y NOTION_DATABASE_ID
