# Sistema de Monitoreo de Heartbeats para Discord Bot

Este sistema implementa un monitoreo robusto de "latidos" (heartbeats) para el bot de Discord, utilizando [Healthchecks.io](https://healthchecks.io) para recibir alertas automáticas si el bot se cae.

## 🔧 Configuración

### 1. Configurar Healthchecks.io

1. **Crear cuenta**: Ve a [healthchecks.io](https://healthchecks.io) y crea una cuenta
2. **Crear check**: Crea un nuevo check con las siguientes configuraciones:
   - **Name**: Discord Bot - Message Listener
   - **Tags**: discord, bot, production
   - **Period**: 10 minutes (600 seconds)
   - **Grace**: 5 minutes (300 seconds)
3. **Copiar URL**: Copia la URL de ping (ejemplo: `https://hc-ping.com/f679a27c-8a41-4ae2-9504-78f1b260e71d`)

### 2. Configurar Variables de Entorno

Añade las siguientes variables a tu archivo `.env`:

```bash
# URL de ping de Healthchecks.io
HEALTHCHECKS_PING_URL=https://hc-ping.com/tu-uuid-aqui

# Intervalo de heartbeats en segundos (default: 300 = 5 minutos)
HEARTBEAT_INTERVAL=300

# Intervalo de monitoreo del bot en segundos (default: 120 = 2 minutos)
MONITOR_INTERVAL=120

# Auto-reiniciar el bot si se detecta que no está funcionando
AUTO_RESTART_BOT=true
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las nuevas dependencias incluyen:
- `aiohttp`: Para envío asíncrono de pings
- `psutil`: Para monitoreo de procesos

## 🚀 Uso

### Modo Integrado (Recomendado)

El sistema de heartbeats está integrado directamente en el bot principal:

```bash
# Iniciar el bot con heartbeats automáticos
./start_simple_listener.sh
```

### Modo Monitor Independiente

Para un monitoreo más robusto, puedes usar el monitor independiente:

```bash
# Iniciar el monitor
./start_monitor.sh start

# Ver estado del monitor
./start_monitor.sh status

# Ver logs del monitor
./start_monitor.sh logs

# Detener el monitor
./start_monitor.sh stop

# Reiniciar el monitor
./start_monitor.sh restart

# Probar conexión con Healthchecks.io
./start_monitor.sh test
```

## 📊 Funcionalidades

### Sistema de Heartbeats Integrado

- **Ping automático**: Envía pings regulares a Healthchecks.io
- **Estado de conexión**: Reporta reconexiones y desconexiones
- **Manejo de errores**: Envía pings de error cuando ocurren problemas
- **Graceful shutdown**: Envía ping final al detener el bot

### Monitor Independiente

- **Monitoreo de procesos**: Verifica que el bot esté corriendo
- **Monitoreo de logs**: Verifica actividad reciente en los logs
- **Auto-reinicio**: Reinicia automáticamente el bot si se cae
- **Reportes detallados**: Incluye información de estado en los pings

## 🔔 Tipos de Pings

### Pings de Estado

- **`start`**: Bot/monitor iniciado
- **`success`**: Funcionando correctamente
- **`fail`**: Error o bot caído

### Información Incluida

Cada ping incluye información relevante:
- Número de pings enviados
- Número de fallos
- Estado de procesos
- Actividad reciente en logs
- Número de reinicios automáticos

## 📈 Monitoreo y Alertas

### Healthchecks.io

- **Email**: Alertas por email cuando el bot se cae
- **SMS**: Alertas por SMS (planes pagos)
- **Slack/Discord**: Webhooks para canales de equipo
- **Dashboard**: Panel web para ver estado e historial

### Logs Locales

Los logs se guardan en:
- `logs/messages.txt`: Mensajes del bot
- `logs/monitor.log`: Logs del monitor independiente

## 🛠️ Comandos Útiles

```bash
# Ver estado del bot
ps aux | grep simple_message_listener.py

# Ver logs en tiempo real
tail -f logs/monitor.log

# Probar heartbeat manualmente
python3 -c "
import asyncio
from heartbeat_system import HeartbeatSystem
heartbeat = HeartbeatSystem('tu-url-aqui')
asyncio.run(heartbeat.send_manual_ping('Test manual'))
"

# Verificar última modificación del log
ls -la logs/messages.txt
```

## 🔧 Configuración Avanzada

### Personalizar Intervalos

```bash
# Heartbeats cada 2 minutos
HEARTBEAT_INTERVAL=120

# Monitoreo cada 30 segundos
MONITOR_INTERVAL=30
```

### Configurar Alertas

En Healthchecks.io puedes configurar:
- **Channels**: Email, SMS, Slack, Discord, etc.
- **Schedules**: Diferentes alertas para diferentes horarios
- **Escalation**: Alertas escalonadas si el problema persiste

## 📋 Troubleshooting

### Bot no envía pings

1. Verificar URL de Healthchecks.io
2. Verificar conexión a internet
3. Revisar logs para errores

### Monitor no reinicia el bot

1. Verificar permisos del script `start_simple_listener.sh`
2. Verificar que `AUTO_RESTART_BOT=true`
3. Revisar logs del monitor

### Alertas falsas

1. Ajustar `HEARTBEAT_INTERVAL` y `MONITOR_INTERVAL`
2. Aumentar el "Grace period" en Healthchecks.io
3. Verificar estabilidad de la conexión

## 🚨 Ejemplo de Configuración de Producción

```bash
# .env para producción
HEALTHCHECKS_PING_URL=https://hc-ping.com/tu-uuid-aqui
HEARTBEAT_INTERVAL=300        # 5 minutos
MONITOR_INTERVAL=120          # 2 minutos
AUTO_RESTART_BOT=true
```

```bash
# Iniciar ambos sistemas
./start_simple_listener.sh    # Bot principal
./start_monitor.sh start      # Monitor independiente
```

Esta configuración dual proporciona:
- **Redundancia**: Si el bot falla, el monitor lo detecta
- **Auto-recuperación**: Reinicio automático del bot
- **Monitoreo continuo**: Alertas inmediatas si algo falla
- **Visibilidad**: Logs detallados de todo el sistema

## 💡 Consejos

1. **Usa el monitor independiente** para mayor robustez
2. **Configura múltiples canales** de alerta en Healthchecks.io
3. **Revisa los logs regularmente** para detectar patrones
4. **Ajusta los intervalos** según tu caso de uso
5. **Prueba el sistema** regularmente con `./start_monitor.sh test`
