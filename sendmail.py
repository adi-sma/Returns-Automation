import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate
from email import encoders as Encoders
import configparser as ConfigParser

def send_mail(send_from, send_to, subject, text, files=None, 
                          data_attachments=None, server="smtp.office365.com", port=587, 
                          tls=True, html=False, images=None,
                          username=None, password=None, 
                          config_file=None, config=None):

    if files is None:
        files = []

    if images is None:
        images = []

    if data_attachments is None:
        data_attachments = []

    if config_file is not None:
        config = ConfigParser.ConfigParser()
        config.read(config_file)

    if config is not None:
        server = config.get('smtp', 'server')
        port = config.get('smtp', 'port')
        tls = config.get('smtp', 'tls').lower() in ('true', 'yes', 'y')
        username = config.get('smtp', 'username')
        password = config.get('smtp', 'password')

    msg = MIMEMultipart('related')
    msg['From'] = send_from
    if type(send_to) == type("asdf"):
        msg['To'] = send_to
    else:
        msg['To'] = ", ".join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text, 'html' if html else 'plain') )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    for f in data_attachments:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( f['data'] )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % f['filename'])
        msg.attach(part)

    for (n, i) in enumerate(images):
        fp = open(i, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image{0}>'.format(str(n+1)))

    smtp = smtplib.SMTP(server, int(port))
    if tls:
        smtp.starttls()

    if username is not None:
        smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
