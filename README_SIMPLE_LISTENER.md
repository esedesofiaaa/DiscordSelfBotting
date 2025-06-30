# Discord Message Listener

Un bot simple y enfocado que **únicamente escucha y registra** todos los mensajes de un servidor o canal específico de Discord.

## ¿Qué hace exactamente?

- ✅ Se conecta a Discord como un self-bot
- ✅ Escucha mensajes de un servidor específico
- ✅ Guarda todos los mensajes en un archivo de texto
- ✅ Funciona silenciosamente en segundo plano
- ❌ NO envía mensajes
- ❌ NO tiene comandos
- ❌ NO interactúa con usuarios

## Configuración rápida

### 1. Instalar dependencias
```bash
pip3 install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar la configuración
nano .env
```

### 3. Configurar el archivo .env

Necesitas configurar estos valores en el archivo `.env`:

```env
# Token de tu cuenta de Discord
DISCORD_TOKEN=tu_token_aqui

# ID del servidor que quieres monitorear
MONITORING_SERVER_ID=123456789

# (Opcional) IDs de canales específicos
MONITORING_CHANNEL_IDS=canal1,canal2,canal3

# Archivo donde guardar los mensajes
LOG_FILE=./logs/messages.txt
```

### 4. Obtener tu token de Discord

⚠️ **IMPORTANTE**: Usar un self-bot viola los términos de servicio de Discord. Úsalo bajo tu propio riesgo.

1. Abre Discord en tu navegador web
2. Presiona F12 para abrir las herramientas de desarrollador
3. Ve a la pestaña "Network" o "Red"
4. Recarga la página (F5)
5. Busca una petición a `api/v*/users/@me`
6. En los headers de la petición, busca `Authorization` 
7. Copia el valor (será algo como `mfa.xyz123...`)

### 5. Obtener IDs de servidor y canales

1. Activa el "Modo desarrollador" en Discord:
   - Configuración → Avanzado → Modo desarrollador
2. Para el ID del servidor:
   - Click derecho en el servidor → Copiar ID
3. Para IDs de canales (opcional):
   - Click derecho en el canal → Copiar ID

## Ejecución

### Opción 1: Script automático
```bash
./start_simple_listener.sh
```

### Opción 2: Ejecución directa
```bash
python3 simple_message_listener.py
```

## Formato de los logs

Los mensajes se guardan en el siguiente formato:

```
[2025-06-17T18:21:16.336715] #canal-nombre | @usuario: contenido del mensaje
--------------------------------------------------------------------------------
[2025-06-17T18:22:27.879618] #otro-canal | @otro-usuario: otro mensaje [Archivos: 1]
--------------------------------------------------------------------------------
```

## Configuración avanzada

### Monitorear canales específicos

Si quieres monitorear solo ciertos canales, configura `MONITORING_CHANNEL_IDS`:

```env
MONITORING_CHANNEL_IDS=123456789,987654321,111222333
```

### Monitorear todos los canales

Deja `MONITORING_CHANNEL_IDS` vacío para monitorear todos los canales del servidor:

```env
MONITORING_CHANNEL_IDS=
```

## Estructura de archivos

```
simple_message_listener.py  # Bot principal (simplificado)
start_simple_listener.sh    # Script de inicio
.env.example               # Configuración de ejemplo
logs/
  └── messages.txt         # Mensajes registrados
```

## Ventajas de esta versión simplificada

1. **Enfoque único**: Solo hace una cosa y la hace bien
2. **Simplicidad**: Menos código = menos errores
3. **Eficiencia**: Sin funcionalidades innecesarias
4. **Fácil configuración**: Solo necesitas token y servidor ID
5. **Logs claros**: Formato simple y legible

## Consideraciones importantes

⚠️ **Legalidad**: Los self-bots violan los términos de servicio de Discord
⚠️ **Riesgo**: Tu cuenta podría ser suspendida
⚠️ **Uso responsable**: Úsalo solo para propósitos legítimos y con servidores donde tengas permiso
⚠️ **Privacidad**: Respeta la privacidad de otros usuarios

## Solución de problemas

### "Bot no se conecta"
- Verifica que el token sea correcto
- Asegúrate de que no uses tu ID de usuario como token

### "Servidor no encontrado"
- Verifica el ID del servidor
- Asegúrate de estar en ese servidor con tu cuenta

### "No se registran mensajes"
- Verifica que hayas configurado el servidor correcto
- Si configuraste canales específicos, verifica los IDs
