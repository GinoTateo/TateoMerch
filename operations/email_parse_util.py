import imaplib
import email as email_lib
from pymongo import MongoClient
from datetime import datetime


def fetch_last_email_content(email_address, password):
    """
    Connects to a Gmail account and fetches the content of the last email in the inbox.

    :param email_address: Your Gmail email address.
    :param password: Your Gmail password or app-specific password.
    :return: Raw email content of the last email.
    """
    try:
        # Connect to Gmail's IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_address, password)
        mail.select('inbox')

        # Search for all emails in the inbox
        status, email_ids = mail.search(None, 'ALL')
        if status != 'OK':
            print("No emails found!")
            return None

        # Fetch the last email ID
        last_email_id = email_ids[0].split()[-1]
        status, email_data = mail.fetch(last_email_id, '(RFC822)')
        if status != 'OK':
            print("Failed to fetch the email.")
            return None

        raw_email = email_data[0][1]

        # Close the connection and logout
        mail.close()
        mail.logout()

        return raw_email, last_email_id.decode()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
# email_content = fetch_last_email_content('your_email@gmail.com', 'your_password')


def parse_email(raw_email_content):
    """
    Parses the raw content of an email, handles forwarded emails, and extracts specific data points and order details.
    Adjusted to handle multi-line item details format.

    :param raw_email_content: The raw email content.
    :return: A dictionary containing the extracted data points and order details.
    """
    if not raw_email_content:
        print("No email content provided.")
        return None

    email_message = email_lib.message_from_bytes(raw_email_content)
    email_id = email_message.get('Message-ID')  # Get the email's unique ID

    # Define a dictionary to hold the extracted data
    extracted_data = {
        'Route Name': None,
        'Route Number': None,
        'Pick up Date': None,
        'Pick up Time': None,
        'Total Cases': None,
        'Order Details': [],
        'Email ID': email_id
    }

    def decode_payload(payload, charset='utf-8'):
        try:
            return payload.decode(charset)
        except UnicodeDecodeError:
            return payload.decode('ISO-8859-1')  # Fallback decoding

    # Extract the body of the email
    body = ''
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = decode_payload(part.get_payload(decode=True))
                break
    else:
        body = decode_payload(email_message.get_payload(decode=True))

    # Parsing the body for the specific data points and order form
    capturing_items = False
    item_buffer = []  # Temporary buffer to hold multi-line item details

    for line in body.splitlines():
        line = line.strip()
        if not capturing_items:
            # Check for and extract key data points before items
            if ":" in line:
                key, value = line.split(':', 1)
                if key in extracted_data:
                    extracted_data[key] = value.strip()
            if "Quantity" in line:
                capturing_items = True  # Start capturing items after this line
                continue
        else:
            # Handle item details spread across multiple lines
            if line:  # Ensure line is not empty
                # Check for the end of item details or start of additional information
                if "Additional Items Needed" in line or line.startswith("Item Number"):
                    # Process buffered item details
                    if len(item_buffer) == 3:  # Assuming item details are complete
                        extracted_data['Order Details'].append({
                            'Item Number': item_buffer[0],
                            'Item Description': item_buffer[1],
                            'Quantity': item_buffer[2]
                        })
                    item_buffer.clear()  # Reset buffer for the next item
                    if "Additional Items Needed" in line:
                        break  # Stop capturing after this line
                else:
                    # Continue buffering item details
                    item_buffer.append(line)
                    if len(item_buffer) == 3:  # Assuming item details are complete
                        extracted_data['Order Details'].append({
                            'Item Number': item_buffer[0],
                            'Item Description': item_buffer[1],
                            'Quantity': item_buffer[2]
                        })
                        item_buffer.clear()  # Prepare for next item

    # Debugging print of the extracted data
    for key, value in extracted_data.items():
        if key != 'Order Details':
            print(f"{key}: {value}")
        else:
            print("Order Details:")
            for item in value:
                print(item)

    return extracted_data


# Example usage
# raw_email_content = fetch_last_email_content('your_email@gmail.com', 'your_password')
# parsed_data = parse_email(raw_email_content)


def insert_order_into_mongodb(extracted_data, client, db_name='mydatabase', orders_collection='orders',
                              status_collection='status'):
    """
    Inserts the order details into a MongoDB collection, organized by date and route.

    :param status_collection:
    :param extracted_data: The data to be inserted, including the order details.
    :param db_name: The name of the database.
    :param orders_collection: The name of the collection for orders.
    """
    # Check if the necessary data is available
    if not extracted_data.get('Order Details') or not extracted_data.get('Pick up Date') or not extracted_data.get(
            'Route Number'):
        print("Missing order details, date, or route number.")
        return

    # Select the database and collection
    db = client[db_name]
    collection = db[orders_collection]

    # Prepare the document to be inserted
    order_document = {
        'email_id': extracted_data['Email ID'],
        'date': datetime.strptime(extracted_data['Pick up Date'], "%m/%d/%Y"),  # Adjust date format if necessary
        'route': extracted_data['Route Number'],
        'orders': extracted_data['Order Details'],
        'status': "Received",
    }

    # Insert the document into the collection
    result = collection.insert_one(order_document)
    print(f"Order data inserted with record id: {result.inserted_id}")

    db = client[db_name]
    collection = db[status_collection]
    collection.update_one({'variable': 'last_parsed'}, {'$set': {'value': extracted_data['Email ID']}}, upsert=True)


# Example usage
# parsed_data = parse_email(raw_email_content)
# insert_order_into_mongodb(parsed_data)
def get_last_parsed_email_id(client, db_name='mydatabase', status_collection='status'):
    db = client[db_name]
    collection = db[status_collection]
    status_document = collection.find_one({'variable': 'last_parsed'})
    last_parsed_email_id = status_document.get('value') if status_document else None
    return last_parsed_email_id


def get_latest_email_id(email_address, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_address, password)
    mail.select('inbox')
    status, email_ids = mail.search(None, 'ALL')
    if status != 'OK':
        print("No emails found!")
        return None
    last_email_id = email_ids[0].split()[-1].decode()
    mail.close()
    mail.logout()
    return last_email_id


def fetch_unread_emails(email_address, password):
    """
    Fetches unread emails from the Gmail account.
    """
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_address, password)
    mail.select('inbox')

    # Search for unread emails
    result, data = mail.search(None, 'UNSEEN')
    if result != 'OK':
        print("Failed to retrieve unread emails.")
        return []

    if data is None:
        print("All orders parsed")

    email_ids = data[0].split()
    emails = []

    for e_id in email_ids:
        result, email_data = mail.fetch(e_id, '(RFC822)')
        if result == 'OK':
            emails.append(email_data[0][1])

    mail.close()
    mail.logout()
    return emails


def check_and_parse_new_emails(email_address, email_password, client, db_name='mydatabase', orders_collection='orders'):
    """
    Fetches unread emails, parses them, and inserts order details into MongoDB.
    """
    unread_emails = fetch_unread_emails(email_address, email_password)

    for raw_email in unread_emails:
        email_message = email_lib.message_from_bytes(raw_email)
        subject = str(email_lib.header.make_header(email_lib.header.decode_header(email_message['Subject'])))

        if 'Concord Peet\'s Route Replenishment Submission' in subject:
            parsed_data = parse_email(raw_email)
            if parsed_data is not None:
                insert_order_into_mongodb(parsed_data, client, db_name, orders_collection)


# Example usage
# client = MongoClient('mongodb://localhost:27017/')  # or your MongoDB connection details
# check_and_parse_new_emails('your_email@gmail.com', 'your_password', client)