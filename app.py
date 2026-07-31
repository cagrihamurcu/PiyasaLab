import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Borsa Karar Oyunu",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# OYUN VERİLERİ
# -----------------------------------------------------------------------------
STARTING_CASH = 100_000.0

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
        "Nova Teknoloji": 100.0,
        "Güven Bank": 100.0,
        "Yeşil Enerji": 100.0,
        "Hızlı Havayolları": 100.0,
        "Bereket Gıda": 100.0,
        "SağlıkPlus": 100.0,
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
        "title": "Güçlü haber her zaman yeterli midir?",
        "news": "Nova Teknoloji yeni bir fabrika yatırımı açıkladı. İlk açıklamada yatırımın üretim kapasitesini önemli ölçüde artıracağı belirtildi.",
        "detail": "Yatırımın büyük bölümü borçla finanse edilecek. Bu durum büyüme fırsatının yanında finansman riskini de artırıyor.",
        "lesson": "Bir haberin yalnızca başlığına değil, ayrıntılarına ve finansman biçimine de bakılmalıdır.",
        "good_reasons": [
            "Haberin ayrıntılarını ve borçluluk etkisini birlikte değerlendiriyorum.",
            "Risk yükseldiği için portföyümü daha dayanıklı bir şirkete taşıyorum.",
        ],
        "risk_reasons": [
            "Yeni yatırım açıklandı; fiyat kesin yükselmeye devam eder.",
            "Şirket adı ve sektörü bana güven veriyor.",
        ],
        "bias": "Başlık etkisi / aşırı iyimserlik",
    },
    {
        "title": "Geçmişte çok yükselen hisse alınır mı?",
        "news": "Nova Teknoloji son altı ayda yaklaşık %80 yükseldi ve sosyal medyada günün en çok konuşulan hissesi oldu.",
        "detail": "Şirketin değerlemesi sektör ortalamasının oldukça üzerine çıktı. Yeni bilgi, geçmiş performansın gelecekte aynı şekilde süreceğini garanti etmiyor.",
        "lesson": "Geçmiş fiyat artışı ve popülerlik tek başına yatırım gerekçesi değildir; sürü psikolojisine dikkat edilmelidir.",
        "good_reasons": [
            "Geçmiş performansın geleceği garanti etmediğini dikkate alıyorum.",
            "Popülerlik yerine temel göstergeleri karşılaştırıyorum.",
        ],
        "risk_reasons": [
            "Herkes aldığı için ben de almalıyım.",
            "Çok yükseldiğine göre daha da yükselecektir.",
        ],
        "bias": "Sürü psikolojisi / trend takibi",
    },
    {
        "title": "Kâr arttı ama neden?",
        "news": "Yeşil Enerji dönem kârının %50 arttığını açıkladı. İlk bakışta şirketin operasyonel performansı çok güçlü görünüyor.",
        "detail": "Kâr artışının önemli kısmı ana faaliyetlerden değil, tek seferlik bir gayrimenkul satışından kaynaklandı.",
        "lesson": "Kâr rakamına tek başına bakılmaz; kârın sürdürülebilir olup olmadığı ve hangi kaynaktan geldiği sorgulanır.",
        "good_reasons": [
            "Kârın kaynağını ve sürdürülebilirliğini inceliyorum.",
            "Tek seferlik gelir ile faaliyet kârını ayırıyorum.",
        ],
        "risk_reasons": [
            "Kâr %50 arttıysa hisse mutlaka yükselir.",
            "Yalnızca açıklanan kâr rakamına göre karar veriyorum.",
        ],
        "bias": "Yüzeysel analiz / çerçeveleme etkisi",
    },
    {
        "title": "Kötü haber geldiğinde hemen satılır mı?",
        "news": "Yakıt fiyatlarındaki sert artış nedeniyle Hızlı Havayolları hissesi baskı altında kaldı.",
        "detail": "Şirketin yakıt maliyetlerinin önemli kısmını önceden sabitlediği ve fiyat artışına karşı koruma yaptığı açıklandı.",
        "lesson": "İlk olumsuz haberde panikle işlem yapmak yerine şirketin riski nasıl yönettiği araştırılmalıdır.",
        "good_reasons": [
            "Şirketin korunma politikasını görmeden panikle karar vermiyorum.",
            "İlk haberin tablonun tamamı olmadığını düşünüyorum.",
        ],
        "risk_reasons": [
            "Fiyat düştü; daha fazla düşmeden hemen kaçmalıyım.",
            "Kötü haber gördüğüm anda ayrıntıya bakmadan satıyorum.",
        ],
        "bias": "Panik satışı / kayıptan kaçınma",
    },
    {
        "title": "Şirket iyi olsa da hisse düşebilir mi?",
        "news": "SağlıkPlus satış ve faaliyet kârında artış bildirdi. Ancak merkez bankasının beklenmedik faiz artışı sonrası piyasanın tamamında satış başladı.",
        "detail": "Faiz artışı, şirketlerin finansman maliyetini ve yatırımcıların hisse değerlemelerini etkileyebilir. Güçlü şirketler de genel piyasa hareketinden etkilenebilir.",
        "lesson": "Hisse fiyatını yalnızca şirket performansı değil, faizler ve genel ekonomik koşullar da etkiler.",
        "good_reasons": [
            "Şirket verileriyle birlikte genel piyasa ve faiz koşullarını değerlendiriyorum.",
            "Piyasa riskini azaltmak için daha savunmacı bir tercih yapıyorum.",
        ],
        "risk_reasons": [
            "Şirket iyi olduğu için piyasa düşüşünden etkilenmez.",
            "Makroekonomik koşulların hisse fiyatıyla ilgisi yoktur.",
        ],
        "bias": "Şirket odaklı dar bakış / piyasa riskini ihmal",
    },
    {
        "title": "Söylenti mi, güvenilir bilgi mi?",
        "news": "Sosyal medyada SağlıkPlus'ın çok büyük bir kamu sözleşmesi alacağı iddia edildi. Paylaşımlar kısa sürede yayıldı.",
        "detail": "Şirket daha sonra bu iddianın gerçeği yansıtmadığını açıkladı. Buna karşılık resmî açıklamayla yeni bir dijital sağlık ihracat anlaşması duyurdu.",
        "lesson": "Sosyal medya söylentisi ile resmî açıklama aynı değerde değildir; bilginin kaynağı mutlaka sorgulanmalıdır.",
        "good_reasons": [
            "Resmî ve doğrulanabilir bilgiye göre karar veriyorum.",
            "Söylenti teyit edilmeden işlem yapmıyorum.",
        ],
        "risk_reasons": [
            "Sosyal medyada çok paylaşıldığı için bilgi doğrudur.",
            "Başkalarından önce almak için hemen harekete geçmeliyim.",
        ],
        "bias": "Söylentiye kapılma / kaçırma korkusu",
    },
]

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
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# KENAR ÇUBUĞU
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("📈 Borsa Karar Oyunu")
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
          <h1>Şans mı, Strateji mi?</h1>
          <p>100.000 TL sanal sermayeyle altı hayalî şirket arasından seçim yapın. Haberleri değerlendirin, karar verin ve yatırımcı profilinizi keşfedin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Başlangıç sermayesi", "100.000 TL")
    c2.metric("Hayalî şirket", "6")
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
                st.write("**Başlangıç fiyatı:** 100 TL")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### İlk yatırım kararınız")
    selected = st.selectbox("Sermayenizin tamamını hangi hisseye yatıracaksınız?", names, index=None, placeholder="Bir şirket seçin")
    initial_reason = st.selectbox(
        "Bu şirketi seçmenizin temel nedeni nedir?",
        ALL_REASONS,
        index=None,
        placeholder="Bir gerekçe seçin",
    )
    if st.button("100.000 TL ile yatırımı yap", type="primary", use_container_width=True, disabled=not (selected and initial_reason)):
        st.session_state.initial_company = selected
        st.session_state.holding = selected
        st.session_state.shares = STARTING_CASH / PRICE_PATH[0][selected]
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
                "Karar Puanı": 7 if any(k in initial_reason.lower() for k in ["temel", "risk", "mali", "piyasa", "güvenilir"]) else 3,
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
    st.title(r["title"])
    st.markdown(f'<div class="news-card"><b>📰 Piyasa haberi</b><br><br>{r["news"]}</div>', unsafe_allow_html=True)

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
                "Başlangıca göre (%)": [round((p / 100 - 1) * 100, 1) for p in prices.values()],
            }
        )
        st.dataframe(df_prices, hide_index=True, use_container_width=True)

    if not st.session_state.show_detail:
        st.warning("Karar vermeden önce haberin ayrıntısını görmek isteyebilirsiniz. Ayrıntıyı açmak zorunlu değildir; tercihiniz yatırımcı profilinize yansır.")
        if st.button("🔎 Haberin ayrıntısını incele"):
            st.session_state.show_detail = True
            st.rerun()
    else:
        st.info(f"**Ek bilgi:** {r['detail']}")

    st.markdown("### Kararınız")
    action = st.radio("Ne yapacaksınız?", ["Tut", "Sat ve nakitte kal", "Sat ve başka hisse al"], horizontal=True)
    target = None
    if action == "Sat ve başka hisse al":
        options = [x for x in COMPANIES if x != st.session_state.holding]
        target = st.selectbox("Hangi hisseye geçeceksiniz?", options, index=None, placeholder="Yeni hisseyi seçin")

    round_reasons = r["good_reasons"] + r["risk_reasons"] + [x for x in ALL_REASONS if x not in r["good_reasons"] + r["risk_reasons"]]
    reason = st.selectbox("Kararınızın temel gerekçesi", round_reasons, index=None, placeholder="Bir gerekçe seçin")

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
        st.success("🏆 Profil: Bilinçli Risk Yöneticisi")
    elif total_score >= 65:
        st.info("🥈 Profil: Analitik Yatırımcı")
    elif total_score >= 50:
        st.warning("🥉 Profil: Gelişen Yatırımcı")
    else:
        st.error("🎯 Profil: Hızlı Karar Veren Yatırımcı — haber ayrıntısı ve kaynak kontrolüne daha fazla ağırlık vermelisiniz.")

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

    csv = history_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Karar karnesini CSV olarak indir",
        data=csv,
        file_name=f"borsa_karar_oyunu_{st.session_state.nickname}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("Ana mesaj")
    st.write("Borsa yalnızca doğru hisseyi bulma oyunu değildir. Bilgiyi sorgulama, riski yönetme ve duyguları kontrol etme sürecidir.")
