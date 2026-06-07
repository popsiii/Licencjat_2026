# ============================================================
# ANALIZA DANYCH - KOMPETENCJE INFORMACYJNE W ZAKRESIE SZCZEPIEN
# Marta Popielska, praca licencjacka, SWPS 2026
# ============================================================


# ============================================================
# 1. PAKIETY
# ============================================================

library(readxl)
library(dplyr)
library(psych)


# ============================================================
# 2. WCZYTANIE DANYCH
# ============================================================

df <- read_excel("odpowiedziformsbadanieszczepienia.xlsx")
dim(df)  # powinno byc 79 wierszy i 32 kolumny


# ============================================================
# 3. ZMIANA NAZW KOLUMN
# ============================================================

colnames(df) <- c(
  "czas", "zgoda", "pelnoletnosc", "rok_ur", "plec", "wyksztalcenie",
  "internet_czest", "internet_czas", "szczepienia_korzysta", "szczepienia_rodzaj",
  "eh1", "eh2", "eh3", "eh4", "eh5", "eh6", "eh7", "eh8",
  "dvl1", "dvl2", "dvl3", "dvl4", "dvl5", "dvl6", "dvl7",
  "weryfikacja_med", "weryfikacja_szczep",
  "weryfikacja_sposob", "weryfikacja_przyczyna", "wsparcie",
  "przestrzenie", "social_media"
)


# ============================================================
# 4. CZYSZCZENIE DANYCH
# ============================================================

# --- 4.1 Rok urodzenia ---
# usuwamy format ".0" i zamieniamy na liczbe
df$rok_ur <- as.numeric(gsub("\\.0$", "", as.character(df$rok_ur)))
# jedna osoba wpisala date zamiast roku (22) - zamieniamy na NA
df$rok_ur <- ifelse(df$rok_ur < 1900, NA, df$rok_ur)# sprawdzenie
table(df$rok_ur)


# --- 4.2 DVL - rekodowanie opcji neutralnej ---
dvl_cols <- c("dvl1","dvl2","dvl3","dvl4","dvl5","dvl6","dvl7")

# --- DVL: rekodowanie (3 → 0) ---
dvl_cols <- c("dvl1","dvl2","dvl3","dvl4","dvl5","dvl6","dvl7")

df[dvl_cols] <- lapply(df[dvl_cols], function(x) {
  ifelse(x == 3, 0,
         ifelse(x == 4, 3,
                ifelse(x == 5, 4, x)))
})


# ============================================================
# 5. FILTROWANIE PROBY
# ============================================================

df_clean <- df %>%
  filter(!is.na(rok_ur))

nrow(df_clean)  # powinno być 78nrow(df_clean)  # powinno być 78

# obliczamy wiek NA df_clean (po filtrowaniu!)
df_clean$wiek <- 2026 - df_clean$rok_ur

# kodowanie grupy szczepien (do H3)
df_clean$szczepienia_grupa <- case_when(
  df_clean$szczepienia_korzysta == "Tak" ~ "szczepi",
  df_clean$szczepienia_korzysta == "Nie" ~ "nie_szczepi",
  TRUE ~ NA_character_
)


# kodowanie czestotliwosci weryfikacji jako liczba (do H2)
df_clean$weryfikacja_szczep_num <- recode(df_clean$weryfikacja_szczep,
                                          "nigdy"   = 1,
                                          "rzadko"  = 2,
                                          "czasami" = 3,
                                          "często"  = 4,
                                          "zawsze"  = 5
)


# ============================================================
# 6. OBLICZANIE SUM SKAL
# ============================================================

# --- eHEALS (8 itemow, zakres 8-40) ---
# na.rm = FALSE: jesli ktos ma brak, jego suma tez bedzie NA
df_clean$eheals_sum <- rowSums(
  df_clean[, c("eh1","eh2","eh3","eh4","eh5","eh6","eh7","eh8")],
  na.rm = FALSE
)

# --- DVL (7 itemow, zakres 7-28) ---
# metoda: odp 3 = 0

df_clean$dvl_sum <- rowSums(df_clean[, dvl_cols])


# ============================================================
# 6.1 RZETELNOŚĆ SKAL (ALFA CRONBACHA)
# ============================================================

# eHEALS
alpha_eheals <- psych::alpha(df_clean[, c("eh1","eh2","eh3","eh4","eh5","eh6","eh7","eh8")])
print(alpha_eheals)

# DVL
alpha_dvl <- psych::alpha(df_clean[, dvl_cols])
print(alpha_dvl)

# ============================================================
# 7. STATYSTYKI OPISOWE
# ============================================================

# --- proba ---
describe(df_clean$wiek)     # mediana powinna byc okolo 22
table(df_clean$plec)
table(df_clean$wyksztalcenie)
table(df_clean$szczepienia_korzysta)

# --- skale ---
describe(df_clean[, c("eheals_sum", "dvl_sum")])

# --- braki w itemach DVL ---
colSums(is.na(df_clean[dvl_cols]))


# ============================================================
# 8. TESTY NORMALNOSCI (Shapiro-Wilk)
# ============================================================

shapiro.test(df_clean$eheals_sum)
shapiro.test(df_clean$dvl_sum)

# eHEALS narusza normalność (p < 0.05),
# dlatego do analiz użyto korelacji Spearmana

# ============================================================
# 9. WERYFIKACJA HIPOTEZ
# ============================================================

# --- H1: eHEALS <-> DVL ---
cor.test(df_clean$eheals_sum, df_clean$dvl_sum,
         method = "spearman", use = "complete.obs")

# --- H2: DVL <-> czestotliwosc weryfikacji szczepien ---
cor.test(df_clean$dvl_sum, df_clean$weryfikacja_szczep_num,
         method = "spearman", use = "complete.obs")

# --- H3: DVL ~ szczepienia (Mann-Whitney) ---
df_h3 <- df_clean %>%
  filter(!is.na(szczepienia_grupa))

wilcox.test(dvl_sum ~ szczepienia_grupa, data = df_h3)

# srednie dla grup H3
df_h3 %>%
  filter(!is.na(dvl_sum)) %>%   # dodaj ten wiersz
  group_by(szczepienia_grupa) %>%
  summarise(
    n       = n(),
    srednia = mean(dvl_sum),
    sd      = sd(dvl_sum),
    mediana = median(dvl_sum)
  )


# ============================================================
# 10. PYTANIA APLIKACYJNE - statystyki opisowe
# ============================================================

# kodowanie odpowiedzi wielokrotnego wyboru jako zmienne binarne (0/1)

# --- sposoby weryfikacji ---
df_clean$wer_autor      <- as.integer(grepl("autorem lub źródłem",       df_clean$weryfikacja_sposob))
df_clean$wer_porownanie <- as.integer(grepl("porównuję informację",       df_clean$weryfikacja_sposob))
df_clean$wer_instytucje <- as.integer(grepl("stronach instytucji",        df_clean$weryfikacja_sposob))
df_clean$wer_badania    <- as.integer(grepl("poparta badaniami",          df_clean$weryfikacja_sposob))
df_clean$wer_data       <- as.integer(grepl("datę publikacji",            df_clean$weryfikacja_sposob))
df_clean$wer_ai         <- as.integer(grepl("sztucznej inteligencji",     df_clean$weryfikacja_sposob))
df_clean$wer_lekarz     <- as.integer(grepl("pytam lekarza",              df_clean$weryfikacja_sposob))
df_clean$wer_portale    <- as.integer(grepl("portali popularnonaukowych", df_clean$weryfikacja_sposob))
df_clean$wer_brak       <- as.integer(grepl("nie podejmuję",              df_clean$weryfikacja_sposob))

# --- przyczyny nieweryfikowania ---
df_clean$prz_czas      <- as.integer(grepl("brak czasu",                 df_clean$weryfikacja_przyczyna))
df_clean$prz_zaufanie  <- as.integer(grepl("zaufanie do źródła",         df_clean$weryfikacja_przyczyna))
df_clean$prz_zrozum    <- as.integer(grepl("zrozumiałe i wiarygodne",    df_clean$weryfikacja_przyczyna))
df_clean$prz_sprzeczne <- as.integer(grepl("sprzecznych informacji",     df_clean$weryfikacja_przyczyna))
df_clean$prz_potrzeba  <- as.integer(grepl("nie czuję takiej potrzeby",  df_clean$weryfikacja_przyczyna))
df_clean$prz_trudnosc  <- as.integer(grepl("trudność w ocenie",          df_clean$weryfikacja_przyczyna))
df_clean$prz_wiedza    <- as.integer(grepl("brak wiedzy",                df_clean$weryfikacja_przyczyna))
df_clean$prz_narzedzia <- as.integer(grepl("brak odpowiednich narzędzi", df_clean$weryfikacja_przyczyna))

# --- oczekiwane wsparcie ---
df_clean$wsp_platforma    <- as.integer(grepl("platforma z rzetelną",      df_clean$wsparcie))
df_clean$wsp_ekspert      <- as.integer(grepl("pytania ekspertowi",         df_clean$wsparcie))
df_clean$wsp_narzedzie    <- as.integer(grepl("sprawdzania wiarygodności",  df_clean$wsparcie))
df_clean$wsp_rekomendacje <- as.integer(grepl("rekomendacje sprawdzonych",  df_clean$wsparcie))
df_clean$wsp_ai           <- as.integer(grepl("sztucznej inteligencji",     df_clean$wsparcie))
df_clean$wsp_materialy    <- as.integer(grepl("infografiki",                df_clean$wsparcie))
df_clean$wsp_kurs         <- as.integer(grepl("kurs lub szkolenie",         df_clean$wsparcie))
df_clean$wsp_brak         <- as.integer(grepl("nie potrzebuję",             df_clean$wsparcie))

# --- przestrzenie informacyjne ---
df_clean$prz_inst    <- as.integer(grepl("ministerstwa",      df_clean$przestrzenie))
df_clean$prz_portale <- as.integer(grepl("portale medyczne",  df_clean$przestrzenie))
df_clean$prz_fora    <- as.integer(grepl("fora internetowe",  df_clean$przestrzenie))
df_clean$prz_lekarze <- as.integer(grepl("lekarze",           df_clean$przestrzenie))
df_clean$prz_rodzina <- as.integer(grepl("rodzina i znajomi", df_clean$przestrzenie))
df_clean$prz_social  <- as.integer(grepl("Social media",      df_clean$przestrzenie))

# --- social media ---
df_clean$sm_fb   <- as.integer(grepl("Facebook",     df_clean$social_media))
df_clean$sm_ig   <- as.integer(grepl("Instagram",    df_clean$social_media))
df_clean$sm_yt   <- as.integer(grepl("Youtube",      df_clean$social_media))
df_clean$sm_x    <- as.integer(grepl("Platforma X",  df_clean$social_media))
df_clean$sm_tt   <- as.integer(grepl("TikTok",       df_clean$social_media))
df_clean$sm_li   <- as.integer(grepl("LinkedIn",     df_clean$social_media))
df_clean$sm_brak <- as.integer(grepl("Nie korzystam",df_clean$social_media))

# --- podsumowania ---
cat("=== SPOSOBY WERYFIKACJI ===\n")
sort(colSums(df_clean[, c("wer_autor","wer_porownanie","wer_instytucje",
                          "wer_badania","wer_data","wer_ai",
                          "wer_lekarz","wer_portale","wer_brak")]),
     decreasing = TRUE)

cat("\n=== PRZYCZYNY NIEWERYFIKOWANIA ===\n")
sort(colSums(df_clean[, c("prz_czas","prz_zaufanie","prz_zrozum",
                          "prz_sprzeczne","prz_potrzeba","prz_trudnosc",
                          "prz_wiedza","prz_narzedzia")]),
     decreasing = TRUE)

cat("\n=== OCZEKIWANE WSPARCIE ===\n")
sort(colSums(df_clean[, c("wsp_platforma","wsp_ekspert","wsp_narzedzie",
                          "wsp_rekomendacje","wsp_ai","wsp_materialy",
                          "wsp_kurs","wsp_brak")]),
     decreasing = TRUE)

cat("\n=== PRZESTRZENIE INFORMACYJNE ===\n")
sort(colSums(df_clean[, c("prz_inst","prz_portale","prz_fora",
                          "prz_lekarze","prz_rodzina","prz_social")]),
     decreasing = TRUE)

cat("\n=== SOCIAL MEDIA ===\n")
sort(colSums(df_clean[, c("sm_fb","sm_ig","sm_yt","sm_x",
                          "sm_tt","sm_li","sm_brak")]),
     decreasing = TRUE)


# ============================================================
# 11. ZAPIS DANYCH
# ============================================================

saveRDS(df_clean, "df_clean.rds")
# wczytanie w przyszlosci: df_clean <- readRDS("df_clean.rds")


describe(df_clean$wiek)



