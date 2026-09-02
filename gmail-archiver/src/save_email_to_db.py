import email
import imaplib
import os
import sqlite3
from dotenv import load_dotenv
from email.header import decode_header


# --- CONFIGURATION ---
load_dotenv() # load from .env file
IMAP_SERVER = os.getenv("IMAP_SERVER")  # Use "://office365.com" for Outlook
EMAIL_USER = os.getenv("EMAIL_USER")
ACCOUNT = EMAIL_USER.split('@')[0]
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Your 16-character App Password
DB_FILE = "emails.db"

def init_database():
    """Creates the SQLite database and emails table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            account TEXT,
            sender TEXT,
            subject TEXT,
            date TEXT,
            body TEXT
        )
    """)
    conn.commit()
    return conn

def decode_mime_header(header_value):
    """Decodes email headers like Subject and From into human-readable text."""
    if not header_value:
        return ""
    decoded_fragments = decode_header(header_value)
    header_text = ""
    for fragment, encoding in decoded_fragments:
        try: 
            if isinstance(fragment, bytes):
                header_text += fragment.decode(encoding or "utf-8", errors="ignore")
            else:
                header_text += str(fragment)
        except LookupError as e: # TODO: save errors to separate file
            print("Fragment:", fragment)
    return header_text

def get_email_body(msg):
    """Extracts the plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

# TODO: create function to save known senders to a folder. Others go into "unknown" folder
def fetch_and_save_emails():
    # Initialize database connection
    conn = init_database()
    cursor = conn.cursor()
    
    # Connect to the IMAP server
    print(f"Connecting to {IMAP_SERVER}...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    
    # Search for all unread emails ("UNSEEN"). Use "ALL" to fetch everything.
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    
    print(f"Found {len(email_ids)} new emails to process.")
    saved_count = 0
    
    for e_id in email_ids:
        # Fetch the email data (RFC822 standard)
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse bytes into an email Message object
                msg = email.message_from_bytes(response_part[1])

                account = ACCOUNT
                # Extract meta-data
                message_id = msg.get("Message-ID", f"fallback_{e_id.decode()}")
                print("Subject:", msg.get("Subject"))
                subject = decode_mime_header(msg.get("Subject"))
                sender = decode_mime_header(msg.get("From"))
                date = msg.get("Date")
                body = get_email_body(msg)
                
                # Insert details safely using SQL parameters to prevent SQL injection
                try:
                    cursor.execute("""
                        INSERT INTO emails (message_id, account, sender, subject, date, body)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (message_id, account, sender, subject, date, body))
                    saved_count += 1
                except sqlite3.IntegrityError:
                    # Skip if message_id already exists (avoids duplicates)
                    pass

    # Save changes and close everything down
    conn.commit()
    conn.close()
    mail.logout()
    print(f"Successfully processed and saved {saved_count} new emails to {DB_FILE}.")

if __name__ == "__main__":
    fetch_and_save_emails()
