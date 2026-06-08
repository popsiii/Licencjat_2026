import streamlit as st
import anthropic
import json

# ──────────────────────────────────────────────
# KONFIGURACJA
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Weryfikator informacji o szczepieniach",
    page_icon="🔍",
    layout="centered"
)

# ──────────────────────────────────────────────
# CSS — GLOBALNE STYLE
# ──────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Serif+Display:ital@0;1&display=swap');

/* ─── Reset i typografia ─── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
    color: #1a1a2e !important;
}

/* ─── Główny kontener ─── */
.main .block-container {
    max-width: 780px !important;
    padding: 2.5rem 2rem 4rem !important;
}

/* ─── Tytuł strony ─── */
h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.2rem !important;
    font-weight: 400 !important;
    color: #0f3460 !important;
    letter-spacing: -0.5px !important;
    line-height: 1.2 !important;
    margin-bottom: 0.25rem !important;
}

/* ─── Nagłówki ─── */
h2, h3 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: #0f3460 !important;
}

/* ─── Paragrafy i markdowny ─── */
p, .stMarkdown p, li {
    font-size: 16px !important;
    line-height: 1.75 !important;
    margin-bottom: 0.6rem !important;
}

/* ─── Wiadomości czatu ─── */
[data-testid="stChatMessage"] {
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.75rem !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    line-height: 1.75 !important;
}

[data-testid="stChatMessage"] p {
    font-size: 16px !important;
    line-height: 1.75 !important;
    margin-bottom: 0.5rem !important;
}

/* ─── Przyciski ─── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 10px !important;
    border: 1.5px solid #d0d8e8 !important;
    background: #ffffff !important;
    color: #1a1a2e !important;
    transition: all 0.18s ease !important;
    text-align: left !important;
    line-height: 1.5 !important;
    margin-bottom: 0.4rem !important;
    white-space: normal !important;
    height: auto !important;
}

.stButton > button:hover {
    border-color: #0f3460 !important;
    background: #f0f4ff !important;
    color: #0f3460 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(15, 52, 96, 0.12) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ─── Chat input ─── */
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 16px !important;
    padding: 1rem !important;
    border-radius: 12px !important;
    border: 1.5px solid #d0d8e8 !important;
}

/* ─── Alert boxy (st.error, st.warning, st.success, st.info) ─── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
}

[data-testid="stAlert"] p {
    font-size: 16px !important;
    margin-bottom: 0.4rem !important;
}

/* ─── Metryki (karta oceny) ─── */
[data-testid="stMetric"] {
    background: #f8faff !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    border: 1px solid #e0e8f5 !important;
}

[data-testid="stMetricLabel"] {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #4a5568 !important;
}

[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 600 !important;
    font-family: 'DM Serif Display', serif !important;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: #f8faff !important;
    padding: 1.5rem 1rem !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stMarkdown {
    font-size: 15px !important;
    line-height: 1.7 !important;
}

/* ─── Divider ─── */
hr {
    border-color: #e0e8f5 !important;
    margin: 1.5rem 0 !important;
}

/* ─── Caption ─── */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 14px !important;
    color: #6b7a9a !important;
    line-height: 1.6 !important;
    margin-bottom: 1.5rem !important;
}

/* ─── Postęp (progress bar) ─── */
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #0f3460, #16537e) !important;
    border-radius: 4px !important;
}

/* ─── Linki ─── */
a {
    color: #0f3460 !important;
    text-decoration: underline !important;
    text-underline-offset: 3px !important;
}

a:hover {
    color: #e94560 !important;
}
</style>
""", unsafe_allow_html=True)

client = anthropic.Anthropic()

# ──────────────────────────────────────────────
# SCHEMATY DEZINFORMACJI (teoria inokulacji)
# ──────────────────────────────────────────────

SCHEMATY_DEZINFO = {
    "fake_experts": {
        "nazwa": "Fake Experts (fałszywy autorytet)",
        "ikona": "👨‍⚕️",
        "opis": (
            "Prezentowanie osoby lub instytucji bez odpowiednich kwalifikacji jako wiarygodnego eksperta. "
            "Popularność, tytuł lub pewność siebie nie zastępują kompetencji medycznych ani konsensusu naukowego."
        ),
        "przyklad": "Influencer zdrowotny bez wykształcenia medycznego przedstawia się jako ekspert od szczepień.",
        "jak_rozpoznac": (
            "Sprawdź, czy autor ma odpowiednie kwalifikacje oraz czy jego stanowisko jest zgodne "
            "z konsensusem instytucji naukowych i medycznych."
        ),
    },
    "logical_fallacies": {
        "nazwa": "Logical Fallacies (błędy logiczne)",
        "ikona": "🧠",
        "opis": (
            "Argumentacja, w której wniosek nie wynika poprawnie z przedstawionych przesłanek. "
            "Informacja może brzmieć logicznie, ale opierać się na uproszczeniu, fałszywej analogii, "
            "błędnym związku przyczynowym lub dowodzie anegdotycznym."
        ),
        "przyklad": "Szczepionki mRNA zawierają informację genetyczną, więc muszą zmieniać ludzkie DNA.",
        "jak_rozpoznac": (
            "Sprawdź, czy wniosek rzeczywiście wynika z podanych przesłanek i czy nie pominięto "
            "istotnych etapów wyjaśnienia."
        ),
    },
    "impossible_expectations": {
        "nazwa": "Impossible Expectations (niemożliwe oczekiwania)",
        "ikona": "🎯",
        "opis": (
            "Stawianie nauce nierealistycznie wysokich wymagań, których żaden dowód nie jest w stanie spełnić. "
            "Technika ta polega na odrzucaniu dostępnych danych, ponieważ nie dają absolutnej pewności."
        ),
        "przyklad": "Dopóki nie ma 50-letnich badań, nie można powiedzieć, że szczepionka jest bezpieczna.",
        "jak_rozpoznac": (
            "Zastanów się, czy wymagany poziom dowodu jest realistyczny i czy taki sam standard "
            "stosuje się wobec ryzyka samej choroby."
        ),
    },
    "cherry_picking": {
        "nazwa": "Cherry Picking (wybiórczy dobór danych)",
        "ikona": "🍒",
        "opis": (
            "Wybieranie tylko tych danych, które wspierają daną tezę, przy jednoczesnym pomijaniu danych, "
            "które jej przeczą. Liczby mogą być prawdziwe, ale użyte bez kontekstu tworzą mylące wrażenie."
        ),
        "przyklad": "Podanie liczby niepożądanych odczynów poszczepiennych bez informacji, ile milionów dawek podano.",
        "jak_rozpoznac": (
            "Sprawdź, czy podano kontekst, wielkość próby, grupę porównawczą i dane przeczące prezentowanej tezie."
        ),
    },
    "conspiracy_theories": {
        "nazwa": "Conspiracy Theories (teorie spiskowe)",
        "ikona": "🕸️",
        "opis": (
            "Zakładanie istnienia ukrytej zmowy między wieloma osobami lub instytucjami. "
            "Każdy kontrargument może być interpretowany jako kolejny dowód spisku, co sprawia, "
            "że taka narracja staje się odporna na fakty."
        ),
        "przyklad": "Big Pharma, WHO i rządy ukrywają prawdę o szczepieniach dla zysku.",
        "jak_rozpoznac": (
            "Zwróć uwagę na narracje typu: wszyscy kłamią, prawda jest ukrywana, "
            "tylko my wiemy, co naprawdę się dzieje."
        ),
    },
}


# ──────────────────────────────────────────────
# BAZA MITÓW
# ──────────────────────────────────────────────

MITY = [
    {
        "id": "autyzm",
        "slowa_kluczowe": ["autyzm", "autystyczny", "autystyczne", "wakefield", "mmr autyzm"],
        "mit": "Szczepionki powodują autyzm",
        "schemat": "cherry_picking",
        "obalenie": (
            "Nie istnieją badania potwierdzające związek między jakąkolwiek szczepionką a autyzmem. "
            "Dezinformacja ta często opiera się na powoływaniu na wycofane badanie przy jednoczesnym "
            "pomijaniu wielu późniejszych badań, które nie wykazały związku między szczepieniami a autyzmem. "
            "Od czasu publikacji badania Wakefielda setki dobrze zaprojektowanych badań potwierdziły, "
            "że szczepionki nie powodują autyzmu (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "skladniki",
        "slowa_kluczowe": ["rtęć", "aluminium", "formaldehyd", "tiomersal", "składniki", "toksyczne", "trucizna", "chemikalia"],
        "mit": "Składniki szczepionek są toksyczne",
        "schemat": "cherry_picking",
        "obalenie": (
            "Substancje wymieniane na etykietach szczepionek, takie jak aluminium czy formaldehyd, "
            "występują w bardzo małych ilościach i są oceniane pod względem bezpieczeństwa. "
            "Dezinformacja często pokazuje samą nazwę składnika bez kontekstu dawki, formy chemicznej "
            "i porównania z naturalną ekspozycją w środowisku. Szczepionki przechodzą rygorystyczne "
            "badania kliniczne oraz procesy kontroli bezpieczeństwa (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "harmonogram",
        "slowa_kluczowe": ["za dużo szczepionek", "przeciąża układ odpornościowy", "za wcześnie", "harmonogram szczepień"],
        "mit": "Zbyt wiele szczepionek naraz przeciąża układ odpornościowy",
        "schemat": "logical_fallacies",
        "obalenie": (
            "Podanie więcej niż jednej szczepionki jednocześnie nie wykazało negatywnego wpływu "
            "na odporność organizmu. Układ odpornościowy codziennie styka się z wieloma antygenami "
            "i jest przygotowany do reagowania na liczne bodźce. Wniosek, że kilka szczepionek "
            "automatycznie przeciąża odporność, jest uproszczeniem mechanizmu działania układu immunologicznego "
            "(PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "naturalna_odpornosc",
        "slowa_kluczowe": ["naturalna odporność", "naturalne szczepienie", "lepiej przechorować", "naturalna immunizacja"],
        "mit": "Naturalna odporność jest lepsza niż szczepionkowa",
        "schemat": "cherry_picking",
        "obalenie": (
            "Odporność po przechorowaniu może powstać, ale jej kosztem jest ryzyko ciężkiego przebiegu choroby, "
            "hospitalizacji, powikłań lub śmierci. Szczepienie pozwala układowi odpornościowemu nauczyć się "
            "rozpoznawać patogen bez konieczności przechodzenia przez chorobę. Mit ten często pomija ryzyko "
            "samego zakażenia i pokazuje tylko wybrane korzyści naturalnej odporności (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "niepotrzebne",
        "slowa_kluczowe": ["choroby zniknęły", "nie ma już tych chorób", "niepotrzebne szczepienia", "odra zniknęła"],
        "mit": "Szczepionki są niepotrzebne, bo choroby i tak zniknęły",
        "schemat": "cherry_picking",
        "obalenie": (
            "Wiele chorób stało się rzadkich właśnie dzięki szczepieniom. Wirusy i bakterie, które je powodują, "
            "nadal mogą krążyć w populacji lub zostać zawleczone z innych regionów. Gdy wyszczepialność spada, "
            "choroby mogą wracać. Mit ten wybiera fakt rzadszego występowania chorób, ale pomija przyczynę tego zjawiska "
            "(PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "dieta_zastepuje",
        "slowa_kluczowe": ["zdrowa dieta", "witaminy", "suplementy", "ćwiczenia zamiast szczepień", "naturalne metody odporności"],
        "mit": "Zdrowa dieta i witaminy zastępują szczepionki",
        "schemat": "logical_fallacies",
        "obalenie": (
            "Zrównoważona dieta, sen i aktywność fizyczna wspierają ogólny stan zdrowia, ale nie zastępują "
            "odporności swoistej wytwarzanej po szczepieniu. Wniosek, że dbanie o zdrowie ogólne wystarcza "
            "do ochrony przed chorobami takimi jak odra, polio czy krztusiec, jest fałszywym uproszczeniem "
            "(PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "nop",
        "slowa_kluczowe": ["nop", "niepożądany", "odczyn", "skutki uboczne", "powikłania po szczepieniu", "śmierć po szczepieniu", "długoterminowe skutki"],
        "mit": "Szczepionki powodują niebezpieczne długoterminowe skutki uboczne",
        "schemat": "cherry_picking",
        "obalenie": (
            "Zdecydowana większość niepożądanych odczynów poszczepiennych to łagodne reakcje, takie jak ból "
            "w miejscu wkłucia lub krótkotrwała gorączka. Szczepionki są stale monitorowane pod kątem bezpieczeństwa "
            "przez krajowe i międzynarodowe agencje. Dezinformacja często eksponuje pojedyncze przypadki działań "
            "niepożądanych bez podania ich częstości i bez porównania z ryzykiem powikłań po chorobie (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "ciaza",
        "slowa_kluczowe": ["ciąża szczepienie", "szczepienie w ciąży", "bezpłodność", "płodność", "wpływ na płodność", "niebezpieczne w ciąży"],
        "mit": "Szczepienia w ciąży są niebezpieczne",
        "schemat": "fake_experts",
        "obalenie": (
            "Wybrane szczepienia w ciąży są zalecane i mogą chronić zarówno matkę, jak i dziecko. "
            "Twierdzenia o szkodliwości szczepień dla płodności lub ciąży często są rozpowszechniane przez osoby, "
            "które nie opierają się na aktualnych zaleceniach medycznych. Decyzje dotyczące szczepień w ciąży "
            "powinny być konsultowane z lekarzem i oparte na rekomendacjach instytucji medycznych (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "mrna_dna_covid",
        "slowa_kluczowe": [
            "mrna dna",
            "modyfikuje dna",
            "zmienia dna",
            "zmienia geny",
            "modyfikuje geny",
            "szczepionka COVID-19 w dna",
            "ingeruje w geny",
            "szczepionka genetyczna",
            "genetyczna szczepionka",
            "edytuje dna",
            "COVID-19 modyfikuje DNA",
            "szczepionka na koronawirus modyfikuje DNA",
        ],
        "mit": "Szczepionka mRNA przeciw COVID-19 modyfikuje ludzkie DNA",
        "schemat": "logical_fallacies",
        "obalenie": (
            "Szczepionki mRNA nie zmieniają ludzkiego DNA. mRNA dostarcza komórkom krótką instrukcję "
            "do wytworzenia białka, na które reaguje układ odpornościowy. Nie wchodzi ono do jądra komórkowego, "
            "gdzie znajduje się DNA, i ulega rozpadowi po krótkim czasie. Twierdzenie, że obecność mRNA oznacza "
            "modyfikację DNA, jest błędnym wnioskiem dotyczącym mechanizmu działania szczepionki."
        ),
        "link": "https://szczepienia.pzh.gov.pl/faq/obalamy-najczestsze-mity-na-temat-szczepionek-i-szczepien-przeciw-covid-19/",
        "link_nazwa": "PZH — obalanie mitów o szczepionkach mRNA"
    },
    {
        "id": "chip",
        "slowa_kluczowe": ["chip", "czip", "śledzenie", "5g", "bill gates", "mikrochip", "kontrola umysłu"],
        "mit": "W szczepionkach są chipy do śledzenia ludzi",
        "schemat": "conspiracy_theories",
        "obalenie": (
            "Szczepionki nie zawierają chipów ani urządzeń elektronicznych. Składniki szczepionek są publicznie "
            "dostępne i podlegają kontroli niezależnych agencji regulacyjnych. Mit o chipach opiera się na narracji "
            "o ukrytej kontroli populacji, typowej dla teorii spiskowych (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "spisek",
        "slowa_kluczowe": ["big pharma", "ukrywają", "spisek", "zarabiają na nas", "kontrola", "przemysł farmaceutyczny"],
        "mit": "Firmy farmaceutyczne i rządy ukrywają prawdę o szczepieniach",
        "schemat": "conspiracy_theories",
        "obalenie": (
            "Szczepionki przechodzą niezależną ocenę bezpieczeństwa i skuteczności przez wiele instytucji w różnych krajach, "
            "a dane rejestracyjne są publicznie dostępne w bazach agencji takich jak EMA i FDA. Teoria o globalnym ukrywaniu "
            "prawdy zakłada zmowę wielu niezależnych naukowców, lekarzy i instytucji, co jest typowym mechanizmem narracji "
            "spiskowej (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
]

ZASOBY = [
    ("🏛️ PZH — szczepienia.pzh.gov.pl", "https://szczepienia.pzh.gov.pl"),
    ("🌍 WHO — szczepionki", "https://www.who.int/health-topics/vaccines-and-immunization"),
    ("🔬 HealthFeedback.org", "https://healthfeedback.org"),
    ("🇪🇺 ECDC — Europejskie Centrum Kontroli Chorób", "https://www.ecdc.europa.eu/en/immunisation-vaccines"),
]

# ──────────────────────────────────────────────
# HTML KOMPONENTY
# ──────────────────────────────────────────────

def karta_schematu(schemat_id: str) -> str:
    s = SCHEMATY_DEZINFO.get(schemat_id)
    if not s:
        return ""
    return f"""
<div style="
    background: #fff2f2;
    border: 1.5px solid #c0392b;
    border-left: 5px solid #c0392b;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-family: 'DM Sans', sans-serif;
">
    <div style="font-size: 1.1rem; font-weight: 600; color: #7b0000; margin-bottom: 0.5rem;">
        {s['ikona']} Technika dezinformacji: <em>{s['nazwa']}</em>
    </div>
    <p style="color: #3d0000; font-size: 15px; margin-bottom: 0.5rem; line-height: 1.65;">
        {s['opis']}
    </p>
    <div style="background: #ffe5e5; border-radius: 8px; padding: 0.6rem 0.9rem; margin: 0.5rem 0; font-size: 14px; color: #6b0000;">
        <strong>Przykład:</strong> {s['przyklad']}
    </div>
    <div style="font-size: 14px; color: #3d0000; margin-top: 0.5rem; line-height: 1.6;">
        <strong>Jak rozpoznać:</strong> {s['jak_rozpoznac']}
    </div>
</div>
"""

def karta_mitu(mit: dict) -> str:
    schemat = SCHEMATY_DEZINFO.get(mit.get("schemat", ""), {})
    schemat_badge = ""
    if schemat:
        schemat_badge = f"""<span style="background:#fff3d6;color:#7a4f00;border-radius:6px;padding:2px 10px;font-size:13px;font-weight:500;margin-left:8px;">{schemat.get('ikona','')} {schemat.get('nazwa','')}</span>"""
    return f"""
<div style="
    background: #fffbf0;
    border: 1.5px solid #f0a500;
    border-left: 5px solid #f0a500;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin: 0.5rem 0 1rem 0;
    font-family: 'DM Sans', sans-serif;
">
    <div style="font-size: 1.05rem; font-weight: 600; color: #7a4f00; margin-bottom: 0.6rem; display:flex; align-items:center; flex-wrap:wrap; gap:4px;">
        ⚠️ Rozpoznany mit o szczepieniach: <em style="margin-left:4px;">{mit['mit']}</em>
        {schemat_badge}
    </div>
    <p style="color: #5a3e00; font-size: 15px; line-height: 1.7; margin-bottom: 0.6rem;">
        {mit['obalenie']}
    </p>
    <a href="{mit.get("link", "#")}" target="_blank" style="
        display:inline-block;
        background:#f0a500;color:white;
        text-decoration:none;
        padding:6px 16px;
        border-radius:7px;
        font-size:14px;font-weight:500;
        margin-top:4px;
    ">📎 {mit.get('link_nazwa', 'Źródło')} -></a>
</div>
"""

def banner_powitalny() -> str:
    return """
<div style="
    background: linear-gradient(135deg, #0f3460 0%, #16537e 100%);
    border-radius: 16px;
    padding: 2rem 2.2rem;
    margin: 0.5rem 0 2rem 0;
    color: white;
    font-family: 'DM Sans', sans-serif;
">
    <div style="font-size: 1.6rem; font-weight: 300; font-family: 'DM Serif Display', serif; margin-bottom: 0.75rem; line-height: 1.3;">
        Naucz się oceniać informacje o szczepieniach
    </div>
    <p style="font-size: 15px; line-height: 1.8; opacity: 0.92; color: white; margin: 0;">
        Ten asystent przeprowadzi Cię przez <strong style="color:white;">4 kroki weryfikacji</strong> — 
        pytając o źródło, autora, dowody naukowe i spójność informacji.<br>
        Zamiast mówić Ci co jest prawdą, <strong style="color:white;">pomoże Ci samodzielnie ocenić</strong> wiarygodność tego co czytasz.
    </p>
</div>
"""

def badge_kroku(nr: int, nazwa: str, aktywny: bool = False) -> str:
    bg = "#0f3460" if aktywny else "#e8eef8"
    kolor = "white" if aktywny else "#6b7a9a"
    return f"""<span style="background:{bg};color:{kolor};border-radius:20px;padding:4px 14px;font-size:13px;font-weight:500;margin-right:6px;">{nr}. {nazwa}</span>"""

def pasek_krokow(aktywny_krok: int) -> str:
    kroki = ["Źródło", "Autor", "Dowody", "Spójność"]
    badges = "".join(
        badge_kroku(i+1, n, aktywny=(i+1 == aktywny_krok))
        for i, n in enumerate(kroki)
    )
    return f'<div style="margin: 0.5rem 0 1.5rem 0; display:flex; flex-wrap:wrap; gap:4px;">{badges}</div>'

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────

def init_state():
    defaults = {
        "krok": 0,
        "flagi": [],
        "tekst_uzytkownika": "",
        "historia_czatu": [],
        "znany_mit": None,
        "odpowiedzi": {},
        "skonczone": False,
        "schematy": [],
        "flaga_mitu_dodana": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def dodaj_wiadomosc(rola, tresc):
    st.session_state.historia_czatu.append({"rola": rola, "tresc": tresc})

def dodaj_flage(krok_nazwa, kolor, opis):
    st.session_state.flagi.append({"krok": krok_nazwa, "kolor": kolor, "opis": opis})

def reset():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()
    st.rerun()

def sprawdz_mit(tekst):
    tekst_lower = tekst.lower()
    for mit in MITY:
        for slowo in mit["slowa_kluczowe"]:
            if slowo in tekst_lower:
                return mit
    return None

def ikona_flagi(kolor):
    return {"czerwona": "🔴", "zolita": "🟡", "zielona": "🟢"}.get(kolor, "⚪")

def podsumuj_flagi():
    czerwone = sum(1 for f in st.session_state.flagi if f["kolor"] == "czerwona")
    zolte    = sum(1 for f in st.session_state.flagi if f["kolor"] == "zolita")
    zielone  = sum(1 for f in st.session_state.flagi if f["kolor"] == "zielona")
    total    = len(st.session_state.flagi)
    if total == 0:
        return "brak_danych"
    if czerwone >= 3:
        return "wysoka_czujnosc"
    if czerwone >= 2 or (czerwone >= 1 and zolte >= 2):
        return "ostroznosc"
    if zielone >= 3:
        return "wiarygodna"
    return "ostroznosc"

def sprawdz_mit_przez_api(tekst):
    lista_mitow = "\n".join(f"{i+1}. {m['mit']} (id: {m['id']})" for i, m in enumerate(MITY))
    prompt = (
        f"Poniżej jest informacja wprowadzona przez użytkownika:\n\n\"{tekst}\"\n\n"
        f"Czy ta informacja zawiera lub sugeruje któryś z poniższych mitów o szczepieniach?\n\n"
        f"{lista_mitow}\n\n"
        f"Odpowiedz TYLKO w formacie JSON: {{\"id\": \"id_mitu\"}} lub {{\"id\": null}}. Nic więcej."
    )
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = resp.content[0].text.strip()
        data = json.loads(raw)
        mit_id = data.get("id")
        if mit_id:
            for m in MITY:
                if m["id"] == mit_id:
                    return m
    except Exception:
        pass
    return None

# ──────────────────────────────────────────────
# RENDEROWANIE HISTORII
# ──────────────────────────────────────────────

def renderuj_historie():
    for msg in st.session_state.historia_czatu:
        if msg["rola"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["tresc"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["tresc"])

# ──────────────────────────────────────────────
# KARTA OCENY
# ──────────────────────────────────────────────

def pokaz_karte_oceny():
    wynik = podsumuj_flagi()
    st.divider()

    czerwone = sum(1 for f in st.session_state.flagi if f["kolor"] == "czerwona")
    zolte    = sum(1 for f in st.session_state.flagi if f["kolor"] == "zolita")
    zielone  = sum(1 for f in st.session_state.flagi if f["kolor"] == "zielona")

    st.markdown("### 📋 Karta oceny informacji")
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Ostrzeżenia", czerwone)
    col2.metric("🟡 Niepewność", zolte)
    col3.metric("🟢 Wiarygodność", zielone)

    st.markdown("<div style='margin: 1.2rem 0;'></div>", unsafe_allow_html=True)

    if wynik == "wysoka_czujnosc":
        st.error("### ⚠️ Wysoka czujność — informacja ma cechy dezinformacji\n\nNa podstawie Twoich odpowiedzi ta informacja wykazuje wiele sygnałów dezinformacji. **Nie podejmuj decyzji zdrowotnych** na jej podstawie bez konsultacji z lekarzem.")
    elif wynik == "ostroznosc":
        st.warning("### 🟡 Ostrożność — informacja wymaga dalszej weryfikacji\n\nCzęść sygnałów jest niepokojąca. Warto sprawdzić w dodatkowych wiarygodnych źródłach przed podjęciem jakichkolwiek decyzji.")
    elif wynik == "wiarygodna":
        st.success("### ✅ Informacja ma cechy wiarygodnego źródła\n\nPochodzi z wiarygodnego źródła i ma podstawy naukowe. Pamiętaj — zawsze warto weryfikować, nawet wiarygodne źródła mogą zawierać błędy.")
    else:
        st.info("### ℹ️ Brak wystarczających danych do oceny")

    if st.session_state.flagi:
        st.markdown("<div style='margin-top:1.2rem;'><strong>Zebrane sygnały podczas weryfikacji:</strong></div>", unsafe_allow_html=True)
        for f in st.session_state.flagi:
            st.markdown(f"- {ikona_flagi(f['kolor'])} **{f['krok']}:** {f['opis']}")

    # ── Schematy dezinformacji — najważniejszy element karty oceny ──
    st.divider()
    schematy = st.session_state.get("schematy", [])
    if schematy:
        st.markdown("""
<div style="background:#fff2f2;border:1.5px solid #c0392b;border-radius:12px;padding:1rem 1.5rem;margin-bottom:1rem;">
<div style="font-size:1.1rem;font-weight:700;color:#7b0000;margin-bottom:0.3rem;">
🔴 Rozpoznane techniki dezinformacji
</div>
<div style="font-size:14px;color:#3d0000;line-height:1.6;">
W tej informacji wykryto poniższe techniki manipulacji z taksonomii FLICC (Cook, 2020).
Znajomość tych wzorców pozwala rozpoznawać dezinformację zanim się w nią uwierzy.
</div>
</div>""", unsafe_allow_html=True)
        for s_id in schematy:
            st.markdown(karta_schematu(s_id), unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:#f0fff4;border:1.5px solid #27ae60;border-radius:12px;padding:1rem 1.5rem;margin-bottom:1rem;">
<div style="font-size:1.1rem;font-weight:700;color:#145a32;margin-bottom:0.3rem;">
🟢 Nie wykryto typowych technik dezinformacji
</div>
<div style="font-size:14px;color:#1a5e2a;line-height:1.6;">
Na podstawie Twoich odpowiedzi informacja nie wykazuje typowych technik manipulacji z taksonomii FLICC.
</div>
</div>""", unsafe_allow_html=True)

    # Toggle — poznaj wszystkie techniki dezinformacji
    with st.expander("Poznaj wszystkie techniki dezinformacji (FLICC)"):
        st.markdown("Taksonomia FLICC (Cook, 2020; van der Linden & Lewandowsky, 2021) opisuje pięć głównych technik stosowanych w dezinformacji zdrowotnej.")
        for s_id, s in SCHEMATY_DEZINFO.items():
            st.markdown(karta_schematu(s_id), unsafe_allow_html=True)

    st.divider()
    st.markdown("**📚 Wiarygodne źródła do dalszej weryfikacji:**")
    cols = st.columns(2)
    for i, (nazwa, url) in enumerate(ZASOBY):
        with cols[i % 2]:
            st.markdown(f"[{nazwa}]({url})")

    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Zweryfikuj kolejną informację", use_container_width=True):
        reset()

# ──────────────────────────────────────────────
# KROKI — LOGIKA
# ──────────────────────────────────────────────

def krok_0_input():
    st.markdown(banner_powitalny(), unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown(
            "Wklej poniżej tekst, link lub opis informacji o szczepieniach którą chcesz sprawdzić. "
            "Przeprowadzę Cię przez **4 kroki** oceny jej wiarygodności — "
            "pytając o źródło, autora, dowody naukowe i spójność z innymi źródłami."
        )
    tekst = st.chat_input("Wklej informację do weryfikacji...")
    if tekst:
        st.session_state.tekst_uzytkownika = tekst
        dodaj_wiadomosc("user", tekst)
        mit = sprawdz_mit(tekst) or sprawdz_mit_przez_api(tekst)
        if mit:
            st.session_state.znany_mit = mit
            st.session_state.krok = 0.5
        else:
            st.session_state.krok = 1
        st.rerun()


def krok_0_5_znany_mit():
    renderuj_historie()
    mit = st.session_state.znany_mit

    # Ten krok może uruchamiać się ponownie po st.rerun().
    # Dlatego flaga z bazy mitów jest dodawana tylko raz.
    if not st.session_state.get("flaga_mitu_dodana", False):
        dodaj_flage(
            "Moduł 0 — baza mitów",
            "czerwona",
            f"Rozpoznano znany schemat: {mit['mit']}"
        )
        st.session_state.flaga_mitu_dodana = True

    # Schemat FLICC przypisany do rozpoznanego mitu również dodajemy tylko raz.
    if mit.get("schemat"):
        st.session_state.setdefault("schematy", [])
        if mit["schemat"] not in st.session_state.schematy:
            st.session_state.schematy.append(mit["schemat"])

    with st.chat_message("assistant"):
        st.markdown("Rozpoznałem w tej informacji znany schemat dezinformacji:")
        st.markdown(karta_mitu(mit), unsafe_allow_html=True)

        if mit.get("schemat"):
            st.markdown(karta_schematu(mit["schemat"]), unsafe_allow_html=True)

        st.markdown("Czy chcesz mimo to przejść przez pełny proces weryfikacji krok po kroku?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Tak, przejdź przez weryfikację", use_container_width=True):
            dodaj_wiadomosc(
                "assistant",
                f"🚨 **Rozpoznany schemat:** {mit['mit']}\n\n{mit['obalenie']}\n\nMimo to przejdziemy przez pełny proces weryfikacji."
            )
            st.session_state.krok = 1
            st.rerun()

    with col2:
        if st.button("❌ Nie, to wystarczy", use_container_width=True):
            dodaj_wiadomosc(
                "assistant",
                f"🚨 **Rozpoznany schemat:** {mit['mit']}\n\n{mit['obalenie']}"
            )
            st.session_state.krok = 99
            st.rerun()


def krok_1_zrodlo():
    st.markdown(pasek_krokow(1), unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown("**Krok 1 z 4 — Źródło informacji**\n\nSkąd pochodzi ta informacja?")

    opcje = {
        "A": ("📱 Media społecznościowe lub wideo (FB, TikTok, YT, IG, X)", "czerwona", "Media społecznościowe nie mają mechanizmów weryfikacji treści — każdy może opublikować cokolwiek."),
        "B": ("📰 Portal ogólny / informacyjny (Onet, WP, Gazeta.pl)", "zolita", "Portale ogólne mają zmienne standardy weryfikacji. Sprawdź kto jest autorem artykułu."),
        "C": ("🌿 Portal alternatywny / naturalny / 'eko' / 'wolnościowy'", "czerwona", "Portale promujące medycynę alternatywną często publikują treści niepodlegające recenzji naukowej i mogą rozpowszechniać informacje niezgodne z aktualną wiedzą medyczną."),
        "D": ("🏛️ Oficjalna strona instytucji (WHO, PZH, GIS, MZ)", "zielona", "Oficjalne instytucje posiadają wielopoziomowe procesy weryfikacji i publiczną odpowiedzialność za treść."),
        "E": ("👥 Przekaz ustny / od znajomego / nie wiem skąd", "czerwona", "Brak możliwości weryfikacji źródła to poważny sygnał ostrzegawczy. Wiarygodna informacja zawsze ma podane pochodzenie."),
    }

    for k, (etykieta, kolor, komentarz) in opcje.items():
        if st.button(etykieta, key=f"k1_{k}", use_container_width=True):
            dodaj_wiadomosc("user", etykieta)
            dodaj_wiadomosc("assistant", f"{ikona_flagi(kolor)} {komentarz}")
            dodaj_flage("Krok 1 — źródło", kolor, etykieta)
            st.session_state.krok = 2
            st.rerun()


def krok_2_autor():
    st.markdown(pasek_krokow(2), unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown("**Krok 2 z 4 — Autor informacji**\n\nKto jest autorem tej informacji?")

    opcje = {
        "A": ("🚫 Brak autora / anonimowy", "czerwona", "Anonimowość oznacza brak odpowiedzialności za treść. Wiarygodne informacje medyczne zawsze mają podanego autora z kwalifikacjami (Wineburg & McGrew, 2018."),
        "B": ("👤 Osoba prywatna / influencer / celebryta", "czerwona", "Popularność w internecie nie jest dowodem kompetencji medycznych. To schemat fałszywego autorytetu — jeden z kluczowych mechanizmów dezinformacji (van der Linden, 2021)."),
        "C": ("🏢 Organizacja lub profil promujący narracje antyszczepionkowe", "czerwona", "Organizacje i profile promujące narracje antyszczepionkowe często rozpowszechniają informacje sprzeczne z konsensusem medycznym oraz wzmacniają zamknięte bańki informacyjne."),
        "D": ("📰 Dziennikarz / redakcja portalu", "zolita", "Podpisany autor zwiększa odpowiedzialność redakcyjną, ale nie gwarantuje rzetelności treści (Wineburg & McGrew, 2018)."),
        "E": ("🩺 Lekarz / ekspert / instytucja medyczna", "zielona", "Autor z wykształceniem medycznym lub instytucja to pozytywny sygnał. Pamiętaj jednak że nawet eksperci mogą być sprzeczni z konsensusem — sprawdź co mówią inne instytucje w kroku 4."),
    }

    schematy_k2 = {
        "B": "fake_experts",
        "C": "conspiracy_theories",
    }

    for k, (etykieta, kolor, komentarz) in opcje.items():
        if st.button(etykieta, key=f"k2_{k}", use_container_width=True):
            dodaj_wiadomosc("user", etykieta)
            dodaj_wiadomosc("assistant", f"{ikona_flagi(kolor)} {komentarz}")
            if k in schematy_k2:
                st.session_state.setdefault("schematy", [])
                if schematy_k2[k] not in st.session_state.schematy:
                    st.session_state.schematy.append(schematy_k2[k])
            dodaj_flage("Krok 2 — autor", kolor, etykieta)
            st.session_state.krok = 3
            st.rerun()


def krok_3_dowody():
    st.markdown(pasek_krokow(3), unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown("**Krok 3 z 4 — Dowody naukowe**\n\nCzy informacja powołuje się na jakieś badania lub dowody?")

    opcje = {
        "A": ("🚫 Żadnych — opinia, 'bo tak', 'wszyscy wiedzą'", "czerwona", None),
        "B": ("📢 Mówi o badaniach ale nie podaje źródła ani nazwy", "czerwona", None),
        "C": ("📊 Podaje liczby lub statystyki", "zolita", "cherry_picking"),
        "D": ("📄 Podaje konkretny link lub nazwę badania", "zielona", None),
        "E": ("🔄 Powołuje się na 'ukrywane' lub 'cenzurowane' dane", "czerwona", "conspiracy_theories"),
    }

    komentarze = {
        "A": "🔴 Brak jakichkolwiek dowodów to poważny sygnał ostrzegawczy. Twierdzenia zdrowotne muszą być poparte badaniami, nie tylko opinią (EBM).",
        "B": "🔴 Twierdzenie o istnieniu badań bez podania ich nazwy lub źródła jest niemożliwe do zweryfikowania.",
        "C": "🟡 Liczby mogą być prawdziwe, ale użyte wybiórczo. Sprawdź: ile osób zbadano, w jakim okresie, w porównaniu do czego?",
        "D": "🟢 Podanie konkretnego źródła to pozytywny sygnał — można je sprawdzić i zweryfikować.",
        "E": "🔴 Narracja 'ukrytych danych' to klasyczny schemat teorii spiskowej — każdy kontrargument staje się częścią spisku.",
    }

    for k, (etykieta, kolor, schemat_id) in opcje.items():
        if st.button(etykieta, key=f"k3_{k}", use_container_width=True):
            dodaj_wiadomosc("user", etykieta)
            dodaj_wiadomosc("assistant", komentarze[k])
            if schemat_id:
                st.session_state.setdefault("schematy", [])
                if schemat_id not in st.session_state.schematy:
                    st.session_state.schematy.append(schemat_id)
            dodaj_flage("Krok 3 — dowody", kolor, etykieta)
            st.session_state.krok = 4
            st.rerun()


def krok_4_spojnosc():
    st.markdown(pasek_krokow(4), unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown(
            "**Krok 4 z 4 — Spójność informacji**\n\n"
            "Czy sprawdziłeś/-aś tę informację w innych miejscach?\n\n"
            "Proponowane zasoby: "
            "[PZH](https://szczepienia.pzh.gov.pl) · "
            "[WHO](https://www.who.int/health-topics/vaccines-and-immunization) · "
            "[HealthFeedback](https://healthfeedback.org)"
        )

    opcje = {
        "A": ("✅ Potwierdzają — znalazłem/-am to samo na PZH / WHO", "zielona", "Spójność z wieloma niezależnymi wiarygodnymi źródłami to silny pozytywny sygnał wiarygodności."),
        "B": ("❌ Zaprzeczają — instytucje medyczne mówią inaczej", "czerwona", ": Gdy informacje publikowane przez organizacje zdrowia publicznego i środowisko naukowe są sprzeczne z analizowaną treścią, warto szczególnie dokładnie sprawdzić jakość źródeł i przedstawionych dowodów. "),
        "C": ("🔕 Tylko to jedno źródło tak twierdzi — inne milczą", "czerwona", "Jeśli informacja jest prawdziwa i ważna — inne niezależne źródła powinny ją potwierdzać. Brak potwierdzenia to sygnał ostrzegawczy."),
        "D": ("⚡ Znalazłem/-am sprzeczne informacje", "zolita", "Przy sprzecznych informacjach sprawdź które źródło jest wyżej w hierarchii wiarygodności — widocznej poniżej w karcie oceny."),
        "E": ("⏳ Nie sprawdzałem/-am jeszcze", "zolita", "Sprawdzenie innych źródeł to kluczowy krok. Zajrzyj do przynajmniej jednego z zasobów podanych powyżej."),
    }

    for k, (etykieta, kolor, komentarz) in opcje.items():
        if st.button(etykieta, key=f"k4_{k}", use_container_width=True):
            dodaj_wiadomosc("user", etykieta)
            dodaj_wiadomosc("assistant", f"{ikona_flagi(kolor)} {komentarz}")
            dodaj_flage("Krok 4 — spójność", kolor, etykieta)
            st.session_state.krok = 99
            st.rerun()


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    st.title("🔍 Weryfikator informacji o szczepieniach")
    st.caption(
        "Narzędzie wspierające samodzielną ocenę wiarygodności informacji zdrowotnych. "
        "Oparte na teorii scaffoldingu (Wygotski, 1978) i inokulacji poznawczej (van der Linden & Lewandowsky, 2021)."
    )

    krok = st.session_state.krok

    if krok == 99:
        renderuj_historie()
        pokaz_karte_oceny()
        return

    mapa = {
        0: krok_0_input,
        0.5: krok_0_5_znany_mit,
        1: krok_1_zrodlo,
        2: krok_2_autor,
        3: krok_3_dowody,
        4: krok_4_spojnosc,
    }

    if krok in mapa:
        if krok not in (0, 0.5):
            renderuj_historie()
        mapa[krok]()
    else:
        st.error(f"Nieznany krok: {krok}")
        if st.button("Zacznij od nowa"):
            reset()

    # Sidebar
    if isinstance(krok, (int, float)) and 1 <= krok < 99:
        krok_int = int(krok)
        st.sidebar.markdown("### Postęp weryfikacji")
        st.sidebar.progress(min((krok_int - 1) / 4, 1.0))
        kroki_nazwy = ["Źródło", "Autor", "Dowody", "Spójność"]
        for i, nazwa in enumerate(kroki_nazwy):
            prefix = "✅" if i + 1 < krok_int else ("▶️" if i + 1 == krok_int else "⬜")
            st.sidebar.markdown(f"{prefix} Krok {i+1}: {nazwa}")
        if st.session_state.flagi:
            st.sidebar.markdown("---\n### Zebrane sygnały")
            for f in st.session_state.flagi:
                st.sidebar.markdown(f"{ikona_flagi(f['kolor'])} {f['krok']}")
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Zacznij od nowa", use_container_width=True):
            reset()


if __name__ == "__main__":
    main()