import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
import random
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

st.set_page_config(
    page_title="BorsaLab",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# OYUN VERİLERİ
# -----------------------------------------------------------------------------
STARTING_CASH = 100_000.0
INITIAL_PRICE = 100.0

COMPANIES = {
    "Nova Teknoloji": {
        "symbol": "NOVA",
        "sector": "Teknoloji",
        "sales": "+%24",
        "profitability": "Yüksek fakat dalgalı",
        "debt": "Yüksek",
        "year_change": "+%68",
        "description": "Yapay zekâ ve kurumsal yazılım çözümleri geliştiren hızlı büyüyen bir şirket.",
        "icon": "💻",
    },
    "Güven Bank": {
        "symbol": "GUVEN",
        "sector": "Bankacılık",
        "sales": "+%12",
        "profitability": "İstikrarlı",
        "debt": "Sektör normlarında",
        "year_change": "+%18",
        "description": "Geniş müşteri tabanına sahip, geleneksel ve dijital bankacılık hizmetleri sunan bir banka.",
        "icon": "🏦",
    },
    "Yeşil Enerji": {
        "symbol": "YESIL",
        "sector": "Yenilenebilir Enerji",
        "sales": "+%31",
        "profitability": "Orta ve yükseliyor",
        "debt": "Orta",
        "year_change": "+%42",
        "description": "Güneş ve rüzgâr enerjisi yatırımları bulunan büyüme odaklı bir enerji şirketi.",
        "icon": "🌱",
    },
    "Hızlı Havayolları": {
        "symbol": "HIZLI",
        "sector": "Havacılık",
        "sales": "+%20",
        "profitability": "Yakıt maliyetlerine duyarlı",
        "debt": "Yüksek",
        "year_change": "+%9",
        "description": "İç ve dış hatlarda faaliyet gösteren, maliyetlere duyarlı bir havayolu şirketi.",
        "icon": "✈️",
    },
    "Bereket Gıda": {
        "symbol": "BRKT",
        "sector": "Gıda",
        "sales": "+%8",
        "profitability": "İstikrarlı",
        "debt": "Düşük",
        "year_change": "+%14",
        "description": "Temel tüketim ürünleri üreten, savunmacı özellikleri güçlü bir gıda şirketi.",
        "icon": "🌾",
    },
    "SağlıkPlus": {
        "symbol": "SPLUS",
        "sector": "Sağlık",
        "sales": "+%16",
        "profitability": "Yüksek",
        "debt": "Düşük-Orta",
        "year_change": "+%26",
        "description": "Özel hastane ve dijital sağlık hizmetleri sunan istikrarlı bir sağlık şirketi.",
        "icon": "🏥",
    },
}

# Her satır, ilgili turun kararından SONRA oluşan fiyatları gösterir.
PRICE_PATH = [
    {
        # İlk yatırım ile Tur 1 haberleri arasındaki kısa piyasa eğilimi
        "Nova Teknoloji": 103.0,
        "Güven Bank": 99.0,
        "Yeşil Enerji": 102.0,
        "Hızlı Havayolları": 98.0,
        "Bereket Gıda": 101.0,
        "SağlıkPlus": 100.5,
    },
    {
        "Nova Teknoloji": 106.0,
        "Güven Bank": 99.0,
        "Yeşil Enerji": 101.0,
        "Hızlı Havayolları": 100.0,
        "Bereket Gıda": 99.0,
        "SağlıkPlus": 101.0,
    },
    {
        "Nova Teknoloji": 95.4,
        "Güven Bank": 101.0,
        "Yeşil Enerji": 103.0,
        "Hızlı Havayolları": 98.0,
        "Bereket Gıda": 101.0,
        "SağlıkPlus": 102.0,
    },
    {
        "Nova Teknoloji": 98.0,
        "Güven Bank": 96.0,
        "Yeşil Enerji": 109.0,
        "Hızlı Havayolları": 97.0,
        "Bereket Gıda": 104.0,
        "SağlıkPlus": 100.0,
    },
    {
        "Nova Teknoloji": 96.0,
        "Güven Bank": 99.0,
        "Yeşil Enerji": 106.0,
        "Hızlı Havayolları": 91.0,
        "Bereket Gıda": 106.0,
        "SağlıkPlus": 104.0,
    },
    {
        "Nova Teknoloji": 92.0,
        "Güven Bank": 94.0,
        "Yeşil Enerji": 101.0,
        "Hızlı Havayolları": 88.0,
        "Bereket Gıda": 103.0,
        "SağlıkPlus": 102.0,
    },
    {
        "Nova Teknoloji": 99.0,
        "Güven Bank": 97.0,
        "Yeşil Enerji": 108.0,
        "Hızlı Havayolları": 94.0,
        "Bereket Gıda": 105.0,
        "SağlıkPlus": 111.0,
    },
]

ROUNDS = [
    {
        "title": "Yatırım, büyüme ve finansman riski",
        "market_note": "Şirketlere özgü ilk gelişmeler açıklandı. Haber başlıklarının yanında ayrıntıları da karşılaştırın.",
        "company_news": {
            "Nova Teknoloji": {"summary": "Yeni fabrika yatırımı açıkladı.", "detail": "Yatırımın büyük bölümü borçla finanse edilecek; kapasite artışı fırsat yaratırken finansman riski yükseliyor.", "signal": "Olumlu ama riskli"},
            "Güven Bank": {"summary": "Takipteki kredi oranı sınırlı ölçüde yükseldi.", "detail": "Artış sektör ortalamasına yakın; sermaye yeterliliğinde belirgin bozulma bulunmuyor.", "signal": "Hafif olumsuz"},
            "Yeşil Enerji": {"summary": "Yeni teşvik programına kabul edildi.", "detail": "Teşvik, iki yeni güneş enerjisi projesinin yatırım maliyetini azaltabilir.", "signal": "Olumlu"},
            "Hızlı Havayolları": {"summary": "Yolcu doluluk oranı yatay seyretti.", "detail": "Talep korunurken yakıt maliyetleri şirket üzerinde baskı oluşturmaya devam ediyor.", "signal": "Nötr"},
            "Bereket Gıda": {"summary": "Hammadde maliyetlerinde artış bildirdi.", "detail": "Şirket maliyet artışının bir kısmını fiyatlara yansıtmayı planlıyor.", "signal": "Hafif olumsuz"},
            "SağlıkPlus": {"summary": "Yeni ürün için ruhsat başvurusu yaptı.", "detail": "Başvurunun sonucu henüz belli değil; onay alınırsa gelir potansiyeli oluşabilir.", "signal": "Olumlu ama belirsiz"},
        },
        "lesson": "Olumlu bir haber, finansman ve uygulama riskleriyle birlikte değerlendirilmelidir.",
        "good_reasons": ["Haberin tamamına ve borca bakıyorum.", "Risk arttığı için daha güvenli bir şirkete geçiyorum."],
        "risk_reasons": ["Yatırım haberi geldi, fiyat kesin yükselir.", "Şirketin adı bana güven veriyor."],
        "bias": "Başlık etkisi / aşırı iyimserlik",
    },
    {
        "title": "Popülerlik ve geçmiş performans",
        "market_note": "Fiyat hareketleri ve sosyal medya ilgisi öne çıkıyor. Geçmiş performansın geleceği garanti edip etmediğini düşünün.",
        "company_news": {
            "Nova Teknoloji": {"summary": "Son altı ayda %80 yükseldi ve sosyal medyada gündem oldu.", "detail": "Değerleme çarpanları sektör ortalamasının belirgin biçimde üzerine çıktı.", "signal": "Popüler ama pahalı"},
            "Güven Bank": {"summary": "Dijital müşteri sayısı arttı.", "detail": "Müşteri artışı olumlu; ancak gelir etkisinin kısa vadede sınırlı kalması bekleniyor.", "signal": "Hafif olumlu"},
            "Yeşil Enerji": {"summary": "Yeni proje için ön lisans aldı.", "detail": "Projenin finansmanı henüz kesinleşmedi.", "signal": "Olumlu ama belirsiz"},
            "Hızlı Havayolları": {"summary": "Dış hat rezervasyonları zayıfladı.", "detail": "Mevsimsel etkiler nedeniyle talep geçici olarak geriledi.", "signal": "Hafif olumsuz"},
            "Bereket Gıda": {"summary": "Yeni dağıtım anlaşması imzaladı.", "detail": "Anlaşmanın satışlara kademeli katkı sağlaması bekleniyor.", "signal": "Olumlu"},
            "SağlıkPlus": {"summary": "Yeni klinik açılışı planlıyor.", "detail": "Açılış yatırımı kısa vadede maliyet yaratacak, uzun vadede kapasiteyi artırabilir.", "signal": "Dengeli"},
        },
        "lesson": "Geçmiş fiyat artışı ve popülerlik tek başına yatırım gerekçesi değildir.",
        "good_reasons": ["Geçmişte yükselmesi yine yükseleceği anlamına gelmez.", "Popülerliğe değil şirket bilgilerine bakıyorum."],
        "risk_reasons": ["Herkes alıyor, ben de almalıyım.", "Çok yükseldi, yine yükselir."],
        "bias": "Sürü psikolojisi / trend takibi",
    },
    {
        "title": "Kârın kaynağını sorgulamak",
        "market_note": "Şirketler dönem sonuçlarını açıklıyor. Kârın büyüklüğü kadar kaynağına ve sürdürülebilirliğine bakın.",
        "company_news": {
            "Nova Teknoloji": {"summary": "Siparişlerde toparlanma açıkladı.", "detail": "Sipariş artışı henüz nakit akışına tam yansımadı.", "signal": "Hafif olumlu"},
            "Güven Bank": {"summary": "Net faiz marjı daraldı.", "detail": "Mevduat maliyetlerindeki artış kârlılığı baskılıyor.", "signal": "Olumsuz"},
            "Yeşil Enerji": {"summary": "Dönem kârı %50 arttı.", "detail": "Artışın önemli kısmı ana faaliyetlerden değil, tek seferlik gayrimenkul satışından kaynaklandı.", "signal": "Göründüğünden zayıf"},
            "Hızlı Havayolları": {"summary": "Kargo gelirleri sınırlı arttı.", "detail": "Yolcu gelirlerindeki zayıflığı kısmen telafi etti.", "signal": "Nötr"},
            "Bereket Gıda": {"summary": "Faaliyet kâr marjı yükseldi.", "detail": "Maliyet kontrolü ve ürün karması iyileşmesi marjı destekledi.", "signal": "Olumlu"},
            "SağlıkPlus": {"summary": "Tek seferlik yeniden yapılandırma gideri açıkladı.", "detail": "Gider kârı düşürdü; ana faaliyet performansı büyük ölçüde korundu.", "signal": "Geçici olumsuz"},
        },
        "lesson": "Kâr rakamı tek başına yeterli değildir; sürdürülebilir faaliyet kârı ile tek seferlik gelir ayrılmalıdır.",
        "good_reasons": ["Kârın nereden geldiğine bakıyorum.", "Bu kârın sürekli olup olmadığını kontrol ediyorum."],
        "risk_reasons": ["Kâr arttı, hisse kesin yükselir.", "Sadece kâr rakamına bakıyorum."],
        "bias": "Yüzeysel analiz / çerçeveleme etkisi",
    },
    {
        "title": "Kötü haber ve risk yönetimi",
        "market_note": "Olumsuz başlıklar piyasada hızlı tepki yaratıyor. Şirketlerin bu risklere karşı önlem alıp almadığını inceleyin.",
        "company_news": {
            "Nova Teknoloji": {"summary": "Tedarik gecikmesi yaşandığını duyurdu.", "detail": "Gecikmenin bir çeyrekle sınırlı kalması ve alternatif tedarikçi kullanılması bekleniyor.", "signal": "Geçici olumsuz"},
            "Güven Bank": {"summary": "Karşılık oranını artırdı.", "detail": "Kısa vadede kârı baskılasa da bilanço dayanıklılığını güçlendirebilir.", "signal": "Temkinli olumlu"},
            "Yeşil Enerji": {"summary": "Bir projede izin süreci uzadı.", "detail": "Diğer projeler planlandığı şekilde ilerliyor.", "signal": "Hafif olumsuz"},
            "Hızlı Havayolları": {"summary": "Yakıt fiyatlarındaki sert artışla baskı gördü.", "detail": "Şirket yakıt maliyetlerinin önemli kısmını önceden sabitlemiş durumda.", "signal": "İlk haberden daha iyi"},
            "Bereket Gıda": {"summary": "Savunmacı ürünlere talep arttı.", "detail": "Temel tüketim ürünleri zayıf piyasa koşullarında istikrarlı seyrediyor.", "signal": "Olumlu"},
            "SağlıkPlus": {"summary": "Yeni geri ödeme düzenlemesinden yararlanacak.", "detail": "Düzenleme bazı tedavilerde hasta hacmini artırabilir.", "signal": "Olumlu"},
        },
        "lesson": "İlk olumsuz başlıkta panikle işlem yapmak yerine şirketin riski nasıl yönettiği araştırılmalıdır.",
        "good_reasons": ["Şirketin önlem alıp almadığına bakıyorum.", "İlk haberin her şeyi göstermediğini biliyorum."],
        "risk_reasons": ["Fiyat düştü, hemen satmalıyım.", "Kötü haberi görünce hemen satıyorum."],
        "bias": "Panik satışı / kayıptan kaçınma",
    },
    {
        "title": "Faiz artışı ve piyasa riski",
        "market_note": "Merkez bankası beklenmedik biçimde faiz artırdı. Şirket haberleri olumlu olsa bile genel piyasa etkisini hesaba katın.",
        "company_news": {
            "Nova Teknoloji": {"summary": "Satış hedefini korudu.", "detail": "Yüksek faiz, büyüme şirketlerinin değerlemesini ve finansman maliyetini olumsuz etkileyebilir.", "signal": "Şirket iyi, piyasa zayıf"},
            "Güven Bank": {"summary": "Mevduat maliyetlerinde artış bekliyor.", "detail": "Faiz artışı kısa vadede marjları baskılayabilir.", "signal": "Olumsuz"},
            "Yeşil Enerji": {"summary": "Uzun vadeli sabit fiyatlı satış sözleşmesi açıkladı.", "detail": "Sözleşme gelir görünürlüğünü artırıyor; ancak yüksek faiz değerlemeyi baskılıyor.", "signal": "Dengeli"},
            "Hızlı Havayolları": {"summary": "Finansman giderleri artabilir.", "detail": "Yüksek borçluluk nedeniyle faiz artışına duyarlılığı yüksek.", "signal": "Olumsuz"},
            "Bereket Gıda": {"summary": "Temel tüketim talebi korunuyor.", "detail": "Düşük borç ve istikrarlı talep şirketi görece savunmacı kılıyor.", "signal": "Görece dayanıklı"},
            "SağlıkPlus": {"summary": "Satış ve faaliyet kârında artış açıkladı.", "detail": "Güçlü faaliyet performansına rağmen piyasa genelindeki satıştan etkilenebilir.", "signal": "Şirket iyi, piyasa zayıf"},
        },
        "lesson": "Hisse fiyatını yalnızca şirket performansı değil, faizler ve genel ekonomik koşullar da etkiler.",
        "good_reasons": ["Şirketle birlikte faizlere ve piyasaya bakıyorum.", "Daha güvenli bir şirket seçiyorum."],
        "risk_reasons": ["Şirket iyiyse piyasa düşse de etkilenmez.", "Faizlerin hisse fiyatıyla ilgisi yoktur."],
        "bias": "Şirket odaklı dar bakış / piyasa riskini ihmal",
    },
    {
        "title": "Söylenti, resmî açıklama ve beklenmeyen gelişme",
        "market_note": "Son turda bilgi kaynakları ve beklenmeyen gelişmeler belirleyici. Söylenti ile doğrulanmış açıklamayı ayırın.",
        "company_news": {
            "Nova Teknoloji": {"summary": "İhracat siparişi aldığını resmen açıkladı.", "detail": "Sözleşme şirketin cirosuna anlamlı katkı sağlayabilir.", "signal": "Olumlu ve doğrulanmış"},
            "Güven Bank": {"summary": "Düzenleyici inceleme başlatıldı.", "detail": "İncelemenin sonucu henüz bilinmiyor; belirsizlik kısa vadeli baskı yaratıyor.", "signal": "Belirsiz ve riskli"},
            "Yeşil Enerji": {"summary": "Yurt dışı proje ortaklığı duyurdu.", "detail": "Açıklama şirketin resmî bildirim kanalı üzerinden yapıldı.", "signal": "Olumlu ve doğrulanmış"},
            "Hızlı Havayolları": {"summary": "Yeni turizm rotaları için talep artışı bildirdi.", "detail": "Rezervasyon verileri şirket tarafından doğrulandı.", "signal": "Olumlu"},
            "Bereket Gıda": {"summary": "Ürün geri çağırma söylentisi yayıldı.", "detail": "Şirket resmî açıklamasında iddiayı yalanladı; denetimlerde sorun bulunmadığını bildirdi.", "signal": "Söylenti doğrulanmadı"},
            "SağlıkPlus": {"summary": "Büyük kamu sözleşmesi alacağı söylentisi yayıldı.", "detail": "Şirket söylentiyi yalanladı; buna karşılık resmî olarak dijital sağlık ihracat anlaşması açıkladı.", "signal": "Söylenti yanlış, resmî haber olumlu"},
        },
        "lesson": "Sosyal medya söylentisi ile resmî açıklama aynı değerde değildir; bilginin kaynağı sorgulanmalıdır.",
        "good_reasons": ["Resmî habere göre karar veriyorum.", "Söylenti doğru mu diye kontrol ediyorum."],
        "risk_reasons": ["Sosyal medyada yazıyorsa doğrudur.", "Geç kalmadan hemen almalıyım."],
        "bias": "Söylentiye kapılma / kaçırma korkusu",
    },
]

INITIAL_REASONS = [
    "Satışları ve kârı iyi göründüğü için seçtim.",
    "Borcu diğer şirketlere göre daha az olduğu için seçtim.",
    "Bu sektörün geleceğinin iyi olduğunu düşünüyorum.",
    "Fiyatı ve şirket bilgilerini birlikte değerlendirdim.",
    "Daha güvenli göründüğü için seçtim.",
    "Daha çok kazanmak için risk aldım.",
    "Son dönemde çok yükseldiği için seçtim.",
    "Şirketin adını veya sektörünü beğendim.",
]

ACTION_REASONS = {
    "Tut": [
        "Şirketin durumu hâlâ iyi görünüyor.",
        "Bu düşüşün geçici olduğunu düşünüyorum.",
        "Diğer şirketler daha iyi görünmüyor.",
        "Tek bir kötü haberle hemen satmak istemiyorum.",
        "Zarar ettiğim için satmak istemiyorum.",
        "İlk seçimimi değiştirmek istemiyorum.",
    ],
    "Sat ve nakitte kal": [
        "Piyasa karışık olduğu için nakitte bekliyorum.",
        "Hiçbir şirket şu anda iyi görünmüyor.",
        "Yeni haberleri beklemek istiyorum.",
        "Piyasanın daha da düşebileceğini düşünüyorum.",
        "Daha fazla zarar etmekten korktuğum için satıyorum.",
        "Kötü haberi görünce hemen satıyorum.",
    ],
    "Sat ve başka hisse al": [
        "Yeni şirket daha iyi görünüyor.",
        "Mevcut şirket riskli, yeni şirket daha güçlü görünüyor.",
        "Şirketlerin haberlerini ve durumlarını karşılaştırdım.",
        "Daha güvenli bir şirkete geçiyorum.",
        "Sosyal medyada çok konuşulduğu için alıyorum.",
        "Çok yükseldiği için yine yükseleceğini düşünüyorum.",
    ],
    "Nakitte kal": [
        "Haberler net olmadığı için nakitte bekliyorum.",
        "İyi bir fırsat görmediğim için risk almıyorum.",
        "Yeni haber gelene kadar paramı koruyorum.",
        "Fiyatların düşeceğini düşündüğüm için nakitte kalıyorum.",
    ],
    "Hisse al": [
        "Seçtiğim şirket iyi görünüyor.",
        "Şirketleri karşılaştırıp en iyisini seçtim.",
        "Beklemek yerine uygun gördüğüm hisseyi alıyorum.",
        "Sosyal medyada çok konuşulduğu için alıyorum.",
        "Çok yükseldiği için yine yükseleceğini düşünüyorum.",
    ],
}

ALL_REASONS = [
    "Haberin tamamına bakıyorum.",
    "Şirket bilgilerini karşılaştırıyorum.",
    "Piyasanın genel durumuna da bakıyorum.",
    "Güvenilir habere göre karar veriyorum.",
    "Yükseldiği için yine yükseleceğini düşünüyorum.",
    "Başkaları aldığı için ben de alıyorum.",
    "Korktuğum için hemen satıyorum.",
    "Şirketin adını veya sektörünü beğeniyorum.",
]

# -----------------------------------------------------------------------------
# YARDIMCI FONKSİYONLAR
# -----------------------------------------------------------------------------
def initialize_state():
    defaults = {
        "page": "welcome",
        "nickname": "",
        "current_round": 0,
        "cash": STARTING_CASH,
        "holding": None,
        "shares": 0.0,
        "history": [],
        "initial_company": None,
        "show_detail": False,
        "completed": False,
        "pending_feedback": None,
        "last_round_return": 0.0,
        "show_countdown": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def fmt_money(value: float) -> str:
    return f"{value:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def current_prices():
    return PRICE_PATH[st.session_state.current_round]


def portfolio_value(price_index=None):
    if price_index is None:
        price_index = st.session_state.current_round
    value = st.session_state.cash
    if st.session_state.holding:
        value += st.session_state.shares * PRICE_PATH[price_index][st.session_state.holding]
    return value


def reason_category(reason: str, round_data: dict) -> str:
    if reason in round_data["good_reasons"]:
        return "good"
    if reason in round_data["risk_reasons"]:
        return "risk"
    positive_words = ["ayrıntı", "risk", "temel", "resmî", "güvenilir", "piyasa", "mali", "karşılaştır", "güvenli"]
    return "good" if any(word in reason.lower() for word in positive_words) else "neutral"


def linked_decision_score(reason: str, round_data: dict, round_return: float) -> tuple[int, str]:
    """Karar gerekçesi ile gerçekleşen sonucu birlikte puanlar."""
    category = reason_category(reason, round_data)
    if round_return > 0.001:
        if category == "good":
            return 10, "Doğru gerekçe kârla sonuçlandı."
        if category == "risk":
            return 5, "Kâr oluştu; ancak karar gerekçesi zayıftı. Sonuçta şans etkili olabilir."
        return 7, "Kâr oluştu; karar kısmen doğruydu."
    if round_return < -0.001:
        if category == "good":
            return 4, "Gerekçe makuldü; ancak karar bu tur zarar getirdi."
        if category == "risk":
            return 0, "Zayıf gerekçe zarar ile sonuçlandı."
        return 3, "Karar yeterince güçlü değildi ve zarar oluştu."
    if category == "good":
        return 6, "Gerekçe doğruydu; ancak sonuç nötr kaldı."
    if category == "risk":
        return 2, "Gerekçe zayıftı; sonuç nötr kaldı."
    return 5, "Karar ve sonuç nötr düzeyde kaldı."


def initial_linked_score(reason: str, round_return: float) -> tuple[int, str]:
    strong_reason = reason not in INITIAL_REASONS[-2:]
    if round_return > 0.001:
        return (10, "Bilgiye dayalı ilk seçim kâr getirdi.") if strong_reason else (5, "Kâr oluştu; ancak ilk seçim gerekçesi zayıftı.")
    if round_return < -0.001:
        return (4, "İlk seçim bilgiye dayalıydı; ancak zarar oluştu.") if strong_reason else (0, "Zayıf ilk seçim gerekçesi zarar ile sonuçlandı.")
    return (6, "İlk seçim bilgiye dayalıydı; sonuç nötr kaldı.") if strong_reason else (2, "İlk seçim gerekçesi zayıftı; sonuç nötr kaldı.")


def decision_quality_evaluation(score: float) -> str:
    if score >= 8.5:
        return "Kararlarınız çoğunlukla doğru gerekçelere dayandı ve kârla sonuçlandı."
    if score >= 7.0:
        return "Kararlarınız genel olarak başarılıydı; bazı turlarda gerekçe ve sonuç tam örtüşmedi."
    if score >= 5.0:
        return "Bazı doğru kararlar verdiniz; ancak kâr ve karar gerekçesi her turda uyumlu değildi."
    if score >= 3.0:
        return "Kararlarınızın önemli bir bölümü zarar veya zayıf gerekçelerle sonuçlandı."
    return "Karar gerekçeleri ve sonuçlar çoğunlukla başarısızdı; haberleri daha dikkatli karşılaştırmalısınız."


def conscious_score_evaluation(score: float) -> str:
    if score >= 80:
        return "Hem kazanç hem de karar kalitesi çok güçlü."
    if score >= 65:
        return "Kazanç ve karar kalitesi genel olarak uyumlu."
    if score >= 50:
        return "Orta düzeyde başarı var; daha tutarlı kararlar gerekli."
    if score >= 35:
        return "Kazanç ve karar kalitesi zayıf kaldı."
    return "Kararlar ve sonuçlar birlikte değerlendirildiğinde gelişime ihtiyaç var."


def render_transition_feedback(feedback: str, round_return: float):
    if feedback == "profit":
        st.balloons()
        pieces = []
        colors = ["#22c55e", "#f59e0b", "#3b82f6", "#ef4444", "#a855f7"]
        for i in range(24):
            left = random.randint(2, 96)
            delay = round(random.uniform(0, 1.2), 2)
            duration = round(random.uniform(2.8, 4.8), 2)
            color = random.choice(colors)
            rotate = random.randint(0, 360)
            pieces.append(
                f'<span class="confetti-piece" style="left:{left}%; animation-delay:{delay}s; animation-duration:{duration}s; background:{color}; transform: rotate({rotate}deg);"></span>'
            )
        st.markdown(
            f"""
            <div class="transition-box profit-box">
                <div class="transition-title">Tebrikler! Bu turu kârla kapattınız.</div>
                <div class="transition-subtitle">Tur getirisi: %{round_return:.2f}</div>
            </div>
            <div class="confetti-overlay">{''.join(pieces)}</div>
            """,
            unsafe_allow_html=True,
        )
    elif feedback == "loss":
        st.markdown(
            f"""
            <div class="transition-box loss-box">
                <div class="transition-title">Bu tur zarar oluştu.</div>
                <div class="transition-subtitle">Tur getirisi: %{round_return:.2f}</div>
            </div>
            <div class="red-flash-overlay"></div>
            """,
            unsafe_allow_html=True,
        )
    elif feedback == "neutral":
        st.info(f"Tur getirisi nötr gerçekleşti: %{round_return:.2f}")


def build_launch_confetti_html() -> str:
    pieces = []
    colors = ["#22c55e", "#f59e0b", "#3b82f6", "#ef4444", "#a855f7", "#06b6d4"]
    for _ in range(26):
        left = random.randint(3, 97)
        delay = round(random.uniform(0, 0.7), 2)
        duration = round(random.uniform(2.5, 4.2), 2)
        color = random.choice(colors)
        rotate = random.randint(0, 360)
        pieces.append(
            f'<span class="confetti-piece confetti-top" style="left:{left}%; animation-delay:{delay}s; animation-duration:{duration}s; background:{color}; transform: rotate({rotate}deg);"></span>'
        )
    for side_class, side_count in [("confetti-left", 14), ("confetti-right", 14)]:
        for _ in range(side_count):
            vertical = random.randint(12, 82)
            delay = round(random.uniform(0, 0.55), 2)
            duration = round(random.uniform(1.8, 2.8), 2)
            color = random.choice(colors)
            rotate = random.randint(0, 360)
            pieces.append(
                f'<span class="confetti-piece {side_class}" style="top:{vertical}%; animation-delay:{delay}s; animation-duration:{duration}s; background:{color}; transform: rotate({rotate}deg);"></span>'
            )
    return f'<div class="launch-confetti-overlay">{"".join(pieces)}</div>'



def execute_decision(action: str, target: str | None, reason: str):
    r_idx = st.session_state.current_round
    prices_before = PRICE_PATH[r_idx]
    round_data = ROUNDS[r_idx]
    value_before = portfolio_value(r_idx)
    old_holding = st.session_state.holding

    # Karar mevcut fiyatlarla uygulanır; daha sonra turun fiyat değişimi gerçekleşir.
    if action in ["Sat ve nakitte kal", "Nakitte kal"]:
        if st.session_state.holding:
            st.session_state.cash += st.session_state.shares * prices_before[st.session_state.holding]
        st.session_state.holding = None
        st.session_state.shares = 0.0

    elif action in ["Sat ve başka hisse al", "Hisse al"]:
        if st.session_state.holding:
            st.session_state.cash += st.session_state.shares * prices_before[st.session_state.holding]
        st.session_state.holding = target
        st.session_state.shares = st.session_state.cash / prices_before[target]
        st.session_state.cash = 0.0

    # "Tut" veya "Nakitte kal" işleminde portföy yapısı değiştirilmez.
    new_price_index = r_idx + 1
    value_after = portfolio_value(new_price_index)
    round_return = (value_after / value_before - 1) * 100 if value_before else 0
    quality, score_note = linked_decision_score(reason, round_data, round_return)

    st.session_state.history.append(
        {
            "Tur": r_idx + 1,
            "Olay": round_data["title"],
            "Önceki Varlık": old_holding or "Nakit",
            "Karar": action,
            "Yeni Varlık": st.session_state.holding or "Nakit",
            "Gerekçe": reason,
            "Davranışsal Risk": round_data["bias"],
            "Karar Puanı": quality,
            "Puan Değerlendirmesi": score_note,
            "Tur Getirisi (%)": round(round_return, 2),
            "Portföy Değeri": round(value_after, 2),
            "Öğrenme": round_data["lesson"],
        }
    )

    if round_return > 0.001:
        feedback = "profit"
    elif round_return < -0.001:
        feedback = "loss"
    else:
        feedback = "neutral"

    st.session_state.pending_feedback = feedback
    st.session_state.last_round_return = round_return
    st.session_state.current_round += 1
    st.session_state.show_detail = False
    if st.session_state.current_round >= len(ROUNDS):
        st.session_state.completed = True
        st.session_state.page = "results"
    else:
        st.session_state.page = "game"
    st.rerun()


def create_report_pdf(
    nickname: str,
    final_value: float,
    total_return: float,
    avg_decision: float,
    total_score: float,
    decision_eval: str,
    conscious_eval: str,
    profile_items: list[str],
    profile_title: str,
    history: list[dict],
) -> bytes:
    """Oyun sonu karar karnesini PDF olarak üretir."""
    buffer = BytesIO()

    # Türkçe karakterler için PDF içine gömülebilen bir TrueType yazı tipi kullanılır.
    # Helvetica Türkçe karakterlerin tamamını desteklemediği için sessiz geri dönüş yapılmaz.
    # İlk seçenek ReportLab paketinin kendi içinde bulunan Vera yazı tipidir.
    # Bu dosyalar Streamlit Cloud'da ReportLab kurulu olduğu sürece her zaman erişilebilirdir.
    reportlab_fonts = Path(reportlab.__file__).resolve().parent / "fonts"
    font_candidates = [
        (str(reportlab_fonts / "Vera.ttf"), str(reportlab_fonts / "VeraBd.ttf")),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
        ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    ]

    regular_path = bold_path = None
    for regular_candidate, bold_candidate in font_candidates:
        if Path(regular_candidate).is_file() and Path(bold_candidate).is_file():
            regular_path, bold_path = regular_candidate, bold_candidate
            break

    if regular_path is None or bold_path is None:
        # Bu durum ancak ReportLab kurulumu eksik veya bozuksa oluşur.
        raise RuntimeError(
            "PDF oluşturulamadı: ReportLab yazı tipi dosyalarına erişilemedi. "
            "requirements.txt içinde reportlab paketinin bulunduğunu kontrol edin."
        )

    # Streamlit her yeniden çalıştığında aynı fontu tekrar kaydetmeye çalışmamak için kontrol edilir.
    registered_fonts = set(pdfmetrics.getRegisteredFontNames())
    if "BorsaLabRegular" not in registered_fonts:
        pdfmetrics.registerFont(TTFont("BorsaLabRegular", regular_path, subfontIndex=0))
    if "BorsaLabBold" not in registered_fonts:
        pdfmetrics.registerFont(TTFont("BorsaLabBold", bold_path, subfontIndex=0))

    regular_font = "BorsaLabRegular"
    bold_font = "BorsaLabBold"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.4 * cm,
        title=f"BorsaLab Karar Karnesi - {nickname}",
        author="Çağrı Hamurcu",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BorsaLabTitle", parent=styles["Title"], fontName=bold_font, fontSize=20,
        leading=24, alignment=TA_CENTER, spaceAfter=12
    )
    heading_style = ParagraphStyle(
        "BorsaLabHeading", parent=styles["Heading2"], fontName=bold_font, fontSize=12,
        leading=15, spaceBefore=8, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BorsaLabBody", parent=styles["BodyText"], fontName=regular_font, fontSize=8.5,
        leading=11, alignment=TA_LEFT
    )
    small_style = ParagraphStyle(
        "BorsaLabSmall", parent=body_style, fontSize=7, leading=9
    )
    center_style = ParagraphStyle(
        "BorsaLabCenter", parent=body_style, alignment=TA_CENTER
    )

    story = [
        Paragraph("BorsaLab Karar Karnesi", title_style),
        Paragraph(f"Oyuncu: <b>{nickname}</b>", center_style),
        Spacer(1, 8),
    ]

    summary_data = [
        [Paragraph("Final Portföy", small_style), Paragraph("Toplam Getiri", small_style),
         Paragraph("Karar Kalitesi", small_style), Paragraph("Bilinçli Yatırımcı Puanı", small_style)],
        [Paragraph(fmt_money(final_value), body_style), Paragraph(f"%{total_return:.2f}", body_style),
         Paragraph(f"{avg_decision:.1f}/10", body_style), Paragraph(f"{total_score:.1f}/100", body_style)],
    ]
    summary_table = Table(summary_data, colWidths=[6.3 * cm] * 4)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF8")),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTNAME", (0, 1), (-1, 1), regular_font),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAB4C3")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([summary_table, Spacer(1, 10)])
    story.append(Paragraph("Puanların Değerlendirmesi", heading_style))
    story.append(Paragraph(f"<b>Karar Kalitesi:</b> {decision_eval}", body_style))
    story.append(Paragraph(f"<b>Bilinçli Yatırımcı Puanı:</b> {conscious_eval}", body_style))
    story.append(Paragraph("Puanlama, karar gerekçesi ile o turdaki kâr veya zarar sonucunu birlikte değerlendirir.", small_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Yatırımcı Profili", heading_style))
    story.append(Paragraph(f"<b>{profile_title}</b>", body_style))
    for item in profile_items:
        story.append(Paragraph(f"• {item}", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Tur Bazında Karar Karnesi", heading_style))
    headers = ["Tur", "Olay", "Karar", "Yeni Varlık", "Gerekçe", "Tur Getirisi", "Portföy", "Puan"]
    table_data = [[Paragraph(h, small_style) for h in headers]]
    for row in history:
        table_data.append([
            Paragraph(str(row["Tur"]), small_style),
            Paragraph(str(row["Olay"]), small_style),
            Paragraph(str(row["Karar"]), small_style),
            Paragraph(str(row["Yeni Varlık"]), small_style),
            Paragraph(str(row["Gerekçe"]), small_style),
            Paragraph(f"%{row['Tur Getirisi (%)']:.2f}", small_style),
            Paragraph(fmt_money(float(row["Portföy Değeri"])), small_style),
            Paragraph(str(row["Karar Puanı"]), small_style),
        ])

    report_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[0.8 * cm, 3.2 * cm, 2.5 * cm, 2.4 * cm, 8.0 * cm, 2.0 * cm, 2.7 * cm, 1.2 * cm],
    )
    report_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTNAME", (0, 1), (-1, -1), regular_font),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C0CC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FB")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(report_table)
    story.append(PageBreak())
    story.append(Paragraph("Tur Öğrenme Mesajları", heading_style))
    for row in [x for x in history if x["Tur"] > 0]:
        story.append(Paragraph(f"<b>Tur {row['Tur']} — {row['Olay']}</b>", body_style))
        story.append(Paragraph(f"Karar: {row['Karar']} | Karar gerekçesi: {row['Gerekçe']}", body_style))
        if row.get("Sonuç Gerekçesi"):
            story.append(Paragraph(f"Sonuç gerekçesi: {row['Sonuç Gerekçesi']}", body_style))
        if row.get("Öz Değerlendirme"):
            story.append(Paragraph(f"Oyuncunun çıkardığı ders: {row['Öz Değerlendirme']}", body_style))
        if row.get("Puan Değerlendirmesi"):
            story.append(Paragraph(f"Puan değerlendirmesi: {row['Puan Değerlendirmesi']}", body_style))
        story.append(Paragraph(f"Temel öğrenme: {row['Öğrenme']}", body_style))
        story.append(Spacer(1, 7))

    def add_page_footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont(regular_font, 6.5)
        canvas.drawString(1.2 * cm, 0.65 * cm, "Bu uygulama Çağrı Hamurcu tarafından yapılmıştır.")
        canvas.drawRightString(landscape(A4)[0] - 1.2 * cm, 0.65 * cm, f"Sayfa {doc_obj.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_footer, onLaterPages=add_page_footer)
    return buffer.getvalue()


def investor_profile(history: list[dict]) -> list[str]:
    if not history:
        return ["Yatırımcı profili oluşturmak için oyun kararları gereklidir."]

    avg_quality = sum(x["Karar Puanı"] for x in history) / len(history)
    panic_count = sum("panik" in x["Gerekçe"].lower() for x in history)
    social_count = sum(
        any(k in x["Gerekçe"].lower() for k in ["herkes", "sosyal", "yükselmeye devam"])
        for x in history
    )
    reliable_count = sum(
        any(k in x["Gerekçe"].lower() for k in ["resmî", "güvenilir", "ayrıntı", "temel"])
        for x in history
    )

    profile = []
    if avg_quality >= 7:
        profile.append("Kararlarınızın çoğu bilgi ve risk değerlendirmesine dayanıyordu.")
    elif avg_quality >= 4:
        profile.append("Bazı kararlarınız analize, bazıları ise ilk izlenimlere dayanıyordu.")
    else:
        profile.append("Haber başlıkları ve kısa vadeli fiyat hareketleri kararlarınızı belirgin biçimde etkiledi.")

    if panic_count:
        profile.append("Olumsuz haberlerde hızlı tepki verme eğilimi gösterdiniz.")
    else:
        profile.append("Panik kararlarına karşı genel olarak direnç gösterdiniz.")

    if social_count:
        profile.append("Popülerlik ve başkalarının davranışları bazı seçimlerinizi etkiledi.")
    if reliable_count >= 3:
        profile.append("Güvenilir bilgi ve haber ayrıntılarına önem verdiniz.")
    else:
        profile.append("Bilginin kaynağını ve haber ayrıntılarını daha sistematik sorgulayabilirsiniz.")
    return profile


initialize_state()

# -----------------------------------------------------------------------------
# GÖRSEL STİL
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main .block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1200px;}
    .hero {padding: 2rem; border-radius: 20px; background: linear-gradient(135deg, #0f172a, #1e3a8a); color: white; margin-bottom: 1rem;}
    .hero h1 {font-size: 2.6rem; margin-bottom: .35rem;}
    .hero p {font-size: 1.08rem; opacity: .92;}
    .welcome-stage {position: relative; overflow: hidden; padding: 2.2rem; border-radius: 24px; background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #0ea5e9 100%); color: white; margin-bottom: 1rem; min-height: 250px; box-shadow: 0 18px 44px rgba(15, 23, 42, .22);}
    .welcome-stage h1 {font-size: 2.8rem; margin-bottom: .45rem; position: relative; z-index: 2;}
    .welcome-stage p {font-size: 1.07rem; max-width: 760px; opacity: .95; position: relative; z-index: 2;}
    .welcome-badges {display: flex; gap: .55rem; flex-wrap: wrap; margin-top: 1rem; position: relative; z-index: 2;}
    .welcome-badge {display: inline-block; padding: .42rem .85rem; border-radius: 999px; font-size: .88rem; font-weight: 600; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(2px);}
    .bubble-wrap {position: absolute; inset: 0; overflow: hidden; pointer-events: none;}
    .bubble {position: absolute; bottom: -90px; border-radius: 50%; opacity: .35; filter: blur(.2px); animation: floatBubble linear infinite;}
    .bubble::after {content: ''; position: absolute; width: 28%; height: 28%; top: 18%; left: 20%; border-radius: 50%; background: rgba(255,255,255,.35);}
    .bubble.one {left: 5%; width: 70px; height: 70px; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.55), rgba(59,130,246,.18)); animation-duration: 11s;}
    .bubble.two {left: 18%; width: 44px; height: 44px; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.5), rgba(34,197,94,.16)); animation-duration: 9s; animation-delay: 1.4s;}
    .bubble.three {left: 32%; width: 92px; height: 92px; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.5), rgba(245,158,11,.16)); animation-duration: 14s; animation-delay: .7s;}
    .bubble.four {left: 52%; width: 56px; height: 56px; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.48), rgba(236,72,153,.14)); animation-duration: 10s; animation-delay: 2s;}
    .bubble.five {left: 69%; width: 78px; height: 78px; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.45), rgba(168,85,247,.16)); animation-duration: 13s; animation-delay: 3s;}
    .bubble.six {left: 84%; width: 50px; height: 50px; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.5), rgba(16,185,129,.16)); animation-duration: 8.5s; animation-delay: 2.4s;}
    .welcome-glow {position: absolute; right: -65px; top: -50px; width: 220px; height: 220px; border-radius: 50%; background: rgba(255,255,255,.12); filter: blur(8px);}
    .welcome-glow.two {left: -40px; bottom: -70px; top: auto; right: auto; width: 170px; height: 170px; background: rgba(14,165,233,.18);}
    @keyframes floatBubble {0% {transform: translateY(0) scale(1); opacity: .10;} 20% {opacity: .28;} 60% {opacity: .38;} 100% {transform: translateY(-330px) scale(1.12); opacity: 0;}}
    .company-card {border: 1px solid rgba(128,128,128,.25); border-radius: 16px; padding: 1rem; min-height: 285px;}
    .news-card {border-left: 6px solid #f59e0b; padding: 1.2rem 1.4rem; border-radius: 12px; background: rgba(245,158,11,.10);}
    .lesson-card {border-left: 6px solid #10b981; padding: 1rem 1.2rem; border-radius: 12px; background: rgba(16,185,129,.10);}
    .metric-box {border-radius: 14px; padding: .7rem; border: 1px solid rgba(128,128,128,.22);}
    div[data-testid="stRadio"] label {padding: .25rem 0;}
    .app-footer {text-align:center; opacity:.68; font-size:.70rem; padding-top:1.5rem;}
    .transition-box {position: relative; z-index: 1001; border-radius: 16px; padding: 1rem 1.2rem; margin: .4rem 0 1rem 0; border: 1px solid rgba(0,0,0,.08); box-shadow: 0 8px 24px rgba(0,0,0,.08);}
    .profit-box {background: linear-gradient(90deg, rgba(34,197,94,.16), rgba(59,130,246,.10)); border-left: 6px solid #22c55e;}
    .loss-box {background: linear-gradient(90deg, rgba(239,68,68,.18), rgba(248,113,113,.08)); border-left: 6px solid #ef4444;}
    .transition-title {font-size: 1.15rem; font-weight: 700; margin-bottom: .15rem;}
    .transition-subtitle {font-size: .95rem; opacity: .9;}
    .confetti-overlay {position: fixed; inset: 0; pointer-events: none; z-index: 999;}
    .confetti-piece {position: fixed; top: -18px; width: 12px; height: 18px; opacity: .9; animation-name: fallConfetti; animation-timing-function: linear; animation-fill-mode: forwards;}
    @keyframes fallConfetti {0% {transform: translateY(-20px) rotate(0deg); opacity: 0.95;} 100% {transform: translateY(110vh) rotate(720deg); opacity: 0;}}
    .launch-confetti-overlay {position: fixed; inset: 0; pointer-events: none; z-index: 1200;}
    .confetti-top {animation-name: fallConfetti;}
    .confetti-left {left: -16px; width: 12px; height: 16px; animation-name: blastLeftConfetti;}
    .confetti-right {right: -16px; width: 12px; height: 16px; animation-name: blastRightConfetti;}
    @keyframes blastLeftConfetti {0% {transform: translateX(0) translateY(0) rotate(0deg); opacity: 0.95;} 100% {transform: translateX(92vw) translateY(-28vh) rotate(760deg); opacity: 0;}}
    @keyframes blastRightConfetti {0% {transform: translateX(0) translateY(0) rotate(0deg); opacity: 0.95;} 100% {transform: translateX(-92vw) translateY(-28vh) rotate(-760deg); opacity: 0;}}
    .red-flash-overlay {position: fixed; inset: 0; background: rgba(239,68,68,.32); pointer-events: none; z-index: 998; animation: redBlink 0.75s ease-in-out 2;}
    @keyframes redBlink {0% {opacity: 0;} 20% {opacity: 1;} 50% {opacity: .15;} 80% {opacity: .85;} 100% {opacity: 0;}}
    .stats-grid {display:grid; grid-template-columns:repeat(4,1fr); gap:.75rem; margin:1rem 0 1.2rem 0;}
    .stat-tile {padding:1rem; border-radius:16px; background:linear-gradient(180deg, rgba(255,255,255,.96), rgba(241,245,249,.96)); border:1px solid rgba(148,163,184,.25); box-shadow:0 8px 22px rgba(15,23,42,.07); text-align:center;}
    .stat-icon {font-size:1.55rem; display:block; margin-bottom:.15rem;}
    .stat-value {font-size:1.3rem; font-weight:800; color:#0f172a;}
    .stat-label {font-size:.78rem; color:#64748b; margin-top:.12rem;}
    .ticker {overflow:hidden; white-space:nowrap; border-radius:14px; background:#081226; color:white; padding:.7rem 0; margin:.7rem 0 1rem 0; box-shadow:0 8px 20px rgba(15,23,42,.14);}
    .ticker-track {display:inline-block; padding-left:100%; animation:tickerMove 18s linear infinite;}
    .ticker-item {display:inline-block; margin-right:2.2rem; font-weight:700; font-size:.9rem;}
    .up {color:#4ade80;} .down {color:#f87171;} .flat {color:#facc15;}
    @keyframes tickerMove {0% {transform:translateX(0);} 100% {transform:translateX(-100%);}}
    div.stButton > button[kind="primary"] {font-size:1.05rem; font-weight:800; min-height:3.2rem; border-radius:14px; box-shadow:0 0 0 0 rgba(37,99,235,.45); animation:pulseButton 2s infinite;}
    div.stButton > button[kind="primary"]:hover {transform:translateY(-1px) scale(1.01);}
    @keyframes pulseButton {0% {box-shadow:0 0 0 0 rgba(37,99,235,.38);} 70% {box-shadow:0 0 0 13px rgba(37,99,235,0);} 100% {box-shadow:0 0 0 0 rgba(37,99,235,0);}}
    .countdown-screen {position:relative; overflow:hidden; border-radius:28px; padding:3.3rem 1rem; text-align:center; color:white; background:radial-gradient(circle at 50% 16%, #3b82f6, #0f172a 72%); min-height:360px; display:flex; flex-direction:column; justify-content:center; align-items:center; box-shadow:0 20px 48px rgba(15,23,42,.30);}
    .countdown-screen::before {content:''; position:absolute; inset:-20%; background:radial-gradient(circle, rgba(255,255,255,.14), rgba(255,255,255,0) 48%); animation:countGlow 1.8s ease-in-out infinite;}
    .countdown-number {position:relative; z-index:2; font-size:7rem; font-weight:900; line-height:1; letter-spacing:.03em; text-shadow:0 0 24px rgba(255,255,255,.18); animation:countPulse 1s ease-in-out infinite;}
    .countdown-text {position:relative; z-index:2; font-size:1.4rem; font-weight:800; margin-top:.75rem;}
    .countdown-subtext {position:relative; z-index:2; font-size:1rem; opacity:.9; margin-top:.4rem;}
    .go-burst {animation:goBurst 1.1s ease-in-out infinite; color:#fef08a;}
    .launch-flash {position:absolute; inset:0; background:radial-gradient(circle, rgba(255,255,255,.26), rgba(255,255,255,0) 55%); animation:launchFlash 1.4s ease-in-out infinite; pointer-events:none; z-index:1;}
    @keyframes countPulse {0% {transform:scale(.78); opacity:.30;} 50% {transform:scale(1.14); opacity:1;} 100% {transform:scale(.78); opacity:.30;}}
    @keyframes countGlow {0% {transform:scale(.86); opacity:.25;} 50% {transform:scale(1.08); opacity:.65;} 100% {transform:scale(.86); opacity:.25;}}
    @keyframes goBurst {0% {transform:scale(.82);} 50% {transform:scale(1.18);} 100% {transform:scale(.82);}}
    @keyframes launchFlash {0% {opacity:0;} 20% {opacity:.55;} 50% {opacity:.10;} 75% {opacity:.45;} 100% {opacity:0;}}
    @media (max-width: 800px) {.stats-grid {grid-template-columns:repeat(2,1fr);} .welcome-stage h1 {font-size:2.15rem;} .welcome-stage {padding:1.5rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# KENAR ÇUBUĞU
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("📈 BorsaLab")
    if st.session_state.nickname:
        st.caption(f"Oyuncu: **{st.session_state.nickname}**")
    st.markdown("---")
    st.write("**Amaç:** Bilgiyi sorgulamak, riski yönetmek ve duygusal kararların etkisini görmek.")
    if st.session_state.page in ["game", "results"]:
        st.progress(min(st.session_state.current_round / len(ROUNDS), 1.0))
        st.caption(f"Tamamlanan tur: {st.session_state.current_round}/{len(ROUNDS)}")
        st.metric("Güncel portföy", fmt_money(portfolio_value()))
        st.write(f"**Varlık:** {st.session_state.holding or 'Nakit'}")
    st.markdown("---")
    if st.button("🔄 Oyunu sıfırla", use_container_width=True):
        reset_game()
    st.caption("Bu uygulama yalnızca eğitim amaçlıdır; yatırım tavsiyesi değildir.")

# -----------------------------------------------------------------------------
# KARŞILAMA
# -----------------------------------------------------------------------------
if st.session_state.page == "welcome":
    st.markdown(
        """
        <div class="welcome-stage">
          <div class="bubble-wrap">
            <span class="bubble one"></span>
            <span class="bubble two"></span>
            <span class="bubble three"></span>
            <span class="bubble four"></span>
            <span class="bubble five"></span>
            <span class="bubble six"></span>
            <span class="welcome-glow"></span>
            <span class="welcome-glow two"></span>
          </div>
          <h1>📈 BorsaLab</h1>
          <p>100.000 TL sanal sermayeyle altı şirket arasından seçim yapın. Haberleri değerlendirin, karar verin ve yatırımcı profilinizi keşfedin.</p>
          <div class="welcome-badges">
            <span class="welcome-badge">🎯 Karar ver</span>
            <span class="welcome-badge">📰 Haberleri yorumla</span>
            <span class="welcome-badge">💼 Portföyünü yönet</span>
            <span class="welcome-badge">📊 Sonucunu gör</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="stats-grid">
          <div class="stat-tile"><span class="stat-icon">💰</span><div class="stat-value">100.000 TL</div><div class="stat-label">Başlangıç sermayesi</div></div>
          <div class="stat-tile"><span class="stat-icon">🏢</span><div class="stat-value">6</div><div class="stat-label">Şirket</div></div>
          <div class="stat-tile"><span class="stat-icon">🎮</span><div class="stat-value">{len(ROUNDS)}</div><div class="stat-label">Karar turu</div></div>
          <div class="stat-tile"><span class="stat-icon">🏆</span><div class="stat-value">2 ölçüt</div><div class="stat-label">Getiri + karar kalitesi</div></div>
        </div>
        <div class="ticker">
          <div class="ticker-track">
            <span class="ticker-item">NOVA <span class="up">▲ %3,0</span></span>
            <span class="ticker-item">GUVEN <span class="down">▼ %1,0</span></span>
            <span class="ticker-item">YESIL <span class="up">▲ %2,0</span></span>
            <span class="ticker-item">HIZLI <span class="down">▼ %2,0</span></span>
            <span class="ticker-item">BRKT <span class="up">▲ %1,0</span></span>
            <span class="ticker-item">SPLUS <span class="flat">● %0,5</span></span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("Oyun sonunda portföy performansınız ve karar kaliteniz birlikte değerlendirilecektir.")

    if st.session_state.show_countdown:
        placeholder = st.empty()
        import time
        for number in [3, 2, 1]:
            placeholder.markdown(
                f'<div class="countdown-screen"><div class="countdown-number">{number}</div><div class="countdown-text">BorsaLab başlıyor...</div><div class="countdown-subtext">Piyasayı oku · Karar ver · Sonucunu gör</div></div>',
                unsafe_allow_html=True,
            )
            time.sleep(1.15)
        launch_confetti = build_launch_confetti_html()
        placeholder.markdown(
            f'<div class="countdown-screen"><div class="launch-flash"></div><div class="countdown-number go-burst">GO!</div><div class="countdown-text">Karar zamanı</div><div class="countdown-subtext">Piyasalar açılıyor...</div></div>{launch_confetti}',
            unsafe_allow_html=True,
        )
        time.sleep(2.6)
        st.session_state.show_countdown = False
        st.session_state.page = "companies"
        st.rerun()

    nickname = st.text_input("Oyuncu rumuzunuz", max_chars=24, placeholder="Örn. RiskUstası")
    accept = st.checkbox("Oyunun eğitim amaçlı olduğunu ve gerçek yatırım tavsiyesi içermediğini anlıyorum.")
    if st.button("🚀 Oyunu Başlat", type="primary", use_container_width=True, disabled=not (nickname.strip() and accept)):
        st.session_state.nickname = nickname.strip()
        st.session_state.show_countdown = True
        st.rerun()

# -----------------------------------------------------------------------------
# ŞİRKETLER VE İLK SEÇİM
# -----------------------------------------------------------------------------
elif st.session_state.page == "companies":
    st.title("1. Şirketleri Tanıyın")
    st.write("Aşağıdaki bilgileri karşılaştırın. Başlangıçta sermayenizin tamamını yalnızca bir şirkete yatıracaksınız.")

    names = list(COMPANIES.keys())
    for row_start in range(0, len(names), 3):
        cols = st.columns(3)
        for col, name in zip(cols, names[row_start:row_start + 3]):
            c = COMPANIES[name]
            with col:
                st.subheader(f"{c['icon']} {name}")
                st.caption(f"{c['symbol']} · {c['sector']}")
                st.write(c["description"])
                st.write(f"**Satış değişimi:** {c['sales']}")
                st.write(f"**Kârlılık:** {c['profitability']}")
                st.write(f"**Borçluluk:** {c['debt']}")
                st.write(f"**Son 1 yıl:** {c['year_change']}")
                st.write(f"**Başlangıç fiyatı:** {INITIAL_PRICE:.0f} TL")

    st.markdown("### İlk yatırım kararınız")
    selected = st.selectbox("Sermayenizin tamamını hangi hisseye yatıracaksınız?", names, index=None, placeholder="Bir şirket seçin")
    initial_reason = st.selectbox(
        "Bu şirketi seçmenizin temel nedeni nedir?",
        INITIAL_REASONS,
        index=None,
        placeholder="Bir gerekçe seçin",
    )
    if st.button("100.000 TL ile yatırımı yap", type="primary", use_container_width=True, disabled=not (selected and initial_reason)):
        st.session_state.initial_company = selected
        st.session_state.holding = selected
        st.session_state.shares = STARTING_CASH / INITIAL_PRICE
        st.session_state.cash = 0.0

        initial_round_return = ((PRICE_PATH[0][selected] / INITIAL_PRICE) - 1) * 100
        initial_value = STARTING_CASH * (1 + initial_round_return / 100)
        initial_score, initial_score_note = initial_linked_score(initial_reason, initial_round_return)

        st.session_state.history.append(
            {
                "Tur": 0,
                "Olay": "Başlangıç seçimi",
                "Önceki Varlık": "Nakit",
                "Karar": "İlk yatırım",
                "Yeni Varlık": selected,
                "Gerekçe": initial_reason,
                "Davranışsal Risk": "İlk izlenim / şirket ve sektör tercihi",
                "Karar Puanı": initial_score,
                "Puan Değerlendirmesi": initial_score_note,
                "Tur Getirisi (%)": round(initial_round_return, 2),
                "Portföy Değeri": round(initial_value, 2),
                "Sonuç Gerekçesi": "",
                "Öz Değerlendirme": "",
                "Öğrenme": "İlk seçimlerin hangi bilgiye dayandığı, sonraki kararların niteliğini etkiler.",
            }
        )
        if initial_round_return > 0.001:
            initial_feedback = "profit"
        elif initial_round_return < -0.001:
            initial_feedback = "loss"
        else:
            initial_feedback = "neutral"
        open_reflection(len(st.session_state.history) - 1, initial_feedback, initial_round_return, "game")
        st.rerun()

# -----------------------------------------------------------------------------
# SONUÇ VE GEREKÇELENDİRME EKRANI
# -----------------------------------------------------------------------------
elif st.session_state.page == "reflection":
    history_index = st.session_state.reflection_history_index
    row = st.session_state.history[history_index]
    feedback = st.session_state.pending_feedback or "neutral"
    round_return = st.session_state.last_round_return

    render_transition_feedback(feedback, round_return)

    if row["Tur"] == 0:
        st.title("İlk yatırımınızın sonucu")
        st.write("İlk kâr veya zararınızın nedenini seçin. Sonra Tur 1’e geçebilirsiniz.")
    else:
        st.title(f"Tur {row['Tur']} kararınızın sonucu")
        st.write("Sonraki tura geçmeden önce kâr veya zararınızın nedenini seçin.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Karar", row["Karar"])
    c2.metric("Yeni varlık", row["Yeni Varlık"])
    c3.metric("Portföy değeri", fmt_money(float(row["Portföy Değeri"])), delta=f"%{round_return:.2f}")
    st.info(f"**Karar puanı: {row['Karar Puanı']}/10** — {row.get('Puan Değerlendirmesi', '')}")

    st.markdown("### Sizce bu sonuç neden oluştu?")
    result_reason = st.selectbox(
        "Bu sonucun nedenini seçin.",
        reflection_reasons(feedback, row),
        index=None,
        placeholder="Bir sonuç gerekçesi seçin",
        key=f"reflection_reason_{history_index}",
    )
    self_review = st.text_area(
        "Bu turdan ne öğrendiniz?",
        placeholder="Örn. Haberin tamamını okumalıyım.",
        max_chars=150,
        key=f"reflection_text_{history_index}",
    )

    button_label = "Gerekçeyi kaydet ve sonuçlara geç" if st.session_state.reflection_next_page == "results" else "Gerekçeyi kaydet ve sonraki aşamaya geç"
    if st.button(
        button_label,
        type="primary",
        use_container_width=True,
        disabled=not (result_reason and self_review.strip()),
    ):
        st.session_state.history[history_index]["Sonuç Gerekçesi"] = result_reason
        st.session_state.history[history_index]["Öz Değerlendirme"] = self_review.strip()
        next_page = st.session_state.reflection_next_page
        st.session_state.pending_feedback = None
        st.session_state.reflection_history_index = None
        st.session_state.page = next_page
        st.rerun()

# -----------------------------------------------------------------------------
# OYUN TURLARI
# -----------------------------------------------------------------------------
elif st.session_state.page == "game":
    r_idx = st.session_state.current_round
    r = ROUNDS[r_idx]
    prices = current_prices()

    pending_feedback = st.session_state.get("pending_feedback")
    if pending_feedback:
        render_transition_feedback(pending_feedback, st.session_state.get("last_round_return", 0.0))
        st.session_state.pending_feedback = None

    st.caption(f"TUR {r_idx + 1} / {len(ROUNDS)}")
    st.title(f"Tur {r_idx + 1} Piyasa Bulteni")

    st.markdown(
        f'<div class="news-card"><b>📰 {r["title"]}</b><br>'
        f'<div style="margin:.55rem 0 0 0;">{r["market_note"]}</div></div>',
        unsafe_allow_html=True,
    )

    # Tur 1'e girildiğinde, ilk seçimden sonra piyasada oluşan kısa fiyat eğilimi görünür.
    if r_idx == 0:
        st.markdown("#### İlk işleminizden sonra oluşan fiyat eğilimi")
        trend_rows = []
        for company, price in prices.items():
            change = (price / INITIAL_PRICE - 1) * 100
            direction = "▲ Yükseliş" if change > 0 else "▼ Düşüş" if change < 0 else "— Yatay"
            trend_rows.append(
                {
                    "Şirket": f"{COMPANIES[company]['icon']} {company}",
                    "İlk alım fiyatı": f"{INITIAL_PRICE:.2f} TL",
                    "Tur 1 başlangıç fiyatı": f"{price:.2f} TL",
                    "Değişim": f"{change:+.1f}%",
                    "Eğilim": direction,
                }
            )
        st.dataframe(pd.DataFrame(trend_rows), hide_index=True, use_container_width=True)
        st.caption("Bu hareket, Tur 1 haberleri açıklanmadan önce piyasada oluşan kısa dönemli fiyat eğilimidir. Kararınızı yalnızca bu harekete göre vermeyin.")

    # Her turda altı şirketin tamamına ait haberler aynı anda ve ayrı satırlarda gösterilir.
    news_rows = []
    for company in COMPANIES:
        item = r["company_news"][company]
        news_rows.append(
            {
                "Şirket": f"{COMPANIES[company]['icon']} {company}",
                "Tur haberi": item["summary"],
                "İlk değerlendirme": item["signal"],
            }
        )
    st.markdown("#### Bu turdaki tüm şirket haberleri")
    st.dataframe(pd.DataFrame(news_rows), hide_index=True, use_container_width=True)
    st.caption("Karar vermeden önce mevcut hissenizin yanı sıra diğer beş şirketin haberini de karşılaştırın.")

    with st.expander("🔎 Haber ayrintilarini sirket bazinda incele", expanded=False):
        for company, item in r["company_news"].items():
            st.markdown(f"**{COMPANIES[company]['icon']} {company} — {item['summary']}**")
            st.write(item["detail"])
            st.caption(f"Ilk degerlendirme: {item['signal']}")
            st.divider()

    st.markdown("### Mevcut durumunuz")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Portföy değeri", fmt_money(portfolio_value()))
    m2.metric("Eldeki varlık", st.session_state.holding or "Nakit")
    m3.metric("Nakit", fmt_money(st.session_state.cash))
    current_price = prices[st.session_state.holding] if st.session_state.holding else 0
    m4.metric("Hisse fiyatı", f"{current_price:.2f} TL" if st.session_state.holding else "—")

    with st.expander("Güncel şirket fiyatlarını karşılaştır"):
        df_prices = pd.DataFrame(
            {
                "Şirket": list(prices.keys()),
                "Fiyat (TL)": list(prices.values()),
                "Başlangıca göre (%)": [round((p / INITIAL_PRICE - 1) * 100, 1) for p in prices.values()],
            }
        )
        st.dataframe(df_prices, hide_index=True, use_container_width=True)

    st.markdown("### Kararınız")
    # Karar seçenekleri öğrencinin o anda hisse mi yoksa nakit mi tuttuğuna göre değişir.
    if st.session_state.holding:
        action_options = ["Tut", "Sat ve nakitte kal", "Sat ve başka hisse al"]
    else:
        action_options = ["Nakitte kal", "Hisse al"]

    action = st.radio("Ne yapacaksınız?", action_options, horizontal=True)
    target = None
    if action in ["Sat ve başka hisse al", "Hisse al"]:
        options = [x for x in COMPANIES if x != st.session_state.holding]
        target_label = "Hangi hisseyi alacaksınız?" if action == "Hisse al" else "Hangi hisseye geçeceksiniz?"
        target = st.selectbox(target_label, options, index=None, placeholder="Bir hisse seçin")

    # Gerekçe seçenekleri verilen kararın türüne göre değişir.
    round_reasons = ACTION_REASONS[action] + r["good_reasons"] + r["risk_reasons"]
    round_reasons = list(dict.fromkeys(round_reasons))
    reason = st.selectbox(
        f"'{action}' kararınızın temel gerekçesi nedir?",
        round_reasons,
        index=None,
        placeholder="Kararınıza uygun bir gerekçe seçin",
        key=f"reason_{r_idx}_{action}",
    )

    disabled = reason is None or (action in ["Sat ve başka hisse al", "Hisse al"] and target is None)
    if st.button("Kararı uygula ve turu tamamla", type="primary", use_container_width=True, disabled=disabled):
        execute_decision(action, target, reason)

# -----------------------------------------------------------------------------
# SONUÇLAR
# -----------------------------------------------------------------------------
elif st.session_state.page == "results":
    pending_feedback = st.session_state.get("pending_feedback")
    if pending_feedback:
        render_transition_feedback(pending_feedback, st.session_state.get("last_round_return", 0.0))
        st.session_state.pending_feedback = None

    final_value = portfolio_value(len(PRICE_PATH) - 1)
    total_return = (final_value / STARTING_CASH - 1) * 100
    decision_rows = [x for x in st.session_state.history if x["Tur"] > 0]
    avg_decision = sum(x["Karar Puanı"] for x in decision_rows) / max(len(decision_rows), 1)
    # Karar puanı her turda gerekçe ile kâr/zarar sonucunu birlikte içerir.
    # Bilinçli yatırımcı puanı: sonuçla uyumlu karar kalitesi %65, toplam getiri %35.
    return_score = max(0, min(100, (total_return + 20) / 40 * 100))
    decision_score = avg_decision * 10
    total_score = 0.65 * decision_score + 0.35 * return_score
    decision_eval = decision_quality_evaluation(avg_decision)
    conscious_eval = conscious_score_evaluation(total_score)

    st.markdown(
        f"""
        <div class="hero">
          <h1>Oyun Tamamlandı, {st.session_state.nickname}!</h1>
          <p>Borsada sonuç kadar, sonuca hangi bilgi ve gerekçeyle ulaştığınız da önemlidir.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final portföy", fmt_money(final_value))
    c2.metric("Toplam getiri", f"%{total_return:.2f}")
    c3.metric("Karar kalitesi", f"{avg_decision:.1f}/10")
    c4.metric("Bilinçli yatırımcı puanı", f"{total_score:.1f}/100")

    st.markdown("### Puanların değerlendirmesi")
    st.info(f"**Karar Kalitesi:** {decision_eval}")
    st.success(f"**Bilinçli Yatırımcı Puanı:** {conscious_eval}")
    st.caption("Karar puanı, seçilen gerekçenin doğruluğu ile o turdaki kâr/zarar sonucunu birlikte değerlendirir. Kâr getiren doğru karar en yüksek; zarar getiren zayıf karar en düşük puanı alır.")

    st.markdown("### Yatırımcı profiliniz")
    for item in investor_profile(decision_rows):
        st.write(f"• {item}")

    if total_score >= 80:
        profile_title = "Bilinçli Risk Yöneticisi"
        st.success(f"🏆 Profil: {profile_title}")
    elif total_score >= 65:
        profile_title = "Analitik Yatırımcı"
        st.info(f"🥈 Profil: {profile_title}")
    elif total_score >= 50:
        profile_title = "Gelişen Yatırımcı"
        st.warning(f"🥉 Profil: {profile_title}")
    else:
        profile_title = "Hızlı Karar Veren Yatırımcı"
        st.error(f"🎯 Profil: {profile_title} — haber ayrıntısı ve kaynak kontrolüne daha fazla ağırlık vermelisiniz.")

    st.markdown("### Tur bazında karar karnesi")
    history_df = pd.DataFrame(st.session_state.history)
    display_cols = ["Tur", "Olay", "Karar", "Yeni Varlık", "Gerekçe", "Tur Getirisi (%)", "Portföy Değeri", "Karar Puanı", "Puan Değerlendirmesi"]
    st.dataframe(history_df[display_cols], hide_index=True, use_container_width=True)

    with st.expander("Her turun öğrenme mesajını göster", expanded=True):
        for row in decision_rows:
            st.markdown(f"**Tur {row['Tur']} — {row['Olay']}**")
            st.write(f"Kararınız: {row['Karar']} · Gerekçeniz: {row['Gerekçe']}")
            st.markdown(f'<div class="lesson-card"><b>Temel öğrenme:</b> {row["Öğrenme"]}</div>', unsafe_allow_html=True)
            st.write("")

    pdf_data = create_report_pdf(
        nickname=st.session_state.nickname,
        final_value=final_value,
        total_return=total_return,
        avg_decision=avg_decision,
        total_score=total_score,
        decision_eval=decision_eval,
        conscious_eval=conscious_eval,
        profile_items=investor_profile(decision_rows),
        profile_title=profile_title,
        history=st.session_state.history,
    )
    safe_nickname = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in st.session_state.nickname)
    st.download_button(
        "📄 Karar karnesini PDF olarak indir",
        data=pdf_data,
        file_name=f"BorsaLab_Karar_Karnesi_{safe_nickname}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("Ana mesaj")
    st.write("Borsa yalnızca doğru hisseyi bulma oyunu değildir. Bilgiyi sorgulama, riski yönetme ve duyguları kontrol etme sürecidir.")


st.markdown(
    '<div class="app-footer">Bu uygulama Çağrı Hamurcu tarafından yapılmıştır.</div>',
    unsafe_allow_html=True,
)
