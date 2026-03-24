import requests
from bs4 import BeautifulSoup
import re

url = "https://sratas.lt/organizators/72"
# Pridedame "User-Agent", kad sratas.lt galvotų, jog čia tikra naršyklė, o ne robotas
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
html_content = response.text

# 1. Iškerpame TIK būsimų renginių sekciją, naudodami Regex (ignoruoja didžiąsias/mažąsias raides)
start_match = re.search(r'(?i)būsimi\s+renginiai', html_content)
end_match = re.search(r'(?i)praėję\s+renginiai|žaidėjų\s+įvertinimai', html_content)

if start_match:
    start_pos = start_match.end()
    end_pos = end_match.start() if end_match else len(html_content)
    future_html = html_content[start_pos:end_pos]
else:
    future_html = html_content # Jei neranda markerių, naudoja visą kodą

soup = BeautifulSoup(future_html, 'html.parser')

# 2. Ieškome visų nuorodų, turinčių "/renginys/"
links = soup.find_all('a', href=re.compile(r'/renginys/'))

# 3. Išfiltruojame dublikatus ir tuščius paveiksliukų linkus
events_dict = {}
for a in links:
    href = a.get('href')
    # Išvalome nereikalingus tarpus iš teksto
    text = " ".join(a.get_text(strip=True).split())
    
    # Saugome tik tą nuorodą, kuri turi ilgiausią tekstą (tikrąjį pavadinimą)
    if href not in events_dict or len(text) > len(events_dict[href]):
        events_dict[href] = text

new_html = ""

# Atrenkame tik tuos, kur tekstas ilgesnis nei 3 raidės (atmeta šiukšles)
valid_events = {k: v for k, v in events_dict.items() if len(v) > 3}

# 4. Formuojame HTML
if valid_events:
    for href, title in list(valid_events.items())[:3]: # Paimame iki 3 renginių
        link = "https://sratas.lt" + href if href.startswith('/') else href
        new_html += f"""
            <div class="event-item" style="margin-bottom: 1.5rem; background-color: var(--card-bg); padding: 1.5rem; border-left: 5px solid var(--primary-color); border-radius: 4px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="flex: 1; min-width: 250px;">
                    <h3 style="margin-bottom: 0.5rem; font-size: 1.3rem;">{title}</h3>
                    <p><a href="{link}" target="_blank" style="color: #aaa; text-decoration: underline; font-size: 0.9rem;">Peržiūrėti informaciją sratas.lt</a></p>
                </div>
                <a href="{link}" target="_blank" style="text-decoration: none;">
                    <button class="btn" style="white-space: nowrap;">Registruotis</button>
                </a>
            </div>
        """
else:
    new_html = "<p style='text-align: center; font-size: 1.2rem; padding: 20px; color: #aaa;'>Šiuo metu suplanuotų renginių nėra. Sekite naujienas!</p>"

# 5. Atnaujiname index.html
try:
    with open('index.html', 'r', encoding='utf-8') as file:
        original_html = file.read()

    updated_html = re.sub(
        r'().*?()',
        f'\\1\n{new_html}\n\\2',
        original_html,
        flags=re.DOTALL
    )

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(updated_html)
    print("Skriptas baigė darbą sėkmingai!")
except Exception as e:
    print(f"Klaida įrašant failą: {e}")
