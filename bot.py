
import os
import requests
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from datetime import datetime, timedelta

def get_smart_weather(city="Thiruvananthapuram"):
    """Fetch live data from OpenWeatherMap."""
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key or "PASTE_YOUR_ACTUAL" in api_key:
        return None, False
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"]
        
        is_heat_wave = temp > 10 # Testing threshold
        is_raining = "rain" in condition.lower() or "drizzle" in condition.lower()
        trigger_alert = is_heat_wave or is_raining
        
        return {
            "temp": round(temp, 1),
            "condition": condition,
            "description": description.capitalize(),
            "city": city,
            "is_heat_wave": is_heat_wave,
            "is_raining": is_raining
        }, trigger_alert
    except Exception:
        return None, False

def get_quote():
    """Fetch random daily motivational quote."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data[0]["q"], data[0]["a"]
    except Exception:
        return "Focus on building great systems daily.", "Engineering Mind"

def scrape_news():
    """Scrape top headlines from BBC, TechCrunch, and The Verge with multi-tag fallback paths."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    articles = []
    current_time = datetime.now().strftime("%I:%M %p")

    # --- SITE 1: TECHCRUNCH ---
    try:
        tc_res = requests.get("https://techcrunch.com/", headers=headers, timeout=10)
        tc_soup = BeautifulSoup(tc_res.text, 'html.parser')
        tc_link = tc_soup.find("a", class_="loop-card__title-link")
        if tc_link:
            articles.append({
                "source": "TechCrunch",
                "title": tc_link.text.strip(),
                "url": tc_link["href"],
                "time": f"Live at {current_time}"
            })
    except Exception as e:
        print(f"TechCrunch scrape issue: {e}")

    # --- SITE 2: THE VERGE ---
    try:
        verge_res = requests.get("https://www.theverge.com/", headers=headers, timeout=10)
        verge_soup = BeautifulSoup(verge_res.text, 'html.parser')
        verge_h2 = verge_soup.find("h2")
        verge_link = verge_h2.find("a") if verge_h2 else None
        if verge_link:
            url = verge_link["href"]
            if url.startswith("/"):
                url = "https://www.theverge.com" + url
            articles.append({
                "source": "The Verge",
                "title": verge_link.text.strip(),
                "url": url,
                "time": f"Live at {current_time}"
            })
    except Exception as e:
        print(f"The Verge scrape issue: {e}")

    # --- SITE 3: BBC NEWS ---
    try:
        bbc_res = requests.get("https://www.bbc.com/news", headers=headers, timeout=10)
        bbc_soup = BeautifulSoup(bbc_res.text, 'html.parser')
        
        # Primary Selector Check: Search for standard promo link wrapper nodes
        bbc_link = bbc_soup.find("a", class_=lambda x: x and 'PromoLink' in x)
        
        # Alternate Selector Check: Search for generic structural anchors if specific class wrapper falls behind
        if not bbc_link:
            bbc_heading = bbc_soup.find("h2")
            if bbc_heading:
                bbc_link = bbc_heading.find_parent("a") or bbc_heading.find("a")
                
        if bbc_link:
            url = bbc_link.get("href", "")
            if url.startswith("/"):
                url = "https://www.bbc.com" + url
                
            # Extract readable headline block text
            title_text = bbc_link.text.strip()
            if not title_text and bbc_link.find("h2"):
                title_text = bbc_link.find("h2").text.strip()
                
            if title_text:
                articles.append({
                    "source": "BBC News",
                    "title": title_text,
                    "url": url,
                    "time": f"Live at {current_time}"
                })
    except Exception as e:
        print(f"BBC Scrape failure: {e}")

    return articles

def build_briefing_html(weather, quote_text, quote_author, news_list):
    """Assemble an advanced, gorgeous morning briefing dashboard card layout."""
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    
    formatted_date = ist_now.strftime("%A, %d %B %Y")
    formatted_time = ist_now.strftime("%I:%M %p")
    
    if weather and weather["temp"] > 35:
        banner_title = "🔥 EXTREME HEAT BRIEFING 🔥"
        gradient = "linear-gradient(135deg, #F857A6, #FF5858)"
    elif weather and weather["is_raining"]:
        banner_title = "🌧️ RAINY MORNING BRIEFING 🌧️"
        gradient = "linear-gradient(135deg, #4facfe, #00f2fe)"
    else:
        banner_title = "✨ YOUR MORNING PULSE ✨"
        gradient = "linear-gradient(135deg, #FF416C, #FF4B2B)"
        
    weather_display = f"{weather['temp']}°C, {weather['description']}" if weather else "Weather Metrics Standby"
    city_name = weather['city'] if weather else "Thiruvananthapuram"

    news_html_blocks = ""
    if news_list:
        for item in news_list:
            news_html_blocks += f"""
            <div class="news-item">
                <span class="news-source">{item['source']}</span>
                <span class="news-time">{item['time']}</span>
                <a class="news-title" href="{item['url']}" target="_blank">{item['title']}</a>
            </div>
            """
    else:
        news_html_blocks = "<div class='news-item' style='border-left-color: #ef4444;'>⚠️ Scraping engines matches structural update downtime.</div>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f4f8; color: #2d3748; margin: 0; padding: 20px 10px; }}
            .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; border: 2px solid #e2e8f0; }}
            .header {{ background: {gradient}; color: #ffffff; padding: 35px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 1.5px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .header .date {{ margin: 8px 0 0 0; opacity: 0.95; font-size: 13px; font-weight: 600; background: rgba(255,255,255,0.2); display: inline-block; padding: 4px 14px; border-radius: 20px; }}
            .content {{ padding: 25px 20px; }}
            .section {{ margin-bottom: 24px; }}
            .section-title {{ font-size: 12px; font-weight: 800; color: #FF416C; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; }}
            .weather-box {{ font-size: 15px; color: #4a5568; padding: 14px; border-radius: 14px; font-weight: bold; border: 2px dashed #ff416c; background: #fff5f7; }}
            .quote-box {{ font-style: italic; font-size: 15px; color: #1a202c; line-height: 1.5; background: #fffbeb; padding: 14px; border-radius: 14px; border: 1px dashed #fcd34d; margin: 0; }}
            .author {{ display: block; text-align: right; margin-top: 6px; font-size: 11px; color: #718096; font-style: normal; font-weight: 700; }}
            .news-item {{ padding: 14px; background: #f8fafc; border-radius: 14px; border-left: 4px solid #4facfe; margin-bottom: 10px; }}
            .news-source {{ font-size: 10px; font-weight: 800; background: #e2e8f0; padding: 2px 8px; border-radius: 10px; color: #4a5568; }}
            .news-time {{ font-size: 10px; color: #94a3b8; margin-left: 6px; font-weight: bold; }}
            .news-title {{ display: block; margin-top: 6px; font-size: 14px; font-weight: 700; color: #1e293b; text-decoration: none; line-height: 1.4; }}
            .footer {{ background: #f8fafc; text-align: center; padding: 15px; font-size: 11px; color: #94a3b8; border-top: 2px solid #f1f5f9; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>{banner_title}</h1>
                <div class="date">📅 {formatted_date} | ⏰ {formatted_time} IST</div>
            </div>
            <div class="content">
                <div class="section">
                    <div class="section-title">🌤️ Atmosphere Metrics ({city_name})</div>
                    <div class="weather-box">{weather_display}</div>
                </div>
                <div class="section">
                    <div class="section-title">📰 World Headlines Radar</div>
                    {news_html_blocks}
                </div>
                <div class="section">
                    <div class="section-title">💡 Morning Spark</div>
                    <blockquote class="quote-box">
                        "{quote_text}"
                        <span class="author">⚡ {quote_author}</span>
                    </blockquote>
                </div>
            </div>
            . <div class="footer">
                Pulse Hub Engine V3.1 • GitHub Actions 🎈
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(html_text):
    """Log into Gmail and send out the master briefing dashboard email."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    msg = MIMEText(html_text, "html")
    msg["Subject"] = "☀️ Your Complete Pulse Morning Briefing Dashboard"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Complete briefing dashboard emailed successfully!")
    except Exception as e:
        print(f"SMTP Connection failure: {e}")

def run():
    """Main execution entry loop."""
    print("Launching dynamic web scraping blocks...")
    weather_info, trigger_alert = get_smart_weather()
    quote, author = get_quote()
    news_highlights = scrape_news()
    
    print(f"Scraper processed {len(news_highlights)} source blocks successfully.")
    
    html_layout = build_briefing_html(weather_info, quote, author, news_highlights)
    
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(html_layout)
        
    send_email(html_layout)
    print("Briefing engine cycle closed out.")

if __name__ == "__main__":
    run()
