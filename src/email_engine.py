import smtplib
import os
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from src.config import (
    DB_PATH,
    RESUME_PATH,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SENDER_EMAIL
)

def send_application_email(job_id, custom_subject, custom_body, target_email):
    """Sends the customized cover letter & resume PDF using SMTP, then records it in the DB."""
    if not SMTP_USER or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials are not set in the configuration/.env file.")

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = target_email
    msg['Subject'] = custom_subject

    # Attach the custom cover letter body
    msg.attach(MIMEText(custom_body, 'plain'))

    # Attach the PDF resume
    if os.path.exists(RESUME_PATH):
        try:
            with open(RESUME_PATH, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename={os.path.basename(RESUME_PATH)}"
                )
                msg.attach(part)
        except Exception as e:
            raise IOError(f"Failed to read/attach resume PDF at {RESUME_PATH}: {e}")
    else:
        raise FileNotFoundError(f"Resume PDF not found at {RESUME_PATH}")

    # Connect and send
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, target_email, msg.as_string())
        server.quit()
    except Exception as e:
        raise ConnectionError(f"SMTP sending failed: {e}")

    # Update database record
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Update job status to APPLIED
        cursor.execute("UPDATE jobs SET status = 'APPLIED' WHERE id = ?", (job_id,))
        
        # Track application record
        cursor.execute("""
            INSERT INTO applications (job_id, email_subject, email_body_sent)
            VALUES (?, ?, ?)
        """, (job_id, custom_subject, custom_body))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    print(f"Successfully applied to Job ID {job_id}. Email sent to {target_email}.")
    return True
