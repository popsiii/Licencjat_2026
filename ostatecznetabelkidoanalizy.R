# ============================================================
# TABELE STATYSTYK OPISOWYCH - APA 7
# Marta Popielska, praca licencjacka, SWPS 2026
# ============================================================

library(dplyr)
library(flextable)
library(officer)

# Upewnij sie ze masz wczytany df_clean
# Jesli nie: df_clean <- readRDS("df_clean.rds")


# ============================================================
# TABELA 1: Charakterystyka próby
# ============================================================

# Wiek
wiek_row <- data.frame(
  Zmienna   = "Wiek (lata)",
  Kategoria = "",
  M_SD_Me   = paste0(
    "M = ", round(mean(df_clean$wiek, na.rm = TRUE), 2),
    ", SD = ", round(sd(df_clean$wiek, na.rm = TRUE), 2),
    ", Me = ", median(df_clean$wiek, na.rm = TRUE),
    ", min = ", min(df_clean$wiek, na.rm = TRUE),
    ", max = ", max(df_clean$wiek, na.rm = TRUE)
  ),
  N       = as.character(sum(!is.na(df_clean$wiek))),
  Procent = "",
  stringsAsFactors = FALSE
)

# Plec
plec_tab <- df_clean %>% count(plec) %>% arrange(desc(n))
plec_rows <- data.frame(
  Zmienna   = c("Płeć", rep("", nrow(plec_tab) - 1)),
  Kategoria = as.character(plec_tab$plec),
  M_SD_Me   = "",
  N         = as.character(plec_tab$n),
  Procent   = paste0(round(100 * plec_tab$n / sum(plec_tab$n), 1), "%"),
  stringsAsFactors = FALSE
)

# Wyksztalcenie
wykszt_tab <- df_clean %>%
  count(wyksztalcenie) %>%
  mutate(wyksztalcenie = factor(wyksztalcenie, levels = c(
    "podstawowe",
    "zawodowe",
    "średnie",
    "wyższe licencjackie/inżynierskie",
    "wyższe magisterskie/magisterskie inżynierskie"
  ))) %>%
  arrange(wyksztalcenie)
wykszt_rows <- data.frame(
  Zmienna   = c("Wykształcenie", rep("", nrow(wykszt_tab) - 1)),
  Kategoria = as.character(wykszt_tab$wyksztalcenie),
  M_SD_Me   = "",
  N         = as.character(wykszt_tab$n),
  Procent   = paste0(round(100 * wykszt_tab$n / sum(wykszt_tab$n), 1), "%"),
  stringsAsFactors = FALSE
)

# Korzystanie z internetu - wszyscy codziennie, wiec tylko 1 wiersz
internet_row <- data.frame(
  Zmienna   = "Częstotliwość korzystania z Internetu",
  Kategoria = "codziennie",
  M_SD_Me   = "",
  N         = as.character(nrow(df_clean)),
  Procent   = "100%",
  stringsAsFactors = FALSE
)

# Czas online - sprawdz unikalne wartosci w danych:
# table(df_clean$internet_czas)
# i upewnij sie ze kolejnosc ponizej pasuje do Twoich danych
czas_kolejnosc <- c(
  "mniej niż 1h dziennie",
  "2-3 h dziennie",
  "3-5 h dziennie",
  "więcej niż 5 h dziennie"
)

czas_tab <- df_clean %>%
  filter(!is.na(internet_czas)) %>%
  count(internet_czas) %>%
  mutate(internet_czas = factor(internet_czas, levels = czas_kolejnosc)) %>%
  arrange(internet_czas)

czas_rows <- data.frame(
  Zmienna   = c("Czas spędzany online dziennie", rep("", nrow(czas_tab) - 1)),
  Kategoria = as.character(czas_tab$internet_czas),
  M_SD_Me   = "",
  N         = as.character(czas_tab$n),
  Procent   = paste0(round(100 * czas_tab$n / sum(czas_tab$n), 1), "%"),
  stringsAsFactors = FALSE
)

# Szczepienia
szczep_tab <- df_clean %>%
  count(szczepienia_korzysta) %>%
  mutate(szczepienia_korzysta = factor(szczepienia_korzysta, levels = c(
    "Tak",
    "Nie",
    "Nie wiem, jakie szczepienia są zalecane dla mojej grupy wiekowej"
  ))) %>%
  arrange(szczepienia_korzysta)

szczep_rows <- data.frame(
  Zmienna   = c("Korzystanie ze szczepień zalecanych", rep("", nrow(szczep_tab) - 1)),
  Kategoria = as.character(szczep_tab$szczepienia_korzysta),
  M_SD_Me   = "",
  N         = as.character(szczep_tab$n),
  Procent   = paste0(round(100 * szczep_tab$n / sum(szczep_tab$n), 1), "%"),
  stringsAsFactors = FALSE
)

# Laczenie wszystkich sekcji
tab1 <- bind_rows(
  wiek_row,
  plec_rows,
  wykszt_rows,
  internet_row,
  czas_rows,
  szczep_rows
)
colnames(tab1) <- c("Zmienna", "Kategoria", "M, SD, Me", "N", "%")

ft1 <- flextable(tab1) %>%
  font(fontname = "Times New Roman", part = "all") %>%
  fontsize(size = 12, part = "all") %>%
  bold(part = "header") %>%
  border_remove() %>%
  hline_top(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "body", border = fp_border(width = 1.5)) %>%
  align(align = "left", part = "all") %>%
  align(j = c("N", "%"), align = "right", part = "all") %>%
  set_caption(caption = as_paragraph(as_b("Tabela 1"))) %>%
  add_footer_lines("Nota. N = 78.") %>%
  font(fontname = "Times New Roman", part = "footer") %>%
  fontsize(size = 12, part = "footer") %>%
  autofit()


# ============================================================
# TABELA 2: Statystyki opisowe skal eHEALS i DVL
# ============================================================

tab2 <- data.frame(
  Skala  = c("eHEALS", "DVL"),
  N      = c(sum(!is.na(df_clean$eheals_sum)), sum(!is.na(df_clean$dvl_sum))),
  M      = c(round(mean(df_clean$eheals_sum, na.rm = TRUE), 2),
             round(mean(df_clean$dvl_sum,    na.rm = TRUE), 2)),
  SD     = c(round(sd(df_clean$eheals_sum,   na.rm = TRUE), 2),
             round(sd(df_clean$dvl_sum,       na.rm = TRUE), 2)),
  Me     = c(median(df_clean$eheals_sum, na.rm = TRUE),
             median(df_clean$dvl_sum,    na.rm = TRUE)),
  Min    = c(min(df_clean$eheals_sum, na.rm = TRUE),
             min(df_clean$dvl_sum,    na.rm = TRUE)),
  Max    = c(max(df_clean$eheals_sum, na.rm = TRUE),
             max(df_clean$dvl_sum,    na.rm = TRUE)),
  Zakres = c("8-40", "0-28"),
  Alpha  = c(0.91, 0.64)
)
colnames(tab2) <- c("Skala", "N", "M", "SD", "Me",
                    "Min", "Max", "Zakres teoret.", "\u03b1")

ft2 <- flextable(tab2) %>%
  font(fontname = "Times New Roman", part = "all") %>%
  fontsize(size = 12, part = "all") %>%
  bold(part = "header") %>%
  border_remove() %>%
  hline_top(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "body", border = fp_border(width = 1.5)) %>%
  align(align = "left", part = "all") %>%
  align(j = c("N", "M", "SD", "Me", "Min", "Max", "\u03b1"),
        align = "right", part = "all") %>%
  set_caption(caption = as_paragraph(as_b("Tabela 2"))) %>%
  add_footer_lines(paste0(
    "Nota. eHEALS = eHealth Literacy Scale; DVL = Digital Vaccine Literacy Scale; ",
    "\u03b1 = alfa Cronbacha. Zakres DVL 0\u201328 wynika z modyfikacji punktowania ",
    "opcji neutralnej (szczeg\u00f3\u0142y w podrozdziale 4.3.2)."
  )) %>%
  font(fontname = "Times New Roman", part = "footer") %>%
  fontsize(size = 12, part = "footer") %>%
  autofit()


# ============================================================
# TABELA 3: Czestotliwosc weryfikacji
# ============================================================

wer_kolejnosc <- c("nigdy", "rzadko", "czasami", "cz\u0119sto", "zawsze")

wm <- df_clean %>%
  count(weryfikacja_med) %>%
  mutate(weryfikacja_med = factor(weryfikacja_med, levels = wer_kolejnosc)) %>%
  arrange(weryfikacja_med)

ws <- df_clean %>%
  count(weryfikacja_szczep) %>%
  mutate(weryfikacja_szczep = factor(weryfikacja_szczep, levels = wer_kolejnosc)) %>%
  arrange(weryfikacja_szczep)

tab3 <- bind_rows(
  data.frame(
    Pytanie = c("Weryfikacja informacji medycznych (og\u00f3lnie)",
                rep("", nrow(wm) - 1)),
    Kat     = as.character(wm$weryfikacja_med),
    N       = as.character(wm$n),
    Procent = paste0(round(100 * wm$n / sum(wm$n), 1), "%"),
    stringsAsFactors = FALSE
  ),
  data.frame(
    Pytanie = c("Weryfikacja informacji o szczepieniach",
                rep("", nrow(ws) - 1)),
    Kat     = as.character(ws$weryfikacja_szczep),
    N       = as.character(ws$n),
    Procent = paste0(round(100 * ws$n / sum(ws$n), 1), "%"),
    stringsAsFactors = FALSE
  )
)
colnames(tab3) <- c("Pytanie", "Cz\u0119stotliwo\u015b\u0107", "N", "%")

ft3 <- flextable(tab3) %>%
  font(fontname = "Times New Roman", part = "all") %>%
  fontsize(size = 12, part = "all") %>%
  bold(part = "header") %>%
  border_remove() %>%
  hline_top(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "body", border = fp_border(width = 1.5)) %>%
  align(align = "left", part = "all") %>%
  align(j = c("N", "%"), align = "right", part = "all") %>%
  set_caption(caption = as_paragraph(as_b("Tabela 3"))) %>%
  add_footer_lines("Nota. N = 78.") %>%
  font(fontname = "Times New Roman", part = "footer") %>%
  fontsize(size = 12, part = "footer") %>%
  autofit()


# ============================================================
# TABELA 4: Sposoby weryfikacji
# ============================================================

wer_labels <- c(
  wer_lekarz     = "Pytam lekarza lub innego specjalist\u0119",
  wer_porownanie = "Por\u00f3wnuj\u0119 z innymi stronami",
  wer_autor      = "Sprawdzam autora lub \u017ar\u00f3d\u0142o informacji",
  wer_instytucje = "Szukam na stronach instytucji publicznych",
  wer_badania    = "Sprawdzam, czy informacja jest poparta badaniami",
  wer_portale    = "Korzystam z portali popularnonaukowych",
  wer_ai         = "Korzystam z narz\u0119dzi AI (np. chatbot\u00f3w)",
  wer_data       = "Sprawdzam dat\u0119 publikacji",
  wer_brak       = "Nie podejmuj\u0119 dzia\u0142a\u0144 weryfikacyjnych"
)
wer_n <- colSums(df_clean[, names(wer_labels)], na.rm = TRUE)

tab4 <- data.frame(
  Sposob  = unname(wer_labels),
  N       = wer_n,
  Procent = paste0(round(100 * wer_n / nrow(df_clean), 1), "%"),
  stringsAsFactors = FALSE
) %>% arrange(desc(N))
rownames(tab4) <- NULL
colnames(tab4) <- c("Spos\u00f3b weryfikacji", "N", "%")

ft4 <- flextable(tab4) %>%
  font(fontname = "Times New Roman", part = "all") %>%
  fontsize(size = 12, part = "all") %>%
  bold(part = "header") %>%
  border_remove() %>%
  hline_top(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "body", border = fp_border(width = 1.5)) %>%
  align(align = "left", part = "all") %>%
  align(j = c("N", "%"), align = "right", part = "all") %>%
  set_caption(caption = as_paragraph(as_b("Tabela 4"))) %>%
  add_footer_lines(paste0(
    "Nota. N = 78. Respondenci mogli wskaza\u0107 maks. 3 odpowiedzi, ",
    "dlatego suma N przekracza liczebno\u015b\u0107 pr\u00f3by."
  )) %>%
  font(fontname = "Times New Roman", part = "footer") %>%
  fontsize(size = 12, part = "footer") %>%
  autofit()


# ============================================================
# TABELA 5: Przyczyny nieweryfikowania
# ============================================================

prz_labels <- c(
  prz_czas      = "Brak czasu",
  prz_zaufanie  = "Zaufanie do \u017ar\u00f3d\u0142a",
  prz_sprzeczne = "Zbyt du\u017ca ilo\u015b\u0107 sprzecznych informacji",
  prz_potrzeba  = "Nie czuj\u0119 takiej potrzeby",
  prz_zrozum    = "Informacje wydaj\u0105 si\u0119 wiarygodne na pierwszy rzut oka",
  prz_trudnosc  = "Trudno\u015b\u0107 w ocenie wiarygodno\u015bci",
  prz_wiedza    = "Brak wiedzy, jak sprawdzi\u0107 informacje",
  prz_narzedzia = "Brak odpowiednich narz\u0119dzi"
)
prz_n <- colSums(df_clean[, names(prz_labels)], na.rm = TRUE)

tab5 <- data.frame(
  Przyczyna = unname(prz_labels),
  N         = prz_n,
  Procent   = paste0(round(100 * prz_n / nrow(df_clean), 1), "%"),
  stringsAsFactors = FALSE
) %>% arrange(desc(N))
rownames(tab5) <- NULL
colnames(tab5) <- c("Przyczyna nieweryfikowania", "N", "%")

ft5 <- flextable(tab5) %>%
  font(fontname = "Times New Roman", part = "all") %>%
  fontsize(size = 12, part = "all") %>%
  bold(part = "header") %>%
  border_remove() %>%
  hline_top(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "body", border = fp_border(width = 1.5)) %>%
  align(align = "left", part = "all") %>%
  align(j = c("N", "%"), align = "right", part = "all") %>%
  set_caption(caption = as_paragraph(as_b("Tabela 5"))) %>%
  add_footer_lines(
    "Nota. N = 78. Respondenci mogli wskaza\u0107 maks. 3 odpowiedzi."
  ) %>%
  font(fontname = "Times New Roman", part = "footer") %>%
  fontsize(size = 12, part = "footer") %>%
  autofit()


# ============================================================
# TABELA 6: Przestrzenie informacyjne
# ============================================================

info_labels <- c(
  prz_lekarze = "Lekarze / personel medyczny",
  prz_portale = "Portale medyczne / naukowe",
  prz_rodzina = "Rodzina i znajomi",
  prz_inst    = "Strony instytucji publicznych (np. ministerstwa, sanepid)",
  prz_social  = "Media spo\u0142eczno\u015bciowe",
  prz_fora    = "Fora internetowe"
)
info_n <- colSums(df_clean[, names(info_labels)], na.rm = TRUE)

tab6 <- data.frame(
  Zrodlo  = unname(info_labels),
  N       = info_n,
  Procent = paste0(round(100 * info_n / nrow(df_clean), 1), "%"),
  stringsAsFactors = FALSE
) %>% arrange(desc(N))
rownames(tab6) <- NULL
colnames(tab6) <- c("\u0179r\u00f3d\u0142o informacji zdrowotnych", "N", "%")

ft6 <- flextable(tab6) %>%
  font(fontname = "Times New Roman", part = "all") %>%
  fontsize(size = 12, part = "all") %>%
  bold(part = "header") %>%
  border_remove() %>%
  hline_top(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "header", border = fp_border(width = 1.5)) %>%
  hline_bottom(part = "body", border = fp_border(width = 1.5)) %>%
  align(align = "left", part = "all") %>%
  align(j = c("N", "%"), align = "right", part = "all") %>%
  set_caption(caption = as_paragraph(as_b("Tabela 6"))) %>%
  add_footer_lines(
    "Nota. N = 78. Mo\u017cliwy by\u0142 wyb\u00f3r wi\u0119cej ni\u017c jednej odpowiedzi."
  ) %>%
  font(fontname = "Times New Roman", part = "footer") %>%
  fontsize(size = 12, part = "footer") %>%
  autofit()


# ============================================================
# ZAPIS DO WORD
# ============================================================

doc <- read_docx() %>%
  body_add_par("Tabela 1", style = "heading 2") %>%
  body_add_par("Charakterystyka pr\u00f3by badanej", style = "Normal") %>%
  body_add_flextable(ft1) %>%
  body_add_break() %>%
  body_add_par("Tabela 2", style = "heading 2") %>%
  body_add_par("Statystyki opisowe skal eHEALS i DVL", style = "Normal") %>%
  body_add_flextable(ft2) %>%
  body_add_break() %>%
  body_add_par("Tabela 3", style = "heading 2") %>%
  body_add_par(
    "Cz\u0119stotliwo\u015b\u0107 weryfikacji informacji zdrowotnych i o szczepieniach",
    style = "Normal") %>%
  body_add_flextable(ft3) %>%
  body_add_break() %>%
  body_add_par("Tabela 4", style = "heading 2") %>%
  body_add_par(
    "Sposoby weryfikacji informacji zdrowotnych stosowane przez respondent\u00f3w",
    style = "Normal") %>%
  body_add_flextable(ft4) %>%
  body_add_break() %>%
  body_add_par("Tabela 5", style = "heading 2") %>%
  body_add_par(
    "Przyczyny nieweryfikowania informacji o szczepieniach",
    style = "Normal") %>%
  body_add_flextable(ft5) %>%
  body_add_break() %>%
  body_add_par("Tabela 6", style = "heading 2") %>%
  body_add_par(
    "Przestrzenie informacyjne wykorzystywane przez respondent\u00f3w",
    style = "Normal") %>%
  body_add_flextable(ft6)

print(doc, target = "tabele_statystyki_opisowe.docx")
cat("\nGotowe! Plik: tabele_statystyki_opisowe.docx\n")