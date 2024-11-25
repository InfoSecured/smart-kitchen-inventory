import sqlite3
import smtplib
from email.mime.text import MIMEText

DB_FILE = "kitchen_inventory.db"

def create_notification(user_id, message):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (user_id, message))
    conn.commit()
    conn.close()

def get_notifications(user_id, include_read=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    query = "SELECT id, message, is_read, created_at FROM notifications WHERE user_id = ?"
    if not include_read:
        query += " AND is_read = 0"
    c.execute(query, (user_id,))
    notifications = c.fetchall()
    conn.close()
    return notifications

def mark_as_read(notification_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()
    


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "your_email@gmail.com"
SMTP_PASSWORD = "your_email_password"

def send_email_notification(recipient, subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = recipient

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, recipient, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}") 