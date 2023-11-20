import datetime
import imaplib
import email
import smtplib
import ssl
import time
import uuid
from email.message import EmailMessage

# Global variables
message_id = str(uuid.uuid4())
sender_email = "felixbrandonlee@gmail.com"
sender_password = "vrsg rtma ozeg xpoe"
recipient_email = "vapidx4@hotmail.com"
subject = f"Light Control #{message_id}"


def send_email(light_intensity):
    print("Creating email...")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    body = f"""
            The Light is ON at {current_time} time.
            """

    em = EmailMessage()
    em["From"] = sender_email
    em["To"] = recipient_email
    em["Subject"] = subject
    em.set_content(body)

    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, recipient_email, em.as_string())
        return
    except Exception as e:
        print(f"Error sending email: {e}")


# def wait_for_response(timeout=300):
#     response_received = False
#     end_time = time.time() + timeout

#     while time.time() < end_time and not response_received:
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         try:
#             mail.login(sender_email, sender_password)
#             mail.select("inbox")

#             status, messages = mail.search(None, f'(HEADER Subject "Re: {subject}" TO "{sender_email}")')
#             messages = messages[0].split()

#             if messages:
#                 latest_message_id = messages[-1]
#                 _, msg_data = mail.fetch(latest_message_id, "(RFC822)")
#                 raw_email = msg_data[0][1]
#                 message = email.message_from_bytes(raw_email)

#                 # Extracting the response from the email
#                 if message.is_multipart():
#                     for part in message.walk():
#                         if part.get_content_type() == "text/plain":
#                             response_text = part.get_payload(decode=True).decode("utf-8", errors="replace")
#                             # print("Response:", response_text)
#                             return response_text.strip()
#                 else:
#                     response_text = message.get_payload(decode=True).decode("utf-8", errors="replace")
#                     print("Response:", response_text)
#                     return response_text.strip()

#         except Exception as e:
#             print(f"Error checking for response: {e}")
#         finally:
#             mail.logout()

#         time.sleep(10)

#     return None


"""def main(temp):
    print("Connecting to SMTP server...")
    send_email(temp)
    print("Email sent.")

    print("Waiting for response...")
    response = wait_for_response()

    if response:
        divider_index = response.find('________________________________')
        response_body = response[:divider_index].strip()
        print("________________________________")
        print("Response received:", response_body)

        # Check if the response is "YES"
        if response_body == "YES":
            print("Light will be turned on.")
            return True
        else:
            print("Light will be turned off.")

    else:
        print("No response received within 5 minutes. Ending the program.")

    return False"""