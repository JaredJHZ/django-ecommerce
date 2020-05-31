import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def send_email(info):

    sender_email = "ardants.shop@gmail.com"
    receiver_email = config('EMAIL')
    password = config('EMAIL_PASSWORD')


    message = MIMEMultipart("alternative")
    message["Subject"] = f"Hubo una nueva compra en Ardants de {info}"
    message["From"] = sender_email
    message["To"] = receiver_email
 
    text = "Hubo una nueva compra en ardants!"


    html = """\
    <html>
    <body>
        <h1>Por favor checa la pagina administrador </h1>
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )