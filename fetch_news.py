import os, json, requests
from bs4 import BeautifulSoup
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Bing Haberler'de arama yapılıyor...")

# Bing News RSS: Doğrudan haber sitelerinin orijinal linklerini verir (Google gibi araya girmez)
url = "https://www.bing.com/news/search?q=osho&format=rss"

# Haber siteleri botumuzu engellemesin diye kendimizi normal bir tarayıcı (Chrome) gibi gösteriyoruz
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, features="xml")
items = soup.findAll('item')

sonuclar = []

for item in items[:5]:
    baslik = item.title.text
    link = item.link.text
    tarih = item.pubDate.text
    
    # Bazı RSS'lerde description olmayabilir, sistem çökmesin diye kontrol ediyoruz
    ozet = item.description.text if item.description else "" 

    tam_metin = ""
    try:
        # Haberin orijinal sitesine git ve metni al
        sayfa = requests.get(link, headers=headers, timeout=10)
        sayfa_soup = BeautifulSoup(sayfa.content, 'html.parser')
        tam_metin = " ".join([p.text for p in sayfa_soup.find_all('p')])
    except Exception as e:
        print(f"Haber sitesine girilemedi, sadece özetle yetinilecek: {link}")

    # <150 karakter engelini kaldırdık. 
    # Site engellese bile elimizdeki başlık ve kısa özetle yapay zekaya haber yazdıracağız.
    prompt = f"Aşağıdaki bilgileri kullanarak, sanki profesyonel bir haber bülteniymiş gibi temiz bir metin oluştur. Sadece haberin metnini ver, başka açıklama yapma.\n\nBaşlık: {baslik}\nKısa Özet: {ozet}\nDetaylı Metin (varsa): {tam_metin[:3000]}"
    
    try:
        ai_cevap = model.generate_content(prompt)
        sonuclar.append({
            "baslik": baslik,
            "link": link,
            "icerik": ai_cevap.text.strip(),
            "tarih": tarih
        })
        print(f"Başarıyla işlendi: {baslik}")
    except Exception as e:
        print(f"Yapay Zeka Hatası ({baslik}): {e}")

# Dosyayı kaydet
with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)
    
print("İşlem tamam! haberler.json dosyası güncellendi.")
