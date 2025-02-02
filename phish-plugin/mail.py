import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from generator import generate_payloads
from log import log
from urllib.parse import quote

def load_attachment(msg, attachment_path):
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}"
    )
    msg.attach(part)


def load_attachment_lnk(msg, attachment_path):
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "x-ms-shortcut")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}"
    )
    msg.attach(part)


# def load_attachment_zip(msg, attachment_path):
#     with open(attachment_path, "rb") as attachment:
#         part = MIMEBase("application", "zip")
#         part.set_payload(attachment.read())
#         encoders.encode_base64(part)
#         part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
#         msg.attach(part)

def load_attachment_zip(msg, attachment_path):

    if not os.path.exists(attachment_path):
        print(f"File not found: {attachment_path}")  # Лучше использовать logging
        return

    filename = os.path.basename(attachment_path)

    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "zip")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)

            # Кодируем имя файла в соответствии с RFC 2231
            encoded_filename = quote(filename)
            part.add_header("Content-Disposition", f"attachment; filename*=UTF-8''{encoded_filename}")
            msg.attach(part)

    except Exception as e:
        print(f"Error attaching file: {e}")

# Функция для отправки email
def send_email_with_attachment(configs, recipient, target_content, attachment_path):
    print("ATTACHMENT PATH:", attachment_path)
    # Создаем письмо
    msg = MIMEMultipart()
    msg["From"] = configs["SMTP_USER"]
    msg["To"] = recipient.email
    msg["Subject"] = target_content.subject

    body = target_content.message
    msg.attach(MIMEText(body, "plain"))

    load_attachment(msg, attachment_path)
    log(f"Attach loaded to email.", "INFO")
    log(f"Connecting to SMTP-server ...", "INFO")
    # Отправка письма через SMTP_SSL
    try:
        with smtplib.SMTP_SSL(configs["SMTP_SERVER"], configs["SMTP_PORT"]) as server:
            log(f"Connected to SMTP-server.", "INFO")
            log(f"Authentication...", "INFO")
            server.login(configs["SMTP_USER"], configs["SMTP_PASSWORD"])
            log(f"Authentication success.", "INFO")
            server.send_message(msg)
        log(f"Email sent to {recipient.email}", "INFO")
    except Exception as e:
        log(f"Someting went wrong for {recipient.email}", "ERROR")


# Логика для массовой рассылки
def mass_email_dispatch(configs, target_content, target_payload, recipients):
    for recipient in recipients:
        log(f"Generating payload for {recipient.email}...", "INFO")
        generate_payloads(configs["DOMAIN_NAME"], configs["PORT"], recipient, target_payload)

        log(f"Sending mail for {recipient.email}.", "INFO")

        send_email_with_attachment(configs, recipient, target_content, target_payload.attachment_path)


