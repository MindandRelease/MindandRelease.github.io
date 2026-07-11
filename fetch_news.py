import os, json, requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime, timedelta

# 1. Şifreleri GitHub'ın gizli kasasından çekiyoruz
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Son 3 günün tarihini hesapla
baslangic = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')

print("Haberler aranıyor...")
# 3. Sadece İngilizce içerikleri NewsAPI üzerinden bul
url = f"https://newsapi.org/v2/everything?q=osho&language=en&from={baslangic}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
response = requests.get(url).json()

sonuclar = []

# Botu yormamak ve GitHub limitlerine takılmamak için en güncel 5 haberi işleyelim
for article in response.get('articles', [])[:5]:
    baslik = article.get('title')
    link = article.get('url')

    try:
        # Haberin kaynağına git ve metni kazı
        sayfa = requests.get(link, timeout=10)
        soup = BeautifulSoup(sayfa.content, 'html.parser')
        tam_metin = " ".join([p.text for p in soup.find_all('p')])

        if len(tam_metin) < 150:
            continue # Boş veya çok kısa içerikleri atla

        # Yapay Zekaya metni kaynağına sadık kalarak tam metin olarak baştan yazdır
        # (Eğer çıktıları İngilizce istiyorsan buradaki Türkçe talimatı İngilizceye çevirebilirsin)
        prompt = f"Aşağıdaki haberi kaynak metne sadık kalarak, sanki profesyonel bir bültenmiş gibi baştan yaz. Sadece haber içeriğini ver.\n\nBaşlık: {baslik}\nMetin: {tam_metin[:3000]}"
        ai_cevap = model.generate_content(prompt)

        sonuclar.append({
            "baslik": baslik,
            "link": link,
            "icerik": ai_cevap.text,
            "tarih": article.get('publishedAt')
        })
        print(f"Başarıyla işlendi: {baslik}")
    except Exception as e:
        print(f"Atlandı (Güvenlik Duvarı/Hata): {baslik}")

# 4. Elde edilen tüm temiz metinleri sitenin okuyabileceği bir dosyaya kaydet
with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)
print("İşlem tamam! haberler.json dosyası güncellendi.")