import smtplib

from email.message import EmailMessage


def send_email(config_email: dict, message: str) -> None:
    """
    Esta função enviará uma mensagem para o e-mail destinatário.
    :param config_email: (dict): configuração do email.
    :param message: (str): menssagem a ser passada.
    """
    msg = EmailMessage()
    msg['Subject'] = config_email['titulo']
    msg['From'] = config_email['distribuidor']['login']
    msg['To'] = config_email['recebedores']
    msg.set_content(message)

    s = smtplib.SMTP(host=config_email['host_smtp'], port=config_email['port'])
    s.starttls()
    s.login(config_email['distribuidor']['login'], config_email['distribuidor']['senha'])
    s.send_message(msg)
    s.quit()
