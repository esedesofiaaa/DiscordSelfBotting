"""
Sistema de monitoreo de latidos (heartbeats) para Discord Bot
Integrado con Healthchecks.io para alertas automáticas
"""
import asyncio
import aiohttp
import logging
import time
from typing import Optional
from datetime import datetime


class HeartbeatSystem:
    """Sistema de monitoreo de latidos para el bot de Discord"""
    
    def __init__(self, ping_url: str, interval: int = 60):
        """
        Inicializar el sistema de heartbeats
        
        Args:
            ping_url: URL completa de ping de Healthchecks.io
            interval: Intervalo en segundos entre pings (default: 60)
        """
        self.ping_url = ping_url
        self.interval = interval
        self.is_running = False
        self.last_ping_time = None
        self.ping_count = 0
        self.failed_pings = 0
        
        # Configurar logging
        self.logger = logging.getLogger('heartbeat')
        self.logger.setLevel(logging.INFO)
        
        # Crear handler para consola si no existe
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    async def send_ping(self, status: str = "success", message: Optional[str] = None):
        """
        Enviar ping a Healthchecks.io
        
        Args:
            status: Estado del ping ("success", "fail", "start")
            message: Mensaje opcional para incluir en el ping
        """
        try:
            url = self.ping_url
            
            # Añadir status al URL si no es success
            if status != "success":
                url += f"/{status}"
            
            # Preparar datos para el ping
            data = None
            if message:
                data = message.encode('utf-8')
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        self.ping_count += 1
                        self.last_ping_time = datetime.now()
                        self.logger.info(f"✅ Ping enviado exitosamente ({status}) - Total: {self.ping_count}")
                        return True
                    else:
                        self.failed_pings += 1
                        self.logger.warning(f"⚠️ Ping falló con código {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            self.failed_pings += 1
            self.logger.error("❌ Timeout al enviar ping - red lenta o inaccesible")
            return False
        except Exception as e:
            self.failed_pings += 1
            self.logger.error(f"❌ Error al enviar ping: {e}")
            return False
    
    async def start_heartbeat(self):
        """Iniciar el sistema de heartbeats"""
        if self.is_running:
            self.logger.warning("El sistema de heartbeats ya está en ejecución")
            return
        
        self.is_running = True
        self.logger.info(f"🚀 Iniciando sistema de heartbeats (intervalo: {self.interval}s)")
        
        # Enviar ping de inicio
        await self.send_ping("start", "Bot iniciado - Sistema de heartbeats activado")
        
        # Loop principal de heartbeats
        while self.is_running:
            try:
                await asyncio.sleep(self.interval)
                
                if self.is_running:  # Verificar si aún debe estar corriendo
                    # Crear mensaje de estado
                    uptime = time.time() - (self.last_ping_time.timestamp() if self.last_ping_time else time.time())
                    status_msg = f"Bot funcionando - Pings: {self.ping_count}, Fallos: {self.failed_pings}"
                    
                    await self.send_ping("success", status_msg)
                    
            except asyncio.CancelledError:
                self.logger.info("⏹️ Heartbeat cancelado")
                break
            except Exception as e:
                self.logger.error(f"❌ Error en loop de heartbeat: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar
    
    async def stop_heartbeat(self):
        """Detener el sistema de heartbeats"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("⏹️ Deteniendo sistema de heartbeats")
        
        # Enviar ping de parada
        final_msg = f"Bot detenido - Total pings: {self.ping_count}, Fallos: {self.failed_pings}"
        await self.send_ping("fail", final_msg)
    
    def get_status(self) -> dict:
        """Obtener estado actual del sistema de heartbeats"""
        return {
            "is_running": self.is_running,
            "ping_count": self.ping_count,
            "failed_pings": self.failed_pings,
            "last_ping_time": self.last_ping_time.isoformat() if self.last_ping_time else None,
            "ping_url": self.ping_url[:50] + "..." if len(self.ping_url) > 50 else self.ping_url,
            "interval": self.interval
        }
    
    async def send_manual_ping(self, message: str = "Ping manual"):
        """Enviar un ping manual (útil para testing)"""
        self.logger.info(f"📤 Enviando ping manual: {message}")
        return await self.send_ping("success", message)


# Función utilitaria para testing
async def test_heartbeat_system():
    """Función de prueba para el sistema de heartbeats"""
    # URL de ejemplo - reemplazar con la URL real
    ping_url = "https://hc-ping.com/f679a27c-8a41-4ae2-9504-78f1b260e71d"
    
    # Crear sistema con intervalo corto para testing
    heartbeat = HeartbeatSystem(ping_url, interval=10)
    
    print("🧪 Probando sistema de heartbeats...")
    
    # Probar ping manual
    await heartbeat.send_manual_ping("Prueba del sistema de heartbeats")
    
    # Mostrar estado
    status = heartbeat.get_status()
    print(f"📊 Estado: {status}")
    
    print("✅ Prueba completada")


if __name__ == "__main__":
    # Ejecutar prueba
    asyncio.run(test_heartbeat_system())
