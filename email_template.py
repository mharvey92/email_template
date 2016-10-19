#Mariah Harvey
#October 19, 2016
#Function to send emails with attachments

import smtplib
import email.utils
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from datetime import timedelta
from datetime import datetime

def email_template(subject, from_email, password, recipient_email, attachment_path, zip_file):
	''' param subject (str): Enter email subject heading.
	param from_email (str): Email address that email is being sent from
	param recipient_email: Email address that the email is being sent to
	param attachment_path (str): Identifies the file path where the attached zip file is located
	param zip_file (str): Name of zip file to send in email'''
	

	msg = MIMEMultipart()
	msg['Subject'] = subject


	msg['From'] = from_email
	msg['To'] = recipient_email

	zf = open(attachment_path+zip_file)
	msg = MIMEBase('application', 'zip')
	msg.set_payload(zf.read())
	encoders.encode_base64(msg)
	msg.add_header('Content-Disposition', 'attachment', 
               filename=zip_file)


	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(from_email, password)
	text = msg.as_string()
	server.sendmail(from_email, recipient_email, msg.as_string())
	server.quit()
	
	return None

