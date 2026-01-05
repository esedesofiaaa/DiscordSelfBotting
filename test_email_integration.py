import os
import sys
import logging
from dotenv import load_dotenv
from email_notifier import EmailNotifier

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_email')

def test_email_integration():
    """
    Script de prueba independiente para verificar la integración de correo.
    Lee la configuración del archivo .env o usa valores por defecto.
    """
    print("🧪 Iniciando prueba de integración de correo electrónico...")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener configuración
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SMTP_SENDER_EMAIL')
    sender_password = os.getenv('SMTP_SENDER_PASSWORD')
    recipient_emails_str = os.getenv('ALERT_RECIPIENT_EMAILS')
    
    # Verificar credenciales
    if not sender_email or not sender_password or not recipient_emails_str:
        print("\n❌ Error: Faltan credenciales en el archivo .env")
        print("Asegúrate de tener configuradas las siguientes variables:")
        print(" - SMTP_SENDER_EMAIL")
        print(" - SMTP_SENDER_PASSWORD")
        print(" - ALERT_RECIPIENT_EMAILS")
        
        # Opción para ingresar credenciales manualmente si no están en .env
        print("\n¿Deseas ingresar las credenciales manualmente para esta prueba? (s/n)")
        response = input("> ").lower()
        if response == 's':
            sender_email = input("Email del remitente: ")
            sender_password = input("Contraseña de aplicación: ")
            recipient_emails_str = input("Email del destinatario: ")
        else:
            return

    recipient_emails = [email.strip() for email in recipient_emails_str.split(',') if email.strip()]
    
    print(f"\n⚙️ Configuración:")
    print(f" - Servidor SMTP: {smtp_server}:{smtp_port}")
    print(f" - Remitente: {sender_email}")
    print(f" - Destinatarios: {recipient_emails}")
    
    try:
        # Inicializar notificador
        notifier = EmailNotifier(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_emails=recipient_emails
        )
        
        print("\n📨 Enviando correo de prueba...")
        
        # Enviar prueba
        success = notifier.test_connection()
        
        if success:
            print("\n✅ ¡ÉXITO! El correo se envió correctamente.")
            print("Por favor revisa tu bandeja de entrada (y la carpeta de spam).")
        else:
            print("\n❌ FALLO: No se pudo enviar el correo.")
            print("Revisa los logs anteriores para ver el error específico.")
            
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_email_integration()
