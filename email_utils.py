import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from fastapi import BackgroundTasks
from jinja2 import Environment, FileSystemLoader

def send_verification_email(email: str, username: str, token: str, background_tasks: BackgroundTasks):
    """
    Відправляє листа з підтвердженням електронної пошти у фоновому режимі.

    :param email: Email одержувача.
    :param username: Ім'я користувача, яке буде відображено в електронному листі.
    :param token: Токен для підтвердження електронної пошти.
    :param background_tasks: Фонові завдання FastAPI, у яких буде виконано відправку.
    :raises ValueError: Якщо SENDER_EMAIL або SENDER_PASSWORD не налаштовані в середовищі.
    """
    smtp_server = 'smtp.meta.ua'
    smtp_port = 587
    sender_email = os.getenv('SENDER_EMAIL')  # Електронна адреса відправника
    sender_password = os.getenv('SENDER_PASSWORD')  # Пароль від електронної адреси відправника

    if not sender_email or not sender_password:
        raise ValueError("SENDER_EMAIL or SENDER_PASSWORD is not set in environment variables")

    # Завантаження шаблону HTML через Jinja2
    env = Environment(loader=FileSystemLoader('templates'))  # Шлях до папки з шаблонами
    template = env.get_template('email_template.html')  # Завантажуємо файл шаблону

    # Рендеримо шаблон, замінюючи змінні на фактичні значення
    html_content = template.render(username=username, host="http://localhost:8000/", token=token)

    # Підготовка повідомлення
    subject = "Email Verification"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    # Додаємо HTML-контент у лист
    msg.attach(MIMEText(html_content, 'html'))

    # Відправка електронного листа
    def send_email_task():
        """
        Виконує реальну відправку електронного листа через SMTP сервер.

        :raises Exception: У разі помилки відправки листа.
        """
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Для безпеки
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, msg.as_string())
                print(f"Verification email sent to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    # Додаємо завдання у фоновий режим
    background_tasks.add_task(send_email_task)
