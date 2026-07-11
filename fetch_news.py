import os, json, requests
import google.generativeai as genai

# Şifremizi alıyoruz
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("RSS köprüsü üzerinden Google Haberler çekiliyor...")

# Terminalde çalışan Google RSS linkimiz
rss_url = "https://news.google.com/rss/search?q=osho+when:3d&hl=en-US&gl=US&ceid=US:en"

# GitHub'ın IP engeline takılmamak için ücretsiz rss2json köprüsünü kullanıyoruz
response = requests.get("https://api.rss2json.com/v1/api.json", params={"rss_url": rss_url})
data = response.json()
items = data.get('items', [])

if not items:
    print("Uyarı: Haber bulunamadı.")

sonuclar = []

# En güncel 5 haberi al
for item in items[:5]:
    baslik = item.get('title', '')
    link = item.get('link', '')
    tarih = item.get('pubDate', '')
    ozet = item.get('description', '')

    # Sitelere tek tek girmek yerine, elimizdeki güçlü haber özeti ve başlıkla
    # Yapay Zekaya profesyonel bir tam metin yazdırıyoruz.
    prompt = f"Elimde şu haberin başlığı ve kısa özeti var.\nBaşlık: '{baslik}'\nÖzet: '{ozet}'\nBu bilgilere dayanarak, haberi okuyan kişiye bilgi verecek profesyonel, 3-4 cümlelik temiz bir haber metni oluştur."

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

with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)
    
print("İşlem tamam! haberler.json dosyası güncellendi.")
