# Pulse - Daily Summary Bot with Email Integration
# Fetches: weather (wttr.in) + a quote (zenquotes.io)
# Runs: every day at 8 AM IST via GitHub Actions

import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, date

def get_weather(city="Thiruvananthapuram"):
    """Fetch today's weather as a one-line text summary."""
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return f"Weather unavailable ({e})"

def get_quote():
    """Fetch a random motivational quote from ZenQuotes."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        return f'"{quote}" - {author}'
    except Exception as e:
        return f"Quote unavailable ({e})"

def build_summary():
    """Assemble the full daily summary from all data sources."""
    today = date.today().strftime("%A, %d %B %Y")
    weather = get_weather()
    quote = get_quote()
    
    summary = f"""
========================================
PULSE - Daily Summary
{today}
========================================

WEATHER
{weather}

TODAY'S QUOTE
{quote}

========================================
"""
    return summary

def send_email(summary_text):
    """Send the generated summary directly to your inbox."""
    # Read variables safely from the cloud environment
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    if not sender or not password or not receiver:
        print("Email configuration missing. Skipping email step.")
        return

    # Set up the email layout
    msg = MIMEText(summary_text)
    msg["Subject"] = f"Pulse - Daily Summary"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        # Securely connect to Gmail's mail server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def run():
    """Main entry point. Called by GitHub Actions."""
    summary = build_summary()
    print(summary)
    
    # Save the file locally inside GitHub
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
        
    # Send it to your inbox!
    send_email(summary)
    print("Pulse ran successfully.")

if __name__ == "__main__":
    run()
