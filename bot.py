# Pulse - Smart Weather Alert System
# Uses OpenWeatherMap API to detect extreme heat or rain conditions

import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

def get_smart_weather(city="Thiruvananthapuram"):
    """Fetch live data from OpenWeatherMap and determine if an alert is needed."""
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        print("Weather API Key missing!")
        return None, False
    
    # URL configured to request metric units (Celsius)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract individual values from JSON structure
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"] # e.g., "Rain", "Clear", "Clouds"
        description = data["weather"][0]["description"]
        
        # Check criteria: Temp > 35 or condition matches "Rain"
        is_heat_wave = temp > 35
        is_raining = "rain" in condition.lower() or "drizzle" in condition.lower()
        
        trigger_alert = is_heat_wave or is_raining
        
        weather_info = {
            "temp": temp,
            "description": description.capitalize(),
            "is_heat_wave": is_heat_wave,
            "is_raining": is_raining,
            "city": city
        }
        
        return weather_info, trigger_alert
        
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None, False

def build_alert_html(weather):
    """Build an urgent styled HTML notice if severe conditions are met."""
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    formatted_time = ist_now.strftime("%I:%M %p IST")
    
    # Determine the status banner type
    reason = "EXTREME TEMPERATURE ALERT" if weather["is_heat_wave"] else "RAIN FORECAST DETECTED"
    banner_color = "#dc3545" if weather["is_heat_wave"] else "#007bff"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #fff5f5; margin: 0; padding: 20px; }}
            .card {{ max-width: 500px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #ffccd5; }}
            .banner {{ background-color: {banner_color}; color: #ffffff; padding: 20px; text-align: center; font-weight: bold; font-size: 18px; letter-spacing: 1px; }}
            .content {{ padding: 25px 20px; text-align: center; }}
            .metric {{ font-size: 48px; font-weight: bold; color: #333333; margin: 10px 0; }}
            .desc {{ font-size: 18px; color: #666666; text-transform: capitalize; margin-bottom: 20px; }}
            .location {{ font-size: 14px; color: #888888; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="banner">⚠️ {reason}</div>
            <div class="content">
                <p class="location">Smart Monitoring Status for <b>{weather['city']}</b></p>
                <div class="metric">{weather['temp']}°C</div>
                <div class="desc">Condition: {weather['description']}</div>
                <p style="color: #555; font-size: 13px;">Captured automatically at {formatted_time}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(html_text):
    """Send alert email directly out to receiver."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    msg = MIMEText(html_text, "html")
    msg["Subject"] = "⚠️ CRITICAL WEATHER NOTICE: Action Required"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Alert notification dispatched cleanly to your inbox.")
    except Exception as e:
        print(f"Failed dispatching mail connection: {e}")

def run():
    """Main application manager loop."""
    print("Evaluating live target metrics...")
    weather_info, trigger_alert = get_smart_weather()
    
    if weather_info and trigger_alert:
        print("Condition matched! Assembling secure layout payload...")
        alert_html = build_alert_html(weather_info)
        send_email(alert_html)
    elif weather_info:
        print(f"Conditions normal ({weather_info['temp']}°C, {weather_info['description']}). No alert needed today.")
    else:
        print("Process aborted due to monitoring network failures.")

if __name__ == "__main__":
    run()
