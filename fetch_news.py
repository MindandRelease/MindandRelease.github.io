import os, json, requests
import xml.etree.ElementTree as ET
import google.generativeai as genai

# Şifre Kontrolü
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Reddit (r/Osho) RSS çekiliyor...")

# Reddit RSS linki
url = "https://www.reddit.com/r/Osho/.rss"

# Reddit'e "Ben bir tarayıcıyım" diye kendimizi tanıtıyoruz
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

sonuclar = []

try:
    response = requests.get(url, headers=headers, timeout=15)
    root = ET.fromstring(response.content)
    # Reddit RSS yapısında <item> etiketleri <entry> (Atom feed) olarak görünebilir veya <item> olabilir.
    # r/Osho için standart RSS kullanıyoruz:
    items = root.findall('.//item')

    if not items:
        print("Uyarı: Reddit akışında içerik bulunamadı.")
    else:
        for item in items[:5]:
            baslik = item.find('title').text if item.find('title') is not None else "Başlıksız"
            link = item.find('link').text if item.find('link') is not None else ""
            ozet = item.find('description').text if item.find('description') is not None else ""
            
            # Reddit başlıkları bazen çok uzun veya karmaşık olabilir, temizletelim
            prompt = f"Şu Reddit paylaşımını profesyonel bir haber özeti gibi temizle: '{baslik}'. Paylaşım içeriği: {ozet[:500]}. 3-4 cümleyle özetle."
            
            try:
                ai_cevap = model.generate_content(prompt)
                sonuclar.append({
                    "baslik": baslik,
                    "link": link,
                    "icerik": ai_cevap.text.strip(),
                    "tarih": "Reddit"
                })
                print(f"Eklendi: {baslik}")
            except Exception as e:
                print(f"AI Hatası: {e}")

except Exception as e:
    print(f"Kritik Hata: {e}")
    sonuclar.append({"hata": f"Sistem hatası: {str(e)}"})

with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)

print("İşlem tamamlandı, Reddit verileri JSON'a yazıldı.")
