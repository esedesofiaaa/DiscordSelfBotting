"""
Discord Message Listener - Simple Version
Un bot que únicamente escucha y registra todos los mensajes de un servidor o canal específico
"""
import discord
import os
import datetime
from typing import Optional, List
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class SimpleMessageListener:
    """Bot simple para escuchar y registrar mensajes de Discord"""
    
    def __init__(self):
        # Configuración básica
        self.token = os.getenv('DISCORD_TOKEN')
        self.target_server_id = os.getenv('MONITORING_SERVER_ID', '1331752826082295899')
        self.target_channel_ids = self._parse_channel_ids(os.getenv('MONITORING_CHANNEL_IDS', ''))
        self.log_file = os.getenv('LOG_FILE', './logs/messages.txt')
        
        # Cliente de Discord (self-bot)
        self.client = discord.Client()
        
        # Asegurar que el directorio de logs existe
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configurar eventos
        self._setup_events()
    
    def _parse_channel_ids(self, channel_ids_str: str) -> List[str]:
        """Parse comma-separated channel IDs, ignorando comentarios"""
        if not channel_ids_str.strip():
            return []
        
        # Eliminar comentarios (todo después de #)
        clean_str = channel_ids_str.split('#')[0].strip()
        
        if not clean_str:
            return []
            
        return [cid.strip() for cid in clean_str.split(',') if cid.strip()]
    
    def _setup_events(self):
        """Configurar manejadores de eventos de Discord"""
        
        @self.client.event
        async def on_ready():
            if self.client.user:
                print(f"🤖 Bot conectado como: {self.client.user}")
                print(f"🆔 User ID: {self.client.user.id}")
            print(f"📝 Escuchando servidor: {self.target_server_id}")
            
            if self.target_channel_ids:
                print(f"📋 Canales específicos: {', '.join(self.target_channel_ids)}")
            else:
                print("📋 Escuchando TODOS los canales del servidor")
            
            print(f"📁 Guardando mensajes en: {self.log_file}")
            print("-" * 60)
            
            # Verificar si el servidor existe
            target_server = self._get_target_server()
            if target_server:
                print(f"✅ Servidor encontrado: {target_server.name}")
                if hasattr(target_server, 'member_count'):
                    print(f"👥 Miembros: {target_server.member_count}")
            else:
                print(f"❌ ¡Servidor no encontrado! Verifica el ID del servidor.")
            print("-" * 60)
        
        @self.client.event
        async def on_message(message):
            # Registrar todos los mensajes que coincidan con los criterios de monitoreo
            if self._should_monitor_message(message):
                self._log_message(message)
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            print(f"❌ Error en evento {event}: {args}")
    
    def _should_monitor_message(self, message: discord.Message) -> bool:
        """Determinar si el mensaje debe ser registrado"""
        # No registrar mensajes sin guild (DMs) a menos que sea específicamente configurado
        if not message.guild:
            return False
            
        # Verificar si el mensaje es del servidor objetivo
        if str(message.guild.id) != self.target_server_id:
            return False
        
        # Si hay canales específicos configurados, verificar si el mensaje es de uno de ellos
        if self.target_channel_ids:
            return str(message.channel.id) in self.target_channel_ids
        
        # Si no hay canales específicos, monitorear todos los canales del servidor
        return True
    
    def _get_target_server(self) -> Optional[discord.Guild]:
        """Obtener el servidor objetivo para monitoreo"""
        if not self.target_server_id.isdigit():
            return None
        
        return discord.utils.get(self.client.guilds, id=int(self.target_server_id))
    
    def _log_message(self, message: discord.Message):
        """Registrar mensaje en el archivo de texto"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            # Obtener nombre del servidor y canal
            server_name = message.guild.name if message.guild else 'DM'
            
            # Obtener nombre del canal de forma segura
            try:
                channel_name = getattr(message.channel, 'name', 'DM')
            except:
                channel_name = 'DM'
            
            # Obtener nombre del autor (usar el nuevo formato de Discord sin discriminador)
            if hasattr(message.author, 'discriminator') and message.author.discriminator == '0':
                author_name = f"@{message.author.name}"  # Nuevo formato
            else:
                author_name = f"@{message.author.name}"  # Simplificado para self-bot
            
            content = message.content or '[Sin contenido de texto]'
            
            # Información sobre archivos adjuntos
            attachments_info = ""
            if message.attachments:
                attachments_info = f" [Archivos: {len(message.attachments)}]"
            
            # Información sobre embeds
            embeds_info = ""
            if message.embeds:
                embeds_info = f" [Embeds: {len(message.embeds)}]"
            
            # Formato del log (similar al formato actual que tienes)
            log_entry = f"[{timestamp}] {server_name} > #{channel_name} | {author_name}: {content}{attachments_info}{embeds_info}\n"
            log_separator = "-" * 80 + "\n"
            
            # Escribir al archivo
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.write(log_separator)
            
            # Mostrar en consola
            print(f"📝 [{server_name}] #{channel_name} | {author_name}: {content[:50]}{'...' if len(content) > 50 else ''}")
            
        except Exception as e:
            print(f"❌ Error al registrar mensaje: {e}")
    
    def validate_config(self) -> bool:
        """Validar configuración del bot"""
        if not self.token:
            print("❌ Token de Discord no encontrado. Configura DISCORD_TOKEN en el archivo .env")
            return False
        
        if not self.target_server_id:
            print("❌ ID del servidor no configurado. Configura MONITORING_SERVER_ID en el archivo .env")
            return False
        
        return True
    
    def run(self):
        """Iniciar el bot"""
        if not self.validate_config():
            return
        
        print("🚀 Iniciando Discord Message Listener...")
        print("📋 Configuración:")
        print(f"   - Servidor: {self.target_server_id}")
        print(f"   - Canales: {'Específicos' if self.target_channel_ids else 'Todos'}")
        print(f"   - Log file: {self.log_file}")
        print("-" * 60)
        
        try:
            if self.token:
                self.client.run(self.token)
            else:
                print("❌ Token no válido")
        except Exception as error:
            print(f"❌ Error al iniciar el bot: {error}")
            if "Improper token" in str(error):
                print("🔑 Asegúrate de usar un token de Discord válido")


def main():
    """Punto de entrada principal"""
    listener = SimpleMessageListener()
    listener.run()


if __name__ == "__main__":
    main()
