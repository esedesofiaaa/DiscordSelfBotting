#!/usr/bin/env python3
"""
Monitor del Bot de Discord - Sistema de Monitoreo Independiente
Este script puede ejecutarse independientemente para monitorear el estado del bot
y enviar heartbeats adicionales a Healthchecks.io
"""
import asyncio
import psutil
import sys
import os
import signal
import time
from pathlib import Path
from datetime import datetime, timedelta
from heartbeat_system import HeartbeatSystem
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class BotMonitor:
    """Monitor independiente para el bot de Discord"""
    
    def __init__(self):
        # Configuración
        self.heartbeat_url = os.getenv('HEALTHCHECKS_PING_URL', 'https://hc-ping.com/f679a27c-8a41-4ae2-9504-78f1b260e71d')
        self.monitor_interval = int(os.getenv('MONITOR_INTERVAL', '120'))  # 2 minutos por defecto
        self.bot_process_name = os.getenv('BOT_PROCESS_NAME', 'simple_message_listener.py')
        self.log_file = os.getenv('LOG_FILE', './logs/messages.txt')
        
        # Sistema de heartbeats
        self.heartbeat = HeartbeatSystem(self.heartbeat_url, interval=self.monitor_interval)
        
        # Estado del monitor
        self.is_running = False
        self.start_time = None
        self.last_bot_check = None
        self.bot_restart_count = 0
        
        print(f"🔍 Monitor del Bot inicializado")
        print(f"   - Proceso a monitorear: {self.bot_process_name}")
        print(f"   - Intervalo de monitoreo: {self.monitor_interval}s")
        print(f"   - URL de heartbeats: {self.heartbeat_url[:50]}...")
    
    def find_bot_process(self) -> list:
        """Buscar procesos del bot en ejecución"""
        bot_processes = []
        
        for process in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(process.info['cmdline']) if process.info['cmdline'] else ''
                
                # Buscar procesos que contengan el nombre del script del bot
                if self.bot_process_name in cmdline:
                    bot_processes.append({
                        'pid': process.info['pid'],
                        'name': process.info['name'],
                        'cmdline': cmdline,
                        'create_time': datetime.fromtimestamp(process.info['create_time'])
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return bot_processes
    
    def check_log_activity(self) -> dict:
        """Verificar actividad reciente en el archivo de log"""
        log_path = Path(self.log_file)
        
        if not log_path.exists():
            return {
                'exists': False,
                'last_modified': None,
                'is_recent': False,
                'size': 0
            }
        
        try:
            stat = log_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            is_recent = (datetime.now() - last_modified) < timedelta(minutes=10)
            
            return {
                'exists': True,
                'last_modified': last_modified,
                'is_recent': is_recent,
                'size': stat.st_size
            }
        except Exception as e:
            print(f"❌ Error al verificar log: {e}")
            return {
                'exists': True,
                'last_modified': None,
                'is_recent': False,
                'size': 0,
                'error': str(e)
            }
    
    async def check_bot_status(self) -> dict:
        """Verificar estado completo del bot"""
        self.last_bot_check = datetime.now()
        
        # Buscar procesos del bot
        bot_processes = self.find_bot_process()
        
        # Verificar actividad del log
        log_status = self.check_log_activity()
        
        # Determinar estado general
        is_healthy = len(bot_processes) > 0 and log_status.get('is_recent', False)
        
        status = {
            'timestamp': self.last_bot_check.isoformat(),
            'is_healthy': is_healthy,
            'processes': bot_processes,
            'log_status': log_status,
            'process_count': len(bot_processes),
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None
        }
        
        return status
    
    async def restart_bot_if_needed(self, status: dict) -> bool:
        """Reiniciar el bot si es necesario"""
        if status['is_healthy']:
            return False
        
        print("⚠️ Bot no está funcionando correctamente, intentando reiniciar...")
        
        # Intentar terminar procesos existentes
        for process_info in status['processes']:
            try:
                process = psutil.Process(process_info['pid'])
                print(f"🔄 Terminando proceso {process_info['pid']}")
                process.terminate()
                
                # Esperar a que termine
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    print(f"💀 Forzando terminación del proceso {process_info['pid']}")
                    process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Esperar un momento
        await asyncio.sleep(5)
        
        # Intentar reiniciar el bot
        try:
            # Buscar el script start_bot.sh
            start_script = Path('./start_bot.sh')
            
            if start_script.exists():
                print("🚀 Reiniciando bot con start_bot.sh")
                process = await asyncio.create_subprocess_exec(
                    'bash', str(start_script),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                self.bot_restart_count += 1
                print(f"✅ Bot reiniciado (intento #{self.bot_restart_count})")
                return True
            else:
                print("❌ Script de inicio no encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Error al reiniciar bot: {e}")
            return False
    
    async def monitor_loop(self):
        """Loop principal de monitoreo"""
        self.is_running = True
        self.start_time = datetime.now()
        
        print(f"🚀 Iniciando monitoreo del bot...")
        
        # Enviar ping inicial
        await self.heartbeat.send_ping("start", "Monitor del bot iniciado")
        
        while self.is_running:
            try:
                # Verificar estado del bot
                status = await self.check_bot_status()
                
                # Crear mensaje de estado
                status_msg = f"Procesos: {status['process_count']}, "
                status_msg += f"Log reciente: {'Sí' if status['log_status']['is_recent'] else 'No'}, "
                status_msg += f"Reinicios: {self.bot_restart_count}"
                
                if status['is_healthy']:
                    print(f"✅ Bot funcionando correctamente - {status_msg}")
                    await self.heartbeat.send_ping("success", status_msg)
                else:
                    print(f"❌ Bot con problemas - {status_msg}")
                    
                    # Intentar reiniciar si está configurado
                    restart_enabled = os.getenv('AUTO_RESTART_BOT', 'true').lower() == 'true'
                    if restart_enabled:
                        restarted = await self.restart_bot_if_needed(status)
                        if restarted:
                            status_msg += ", Auto-reiniciado"
                    
                    await self.heartbeat.send_ping("fail", status_msg)
                
                # Esperar hasta el próximo chequeo
                await asyncio.sleep(self.monitor_interval)
                
            except asyncio.CancelledError:
                print("⏹️ Monitor cancelado")
                break
            except Exception as e:
                print(f"❌ Error en loop de monitoreo: {e}")
                await self.heartbeat.send_ping("fail", f"Error en monitor: {str(e)[:100]}")
                await asyncio.sleep(30)  # Esperar antes de reintentar
    
    async def start(self):
        """Iniciar el monitor"""
        print("🔍 Iniciando sistema de monitoreo...")
        await self.monitor_loop()
    
    async def stop(self):
        """Detener el monitor"""
        self.is_running = False
        await self.heartbeat.send_ping("fail", f"Monitor detenido - Reinicios realizados: {self.bot_restart_count}")
        print("⏹️ Monitor detenido")


async def main():
    """Función principal"""
    monitor = BotMonitor()
    
    # Manejar señales para parada limpia
    def signal_handler(signum, frame):
        print(f"\n📡 Señal {signum} recibida, deteniendo monitor...")
        asyncio.create_task(monitor.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
