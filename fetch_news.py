import os, json, requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Artık NewsAPI yok! Sadece yapay zeka şifremizi alıyoruz.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Google Haberler'de Osho aranıyor...")

# Google News'in gizli, şifresiz ve tamamen ücretsiz haber akışı
# q=osho (kelime), when:3d (son 3 gün), hl=en-US (İngilizce)
url = "https://news.google.com/rss/search?q=osho+when:3d&hl=en-US&gl=US&ceid=US:en"

response = requests.get(url)
soup = BeautifulSoup(response.content, features="xml")
items = soup.findAll('item')

sonuclar = []

# Gelen haberlerden en güncel 5 tanesini seç
for item in items[:5]:
    baslik = item.title.text
    link = item.link.text
    tarih = item.pubDate.text

    try:
        # Haberin kaynağına git ve metni kazı
        sayfa = requests.get(link, timeout=10)
        sayfa_soup = BeautifulSoup(sayfa.content, 'html.parser')
        tam_metin = " ".join([p.text for p in sayfa_soup.find_all('p')])

        if len(tam_metin) < 150:
            continue

        # Yapay Zekaya metni kaynağına sadık kalarak tam metin olarak baştan yazdır
        prompt = f"Aşağıdaki haberi kaynak metne sadık kalarak, sanki profesyonel bir bültenmiş gibi baştan yaz. Sadece haber içeriğini ver.\n\nBaşlık: {baslik}\nMetin: {tam_metin[:3000]}"
        ai_cevap = model.generate_content(prompt)

        sonuclar.append({
            "baslik": baslik,
            "link": link,
            "icerik": ai_cevap.text,
            "tarih": tarih
        })
        print(f"Başarıyla işlendi: {baslik}")
    except Exception as e:
        print(f"Atlandı (Güvenlik Duvarı/Hata): {baslik}")

# Elde edilen temiz metinleri sitenin okuyabileceği dosyaya kaydet
with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)
print("İşlem tamam! haberler.json dosyası güncellendi.")
