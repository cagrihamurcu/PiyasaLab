import streamlit as st
import pandas as pd
from io import BytesIO
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
        "good_reasons": ["Haberin ayrıntılarını ve borçluluk etkisini birlikte değerlendiriyorum.", "Risk yükseldiği için portföyümü daha dayanıklı bir şirkete taşıyorum."],
        "risk_reasons": ["Yeni yatırım açıklandı; fiyat kesin yükselmeye devam eder.", "Şirket adı ve sektörü bana güven veriyor."],
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
        "good_reasons": ["Geçmiş performansın geleceği garanti etmediğini dikkate alıyorum.", "Popülerlik yerine temel göstergeleri karşılaştırıyorum."],
        "risk_reasons": ["Herkes aldığı için ben de almalıyım.", "Çok yükseldiğine göre daha da yükselecektir."],
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
        "good_reasons": ["Kârın kaynağını ve sürdürülebilirliğini inceliyorum.", "Tek seferlik gelir ile faaliyet kârını ayırıyorum."],
        "risk_reasons": ["Kâr %50 arttıysa hisse mutlaka yükselir.", "Yalnızca açıklanan kâr rakamına göre karar veriyorum."],
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
        "good_reasons": ["Şirketin korunma politikasını görmeden panikle karar vermiyorum.", "İlk haberin tablonun tamamı olmadığını düşünüyorum."],
        "risk_reasons": ["Fiyat düştü; daha fazla düşmeden hemen kaçmalıyım.", "Kötü haber gördüğüm anda ayrıntıya bakmadan satıyorum."],
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
        "good_reasons": ["Şirket verileriyle birlikte genel piyasa ve faiz koşullarını değerlendiriyorum.", "Piyasa riskini azaltmak için daha savunmacı bir tercih yapıyorum."],
        "risk_reasons": ["Şirket iyi olduğu için piyasa düşüşünden etkilenmez.", "Makroekonomik koşulların hisse fiyatıyla ilgisi yoktur."],
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
        "good_reasons": ["Resmî ve doğrulanabilir bilgiye göre karar veriyorum.", "Söylenti teyit edilmeden işlem yapmıyorum."],
        "risk_reasons": ["Sosyal medyada çok paylaşıldığı için bilgi doğrudur.", "Başkalarından önce almak için hemen harekete geçmeliyim."],
        "bias": "Söylentiye kapılma / kaçırma korkusu",
    },
]

INITIAL_REASONS = [
    "Satış büyümesi, kârlılık ve borçluluk göstergelerini birlikte değerlendirdim.",
    "Şirketin mali yapısını ve borç düzeyini diğer şirketlerle karşılaştırdım.",
    "Sektörün büyüme potansiyelini ve şirketin faaliyet alanını güçlü buldum.",
    "Son bir yıllık fiyat hareketinin yanında temel göstergeleri de dikkate aldım.",
    "Düşük borçluluk ve istikrarlı kârlılık nedeniyle daha güvenli buldum.",
    "Yüksek büyüme potansiyeli için daha fazla risk almayı kabul ettim.",
    "Yalnızca son dönemde fiyatı çok yükseldiği için seçtim.",
    "Şirketin adı veya sektörü bana yakın geldiği için seçtim.",
]

ACTION_REASONS = {
    "Tut": [
        "Mevcut şirketimin haberi ve temel göstergeleri yatırımımı sürdürmek için yeterli görünüyor.",
        "Kısa vadeli dalgalanmaya rağmen şirketin uzun vadeli görünümünün korunduğunu düşünüyorum.",
        "Diğer şirketlerin haberleri mevcut yatırımımdan daha güçlü bir alternatif sunmuyor.",
        "İlk olumsuz haberde panikle satış yapmak istemiyorum; ayrıntıları dikkate alıyorum.",
        "Zararımı kabullenmek istemediğim için fiyatın mutlaka toparlanacağını düşünüyorum.",
        "Daha önce bu hisseyi seçtiğim için kararımı değiştirmek istemiyorum.",
    ],
    "Sat ve nakitte kal": [
        "Piyasa genelindeki belirsizlik nedeniyle yeni bir hisse almadan riski azaltmak istiyorum.",
        "Mevcut şirketimin haberi olumsuz; diğer şirketlerde de yeterince güçlü ve doğrulanmış fırsat görmüyorum.",
        "Yeni bilgi netleşene kadar nakitte beklemenin daha uygun olduğunu düşünüyorum.",
        "Genel piyasa koşullarının tüm hisseleri baskılayabileceğini değerlendiriyorum.",
        "Fiyat düştüğü için daha fazla kaybetme korkusuyla hemen nakde geçiyorum.",
        "Tek bir olumsuz başlık gördüğüm için ayrıntılara bakmadan satıyorum.",
    ],
    "Sat ve başka hisse al": [
        "Seçtiğim yeni şirketin haberi ve temel göstergeleri mevcut şirketimden daha güçlü görünüyor.",
        "Mevcut şirketimde risk artarken yeni şirkette doğrulanmış ve sürdürülebilir bir gelişme bulunuyor.",
        "Şirketleri borçluluk, kârlılık, haber kaynağı ve piyasa koşulları açısından karşılaştırdım.",
        "Portföyümü daha dayanıklı veya daha uygun risk-getiri sunan bir şirkete taşıyorum.",
        "Yeni hisse sosyal medyada popüler olduğu için hemen geçmek istiyorum.",
        "Son dönemde en çok yükselen hisse olduğu için yükselmeye devam edeceğini düşünüyorum.",
    ],
}

ALL_REASONS = [
    "Haberin ayrıntılarını ve risklerini birlikte değerlendiriyorum.",
    "Temel göstergeleri ve şirketin mali yapısını karşılaştırıyorum.",
    "Genel piyasa koşullarını da dikkate alıyorum.",
    "Resmî ve güvenilir bilgiye göre karar veriyorum.",
    "Fiyat yükseldiği için yükselmeye devam edeceğini düşünüyorum.",
    "Herkes aynı yönde işlem yaptığı için ben de takip ediyorum.",
    "Zarar büyümeden panikle çıkmak istiyorum.",
    "Şirketin adını veya sektörünü sevdiğim için seçiyorum.",
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


def reason_quality(reason: str, round_data: dict) -> int:
    if reason in round_data["good_reasons"]:
        return 10
    if reason in round_data["risk_reasons"]:
        return 0
    positive_words = ["ayrıntı", "risk", "temel", "resmî", "güvenilir", "piyasa", "mali"]
    return 7 if any(word in reason.lower() for word in positive_words) else 3


def execute_decision(action: str, target: str | None, reason: str):
    r_idx = st.session_state.current_round
    prices_before = PRICE_PATH[r_idx]
    round_data = ROUNDS[r_idx]
    value_before = portfolio_value(r_idx)
    old_holding = st.session_state.holding

    # Karar mevcut fiyatlarla uygulanır; daha sonra turun fiyat değişimi gerçekleşir.
    if action == "Sat ve nakitte kal":
        if st.session_state.holding:
            st.session_state.cash += st.session_state.shares * prices_before[st.session_state.holding]
        st.session_state.holding = None
        st.session_state.shares = 0.0

    elif action == "Sat ve başka hisse al":
        if st.session_state.holding:
            st.session_state.cash += st.session_state.shares * prices_before[st.session_state.holding]
        st.session_state.holding = target
        st.session_state.shares = st.session_state.cash / prices_before[target]
        st.session_state.cash = 0.0

    # "Tut" işleminde portföy değiştirilmez.
    new_price_index = r_idx + 1
    value_after = portfolio_value(new_price_index)
    round_return = (value_after / value_before - 1) * 100 if value_before else 0
    quality = reason_quality(reason, round_data)

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
            "Tur Getirisi (%)": round(round_return, 2),
            "Portföy Değeri": round(value_after, 2),
            "Öğrenme": round_data["lesson"],
        }
    )

    st.session_state.current_round += 1
    st.session_state.show_detail = False
    if st.session_state.current_round >= len(ROUNDS):
        st.session_state.completed = True
        st.session_state.page = "results"
    st.rerun()


def create_report_pdf(
    nickname: str,
    final_value: float,
    total_return: float,
    avg_decision: float,
    total_score: float,
    profile_items: list[str],
    profile_title: str,
    history: list[dict],
) -> bytes:
    """Oyun sonu karar karnesini PDF olarak üretir."""
    buffer = BytesIO()

    regular_font = "Helvetica"
    bold_font = "Helvetica-Bold"
    font_candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for regular_path, bold_path in font_candidates:
        try:
            pdfmetrics.registerFont(TTFont("BorsaLabRegular", regular_path))
            pdfmetrics.registerFont(TTFont("BorsaLabBold", bold_path))
            regular_font = "BorsaLabRegular"
            bold_font = "BorsaLabBold"
            break
        except Exception:
            continue

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
        story.append(Paragraph(f"Karar: {row['Karar']} | Gerekçe: {row['Gerekçe']}", body_style))
        story.append(Paragraph(f"Temel öğrenme: {row['Öğrenme']}", body_style))
        story.append(Spacer(1, 7))

    def add_page_footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont(regular_font, 7.5)
        canvas.drawString(1.2 * cm, 0.65 * cm, "Çağrı Hamurcu tarafından yapılmıştır.")
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
    .company-card {border: 1px solid rgba(128,128,128,.25); border-radius: 16px; padding: 1rem; min-height: 285px;}
    .news-card {border-left: 6px solid #f59e0b; padding: 1.2rem 1.4rem; border-radius: 12px; background: rgba(245,158,11,.10);}
    .lesson-card {border-left: 6px solid #10b981; padding: 1rem 1.2rem; border-radius: 12px; background: rgba(16,185,129,.10);}
    .metric-box {border-radius: 14px; padding: .7rem; border: 1px solid rgba(128,128,128,.22);}
    div[data-testid="stRadio"] label {padding: .25rem 0;}
    .app-footer {text-align:center; opacity:.72; font-size:.85rem; padding-top:1.5rem;}
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
        <div class="hero">
          <h1>BorsaLab</h1>
          <p>100.000 TL sanal sermayeyle altı şirket arasından seçim yapın. Haberleri değerlendirin, karar verin ve yatırımcı profilinizi keşfedin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Başlangıç sermayesi", "100.000 TL")
    c2.metric("Şirket", "6")
    c3.metric("Karar turu", str(len(ROUNDS)))

    st.info("Genel sıralama oyun bitene kadar gösterilmez. Başarı yalnızca kazanca değil, karar gerekçelerinin niteliğine de bağlıdır.")
    nickname = st.text_input("Oyuncu rumuzunuz", max_chars=24, placeholder="Örn. RiskUstası")
    accept = st.checkbox("Oyunun eğitim amaçlı olduğunu ve gerçek yatırım tavsiyesi içermediğini anlıyorum.")
    if st.button("Oyuna başla", type="primary", use_container_width=True, disabled=not (nickname.strip() and accept)):
        st.session_state.nickname = nickname.strip()
        st.session_state.page = "companies"
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
                st.markdown('<div class="company-card">', unsafe_allow_html=True)
                st.subheader(f"{c['icon']} {name}")
                st.caption(f"{c['symbol']} · {c['sector']}")
                st.write(c["description"])
                st.write(f"**Satış değişimi:** {c['sales']}")
                st.write(f"**Kârlılık:** {c['profitability']}")
                st.write(f"**Borçluluk:** {c['debt']}")
                st.write(f"**Son 1 yıl:** {c['year_change']}")
                st.write(f"**Başlangıç fiyatı:** {INITIAL_PRICE:.0f} TL")
                st.markdown('</div>', unsafe_allow_html=True)

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
        st.session_state.history.append(
            {
                "Tur": 0,
                "Olay": "Başlangıç seçimi",
                "Önceki Varlık": "Nakit",
                "Karar": "İlk yatırım",
                "Yeni Varlık": selected,
                "Gerekçe": initial_reason,
                "Davranışsal Risk": "İlk izlenim / şirket ve sektör tercihi",
                "Karar Puanı": 3 if initial_reason in INITIAL_REASONS[-2:] else 8,
                "Tur Getirisi (%)": 0.0,
                "Portföy Değeri": STARTING_CASH,
                "Öğrenme": "İlk seçimlerin hangi bilgiye dayandığı, sonraki kararların niteliğini etkiler.",
            }
        )
        st.session_state.page = "game"
        st.rerun()

# -----------------------------------------------------------------------------
# OYUN TURLARI
# -----------------------------------------------------------------------------
elif st.session_state.page == "game":
    r_idx = st.session_state.current_round
    r = ROUNDS[r_idx]
    prices = current_prices()

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
    action = st.radio("Ne yapacaksınız?", ["Tut", "Sat ve nakitte kal", "Sat ve başka hisse al"], horizontal=True)
    target = None
    if action == "Sat ve başka hisse al":
        options = [x for x in COMPANIES if x != st.session_state.holding]
        target = st.selectbox("Hangi hisseye geçeceksiniz?", options, index=None, placeholder="Yeni hisseyi seçin")

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

    disabled = reason is None or (action == "Sat ve başka hisse al" and target is None)
    if st.button("Kararı uygula ve turu tamamla", type="primary", use_container_width=True, disabled=disabled):
        execute_decision(action, target, reason)

# -----------------------------------------------------------------------------
# SONUÇLAR
# -----------------------------------------------------------------------------
elif st.session_state.page == "results":
    final_value = portfolio_value(len(PRICE_PATH) - 1)
    total_return = (final_value / STARTING_CASH - 1) * 100
    decision_rows = [x for x in st.session_state.history if x["Tur"] > 0]
    avg_decision = sum(x["Karar Puanı"] for x in decision_rows) / max(len(decision_rows), 1)
    resilience = sum(
        not any(k in x["Gerekçe"].lower() for k in ["panik", "herkes", "kesin", "hemen"])
        for x in decision_rows
    ) / max(len(decision_rows), 1) * 100

    # Bileşik puan: getiri %50, karar niteliği %30, panik/söylenti direnci %20.
    # Getiri bileşeni 0-100 aralığına sınırlanır: -20% => 0, +20% => 100.
    return_score = max(0, min(100, (total_return + 20) / 40 * 100))
    decision_score = avg_decision * 10
    total_score = 0.50 * return_score + 0.30 * decision_score + 0.20 * resilience

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
    display_cols = ["Tur", "Olay", "Karar", "Yeni Varlık", "Gerekçe", "Tur Getirisi (%)", "Portföy Değeri", "Karar Puanı"]
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
    '<div class="app-footer">Çağrı Hamurcu tarafından yapılmıştır.</div>',
    unsafe_allow_html=True,
)
