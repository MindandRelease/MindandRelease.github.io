import os, json, requests
from bs4 import BeautifulSoup
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Google Haberler'de arama yapılıyor...")

# Terminalden çalıştığını teyit ettiğimiz Google RSS linki
url = "https://news.google.com/rss/search?q=osho+when:3d&hl=en-US&gl=US&ceid=US:en"

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
    
    tam_metin = ""
    try:
        sayfa = requests.get(link, headers=headers, timeout=10)
        sayfa_soup = BeautifulSoup(sayfa.content, 'html.parser')
        tam_metin = " ".join([p.text for p in sayfa_soup.find_all('p')])
    except Exception:
        pass # Hata verirse sessizce geç, çünkü B planımız var

    # B PLANIMIZ: Eğer metni başarıyla çekerse metni kullanarak, 
    # çekemezse SADECE başlığı kullanarak yapay zekaya haber yazdır.
    if len(tam_metin) > 150:
        prompt = f"Aşağıdaki haberi kaynak metne sadık kalarak, sanki profesyonel bir bültenmiş gibi baştan yaz. Sadece haber içeriğini ver.\n\nBaşlık: {baslik}\nMetin: {tam_metin[:3000]}"
    else:
        prompt = f"Elimde sadece şu haber başlığı var: '{baslik}'. Sadece bu başlığa dayanarak, sanki bir haber bülteni sunuyormuş gibi profesyonel, 3-4 cümlelik bir haber özeti metni yaz. Haberin içeriğini mantıksal olarak tahmin et."

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
