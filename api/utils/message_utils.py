import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

from config import APP_HOST, APP_PORT, IS_PROD, EMAIL_ADDRESS, EMAIL_LOGIN, EMAIL_PASS


def send_verify_message(token, email):
    text = f"""<html>
      <body>
      <p>Здравствуйте. Вы прошли регистрацию в мобильном приложении Privet</p>
      <p>Введите данный код в приложении для подтверждения своего аккаунта: {token}</p>
      <p> Если вы не регистрировались в мобильном приложении, то проигнорируйте данное сообщение. </p>
      </body>
    </html>"""
    send(text, email)


def send_reset_message(token, email):
    text = f"""<html>
      <body>
      <p>Здравствуйте. Поступил запрос на смену пароля в мобильном приложении Privet.</p>
      <p>
        Введите данный код: {token}
        если вы и вправду хотите поменять свой пароль.
      </p>
      <p> Если вы не делали запрос, то проигнорируйте данное сообщение. </p>
      </body>
    </html>"""

    send(text, email)


def send(text, email):
    if not IS_PROD:
        print(text)
    else:
        server = smtplib.SMTP_SSL("connect.smtp.bz", 465)
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS

        msg['To'] = email

        msg['Subject'] = "Регистрация в мобильном приложении"

        msg.attach(MIMEText(text, 'html'))
        try:
            server.login(EMAIL_LOGIN, EMAIL_PASS)
            server.sendmail(msg["From"], msg["To"], msg.as_string())
        except Exception as ex:
            raise HTTPException(500, ex.args)
