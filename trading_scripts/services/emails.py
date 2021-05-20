import os
import os.path
import sys
import ssl, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_bug_email(issue_type, area, issue, sender):
    print('Starting daily email job')
    try:
        html = """\
                <html>
                <body>
                <h3>Report submitted by {3}</h3>
                    <p><b>Type: </b>{0}</p>
                    <p><b>Area: </b>{1}</p>
                    <p><b>Description: </b>{2}</p>
                </body>
                </html>
                """.format(issue_type, area, issue, sender)
    
        port = 465
        gmail_password = 'neikdnzctqdtotof'
        # Create a secure SSL context
        context = ssl.create_default_context()

        sender_email = sender
        receiver_email = "blockbotie@gmail.com"
        message = MIMEMultipart("alternative")
        message["Subject"] = issue_type
        message["From"] = sender_email

        part1 = MIMEText(html, "html")
        message.attach(part1)

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            print('Logging into email server')
            server.login(receiver_email, gmail_password)
            print('Sending email')
            message["To"] = receiver_email
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
            print('Email sent by {0}'.format(sender_email))
    except Exception as error:
        print("Error sending order emails ", error)


def send_order_error_email(user, error, no_of_errors):
    print('Starting daily email job')
    errors_remaining = 5 - no_of_errors
    try:
        if errors_remaining == 0:
            html = """\
                <html>
                <body>
                    <h2>Order Error</h2>
                    <p>There was an error while processing your order.</p>
                    <p>Please find the details below.</p>
                    <p><b>Error message: </b>{0}</p>
                    <br>
                    <p>You're strategy pair has been deactivated. Please fix the error on your exchange and reactivate your pair in the MyBlockbot app<p>
                </body>
                </html>
                """.format(error[0])
        else:        
            html = """\
                    <html>
                    <body>
                        <h2>Order Error</h2>
                        <p>There was an error while processing your order.</p>
                        <p>Please find the details below.</p>
                        <p><b>Error message: </b>{0}</p>
                        <br>
                        <p>You're strategy pair will be deactivated after {1} more attempts<p>
                    </body>
                    </html>
                    """.format(error[0], errors_remaining)
        
        port = 465
        gmail_password = 'neikdnzctqdtotof'
        # Create a secure SSL context
        context = ssl.create_default_context()

        sender_email = "blockbotie@gmail.com"
        receiver_email = user.email
        message = MIMEMultipart("alternative")
        message["Subject"] = 'Order Error'
        message["From"] = sender_email

        part1 = MIMEText(html, "html")
        message.attach(part1)

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            print('Logging into email server')
            server.login(sender_email, gmail_password)
            print('Sending email')
            message["To"] = receiver_email
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
            print('Email sent to {0}'.format(receiver_email))
    except Exception as error:
        print("Error sending order emails ", error)