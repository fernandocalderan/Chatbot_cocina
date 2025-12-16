import os
import smtplib
from email.mime.text import MIMEText
from loguru import logger


def send_magic_link(email: str, link: str) -> None:
    """
    Envía un magic link. Usa SMTP si está configurado, si no solo loguea.
    No bloquea el flujo si falla.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_email = os.getenv("SMTP_FROM", smtp_user or "no-reply@opunnence.com")
    use_tls = os.getenv("SMTP_TLS", "1") != "0"

    subject = "Acceso a tu panel Opunnence"
    body = f"""Hola,

Tu panel ya está listo.

Accede aquí para activarlo:
{link}

Por seguridad, este enlace caduca en 30 minutos.
En el primer acceso te pediremos crear tu contraseña.
"""
    if smtp_host and smtp_user and smtp_pass:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = email
        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [email], msg.as_string())
            server.quit()
            logger.info({"event": "magic_link_sent", "email": email})
            return
        except Exception as exc:
            logger.warning({"event": "magic_link_send_failed", "error": str(exc)})
    # Fallback: log
    logger.info({"event": "magic_link_stub", "email": email, "link": link})
