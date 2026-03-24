import requests
from bs4 import BeautifulSoup
import re

url = "https://sratas.lt/organizators/72"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html_text = response.text

# 1. NUPJAUNAME viską, kas yra po žodžių "Praėję renginiai".
# Taip garantuojame, kad skriptas netyčia nepaims senų žaidimų!
if "Praėję renginiai" in html_text:
    html_text = html_text.split("Praėję renginiai")[0]
elif "Praėję žaidimai" in html_text:
    html_text = html_text.split("Praėję žaidimai")[0]

soup = BeautifulSoup(html_text, 'html.parser')

# 2. Dabar ieškome renginių nuorodų tik likusioje (viršutinėje) puslapio dalyje
events = soup.find_all('a', href=re.compile(r'/renginys/'))

new_html = ""

# Jei randa BŪSIMŲ renginių
if events:
    # Išfiltruojame dublikatus (nes sratas.lt kartais tą pačią nuorodą deda 2 kartus - ant foto ir ant teksto)
    seen_links = set()
    unique_events = []
    for event in events:
        if event['href'] not in seen_links:
            seen_links.add(event['href'])
            unique_events.append(event)
            
    # Imame iki 3 artimiausių renginių
    for event in unique_events[:3]:
        title = event.text.strip()
        if not title:
            title = "Airsoft Žaidimas"
            
        link = "https://sratas.lt" + event['href']
        
        new_html += f"""
            <div class="event-item">
                <div>
                    <h3>{title}</h3>
                    <p><a href="{link}" target="_blank" style="color: #e63946; text-decoration: underline;">Daugiau informacijos sratas.lt</a></p>
                </div>
                <a href="{link}" target="_blank"><button class="btn">Registruotis</button></a>
            </div>
        """
else:
    # Jei būsimų renginių nerasta
    new_html = "<p style='text-align: center; font-size: 1.2rem; padding: 20px;'>Šiuo metu suplanuotų renginių nėra. Sekite naujienas!</p>"

# 3. Atnaujiname tavo index.html failą
with open('index.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Saugiai įklijuojame tekstą tarp tavo markerių (niekas nebesusidubliuos)
updated_html = re.sub(
    r'().*?()',
    f'\\1\n{new_html}\n\\2',
    html_content,
    flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as file:
    file.write(updated_html)

print("Renginiai sėkmingai atnaujinti!")
