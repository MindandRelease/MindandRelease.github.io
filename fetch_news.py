import os, json, requests
import xml.etree.ElementTree as ET
import google.generativeai as genai

# Şifreleri al
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("RSS-Bridge üzerinden Reddit akışı çekiliyor...")

# RSS-Bridge'in halka açık bir örneği (Tamamen ücretsiz ve sınırsız)
url = "https://rss-bridge.org/bridge01/?action=display&bridge=Reddit&context=subreddit&subreddit=Osho&format=Xml"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

sonuclar = []

try:
    # Şimdi Reddit değil, RSS-Bridge'e bağlanıyoruz
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    
    root = ET.fromstring(response.content)
    items = root.findall('.//item')

    for item in items[:5]:
        baslik = item.find('title').text if item.find('title') is not None else "Başlıksız"
        link = item.find('link').text if item.find('link') is not None else ""
        ozet = item.find('description').text if item.find('description') is not None else ""
        
        # Yapay zekaya gönder
        prompt = f"Reddit paylaşımını özetle: Başlık: '{baslik}'. İçerik: {ozet[:300]}. 3 cümlelik, sade bir özet yaz."
        
        try:
            ai_cevap = model.generate_content(prompt)
            sonuclar.append({
                "baslik": baslik,
                "link": link,
                "icerik": ai_cevap.text.strip(),
                "tarih": "Reddit"
            })
        except Exception:
            sonuclar.append({"baslik": baslik, "link": link, "icerik": "Özet alınamadı.", "tarih": "Reddit"})

except Exception as e:
    print(f"Hata: {e}")
    sonuclar.append({"baslik": "Hata", "link": "#", "icerik": f"RSS-Bridge hatası: {str(e)}", "tarih": "Hata"})

with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)
