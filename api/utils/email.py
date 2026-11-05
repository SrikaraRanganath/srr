from flask import current_app
from flask_mail import Message
from api.mail import mail
import threading
import os
import time

MAX_RETRIES = int(os.getenv("MAIL_MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("MAIL_RETRY_DELAY", 2))

def send_email_with_retry(app, recipient, subject, body, isHTML):
    if not recipient or not subject or not body:
        return
    
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            with app.app_context():
                message = Message(
                    subject=subject,
                    recipients=[recipient],
                )

                if isHTML:
                    message.html = body
                else:
                    message.body = body

                mail.send(message)
                return True
        
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                app.logger.error(f"Mail failed after retries: {e}")
                return False
            
            # Exponential Backoff
            time.sleep(RETRY_DELAY * (2 ** (attempt - 1)))

def send_email_async(recipient, subject, body, isHTML=True):
    app = current_app._get_current_object()

    thread = threading.Thread(
        target=send_email_with_retry,
        args=(app, recipient, subject, body, isHTML),
        daemon=True
    )
    thread.start()