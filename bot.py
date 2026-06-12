# Pulse - Smart Daily Summary Bot (OpenWeatherMap Edition)
# Fetches: OpenWeatherMap JSON + ZenQuotes
# Runs: Automatically via your GitHub Actions cron schedule

import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

def get_weather(city="Thiruvananthapuram"):
    """Fetch live data from OpenWeatherMap and determine alert status."""
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        print("Weather API Key missing. Skipping real-time metrics evaluation.")
        return None, False
    
    # Request metric units for automated Celsius conversion
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"]
        
        # LOGIC RULES: Temp > 10°C (Testing setting) OR condition matches Rain/Drizzle
        is_heat_wave = temp > 10
        is_raining = "rain" in condition.lower() or "drizzle" in condition.lower()
        trigger_alert = is_heat_wave or is_raining
        
        weather_info = {
            "temp": round(temp, 1),
            "description": description.capitalize(),
            "city": city,
            "condition": condition
        }
        return weather_info, trigger_alert
    except Exception as e:
        print(f"Error fetching OpenWeatherMap data: {e}")
        return None, False

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

def build_html_summary(weather, quote_text, quote_author):
    """Assemble the daily summary using clean HTML, CSS, and localized execution time."""
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    
    formatted_date = ist_now.strftime("%A, %d %B %Y")
    formatted_time = ist_now.strftime("%I:%M:%S %p IST")
    
    weather_display = f"{weather['temp']}°C, {weather['description']}" if weather else "Weather Offline"
    city_name = weather['city'] if weather else "Thiruvananthapuram"
    
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
            .header .date {{ margin: 5px 0 0 0; opacity: 0.9; font-size: 14px; font-weight: bold; }}
            .header .time {{ margin: 2px 0 0 0; opacity: 0.75; font-size: 12px; font-family: monospace; }}
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
                <h1>PULSE WEATHER ALERT</h1>
                <div class="date">{formatted_date}</div>
                <div class="time">Generated at: {formatted_time}</div>
            </div>
            <div class="content">
                <div class="section">
                    <div class="section-title">Current Weather ({city_name})</div>
                    <div class="weather-box">{weather_display}</div>
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

    msg = MIMEText(html_text, "html")
    msg["Subject"] = f"⚠️ Pulse Critical Weather Alert"
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
    """Main execution entry point."""
    print("Evaluating metrics from OpenWeatherMap endpoint...")
    weather_info, trigger_alert = get_weather()
    quote, author = get_quote()
    
    # Generate HTML content structure
    html_summary = build_html_summary(weather_info, quote, author)
    
    # Save a text configuration artifact log
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(html_summary)
        
    # Check conditional branch logic before firing SMTP calls
    if trigger_alert:
        print("Condition matched (High temperature/Rain). Triggering dispatch routing...")
        send_email(html_summary)
    else:
        print("Conditions standard. Alert email route bypassed for today.")
        
    print("Pulse script sequence complete.")

if __name__ == "__main__":
    run()
