import smtplib
from email.mime.text import MIMEText
import random
import string
from dotenv import load_dotenv
import os

load_dotenv()  # carrega as variáveis do arquivo .env

EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')
SENHA_REMETENTE = os.getenv('SENHA_REMETENTE')

def gerar_senha_aleatoria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho))
    return senha

def enviar_email_senha(destinatario, senha_gerada):
    assunto = "Sua conta no Petshop - Senha temporária"
    corpo = f"""Olá!

Sua conta foi criada no sistema Petshop com a senha temporária:

{senha_gerada}

Por favor, altere essa senha no primeiro login para garantir a segurança da sua conta.

Obrigado!
"""

    mensagem = MIMEText(corpo)
    mensagem['Subject'] = assunto
    mensagem['From'] = EMAIL_REMETENTE
    mensagem['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            smtp.send_message(mensagem)
        print(f"Email enviado com sucesso para {destinatario}!")
    except Exception as e:
        print(f"Erro ao enviar email para {destinatario}: {e}")
