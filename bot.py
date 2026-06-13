# Pulse - Daily Summary Bot (Integrated Master Edition)
# Fetches: OpenWeatherMap JSON + ZenQuotes API + 3-Site News Scraper + GitHub REST API Engine

import os
import json
import base64
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# ==========================================
# MODULE 1: WEATHER & QUOTE ENGINES
# ==========================================
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

# ==========================================
# MODULE 2: MULTI-SITE WORLD NEWS SCRAPER
# ==========================================
def scrape_news():
    """Extract top headlines using robust tag fallback paths and direct RSS streams."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    articles = []
    current_time = datetime.now().strftime("%I:%M %p")

    # --- SITE 1: TECHCRUNCH ---
    try:
        tc_res = requests.get("https://techcrunch.com/", headers=headers, timeout=10)
        tc_soup = BeautifulSoup(tc_res.text, 'html.parser')
        tc_link = tc_soup.find("a", class_="loop-card__title-link")
        if tc_link:
            articles.append({
                "source": "TechCrunch", "title": tc_link.text.strip(), "url": tc_link["href"], "time": f"Live at {current_time}"
            })
    except Exception:
        pass

    # --- SITE 2: THE VERGE (RSS Fail-Safe) ---
    try:
        verge_feed = requests.get("https://www.theverge.com/rss/index.xml", headers=headers, timeout=10)
        root = ET.fromstring(verge_feed.content)
        entry = root.find("{http://www.w3.org/2005/Atom}entry")
        if entry is not None:
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            link_node = entry.find("{http://www.w3.org/2005/Atom}link")
            url = link_node.attrib["href"] if link_node is not None else "https://www.theverge.com"
            articles.append({
                "source": "The Verge", "title": title.strip(), "url": url, "time": f"Live at {current_time}"
            })
    except Exception:
        pass

    # --- SITE 3: BBC NEWS ---
    try:
        bbc_res = requests.get("https://www.bbc.com/news", headers=headers, timeout=10)
        bbc_soup = BeautifulSoup(bbc_res.text, 'html.parser')
        bbc_link = bbc_soup.find("a", class_=lambda x: x and 'PromoLink' in x)
        if not bbc_link:
            bbc_heading = bbc_soup.find("h2")
            if bbc_heading:
                bbc_link = bbc_heading.find_parent("a") or bbc_heading.find("a")
        if bbc_link:
            url = bbc_link.get("href", "")
            if url.startswith("/"):
                url = "https://www.bbc.com" + url
            title_text = bbc_link.text.strip() or bbc_link.find("h2").text.strip()
            articles.append({
                "source": "BBC News", "title": title_text, "url": url, "time": f"Live at {current_time}"
            })
    except Exception:
        pass

    return articles

def build_briefing_html(weather, quote_text, quote_author, news_list):
    """Assemble an advanced morning briefing dashboard card layout."""
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
    for item in news_list:
        news_html_blocks += f"""
        <div class="news-item">
            <span class="news-source">{item['source']}</span>
            <span class="news-time">{item['time']}</span>
            <a class="news-title" href="{item['url']}" target="_blank">{item['title']}</a>
        </div>
        """

    return f"""
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
            <div class="footer">
                Pulse Hub Master Engine V4.0 • Built from Zero 🎈
            </div>
        </div>
    </body>
    </html>
    """

def send_email(html_text):
    """Send out the master briefing dashboard email."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    if not sender or not password:
        return
    
    msg = MIMEText(html_text, "html")
    msg["Subject"] = "☀️ Your Complete Pulse Morning Briefing Dashboard"
    msg["From"] = sender
    msg["To"] = receiver
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Briefing dashboard email sent cleanly!")
    except Exception as e:
        print(f"SMTP Error: {e}")

# ==========================================
# MODULE 3: PORTFOLIO SYNCHRONIZATION ENGINE
# ==========================================
def synchronize_portfolio():
    """Fetch repositories via GitHub REST API and automatically update projects.json."""
    token = os.environ.get("GITHUB_TOKEN")
    repo_slug = os.environ.get("GITHUB_REPOSITORY")
    
    if not token or not repo_slug:
        print("GitHub Automation Engine offline: GITHUB_TOKEN missing.")
        return
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    print("Connecting to GitHub REST API Engine...")
    url = "https://api.github.com/user/repos?type=public&sort=updated"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        repos_data = response.json()
        
        projects_list = []
        for repo in repos_data:
            if repo["fork"]:
                continue
            
            project_node = {
                "id": repo["id"],
                "name": repo["name"].replace("-", " ").title(),
                "description": repo["description"] or "An engineering project built from scratch.",
                "url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "language": repo["language"] or "Tech Stack Stacked",
                "updated_at": repo["updated_at"].split("T")[0]
            }
            projects_list.append(project_node)
            
        print(f"Compiled database map for {len(projects_list)} original public projects.")
        
        json_content = json.dumps(projects_list, indent=2)
        base64_bytes = base64.b64encode(json_content.encode("utf-8"))
        base64_string = base64_bytes.decode("utf-8")
        
        target_path = "projects.json"
        content_url = f"https://api.github.com/repos/{repo_slug}/contents/{target_path}"
        
        sha = None
        check_res = requests.get(content_url, headers=headers, timeout=10)
        if check_res.status_code == 200:
            sha = check_res.json()["sha"]
            
        payload = {
            "message": "system(bot): automated portfolio projects.json tree sync [skip ci]",
            "content": base64_string
        }
        if sha:
            payload["sha"] = sha
            
        print("Committing dynamic structured asset array to main tree branch...")
        upload_res = requests.put(content_url, headers=headers, json=payload, timeout=10)
        upload_res.raise_for_status()
        print("Portfolio tracking index asset successfully refreshed!")
        
    except Exception as e:
        print(f"Portfolio Sync Operation crashed: {e}")

# ==========================================
# MASTER TASK AGGREGATOR CONTROLLER
# ==========================================
def run():
    run_mode = os.environ.get("RUN_MODE", "SUMMARY")
    
    if run_mode == "SYNC":
        print("=== EXECUTING OPERATION: PORTFOLIO SYNCHRONIZATION ENGINE ===")
        synchronize_portfolio()
    else:
        print("=== EXECUTING OPERATION: MORNING BRIEFING PAYLOAD SYSTEM ===")
        weather_info, _ = get_smart_weather()
        quote, author = get_quote()
        news_highlights = scrape_news()
        
        html_layout = build_briefing_html(weather_info, quote, author, news_highlights)
        
        with open("daily_summary.txt", "w", encoding="utf-8") as f:
            f.write(html_layout)
            
        send_email(html_layout)
        
    print("All tracking pipeline tasks concluded smoothly.")

if __name__ == "__main__":
    run()
