import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException

from config import APP_HOST, APP_PORT


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
    print(text)
    # server = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
    # msg = MIMEMultipart()
    # emailAddress = "1234"
    # msg['From'] = emailAddress
    #
    # msg['To'] = email
    #
    # msg['Subject'] = "it's test"
    #
    # msg.attach(MIMEText(text, 'html'))
    # try:
    #     server.login(msg['From'], emailAddress)
    #     server.sendmail(msg["From"], msg["To"], msg.as_string())
    # except Exception as ex:
    #     raise HTTPException(400, ex.args)
