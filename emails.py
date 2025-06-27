import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
from dotenv import load_dotenv
import os

load_dotenv() 

EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')
SENHA_REMETENTE = os.getenv('SENHA_REMETENTE')

def gerar_senha_aleatoria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho))
    return senha

def enviar_email_senha(destinatario, senha_gerada):
    assunto = "Sua conta na CyberPet - Senha temporária"
    
    corpo_html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f9f9f9; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
            <h2 style="color: #2E8B57; text-align: center;">🔑 Senha Temporária Gerada</h2>
            <p>Olá,</p>
            <p>Sua conta foi criada no sistema com a seguinte senha temporária:</p>
            
            <div style="text-align: center; margin: 25px 0; font-size: 18px; font-weight: bold; color: #2E8B57; background-color: #e6f2e6; padding: 15px; border-radius: 5px;">
                {senha_gerada}
            </div>
            
            <p>Por favor, altere essa senha no primeiro login para garantir a segurança da sua conta.</p>

            <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;" />

            <div style="text-align: center;">
                <p style="font-size: 12px; color: #777;">Atenciosamente,<br>Equipe Cyberpet</p>
                <img src="https://res.cloudinary.com/diwzoykov/image/upload/v1751022252/Logo_simples_circular_esmaltaria_preto_1_nqjcjh.png" alt="Logo Petshop" width="100" style="margin-top: 10px;"/>
            </div>
        </div>
    </body>
    </html>
    """

    mensagem = MIMEMultipart("alternative")
    mensagem["Subject"] = assunto
    mensagem["From"] = EMAIL_REMETENTE
    mensagem["To"] = destinatario
    mensagem.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            smtp.send_message(mensagem)
        print(f"Email enviado com sucesso para {destinatario}!")
    except Exception as e:
        print(f"Erro ao enviar email para {destinatario}: {e}")




def enviar_email_confirmacao_consulta(destinatario, nome_pet, data, hora, nome_vet):
    assunto = "Confirmação de Consulta - CyberPet"

    corpo_html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f9f9f9; color: #333;">
        <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
            <h2 style="color: #2E8B57; text-align: center;">✅ Consulta Agendada com Sucesso!</h2>
            <p>Olá,</p>
            <p>Temos o prazer de confirmar o agendamento da consulta para o seu pet <strong>{nome_pet}</strong>.</p>
            
            <table style="width: 100%; margin-top: 20px; font-size: 15px;">
                <tr>
                    <td><strong>📅 Data:</strong></td>
                    <td>{data}</td>
                </tr>
                <tr>
                    <td><strong>🕐 Hora:</strong></td>
                    <td>{hora}</td>
                </tr>
                <tr>
                    <td><strong>👨‍⚕️ Veterinário:</strong></td>
                    <td>{nome_vet}</td>
                </tr>
            </table>

            <p style="margin-top: 30px;">Caso precise remarcar, entre em contato conosco pelo nosso sistema ou por telefone.</p>

            <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;" />

            <div style="text-align: center;">
                <p style="font-size: 12px; color: #777;">Atenciosamente,<br>Equipe Cyberpet</p>
                <img src="https://res.cloudinary.com/diwzoykov/image/upload/v1751022252/Logo_simples_circular_esmaltaria_preto_1_nqjcjh.png" alt="Logo Petshop" width="100" style="margin-top: 10px;"/>
            </div>
        </div>
    </body>
    </html>
    """

    mensagem = MIMEMultipart("alternative")
    mensagem["Subject"] = assunto
    mensagem["From"] = EMAIL_REMETENTE
    mensagem["To"] = destinatario
    mensagem.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            smtp.send_message(mensagem)
        print(f"Email responsivo enviado com sucesso para {destinatario} ✅")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")