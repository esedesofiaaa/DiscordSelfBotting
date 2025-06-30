import discord
import asyncio
import time
import os
from utils.logger import MessageLogger
import config


# Create bot instance
client = discord.Client()

# Initialize message logger
message_logger = MessageLogger(config.MONITORING['log_file'])


@client.event
async def on_ready():
    """Event fired when bot is ready"""
    print(f"{client.user.name} is ready!")
    print(f"Logged in as: {client.user}")
    print(f"User ID: {client.user.id}")
    
    # Log monitoring status
    if config.MONITORING['enabled']:
        print(f"📝 Message monitoring enabled for server: {config.MONITORING['server_id']}")
        print(f"📁 Log file: {config.MONITORING['log_file']}")
        
        # Check if server exists
        target_server = None
        if config.MONITORING['server_id'].isdigit():
            target_server = discord.utils.get(client.guilds, id=int(config.MONITORING['server_id']))
        if target_server:
            print(f"✅ Target server found: {target_server.name}")
        else:
            print(f"❌ Target server not found! Check server ID in config.")


@client.event
async def on_message(message):
    """Event fired when a message is received"""
    # Monitor messages in target server
    if config.MONITORING['enabled'] and should_monitor_message(message):
        message_logger.log_message(message)
    
    # Ignore messages from other users and bots for commands
    if message.author.id != client.user.id:
        return
    
    # Log messages if enabled
    if config.SETTINGS['log_messages']:
        guild_name = message.guild.name if message.guild else 'DM'
        print(f"[{guild_name}] {message.author}: {message.content}")
    
    # Check if message starts with prefix
    if not message.content.startswith(config.PREFIX):
        return
    
    # Parse command and arguments
    args = message.content[len(config.PREFIX):].strip().split()
    if not args:
        return
    
    command = args[0].lower()
    command_args = args[1:]
    
    # Command handling
    try:
        if command == 'ping':
            await handle_ping_command(message)
        elif command == 'info':
            await handle_info_command(message)
        elif command == 'purge':
            await handle_purge_command(message, command_args)
        elif command == 'help':
            await handle_help_command(message)
        elif command == 'monitor':
            await handle_monitor_command(message, command_args)
        elif command == 'logs':
            await handle_logs_command(message)
        else:
            print(f"Unknown command: {command}")
    except Exception as e:
        print(f"Error executing command {command}: {e}")


def should_monitor_message(message):
    """Determine if message should be monitored"""
    # Check if message is from target server
    if not message.guild or str(message.guild.id) != config.MONITORING['server_id']:
        return False
    
    # Check if specific channels are configured
    if config.MONITORING['channel_ids']:
        return str(message.channel.id) in config.MONITORING['channel_ids']
    
    # Monitor all channels if no specific channels configured
    return True


async def handle_ping_command(message):
    """Handle ping command"""
    try:
        start_time = time.time()
        sent = await message.reply('Pinging...')
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000)
        ws_ping = round(client.latency * 1000)
        
        await sent.edit(content=f"🏓 Pong! Latency: {latency}ms | API: {ws_ping}ms")
    except Exception as error:
        print(f"Error in ping command: {error}")


async def handle_info_command(message):
    """Handle info command"""
    try:
        uptime = time.time() - client.start_time if hasattr(client, 'start_time') else 0
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        guild_count = len(client.guilds)
        user_count = len(client.users)
        
        info = f"""**Self-Bot Info**
📊 Uptime: {hours}h {minutes}m {seconds}s
🌐 Guilds: {guild_count}
👥 Users: {user_count}
📝 Prefix: {config.PREFIX}"""
        
        await message.reply(info)
    except Exception as error:
        print(f"Error in info command: {error}")


async def handle_purge_command(message, args):
    """Handle purge command"""
    try:
        if not args or not args[0].isdigit():
            await message.reply('Please provide a number between 1 and 100')
            return
        
        amount = int(args[0])
        if amount < 1 or amount > 100:
            await message.reply('Please provide a number between 1 and 100')
            return
        
        # Get messages from the channel
        messages = []
        async for msg in message.channel.history(limit=amount + 1):
            if msg.author.id == client.user.id:
                messages.append(msg)
        
        deleted = 0
        for msg in messages:
            try:
                await msg.delete()
                deleted += 1
                await asyncio.sleep(1)  # Rate limit protection
            except Exception as err:
                print(f"Failed to delete message: {err}")
        
        print(f"Deleted {deleted} messages")
    except Exception as error:
        print(f"Error in purge command: {error}")


async def handle_monitor_command(message, args):
    """Handle monitor command"""
    try:
        if not args:
            await message.reply(f"Usage: {config.PREFIX}monitor <start|stop|status>")
            return
        
        subcommand = args[0].lower()
        
        if subcommand == 'start':
            config.MONITORING['enabled'] = True
            await message.reply('✅ Message monitoring started')
        elif subcommand == 'stop':
            config.MONITORING['enabled'] = False
            await message.reply('⏹️ Message monitoring stopped')
        elif subcommand == 'status':
            target_server = None
            if config.MONITORING['server_id'].isdigit():
                target_server = discord.utils.get(client.guilds, id=int(config.MONITORING['server_id']))
            server_name = target_server.name if target_server else 'Server not found'
            
            channels_text = 'All channels' if not config.MONITORING['channel_ids'] else f"{len(config.MONITORING['channel_ids'])} specific channels"
            
            status = f"""**Monitoring Status:**
🔧 Enabled: {'Yes' if config.MONITORING['enabled'] else 'No'}
🏠 Server: {server_name}
📁 Log file: {config.MONITORING['log_file']}
📊 Channels: {channels_text}"""
            
            await message.reply(status)
        else:
            await message.reply(f"Usage: {config.PREFIX}monitor <start|stop|status>")
    except Exception as error:
        print(f"Error in monitor command: {error}")
        await message.reply('❌ Error executing monitor command')


async def handle_logs_command(message):
    """Handle logs command"""
    try:
        stats = message_logger.get_log_stats()
        
        if not stats['exists']:
            await message.reply('📝 No log file found. Start monitoring to create logs.')
            return
        
        size_kb = stats['size'] / 1024
        last_modified = stats.get('last_modified', 'Unknown')
        last_modified_str = last_modified.strftime('%Y-%m-%d %H:%M:%S') if last_modified != 'Unknown' else 'Unknown'
        
        log_info = f"""**Log File Statistics:**
📁 File: {config.MONITORING['log_file']}
📊 Size: {size_kb:.2f} KB
📝 Lines: {stats['lines']}
🕒 Last modified: {last_modified_str}"""
        
        await message.reply(log_info)
    except Exception as error:
        print(f"Error in logs command: {error}")
        await message.reply('❌ Error getting log information')


async def handle_help_command(message):
    """Handle help command"""
    try:
        help_text = f"""**Available Commands:**
{config.PREFIX}ping - Check bot latency
{config.PREFIX}info - Show bot information
{config.PREFIX}purge <amount> - Delete your messages
{config.PREFIX}monitor <start|stop|status> - Control message monitoring
{config.PREFIX}logs - Show log file statistics
{config.PREFIX}help - Show this help message"""
        
        await message.reply(help_text)
    except Exception as error:
        print(f"Error in help command: {error}")


@client.event
async def on_error(event, *args, **kwargs):
    """Handle errors"""
    print(f"Error in event {event}: {args}")


def main():
    """Main function"""
    if not config.TOKEN:
        print("❌ No Discord token found! Please set DISCORD_TOKEN in your .env file")
        return
    
    if config.TOKEN == "1384570203022692392":
        print("❌ Invalid token! You're using your user ID instead of your Discord token.")
        print("🔑 Please get your real Discord token and update the .env file")
        return
    
    # Set start time for uptime calculation
    client.start_time = time.time()
    
    # Run the bot
    try:
        client.run(config.TOKEN)
    except Exception as error:
        print(f"❌ Error starting bot: {error}")
        if "Improper token" in str(error):
            print("🔑 Make sure you're using a valid Discord token, not your user ID")


if __name__ == "__main__":
    main()
