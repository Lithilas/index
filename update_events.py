import requests
from bs4 import BeautifulSoup

# Einame į bendrą renginių puslapį (nes ten nėra jokių blokavimų)
url = "https://sratas.lt/renginiai"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

events_found = []

# Ieškome visų nuorodų į renginius
links = soup.find_all('a', href=True)

for a in links:
    if '/renginys/' in a['href']:
        # Tikriname, ar šalia nuorodų (bloke) yra žodis "Lithilas"
        parent_text = a.find_parent('div').get_text(strip=True) if a.find_parent('div') else a.get_text(strip=True)
        if "Lithilas" in parent_text:
            title = a.get_text(strip=True)
            # Atsijojame tuščias nuorodas ar paveiksliukus
            if len(title) > 4:
                events_found.append({
                    'title': title,
                    'link': "https://sratas.lt" + a['href'] if a['href'].startswith('/') else a['href']
                })

# Išfiltruojame dublikatus
unique_events = []
seen = set()
for e in events_found:
    if e['link'] not in seen:
        seen.add(e['link'])
        unique_events.append(e)

# Formuojame gražų HTML
new_html = ""
if unique_events:
    for event in unique_events[:3]:
        new_html += f"""
            <div class="event-item" style="margin-bottom: 1.5rem; background-color: var(--card-bg); padding: 1.5rem; border-left: 5px solid var(--primary-color); border-radius: 4px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="flex: 1; min-width: 250px;">
                    <h3 style="margin-bottom: 0.5rem; font-size: 1.3rem;">{event['title']}</h3>
                    <p><a href="{event['link']}" target="_blank" style="color: #aaa; text-decoration: underline; font-size: 0.9rem;">Peržiūrėti informaciją sratas.lt</a></p>
                </div>
                <a href="{event['link']}" target="_blank" style="text-decoration: none;">
                    <button class="btn" style="white-space: nowrap; background-color: #e63946; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer;">Registruotis</button>
                </a>
            </div>
        """
else:
    new_html = "<p style='text-align: center; font-size: 1.2rem; padding: 20px; color: #aaa;'>Šiuo metu suplanuotų renginių nėra. Sekite naujienas!</p>"

# Saugiausias įmanomas failo atnaujinimas (niekada neištrins viso failo)
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "" in content and "" in content:
        # Padaliname failą į dvi dalis ir įkišame kodą tiksliai per vidurį
        part1 = content.split("")[0]
        part2 = content.split("")[1]
        
        updated_content = part1 + "\n" + new_html + "\n" + part2
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Sėkmingai atnaujinta!")
    else:
        print("Klaida: index.html faile nerasti markeriai!")
except Exception as e:
    print(f"Sistemos klaida: {e}")
