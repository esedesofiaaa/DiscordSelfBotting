"""
Discord Message Listener - Simple Version con integración a Notion
Un bot que únicamente escucha y registra todos los mensajes de un servidor o canal específico
Guarda la información directamente en una base de datos de Notion
Incluye sistema de monitoreo de heartbeats con Healthchecks.io
"""
import discord
import os
import datetime
import asyncio
from typing import Optional, List
from dotenv import load_dotenv
from notion_client import Client
from heartbeat_system import HeartbeatSystem

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
        
        # Configuración de Notion
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.notion_client = None
        
        # Configuración de Heartbeats
        self.heartbeat_url = os.getenv('HEALTHCHECKS_PING_URL', 'https://hc-ping.com/f679a27c-8a41-4ae2-9504-78f1b260e71d')
        self.heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', '300'))  # 5 minutos por defecto
        self.heartbeat_system = None
        
        # Inicializar sistema de heartbeats
        if self.heartbeat_url:
            self.heartbeat_system = HeartbeatSystem(self.heartbeat_url, self.heartbeat_interval)
            print(f"✅ Sistema de heartbeats configurado (intervalo: {self.heartbeat_interval}s)")
        
        # Inicializar Notion si está configurado
        if self.notion_token and self.notion_database_id:
            try:
                self.notion_client = Client(auth=self.notion_token)
                print("✅ Cliente de Notion inicializado correctamente")
            except Exception as e:
                print(f"❌ Error al inicializar Notion: {e}")
                self.notion_client = None
        
        # Cliente de Discord (self-bot)
        self.client = discord.Client()
        
        # Asegurar que el directorio de logs existe (backup)
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
            
            # Iniciar sistema de heartbeats
            if self.heartbeat_system:
                print("💓 Iniciando sistema de heartbeats...")
                # Crear tarea para el sistema de heartbeats
                asyncio.create_task(self.heartbeat_system.start_heartbeat())
            
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
            
            # Enviar ping de error al sistema de heartbeats
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("fail", f"Error en evento {event}: {str(args)[:100]}")
        
        @self.client.event
        async def on_disconnect():
            print("🔌 Bot desconectado")
            
            # Enviar ping de desconexión
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("fail", "Bot desconectado de Discord")
        
        @self.client.event
        async def on_resumed():
            print("🔄 Conexión reanudada")
            
            # Enviar ping de reconexión
            if self.heartbeat_system:
                await self.heartbeat_system.send_ping("success", "Conexión reanudada exitosamente")
    
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
    
    def _find_message_in_notion(self, message_id: str) -> Optional[str]:
        """
        Buscar un mensaje en Notion por su ID y retornar la URL de la página de Notion
        """
        if not self.notion_client or not self.notion_database_id:
            return None
        
        try:
            # Buscar en la base de datos de Notion usando el ID del mensaje
            query_filter = {
                "property": "Message ID",
                "title": {
                    "equals": message_id
                }
            }
            
            print(f"🔍 Buscando mensaje en Notion: {message_id}")
            
            # Realizar la consulta - notion-client 2.2.1 es síncrono
            response = self.notion_client.databases.query(
                database_id=self.notion_database_id,
                filter=query_filter
            )
            
            # Acceder a los resultados usando indexación directa
            # Ignorar advertencias del linter - notion-client 2.2.1 devuelve un dict
            results = response['results']  # type: ignore
            
            if results and len(results) > 0:
                page_id = results[0]['id']
                # Generar la URL de la página de Notion
                page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
                print(f"✅ Mensaje encontrado en Notion: {page_url}")
                return page_url
            else:
                print(f"❌ Mensaje no encontrado en Notion: {message_id}")
                return None
            
        except Exception as e:
            print(f"❌ Error al buscar mensaje en Notion: {e}")
            return None
    
    def _save_message_to_notion(self, message: discord.Message):
        """Guardar mensaje en la base de datos de Notion con soporte para respuestas"""
        if not self.notion_client or not self.notion_database_id:
            return False
        
        try:
            # Obtener información del mensaje
            server_name = message.guild.name if message.guild else 'DM'
            
            try:
                channel_name = getattr(message.channel, 'name', 'DM')
            except:
                channel_name = 'DM'
            
            # Obtener nombre del autor
            if hasattr(message.author, 'discriminator') and message.author.discriminator == '0':
                author_name = f"@{message.author.name}"
            else:
                author_name = f"@{message.author.name}"
            
            content = message.content or '[Sin contenido de texto]'
            
            # ID del mensaje de Discord
            message_id = str(message.id)
            
            # Verificar si hay archivos adjuntos
            has_attachment = len(message.attachments) > 0
            
            # Preparar archivos adjuntos para Notion (solo URLs de los archivos)
            attachment_files = []
            if has_attachment:
                for attachment in message.attachments:
                    # Notion espera objetos de archivo con nombre y URL externa
                    attachment_files.append({
                        "name": attachment.filename,
                        "external": {
                            "url": attachment.url
                        }
                    })
            
            # Verificar si hay URLs en el contenido
            import re
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)
            has_url = len(urls) > 0
            url_adjunta = urls[0] if urls else ""
            
            # URL del mensaje original
            message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else ""
            
            # Fecha en formato ISO
            fecha_mensaje = message.created_at.isoformat()
            
            # Verificar si es una respuesta a otro mensaje
            replied_message_notion_url = None
            if message.reference and message.reference.message_id:
                replied_message_id = str(message.reference.message_id)
                replied_message_notion_url = self._find_message_in_notion(replied_message_id)
                
                if replied_message_notion_url:
                    print(f"🔗 Mensaje es respuesta a: {replied_message_id}")
                else:
                    print(f"⚠️  Mensaje original no encontrado en Notion: {replied_message_id}")
            
            # Crear el objeto de página para Notion
            notion_page = {
                "parent": {"database_id": self.notion_database_id},
                "properties": {
                    "Message ID": {
                        "title": [
                            {
                                "text": {
                                    "content": message_id
                                }
                            }
                        ]
                    },
                    "Autor": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": author_name
                                }
                            }
                        ]
                    },
                    "Fecha": {
                        "date": {
                            "start": fecha_mensaje
                        }
                    },
                    "Servidor": {
                        "select": {
                            "name": server_name
                        }
                    },
                    "Canal": {
                        "select": {
                            "name": channel_name
                        }
                    },
                    "Contenido": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": content[:2000]  # Notion tiene límite de caracteres
                                }
                            }
                        ]
                    },
                    "URL adjunta": {
                        "url": url_adjunta if has_url else None
                    },
                    "URL del mensaje": {
                        "url": message_url if message_url else None
                    }
                }
            }
            
            # Añadir archivos adjuntos solo si existen
            if attachment_files:
                notion_page["properties"]["Archivo Adjunto"] = {
                    "files": attachment_files
                }
            
            # Añadir URL del mensaje original si es una respuesta
            if replied_message_notion_url:
                notion_page["properties"]["Original Message"] = {
                    "url": replied_message_notion_url
                }
            
            # Crear la página en Notion
            response = self.notion_client.pages.create(**notion_page)
            
            reply_info = " (respuesta)" if replied_message_notion_url else ""
            print(f"✅ Mensaje guardado en Notion: {author_name} en #{channel_name}{reply_info}")
            return True
                
        except Exception as e:
            print(f"❌ Error al guardar mensaje en Notion: {e}")
            return False
    
    def _log_message(self, message: discord.Message):
        """Registrar mensaje en Notion y como backup en archivo de texto"""
        try:
            # Intentar guardar en Notion primero
            notion_success = False
            if self.notion_client:
                notion_success = self._save_message_to_notion(message)
            
            # Si Notion falla o no está configurado, usar archivo de texto como backup
            if not notion_success:
                self._log_message_to_file(message)
                
        except Exception as e:
            print(f"❌ Error al registrar mensaje: {e}")
            # Como último recurso, intentar guardar en archivo
            try:
                self._log_message_to_file(message)
            except:
                print(f"❌ Error crítico: No se pudo guardar el mensaje de ninguna manera")
    
    def _log_message_to_file(self, message: discord.Message):
        """Registrar mensaje en el archivo de texto (método de backup)"""
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
            print(f"📝 [BACKUP FILE] [{server_name}] #{channel_name} | {author_name}: {content[:50]}{'...' if len(content) > 50 else ''}")
            
        except Exception as e:
            print(f"❌ Error al registrar mensaje en archivo: {e}")
    
    def validate_config(self) -> bool:
        """Validar configuración del bot"""
        if not self.token:
            print("❌ Token de Discord no encontrado. Configura DISCORD_TOKEN en el archivo .env")
            return False
        
        if not self.target_server_id:
            print("❌ ID del servidor no configurado. Configura MONITORING_SERVER_ID en el archivo .env")
            return False
        
        # Validar configuración de Notion (opcional pero recomendada)
        if not self.notion_token or not self.notion_database_id:
            print("⚠️  Configuración de Notion no encontrada. Los mensajes se guardarán solo en archivo de texto.")
            print("   Para usar Notion, configura NOTION_TOKEN y NOTION_DATABASE_ID en el archivo .env")
        else:
            print("✅ Configuración de Notion encontrada. Los mensajes se guardarán en Notion.")
        
        # Validar configuración de heartbeats
        if not self.heartbeat_url:
            print("⚠️  URL de heartbeats no configurada. Configura HEALTHCHECKS_PING_URL en el archivo .env")
        else:
            print(f"✅ Sistema de heartbeats configurado: {self.heartbeat_url[:50]}...")
        
        return True
    
    def run(self):
        """Iniciar el bot"""
        if not self.validate_config():
            return
        
        print("🚀 Iniciando Discord Message Listener...")
        print("📋 Configuración:")
        print(f"   - Servidor: {self.target_server_id}")
        print(f"   - Canales: {'Específicos' if self.target_channel_ids else 'Todos'}")
        print(f"   - Notion: {'✅ Configurado' if self.notion_client else '❌ No configurado'}")
        print(f"   - Heartbeats: {'✅ Configurado' if self.heartbeat_system else '❌ No configurado'}")
        print(f"   - Backup file: {self.log_file}")
        print("-" * 60)
        
        try:
            if self.token:
                self.client.run(self.token)
            else:
                print("❌ Token no válido")
        except KeyboardInterrupt:
            print("\n⏹️ Deteniendo bot...")
            # Detener sistema de heartbeats
            if self.heartbeat_system:
                asyncio.run(self.heartbeat_system.stop_heartbeat())
        except Exception as error:
            print(f"❌ Error al iniciar el bot: {error}")
            if "Improper token" in str(error):
                print("🔑 Asegúrate de usar un token de Discord válido")
            
            # Enviar ping de error crítico
            if self.heartbeat_system:
                asyncio.run(self.heartbeat_system.send_ping("fail", f"Error crítico: {str(error)[:100]}"))
    
    async def get_heartbeat_status(self) -> dict:
        """Obtener estado del sistema de heartbeats"""
        if not self.heartbeat_system:
            return {"status": "not_configured"}
        
        return self.heartbeat_system.get_status()
    
    async def send_manual_heartbeat(self, message: str = "Ping manual desde bot"):
        """Enviar heartbeat manual"""
        if not self.heartbeat_system:
            return False
        
        return await self.heartbeat_system.send_manual_ping(message)


def main():
    """Punto de entrada principal"""
    listener = SimpleMessageListener()
    listener.run()


if __name__ == "__main__":
    main()
