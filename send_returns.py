import sendmail
import time

EMAIL_FROM = "johnl@socialmarketanalytics.com"
EMAIL_PWD = "ua$3AdM@"
EMAIL_TO = ["johnl@socialmarketanalytics.com", "coltons@socialmarketanalytics.com", "adi@socialmarketanalytics.com", "jeffb@socialmarketanalytics.com"]
EMAIL_SUBJECT = "Weekly Returns Charts"
dow = time.strftime("%a")

MESSAGE_BODY = "Attached is an updated version of the returns charts." + \
"\n\n\nThis is an automated message"

sendmail.send_mail(EMAIL_FROM, EMAIL_TO, EMAIL_SUBJECT, \
MESSAGE_BODY, username=EMAIL_FROM, password=EMAIL_PWD,\
files = ["/home/sma-analytics/Data/Returns/Returns.pptx"])
