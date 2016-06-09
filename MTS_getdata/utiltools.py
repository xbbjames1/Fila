import urllib
import requests
import smtplib
from email.mime.text import MIMEText

def enhanced_catch(str_):
    if str_.find('https')==0:
        return True
    else:
        return False

# Validating all the item attrs
def validate_attr(item_attr, item_name):
    return True

def download_image(url):
    url_return = urllib.urlopen(url)
    # img_jpg = open('test.jpg','wb')
    # img_jpg.write(url_return.read())
    return url_return.read()

def send_mail(text_content, me_addr='xbbjames1@gmail.com', to_addr='xbb23james@gmail.com'):
    msg = MIMEText(text_content)
    msg['Subject'] = 'Potential Changing of the Webpage'
    msg['From'] = me_addr
    msg['To'] = to_addr
    conn_s = smtplib.SMTP('smtp.gmail.com:587')
    conn_s.ehlo()
    conn_s.starttls()

    PASSWORD = '920911920911'
    conn_s.login(me_addr, PASSWORD)

    try:
        conn_s.sendmail(me_addr, [to_addr], msg.as_string())
    finally:
        conn_s.quit()

    return 'Done'

