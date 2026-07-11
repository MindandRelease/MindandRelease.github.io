import os, json, requests
import xml.etree.ElementTree as ET
import google.generativeai as genai

# 1. Şifre Kontrolü
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("HATA: GEMINI_API_KEY bulunamadı!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Google Haberler RSS doğrudan çekiliyor (Aracısız)...")

# Orijinal Google News Linkimiz
url = "https://news.google.com/rss/search?q=osho+when:3d&hl=en-US&gl=US&ceid=US:en"

# Google'ın bizi GitHub botu sanmasını engellemek için güçlü tarayıcı kimliği
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

sonuclar = []

try:
    # Aracı kullanmadan doğrudan Google'a gidiyoruz
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status() # Bağlantı hatası varsa yakalar

    # Gelen XML verisini Python'un yerleşik aracıyla okuyoruz
    root = ET.fromstring(response.content)
    items = root.findall('.//item')

    if not items:
        print("Uyarı: Google bağlantısı başarılı ama son 3 günde haber yok.")
        sonuclar.append({"hata": "Google RSS çekildi ancak aranılan kelimeyle ilgili yeni haber bulunamadı."})
    else:
        print(f"Bulunan haber sayısı: {len(items)}")
        
        for item in items[:5]:
            # XML içindeki etiketleri güvenli bir şekilde al
            baslik = item.find('title').text if item.find('title') is not None else "Başlıksız"
            link = item.find('link').text if item.find('link') is not None else ""
            tarih = item.find('pubDate').text if item.find('pubDate') is not None else ""

            # Yapay Zekaya sadece başlığı göndererek haberi baştan yazdırıyoruz
            prompt = f"Elimde şu haberin başlığı var: '{baslik}'. Bu bilgiye dayanarak, haberi okuyan kişiye bilgi verecek profesyonel, 3-4 cümlelik temiz bir haber metni oluştur."
            
            try:
                ai_cevap = model.generate_content(prompt)
                sonuclar.append({
                    "baslik": baslik,
                    "link": link,
                    "icerik": ai_cevap.text.strip(),
                    "tarih": tarih
                })
                print(f"Eklendi: {baslik}")
            except Exception as e:
                print(f"Yapay Zeka Hatası ({baslik}): {e}")
                sonuclar.append({
                    "baslik": baslik, 
                    "link": link, 
                    "icerik": "Yapay zeka özeti alınamadı.", 
                    "tarih": tarih
                })

except Exception as e:
    print(f"Kritik Hata: {e}")
    # Sistem çökerse JSON boş kalmasın, hatayı siteye yansıtsın
    sonuclar.append({"hata": f"Sistem hatası: {str(e)}"})

# JSON dosyasını oluştur ve kaydet
with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)

print("İşlem tamamlandı, JSON güncellendi.")
