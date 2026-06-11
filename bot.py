# Pulse - Daily Summary Bot (HTML & CSS Edition)
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
        return quote, author
    except Exception as e:
        return f"Quote unavailable ({e})", "System"

def build_html_summary():
    """Assemble the daily summary using clean HTML and embedded CSS styling."""
    today = date.today().strftime("%A, %d %B %Y")
    weather = get_weather()
    quote_text, quote_author = get_quote()
    
    # Designing a premium, clean card layout using inline CSS
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; }}
            .card {{ max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden; border: 1px solid #eef2f5; }}
            .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: #ffffff; padding: 30px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 1px; }}
            .header p {{ margin: 5px 0 0 0; opacity: 0.9; font-size: 14px; }}
            .content {{ padding: 25px 20px; }}
            .section {{ margin-bottom: 25px; }}
            .section-title {{ font-size: 12px; font-weight: bold; color: #007bff; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; border-bottom: 1px solid #f0f0f0; padding-bottom: 4px; }}
            .weather-box {{ font-size: 16px; color: #495057; background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #17a2b8; font-weight: 500; }}
            .quote-box {{ font-style: italic; font-size: 16px; color: #212529; line-height: 1.6; background: #fdfffe; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745; margin: 0; }}
            .author {{ display: block; text-align: right; margin-top: 8px; font-size: 13px; color: #6c757d; font-style: normal; font-weight: 600; }}
            .footer {{ background: #f8f9fa; text-align: center; padding: 15px; font-size: 11px; color: #adb5bd; border-top: 1px solid #eef2f5; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>PULSE</h1>
                <p>{today}</p>
            </div>
            <div class="content">
                <div class="section">
                    <div class="section-title">Current Weather</div>
                    <div class="weather-box">{weather}</div>
                </div>
                <div class="section">
                    <div class="section-title">Morning Inspiration</div>
                    <blockquote class="quote-box">
                        "{quote_text}"
                        <span class="author">— {quote_author}</span>
                    </blockquote>
                </div>
            </div>
            <div class="footer">
                Automated via GitHub Actions • Built from Zero
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(html_text):
    """Send the generated summary directly to your inbox as an HTML layout."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    if not sender or not password or not receiver:
        print("Email configuration missing. Skipping email step.")
        return

    # Crucial change: We specify 'html' here instead of 'plain' text
    msg = MIMEText(html_text, "html")
    msg["Subject"] = f"✨ Your Daily Pulse Summary"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Beautiful HTML Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def run():
    """Main entry point."""
    html_summary = build_html_summary()
    
    # We still save a copy to the cloud folder as a backup
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(html_summary)
        
    send_email(html_summary)
    print("Pulse ran successfully.")

if __name__ == "__main__":
    run()
