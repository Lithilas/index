import requests
from bs4 import BeautifulSoup
import re

url = "https://sratas.lt/organizators/72"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
html_text = response.text

# Atskiriame tik būsimus renginius
if "BŪSIMI RENGINIAI" in html_text:
    future_html = html_text.split("BŪSIMI RENGINIAI")[1]
    if "Praėję renginiai" in future_html:
        future_html = future_html.split("Praėję renginiai")[0]
else:
    future_html = html_text

soup = BeautifulSoup(future_html, 'html.parser')
links = soup.find_all('a', href=re.compile(r'/renginys/'))

events_dict = {}
for a in links:
    href = a.get('href')
    text = " ".join(a.get_text(strip=True).split())
    if href not in events_dict or len(text) > len(events_dict.get(href, "")):
        events_dict[href] = text

new_html = ""
valid_events = {k: v for k, v in events_dict.items() if len(v) > 3}

if valid_events:
    for href, title in list(valid_events.items())[:3]:
        link = "https://sratas.lt" + href if href.startswith('/') else href
        new_html += f"""
            <div class="event-item" style="margin-bottom: 1.5rem; background-color: var(--card-bg); padding: 1.5rem; border-left: 5px solid var(--primary-color); border-radius: 4px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="flex: 1; min-width: 250px;">
                    <h3 style="margin-bottom: 0.5rem; font-size: 1.3rem;">{title}</h3>
                    <p><a href="{link}" target="_blank" style="color: #aaa; text-decoration: underline; font-size: 0.9rem;">Peržiūrėti informaciją sratas.lt</a></p>
                </div>
                <a href="{link}" target="_blank" style="text-decoration: none;">
                    <button class="btn" style="white-space: nowrap; background-color: #e63946; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer;">Registruotis</button>
                </a>
            </div>
        """
else:
    new_html = "<p style='text-align: center; font-size: 1.2rem; padding: 20px; color: #aaa;'>Šiuo metu suplanuotų renginių nėra.</p>"

# Atnaujiname index.html failą
try:
    with open('index.html', 'r', encoding='utf-8') as file:
        original_html = file.read()

    # Saugus teksto pakeitimas
    updated_html = re.sub(
        r'().*?()',
        f'\n{new_html}\n',
        original_html,
        flags=re.DOTALL
    )

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(updated_html)
        
except Exception as e:
    print(f"Klaida: {e}")
