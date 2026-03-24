import requests
from bs4 import BeautifulSoup
import re

# 1. Nuskaitome sratas.lt puslapį
url = "https://sratas.lt/organizators/72"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# ČIA GALI REIKĖTI KOREKCIJŲ PAGAL SRATAS.LT DIZAINĄ
# Ieškome renginių blokų. Dažniausiai tai būna <a> tagai su renginio klase arba <div> blokai
# Pavyzdžiui, bandome rasti visus blokus, kurie turi nuorodas į renginius
events = soup.find_all('a', href=re.compile(r'/renginys/')) 

new_html = ""

# Jei randa renginių, formuojame tavo HTML
if events:
    # Imam tik pirmi 3 ar 4 renginius, kad neperpildytume puslapio
    for event in events[:3]:
        title = event.text.strip()
        link = "https://sratas.lt" + event['href']
        
        # Generuojame HTML tavo puslapiui
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
    new_html = "<p style='text-align: center;'>Šiuo metu suplanuotų renginių nėra.</p>"

# 2. Atnaujiname tavo index.html failą
with open('index.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Įklijuojame naujus renginius tarp marker'ių
updated_html = re.sub(
    r'().*?()',
    rf'\1\n{new_html}\n\2',
    html_content,
    flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as file:
    file.write(updated_html)

print("Renginiai sėkmingai atnaujinti!")
