# Discord Self Bot - Deployment Guide

## 🚀 Automated Deployment to Linode

Este proyecto incluye un workflow de GitHub Actions para deployment automático a un servidor Linode.

### 📋 Requisitos Previos

1. **Servidor Linode** con Ubuntu/Debian
2. **Usuario con acceso SSH** al servidor
3. **Repositorio en GitHub** con los secrets configurados

### 🔧 Configuración del Servidor

#### Opción A: Setup Completo (Servidor Nuevo)
```bash
# En tu servidor Linode, ejecuta:
wget https://raw.githubusercontent.com/esedesofiaaa/DiscordSelfBotting/main/setup-linode.sh
chmod +x setup-linode.sh
sudo ./setup-linode.sh
```

#### Opción B: Solo Configurar Sudo (Servidor Existente)
```bash
# Si ya tienes el entorno configurado, solo ejecuta:
wget https://raw.githubusercontent.com/esedesofiaaa/DiscordSelfBotting/main/configure-sudo.sh
chmod +x configure-sudo.sh
sudo ./configure-sudo.sh
```

### 🔑 Secrets de GitHub

Configura estos secrets en tu repositorio de GitHub (`Settings` → `Secrets and variables` → `Actions`):

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `SSH_PRIVATE_KEY` | Tu clave privada SSH (completa) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `LINODE_HOST` | IP de tu servidor Linode | `192.168.1.100` |
| `LINODE_USERNAME` | Usuario para conectarse | `discord-bot` |

#### Generar Claves SSH (si no las tienes):
```bash
# En tu máquina local:
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Copiar la clave pública al servidor:
ssh-copy-id discord-bot@YOUR_LINODE_IP

# El contenido de ~/.ssh/id_rsa va en SSH_PRIVATE_KEY
cat ~/.ssh/id_rsa
```

### 🛠️ Configuración Manual en el Servidor

Si prefieres configurar manualmente:

```bash
# 1. Crear usuario discord-bot
sudo useradd -m -s /bin/bash discord-bot

# 2. Crear directorio del proyecto
sudo mkdir -p /opt/discord-bot
sudo chown discord-bot:discord-bot /opt/discord-bot

# 3. Configurar como usuario discord-bot
sudo -u discord-bot bash
cd /opt/discord-bot

# 4. Clonar el repositorio
git clone https://github.com/esedesofiaaa/DiscordSelfBotting.git .

# 5. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Crear directorio de logs
mkdir -p logs

# 7. Configurar systemd (como root)
exit
sudo cp /opt/discord-bot/discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-bot

# 8. Configurar sudo sin contraseña
sudo /opt/discord-bot/configure-sudo.sh
```

### 🎯 Deployment Automático

El deployment se ejecuta automáticamente cuando:
- Haces push a la rama `main`
- Ejecutas manualmente el workflow desde GitHub Actions

#### Proceso de Deployment:
1. ✅ **Checkout del código**
2. 🔐 **Configuración SSH**
3. 🧪 **Test de conexión**
4. 🚀 **Deployment**:
   - Para el servicio
   - Actualiza/clona el repositorio
   - Instala dependencias
   - Inicia el servicio
   - Verifica el estado
5. ✅ **Verificación final**

### 🐛 Troubleshooting

#### Error: "sudo: a terminal is required to read the password"
**Solución**: Ejecuta `configure-sudo.sh` en tu servidor para configurar sudo sin contraseña.

#### Error: "fatal: not a git repository"
**Solución**: El workflow ahora maneja automáticamente este caso clonando el repositorio si no existe.

#### Error: "Failed to activate virtual environment"
**Solución**: Asegúrate de que el entorno virtual esté creado:
```bash
sudo -u discord-bot bash -c "cd /opt/discord-bot && python3 -m venv venv"
```

#### Verificar el estado del servicio:
```bash
sudo systemctl status discord-bot
sudo journalctl -u discord-bot -f  # Ver logs en tiempo real
```

### 📊 Comandos Útiles

```bash
# Ver logs del bot
sudo journalctl -u discord-bot -f

# Reiniciar el servicio
sudo systemctl restart discord-bot

# Parar el servicio
sudo systemctl stop discord-bot

# Ver estado del servicio
sudo systemctl status discord-bot

# Ver logs de deployment en GitHub Actions
# Ve a: https://github.com/esedesofiaaa/DiscordSelfBotting/actions
```

### 🔒 Seguridad

- El usuario `discord-bot` tiene permisos limitados solo para gestionar su propio servicio
- Solo los comandos `systemctl` específicos están permitidos sin contraseña
- El bot se ejecuta con un usuario dedicado, no como root

### 📝 Notas

- El bot se reinicia automáticamente si falla (configurado en el servicio systemd)
- Los logs se guardan en el journal del sistema
- El deployment preserva la configuración y logs existentes
