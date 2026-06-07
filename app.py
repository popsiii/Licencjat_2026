import streamlit as st
import anthropic
import json

# ──────────────────────────────────────────────
# KONFIGURACJA
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Asystent oceny wiarygodności informacji o szczepieniach",
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
    # ── UŻYWANE PRZEZ SYSTEM FLAG (3 główne kategorie FLICC) ──
    "falszywy_ekspert": {
        "nazwa": "Fake Experts (fałszywy autorytet)",
        "ikona": "👨‍⚕️",
        "opis": "Prezentowanie osoby bez odpowiednich kwalifikacji jako wiarygodnego eksperta. Popularność, tytuł lub pewność siebie nie zastępują kompetencji medycznych ani recenzji naukowej.",
        "przyklad": "Influencer zdrowotny bez wykształcenia medycznego lub jeden lekarz twierdzący coś inaczej niż WHO i setki badań.",
        "jak_rozpoznac": "Sprawdź czy to stanowisko jednej osoby czy konsensus towarzystw naukowych. Czy opinia została opublikowana w recenzowanych pismach?",
    },
    "cherry_picking": {
        "nazwa": "Cherry Picking (wybiórczy dobór danych)",
        "ikona": "🍒",
        "opis": "Wybieranie tylko tych danych które wspierają daną tezę przy pomijaniu tych które jej przeczą. Liczby mogą być prawdziwe — manipulacja polega wyłącznie na selekcji.",
        "przyklad": "100 dzieci miało NOP po szczepieniu — bez informacji że szczepiono 10 milionów.",
        "jak_rozpoznac": "Brak kontekstu dla liczb. Brak porównania do grupy kontrolnej. Brak informacji o wielkości próby.",
    },
    "teoria_spiskowa": {
        "nazwa": "Conspiracy Theories (teorie spiskowe)",
        "ikona": "🕸️",
        "opis": "Zakładanie istnienia ukrytej zmowy między wieloma niezależnymi instytucjami. Strukturalnie odporne na obalenie — każdy kontrargument jest interpretowany jako kolejny dowód spisku.",
        "przyklad": "Big Pharma, WHO i rządy ukrywają prawdę o szczepieniach dla zysku.",
        "jak_rozpoznac": "Schemat: wszyscy się mylą / są opłaceni, tylko my wiemy prawdę. Niemożność obalenia — każdy dowód przeciwko to część spisku.",
    },

    # ── UŻYWANE PRZY BAZIE MITÓW ──
    "anegdota": {
        "nazwa": "Anecdote (dowód anegdotyczny)",
        "ikona": "💬",
        "opis": "Używanie jednostkowego doświadczenia jako dowodu powszechnego. Podkategoria błędów logicznych (Logical Fallacies).",
        "przyklad": "Dziecko zachorowało wkrótce po szczepieniu -> wniosek że szczepionka spowodowała chorobę.",
        "jak_rozpoznac": "Zwróć uwagę na: znam kogoś kto..., u mnie po szczepieniu..., moja sąsiadka mówiła że...",
    },
    "ukryta_prawda": {
        "nazwa": "Misrepresentation (fałszywe przedstawienie)",
        "ikona": "🕵️",
        "opis": "Zniekształcanie sytuacji lub stanowiska oponenta w celu manipulacji odbiorcą. Podkategoria teorii spiskowych.",
        "przyklad": "Tego nie powiedzą ci lekarze... / Co WHO ukrywa o szczepieniach.",
        "jak_rozpoznac": "Słowa klucze: ukrywają, nie chcą żebyś wiedział, prawda o której milczą, przebudź się.",
    },
    "wycofane_badanie": {
        "nazwa": "Cherry Picking — wycofane badanie",
        "ikona": "📄",
        "opis": "Szczególna forma wybiórczego doboru danych: cytowanie publikacji wycofanej z literatury naukowej przy pomijaniu setek badań które jej przeczą.",
        "przyklad": "Badanie Wakefielda z 1998 r. łączące MMR z autyzmem — wycofane przez Lancet po ujawnieniu fałszerstw.",
        "jak_rozpoznac": "Sprawdź status publikacji na PubMed. Wyszukaj nazwę badania + retracted.",
    },

    # ── TYLKO W KAFELKU POZNAJ WSZYSTKIE ──
    "logical_fallacies": {
        "nazwa": "Logical Fallacies (błędy logiczne)",
        "ikona": "🧠",
        "opis": "Argumentacja w której wniosek nie wynika logicznie z przesłanek. Obejmuje wiele podkategorii — ad hominem, fałszywy wybór, równię pochyłą, anegdotę i inne. Jedna z pięciu głównych kategorii FLICC.",
        "przyklad": "Szczepionka nie jest w 100% skuteczna, więc jest bezużyteczna. / Klimat zmieniał się naturalnie w przeszłości, więc obecne zmiany też są naturalne.",
        "jak_rozpoznac": "Sprawdź czy wniosek rzeczywiście wynika z podanych przesłanek. Czy nie pomija innych możliwych wyjaśnień?",
    },
    "impossible_expectations": {
        "nazwa": "Impossible Expectations (niemożliwe oczekiwania)",
        "ikona": "🎯",
        "opis": "Stawianie standardów pewności tak wysokich, że żaden dowód naukowy nie jest w stanie ich spełnić. Znane też jako 'przesuwanie bramek'. Jedna z pięciu głównych kategorii FLICC.",
        "przyklad": "Dopóki nie ma 50-letnich badań nie możemy mówić że szczepionka jest bezpieczna.",
        "jak_rozpoznac": "Czy wymagany standard dowodu jest w ogóle osiągalny? Czy ta sama poprzeczka jest stosowana do chorób zakaźnych?",
    },
    "ad_hominem": {
        "nazwa": "Ad Hominem (atak na osobę)",
        "ikona": "🎯",
        "opis": "Atakowanie osoby lub grupy zamiast jej argumentów. Podkategoria błędów logicznych.",
        "przyklad": "Nie słuchaj tego lekarza — jest opłacany przez Big Pharmę.",
        "jak_rozpoznac": "Czy argument odnosi się do treści czy do osoby która ją głosi?",
    },
    "false_choice": {
        "nazwa": "False Choice (fałszywy wybór)",
        "ikona": "⚖️",
        "opis": "Przedstawianie dwóch opcji jako jedynych możliwości gdy istnieją inne. Podkategoria błędów logicznych.",
        "przyklad": "Albo szczepionka albo naturalna odporność — nie ma innych opcji ochrony.",
        "jak_rozpoznac": "Czy naprawdę istnieją tylko dwie możliwości? Jakie inne opcje są pomijane?",
    },
    "oversimplification": {
        "nazwa": "Oversimplification (nadmierne uproszczenie)",
        "ikona": "📉",
        "opis": "Upraszczanie złożonej sytuacji w sposób zniekształcający rzeczywistość i prowadzący do błędnych wniosków. Podkategoria błędów logicznych.",
        "przyklad": "Szczepionki zawierają rtęć więc są toksyczne — bez uwzględnienia dawki i formy chemicznej.",
        "jak_rozpoznac": "Czy pomija się istotny kontekst, dawkę, mechanizm lub inne czynniki?",
    },
    "single_cause": {
        "nazwa": "Single Cause (pojedyncza przyczyna)",
        "ikona": "🔗",
        "opis": "Zakładanie że zjawisko ma jedną przyczynę gdy w rzeczywistości może ich być wiele. Podkategoria błędów logicznych.",
        "przyklad": "Wzrost zachorowań na autyzm to dowód że szczepionki są przyczyną — bez uwzględnienia zmian w kryteriach diagnozy.",
        "jak_rozpoznac": "Czy brane są pod uwagę inne możliwe przyczyny? Czy korelacja jest mylona z przyczynowością?",
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
        "schemat": "wycofane_badanie",
        "obalenie": (
            "Nie istnieją badania potwierdzające związek między jakąkolwiek szczepionką a autyzmem. "
            "Dezinformacja ta pochodzi z badania które zostało definitywnie obalone i wycofane z czasopisma naukowego. "
            "Od tego czasu setki dobrze zaprojektowanych badań potwierdziły że szczepionki nie powodują autyzmu "
            "(PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "skladniki",
        "slowa_kluczowe": ["rtęć", "aluminium", "formaldehyd", "tiomersal", "składniki", "toksyczne", "trucizna", "chemikalia"],
        "mit": "Składniki szczepionek (rtęć, aluminium) są toksyczne",
        "schemat": "cherry_picking",
        "obalenie": (
            "Substancje wymieniane na etykietach szczepionek — rtęć, aluminium, formaldehyd — "
            "występują naturalnie w organizmie, spożywanej żywności i środowisku. "
            "Ich ilości w szczepionkach są bardzo małe i nie są szkodliwe dla organizmu. "
            "Szczepionki przechodzą rygorystyczne badania kliniczne i procesy certyfikacji WHO "
            "potwierdzające ich bezpieczeństwo (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "harmonogram",
        "slowa_kluczowe": ["za dużo szczepionek", "przeciąża układ odpornościowy", "za wcześnie", "harmonogram szczepień"],
        "mit": "Zbyt wiele szczepionek naraz przeciąża układ odpornościowy",
        "schemat": "cherry_picking",
        "obalenie": (
            "Podanie więcej niż jednej szczepionki jednocześnie nie wykazało żadnych negatywnych efektów "
            "dla odporności organizmu. Nasz układ odpornościowy codziennie styka się z ogromną liczbą patogenów "
            "i jest przygotowany do obsługi wielu antygenów jednocześnie. "
            "Harmonogram szczepień jest precyzyjnie zaplanowany przez naukowców i lekarzy "
            "by zapewnić maksymalną ochronę zanim ryzyko choroby jest największe (PAHO, 2025)."
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
            "Szczepionki uczą układ odpornościowy walczyć z chorobami bez ryzyka jakie niosą same choroby — "
            "poważnej choroby, hospitalizacji, długotrwałych skutków i śmierci. "
            "Układ odpornościowy wytwarza przeciwciała zarówno po kontakcie z patogenem jak i po szczepieniu. "
            "Szczepienie niesie minimalne ryzyko, podczas gdy zachorowanie na chorobę możliwą do zapobieżenia "
            "jest znacznie bardziej ryzykowne (PAHO, 2025)."
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
            "Dzięki szczepieniom wiele chorób stało się rzadkich lub zostało wyeliminowanych. "
            "Jednak wirusy i bakterie które je powodują nadal krążą w niektórych częściach świata "
            "i nie respektują granic. Mogą zainfekować każdego kto nie jest chroniony. "
            "Gdy wyszczepialność spada, choroby wracają (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "dieta_zastepuje",
        "slowa_kluczowe": ["zdrowa dieta", "witaminy", "suplementy", "ćwiczenia zamiast szczepień", "naturalne metody odporności"],
        "mit": "Zdrowa dieta i witaminy zastępują szczepionki",
        "schemat": "false_choice",
        "obalenie": (
            "Szczepionki są najskuteczniejszym i najmniej ryzykownym sposobem budowania odporności "
            "na choroby którym można zapobiegać. Zrównoważona dieta i ćwiczenia są ważne dla zdrowia, "
            "ale same nie ochronią przed chorobami takimi jak polio, odra czy krztusiec. "
            "Witaminy i suplementy również nie zapobiegają zakażeniom. "
            "Jeśli ktoś twierdzi inaczej — zastanów się czy nie czerpie z tego korzyści finansowych (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "nop",
        "slowa_kluczowe": ["nop", "niepożądany", "odczyn", "skutki uboczne", "powikłania po szczepieniu", "śmierć po szczepieniu", "długoterminowe skutki"],
        "mit": "Szczepionki powodują niebezpieczne długoterminowe skutki uboczne",
        "schemat": "impossible_expectations",
        "obalenie": (
            "Zdecydowana większość niepożądanych odczynów poszczepiennych to łagodne reakcje — "
            "ból w miejscu wkłucia, nieznaczna gorączka — trwające 1–3 dni. "
            "Szczepionki są stale monitorowane pod kątem bezpieczeństwa przez krajowe i międzynarodowe agencje. "
            "Ryzyko powikłań po szczepieniu jest wielokrotnie mniejsze niż ryzyko powikłań po samej chorobie (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "ciaza",
        "slowa_kluczowe": ["ciąża szczepienie", "szczepienie w ciąży", "szczepienia w ciąży", "niebezpieczne w ciąży", "kobiety w ciąży"],
        "mit": "Szczepienia w ciąży są niebezpieczne",
        "schemat": "falszywy_ekspert",
        "obalenie": (
            "Szczepienia w ciąży są zalecane i bezpieczne — chronią zarówno matkę jak i dziecko. "
            "Twierdzenia o szkodliwości szczepień dla płodności lub w ciąży nie mają potwierdzenia w badaniach naukowych. "
            "Zalecenia dotyczące szczepień w ciąży opierają się na rozległych badaniach klinicznych "
            "i są wydawane przez organizacje medyczne na całym świecie (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "chip",
        "slowa_kluczowe": ["chip", "czip", "śledzenie", "5g", "bill gates", "mikrochip", "kontrola umysłu"],
        "mit": "W szczepionkach są chipy do śledzenia ludzi",
        "schemat": "teoria_spiskowa",
        "obalenie": (
            "Szczepionki nie zawierają chipów ani żadnych urządzeń elektronicznych. "
            "To szkodliwa dezinformacja rozpowszechniana w internecie. "
            "Składniki wszystkich szczepionek są publicznie dostępne i rygorystycznie weryfikowane "
            "przez niezależne agencje regulacyjne (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },
    {
        "id": "spisek",
        "slowa_kluczowe": ["big pharma", "ukrywają", "spisek", "zarabiają na nas", "kontrola", "przemysł farmaceutyczny", "stop nop"],
        "mit": "Firmy farmaceutyczne i rządy ukrywają prawdę o szczepieniach",
        "schemat": "teoria_spiskowa",
        "obalenie": (
            "Wszystkie dane rejestracyjne szczepionek są publicznie dostępne w bazach EMA i FDA. "
            "Teorie spiskowe zakładają zmowę milczenia tysięcy niezależnych naukowców w dziesiątkach krajów "
            "— co jest statystycznie niemożliwe do utrzymania. "
            "Szczepionki przechodzą niezależną weryfikację przez wiele instytucji w różnych krajach (PAHO, 2025)."
        ),
        "link": "https://www.paho.org/en/topics/immunization/debunking-immunization-myths",
        "link_nazwa": "PAHO/WHO — obalanie mitów o szczepieniach"
    },

    {
    "id": "mrna_dna",
    "slowa_kluczowe": [
        "mrna zmienia dna",
        "zmienia genom",
        "modyfikuje dna",
        "ingeruje w dna",
        "szczepionka mrna zmienia geny",
        "zmienia materiał genetyczny",
        "szczepionki genetyczne" ,
    ],
    "mit": "Szczepionki mRNA przeciw COVID-19 zmieniają geny człowieka",
    "schemat": "oversimplification",
    "obalenie": (
        "Szczepionki mRNA nie integrują się z ludzkim DNA i nie mogą zmieniać materiału genetycznego człowieka. "
        "mRNA zawarte w szczepionce jest jedynie krótkotrwałą instrukcją do wytworzenia białka wirusa, które pobudza układ odpornościowy do odpowiedzi. "
        "Nie wnika ono do jądra komórkowego, gdzie znajduje się DNA, a po spełnieniu swojej funkcji ulega naturalnemu rozkładowi w ciągu kilkudziesięciu godzin. "
        "Twierdzenie o zmianie genomu wynika najczęściej z mylenia pojęć DNA i RNA oraz uproszczonego przedstawiania mechanizmu działania szczepionek mRNA."
    ),
    "link": "https://szczepienia.pzh.gov.pl/faq/czy-szczepionki-mrna-zmieniaja-ludzkie-dna/",
    "link_nazwa": "PZH — Czy szczepionki mRNA zmieniają ludzkie DNA?"
}
]

ZASOBY = [
    ("🏛️ PZH — szczepienia.pzh.gov.pl", "https://szczepienia.pzh.gov.pl"),
    ("🌍 WHO — szczepionki", "https://www.who.int/health-topics/vaccines-and-immunization"),
    ("🔬 HealthFeedback.org", "https://healthfeedback.org"),
    ("🇪🇺 ECDC — Europejskie Centrum Kontroli Chorób", "https://www.ecdc.europa.eu/en/immunisation-and-vaccines"),
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
        st.markdown(
            "Taksonomia FLICC (Cook, 2020; Zanartu i in., 2024) opisuje pięć głównych kategorii "
            "technik dezinformacji naukowej oraz ich podkategorie."
        )
        st.markdown("#### F — Fake Experts (fałszywy autorytet)")
        st.markdown(karta_schematu("falszywy_ekspert"), unsafe_allow_html=True)

        st.markdown("#### L — Logical Fallacies (błędy logiczne)")
        st.markdown(karta_schematu("logical_fallacies"), unsafe_allow_html=True)
        st.markdown("**Wybrane podkategorie:**")
        for s_id in ["ad_hominem", "anegdota", "false_choice", "oversimplification", "single_cause"]:
            st.markdown(karta_schematu(s_id), unsafe_allow_html=True)

        st.markdown("#### I — Impossible Expectations (niemożliwe oczekiwania)")
        st.markdown(karta_schematu("impossible_expectations"), unsafe_allow_html=True)

        st.markdown("#### C — Cherry Picking (wybiórczy dobór danych)")
        st.markdown(karta_schematu("cherry_picking"), unsafe_allow_html=True)
        st.markdown("**Wybrana podkategoria:**")
        st.markdown(karta_schematu("wycofane_badanie"), unsafe_allow_html=True)

        st.markdown("#### C — Conspiracy Theories (teorie spiskowe)")
        st.markdown(karta_schematu("teoria_spiskowa"), unsafe_allow_html=True)
        st.markdown("**Wybrana podkategoria:**")
        st.markdown(karta_schematu("ukryta_prawda"), unsafe_allow_html=True)

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
            if mit.get("schemat"):
                st.session_state.setdefault("schematy", [])
                if mit["schemat"] not in st.session_state.schematy:
                    st.session_state.schematy.append(mit["schemat"])
            st.session_state.krok = 0.5
        else:
            st.session_state.krok = 1
        st.rerun()


def krok_0_5_znany_mit():
    renderuj_historie()
    mit = st.session_state.znany_mit

    if not st.session_state.get("flaga_mitu_dodana", False):
        dodaj_flage(
            "Moduł 0 — baza mitów",
            "czerwona",
            f"Rozpoznano znany schemat: {mit['mit']}"
        )
        st.session_state.flaga_mitu_dodana = True


    with st.chat_message("assistant"):
        st.markdown("Rozpoznałem w tej informacji znany schemat dezinformacji:")
        st.markdown(karta_mitu(mit), unsafe_allow_html=True)
        # pokaż też kartę schematu
        if mit.get("schemat"):
            st.markdown(karta_schematu(mit["schemat"]), unsafe_allow_html=True)
        st.markdown("Czy chcesz mimo to przejść przez pełny proces weryfikacji krok po kroku?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Tak, przejdź przez weryfikację", use_container_width=True):
            dodaj_wiadomosc("assistant",
                f"🚨 **Rozpoznany schemat:** {mit['mit']}\n\n{mit['obalenie']}\n\nMimo to przejdziemy przez pełny proces weryfikacji."
            )
            st.session_state.krok = 1
            st.rerun()
    with col2:
        if st.button("❌ Nie, to wystarczy", use_container_width=True):
            dodaj_wiadomosc("assistant", f"🚨 **Rozpoznany schemat:** {mit['mit']}\n\n{mit['obalenie']}")
            st.session_state.krok = 99
            st.rerun()


def krok_1_zrodlo():
    st.markdown(pasek_krokow(1), unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown("**Krok 1 z 4 — Źródło informacji**\n\nSkąd pochodzi ta informacja?")

    opcje = {
        "A": ("📱 Media społecznościowe lub wideo (FB, TikTok, YT, IG, X)", "czerwona", "Media społecznościowe nie mają mechanizmów weryfikacji treści — każdy może opublikować cokolwiek."),
        "B": ("📰 Portal ogólny / informacyjny (Onet, WP, Gazeta.pl)", "zolita", "Portale ogólne mają zmienne standardy weryfikacji. Sprawdź kto jest autorem artykułu."),
        "C": ("🌿 Portal alternatywny / naturalny / 'eko' / 'wolnościowy'", "czerwona", "Portale promujące medycynę alternatywną często publikują treści pseudonaukowe bez recenzji ekspertów."),
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
        "C": ("🏢 Organizacja antyszczepionkowa (np. STOP NOP)", "czerwona", "Organizacje antyszczepionkowe w Polsce funkcjonują w bańkach informacyjnych i konsekwentnie rozpowszechniają informacje sprzeczne z konsensusem medycznym (Demczuk, 2022)."),
        "D": ("📰 Dziennikarz / redakcja portalu", "zolita", "Podpisany autor zwiększa odpowiedzialność redakcyjną, ale nie gwarantuje rzetelności treści (Wineburg & McGrew, 2018)."),
        "E": ("🩺 Lekarz / ekspert / instytucja medyczna", "zielona", "Autor z wykształceniem medycznym lub instytucja to pozytywny sygnał. Pamiętaj jednak że nawet eksperci mogą być sprzeczni z konsensusem — sprawdź co mówią inne instytucje w kroku 4."),
    }

    schematy_k2 = {
        "B": "falszywy_ekspert",
        "C": "teoria_spiskowa",
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
        "E": ("🔄 Powołuje się na 'ukrywane' lub 'cenzurowane' dane", "czerwona", "ukryta_prawda"),
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
        "B": ("❌ Zaprzeczają — instytucje medyczne mówią inaczej", "czerwona", "Gdy renomowane instytucje zaprzeczają informacji — to poważna czerwona flaga. Instytucje jak WHO czy PZH opierają zalecenia na tysiącach badań."),
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
    st.title("🔍 Asystent oceny wiarygodności informacji o szczepieniach")
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