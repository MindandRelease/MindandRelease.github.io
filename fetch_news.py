import os, json, requests
import google.generativeai as genai

# Şifreleri çek
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Reddit JSON API'sine bağlanılıyor...")

# Reddit'in doğrudan JSON kanalı. RSS'den bin kat daha sağlamdır.
# /new.json?limit=5 diyerek en taze 5 gönderiyi istiyoruz.
url = "https://www.reddit.com/r/Osho/new.json?limit=5"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

sonuclar = []

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    # Reddit'in JSON yapısı: data -> children -> [her bir gönderi]
    posts = data['data']['children']
    
    for post in posts:
        p_data = post['data']
        baslik = p_data.get('title', 'Başlıksız')
        link = f"https://www.reddit.com{p_data.get('permalink', '')}"
        ozet = p_data.get('selftext', '')[:500] # Gönderi içeriği
        
        # Yapay Zeka özetlemesi
        prompt = f"Şu Reddit paylaşımını profesyonelce özetle: '{baslik}'. İçerik: {ozet}. 3-4 cümlelik temiz bir metin yaz."
        
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
            sonuclar.append({"baslik": baslik, "link": link, "icerik": "Özet alınamadı.", "tarih": "Reddit"})

except Exception as e:
    print(f"Kritik Hata: {e}")
    sonuclar.append({"baslik": "Hata", "link": "#", "icerik": f"Veri çekilemedi: {str(e)}", "tarih": "Hata"})

# JSON dosyasına yaz
with open('haberler.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=4)

print("İşlem tamam!")
