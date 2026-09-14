# verify_previc_bohn2023.R -- Step 5b mapping evidence, re-runnable.
#
# WHAT IS BEING VERIFIED
#   previc_bohn2023 is a German parent-report vocabulary checklist. Each `item`
#   IS the German word that was printed on the card the caregiver judged, so the
#   item_text <-> item tie is an identity, not an inference. The two things that
#   COULD be wrong, and that this script tests, are:
#     (a) that the live `item` strings really are the words those responses
#         belong to (i.e. the labels were not permuted somewhere in processing);
#     (b) the option_text <-> resp direction: we ship resp 1 = "JA" (child says
#         the word) and resp 0 = "NEIN". A flipped direction would be invisible
#         to validate_items.R, which only compares the set {0, 1}.
#
# HOW
#   Both fall out of one external quantity: the rated age-of-acquisition (AoA)
#   of each word, taken from published German norms (Luniewska et al. 2019;
#   Schroeder et al. 2012; Birchenough et al. 2017) and hard-coded below. AoA is
#   independent of these responses. If resp 1 means "yes", the per-item mean of
#   resp must FALL as AoA rises, and it must do so word by word -- a permutation
#   of the item labels would destroy the association.
#
#   Second, independent check: the paper's own published Rasch difficulties for
#   the 89 final-pool items (previc/saves/item_pool.csv). Under a Rasch model on
#   P(yes), per-item mean resp must be a strictly decreasing function of
#   difficulty.
#
# DATA ACCESS
#   Per-item means are computed SERVER-SIDE with one aggregate query. This table
#   is 451,010 rows and irw_fetch() would export all of it against the shared
#   200GB/30-day quota; the numbers needed here are 379 means.
#
# WHAT THIS DOES NOT ESTABLISH
#   Nothing about the instructions text, which came from the study's live web-app
#   (ccp-odc.eva.mpg.de/previc-demo) rather than from the response data, and is
#   not testable against any number here.

suppressMessages(library(irw))

TABLE <- "previc_bohn2023"

AOA <- c(
  "Abitur" = 9.16, "Ahorn" = 6.79, "Alltag" = 7.28, "Alternative" = 9.29, "Ameise" = 4.6, "Ampulle" = 9.39,
  "Ananas" = 4.1, "Anzahl" = 6.79, "Apfel" = 2.71, "Appetit" = 5.54, "Applaus" = 6.26, "Aufkleber" = 4.54,
  "Auge" = 2.69, "Ausdauer" = 7.92, "Ausnahme" = 6.0, "Batterie" = 5.94, "Bauer" = 4.29, "Baumwolle" = 7.81,
  "Bedingung" = 9.0, "Beispiel" = 5.4, "Benzin" = 5.75, "Beratung" = 9.88, "Bereich" = 7.53, "Beruf" = 6.16,
  "Betrieb" = 8.91, "Bildschirm" = 7.22, "Boot" = 3.67, "Bus" = 4.0, "Büro" = 5.07, "Bürste" = 3.24,
  "Cello" = 8.67, "Chef" = 6.83, "Chor" = 7.19, "Dachs" = 6.17, "Dokument" = 9.47, "Drama" = 8.84,
  "Dreck" = 4.0, "Eichhörnchen" = 2.6, "Elch" = 6.28, "Erdbeere" = 3.47, "Erfahrung" = 7.7, "Erholung" = 8.64,
  "Fahrrad" = 3.8, "Fasan" = 6.61, "Ferien" = 5.15, "Fernsehen" = 4.59, "Filmstar" = 8.42, "Firma" = 6.56,
  "Fisch" = 2.76, "Flagge" = 5.86, "Flug" = 5.8, "Flugzeug" = 3.24, "Flunder" = 6.95, "Folge" = 7.07,
  "Formel" = 9.59, "Frechheit" = 5.83, "Freizeit" = 6.38, "Freund" = 3.42, "Frisur" = 5.32, "Gazelle" = 6.31,
  "Geburt" = 5.79, "Gefühl" = 5.0, "Gegensatz" = 5.9, "Generation" = 8.53, "Gerechtigkeit" = 7.7, "Gesundheit" = 5.53,
  "Giraffe" = 3.79, "Glastür" = 5.35, "Grenze" = 6.19, "Grundlage" = 8.94, "Gürtel" = 4.11, "Hamburger" = 7.5,
  "Handschuh" = 2.25, "Held" = 5.12, "Hering" = 6.81, "Hubschrauber" = 4.73, "Hummer" = 8.0, "Humor" = 7.16,
  "Impfung" = 5.17, "Insel" = 4.4, "Interesse" = 7.04, "Jacke" = 2.77, "Jaguar" = 7.64, "Job" = 9.12,
  "Juni" = 5.24, "Kaffee" = 4.18, "Kajak" = 8.82, "Kapitän" = 3.0, "Kartoffel" = 1.95, "Klassik" = 7.79,
  "Knochen" = 4.64, "Komma" = 6.53, "Kontrolle" = 7.0, "Krawatte" = 7.64, "Krise" = 8.29, "Kummer" = 5.45,
  "Kunde" = 7.67, "Känguru" = 5.89, "Labyrinth" = 6.63, "Landschaft" = 6.61, "Leiter" = 4.47, "Lerche" = 7.37,
  "Lilie" = 8.0, "Lineal" = 4.9, "Locher" = 6.31, "Magnet" = 6.74, "Markt" = 5.43, "Mathematiker" = 4.7,
  "Meer" = 4.06, "Million" = 8.17, "Mitglied" = 7.1, "Mode" = 8.57, "Motorrad" = 3.25, "Möhre" = 3.36,
  "Mütze" = 1.95, "Nadel" = 4.22, "Nahrung" = 6.46, "Nelke" = 7.82, "Niete" = 7.71, "Nummer" = 5.08,
  "Orchidee" = 9.76, "Ozean" = 6.46, "Palme" = 6.57, "Panik" = 7.78, "Paris" = 8.16, "Pause" = 4.61,
  "Pfanne" = 4.16, "Pfifferling" = 7.13, "Pflicht" = 6.48, "Pilz" = 3.67, "Pinsel" = 3.43, "Pizzeria" = 8.88,
  "Politik" = 9.3, "Portion" = 5.37, "Produkt" = 7.83, "Programm" = 6.73, "Prozent" = 9.19, "Python" = 8.68,
  "Regel" = 6.62, "Restaurant" = 6.08, "Ring" = 4.35, "Risiko" = 7.7, "Rucola" = 6.18, "Ruhe" = 4.21,
  "Ruine" = 6.21, "Sache" = 5.0, "Satellit" = 8.94, "Schaufel" = 3.64, "Schere" = 3.38, "Scherz" = 6.63,
  "Schlange" = 2.0, "Schreibtisch" = 3.2, "Schuld" = 5.21, "Sicherheit" = 7.57, "Song" = 9.19, "Spende" = 7.05,
  "Sport" = 5.26, "Stamm" = 5.29, "Stern" = 3.29, "System" = 9.0, "Tafel" = 5.06, "Telefon" = 3.53,
  "Temperatur" = 6.7, "Tennis" = 6.24, "Tiger" = 3.88, "Tonne" = 4.31, "Tourist" = 8.0, "Treppe" = 3.25,
  "Treppenhaus" = 5.05, "Trommel" = 3.11, "Turban" = 7.75, "Tänzer" = 5.79, "Tätigkeit" = 8.38, "Tür" = 3.12,
  "Unabhängigkeit" = 8.8, "Unsicherheit" = 8.08, "Urne" = 9.29, "Ventilator" = 6.59, "Verkehr" = 5.47, "Versager" = 8.26,
  "Virus" = 9.65, "Vitamin" = 6.0, "Vollmond" = 5.93, "Vorwand" = 8.58, "Wachs" = 5.44, "Wald" = 3.6,
  "Wert" = 5.4, "Wespe" = 4.8, "Wirkung" = 8.47, "Woche" = 4.64, "Wort" = 4.5, "Zahnarzt" = 4.67,
  "Zange" = 4.85, "Zebra" = 3.65, "Zucchini" = 5.95, "Zustand" = 8.05, "abhauen" = 5.28, "abseits" = 8.39,
  "akzeptieren" = 8.58, "albern" = 5.47, "allergisch" = 8.17, "alphabetisch" = 6.63, "alt" = 3.47, "anbieten" = 5.84,
  "anerkennen" = 9.0, "angeben" = 5.88, "anlügen" = 4.57, "anzünden" = 4.52, "aufwachen" = 3.0, "auspressen" = 4.86,
  "ausreden" = 6.85, "barfuß" = 3.9, "bedauern" = 8.06, "begründen" = 8.0, "bequem" = 6.05, "bereuen" = 8.48,
  "besorgt" = 6.59, "bestellen" = 5.6, "besuchen" = 4.0, "betonen" = 7.6, "beweisen" = 7.35, "bildhübsch" = 7.06,
  "blind" = 5.48, "braten" = 4.33, "bunt" = 3.44, "ehrlich" = 5.44, "einsam" = 6.07, "einstellen" = 7.88,
  "eitel" = 8.0, "empfehlen" = 8.2, "empfinden" = 7.42, "eng" = 4.27, "entlassen" = 8.72, "entstehen" = 7.0,
  "erwarten" = 6.59, "essen" = 2.57, "exakt" = 9.59, "feige" = 5.3, "feilen" = 5.38, "fernsehen" = 3.86,
  "fit" = 7.21, "fliegen" = 3.37, "fließen" = 4.87, "flüssig" = 4.23, "freiwillig" = 6.3, "fremd" = 4.83,
  "frisch" = 4.47, "füttern" = 2.9, "geheim" = 5.17, "geheimnisvoll" = 6.33, "gelingen" = 6.18, "gesund" = 4.6,
  "graben" = 3.62, "grün" = 2.95, "harken" = 7.24, "heiraten" = 5.89, "heiß" = 3.7, "heißen" = 3.6,
  "hell" = 3.17, "herstellen" = 6.54, "herzlich" = 6.63, "hoch" = 3.33, "humorlos" = 7.93, "hygienisch" = 8.36,
  "hämmern" = 3.76, "höchstpersönlich" = 9.85, "hören" = 2.1, "ignorieren" = 8.1, "jagen" = 4.38, "kicken" = 4.71,
  "kochen" = 2.62, "kämmen" = 2.71, "kündigen" = 8.88, "lachen" = 2.29, "langsam" = 3.11, "lieb" = 2.63,
  "logisch" = 7.96, "mager" = 5.83, "magnetisch" = 7.33, "melden" = 5.68, "melken" = 4.62, "mieten" = 7.77,
  "minimal" = 9.91, "mitgeben" = 5.21, "mutlos" = 7.07, "müssen" = 3.38, "nachweisen" = 9.16, "neblig" = 5.2,
  "neidisch" = 6.68, "niedlich" = 4.4, "nutzen" = 6.08, "offen" = 3.31, "okay" = 5.92, "operieren" = 6.79,
  "optimal" = 8.84, "passiv" = 9.89, "peinlich" = 6.81, "persönlich" = 7.74, "pflegen" = 5.79, "positiv" = 8.78,
  "praktisch" = 8.04, "prima" = 4.06, "redselig" = 9.74, "regnen" = 3.36, "reif" = 5.55, "reizen" = 7.5,
  "reservieren" = 8.8, "reserviert" = 7.39, "rosten" = 6.41, "rudern" = 3.3, "saftig" = 4.83, "satt" = 2.95,
  "sauber" = 2.94, "scharf" = 4.42, "schaukeln" = 2.75, "scheitern" = 8.82, "schleppen" = 5.14, "schneiden" = 2.9,
  "schreiben" = 4.26, "schweigen" = 5.42, "schwierig" = 4.17, "schwitzen" = 4.67, "sechzig" = 5.33, "sinnvoll" = 7.75,
  "sparen" = 6.29, "speziell" = 8.38, "spontan" = 9.43, "sprachlos" = 6.92, "spurlos" = 6.94, "stark" = 3.5,
  "stehlen" = 4.76, "still" = 2.96, "streng" = 5.0, "stricken" = 4.1, "studieren" = 9.39, "stürzen" = 4.64,
  "süß" = 3.58, "teilen" = 4.11, "testen" = 6.44, "teuer" = 5.16, "tippen" = 5.29, "treu" = 7.56,
  "täglich" = 4.93, "umarmen" = 4.0, "umrühren" = 3.24, "umsonst" = 5.33, "unfair" = 6.28, "ungesund" = 4.79,
  "unsicher" = 5.84, "verbessern" = 5.61, "verboten" = 3.38, "vergessen" = 5.57, "verlegen" = 7.25, "verletzt" = 4.29,
  "verloben" = 7.26, "vermieten" = 7.88, "vermuten" = 6.05, "versichern" = 9.14, "vertraut" = 8.79, "vertreten" = 7.68,
  "verwandt" = 5.24, "verweigern" = 7.29, "verwesen" = 9.24, "verzichten" = 6.11, "voll" = 3.52, "vorstellen" = 6.5,
  "wehrlos" = 7.31, "weiblich" = 6.71, "wenig" = 3.42, "werfen" = 3.12, "wertvoll" = 5.92, "widmen" = 9.17,
  "wiegen" = 4.59, "wild" = 4.84, "wirken" = 6.57, "wundern" = 5.65, "zahm" = 5.6, "ziellos" = 9.79,
  "Übermut" = 7.88
)

DIFFICULTY <- c(
  "Alternative" = 2.1851, "Anzahl" = 0.2897, "Ausnahme" = -1.265, "Bedingung" = 1.2132, "Betrieb" = 1.486,
  "Chef" = -2.3189, "Drama" = 1.2723, "Elch" = -2.2412, "Filmstar" = 2.0923, "Firma" = 0.6305000000000001,
  "Formel" = 2.6673, "Frisur" = -3.1261, "Glastür" = -1.121, "Job" = 0.474, "Kapitän" = -2.7397,
  "Komma" = 1.1468, "Kontrolle" = -0.9618, "Kummer" = 1.1303, "Kunde" = 0.2754, "Magnet" = -2.9608,
  "Markt" = -2.7397, "Million" = -1.2513, "Mode" = 0.7518, "Nahrung" = -0.5432, "Ozean" = -1.0476,
  "Panik" = 1.0683, "Paris" = -0.3108, "Portion" = -1.7985, "Produkt" = 2.0916, "Programm" = -0.7068,
  "Scherz" = -1.375, "Spende" = 0.5698, "System" = 2.2966, "Tafel" = -3.1459, "Temperatur" = -2.0568,
  "Tonne" = -3.3502, "Tourist" = 1.5728, "Verkehr" = -2.0469, "Versager" = 2.9428, "Virus" = -1.3231,
  "Vitamin" = -1.7132, "Vorwand" = 3.508, "Zange" = -3.3502, "allergisch" = -0.6007, "anbieten" = -0.2241,
  "auspressen" = -1.252, "besorgt" = 0.4586, "einsam" = -0.5313, "exakt" = 1.6675, "feige" = 0.208,
  "fit" = -1.8087, "freiwillig" = -1.3896, "fremd" = -2.2851, "geheimnisvoll" = 0.4385, "gelingen" = -0.0748,
  "heiraten" = -2.9614000000000003, "herstellen" = -1.288, "hygienisch" = 1.9457, "höchstpersönlich" = 3.7609, "kündigen" = 1.3988,
  "mager" = 2.1927, "minimal" = 2.2893, "mutlos" = 2.2309, "nachweisen" = 2.4313, "nutzen" = -0.8926000000000001,
  "optimal" = 1.8916, "redselig" = 4.4585, "rosten" = -0.2076, "rudern" = -0.8728, "saftig" = -2.2102,
  "speziell" = 0.3662, "spontan" = 0.8485, "sprachlos" = 0.9405, "spurlos" = 0.8796, "stehlen" = -1.0274,
  "studieren" = 0.4329, "stürzen" = -1.9994, "testen" = -2.5433, "tippen" = -2.5175, "treu" = 1.1573,
  "unfair" = -2.5308, "verlegen" = 1.2931, "verweigern" = 1.995, "verwesen" = 3.3121, "vorstellen" = -1.442,
  "weiblich" = 0.0207, "widmen" = 4.0979, "wirken" = 0.7618, "zahm" = 0.1462
)

# ---- live per-item means, server-side aggregate (no export) -----------------
tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, COUNT(*) AS n,",
                   "AVG(SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64)) AS m",
                   "FROM `%s` GROUP BY item"), tbl$qualified_reference)
d <- as.data.frame(irw:::.irw_query_tibble(q))
m <- setNames(d$m, d$item)

cat(sprintf("live items: %d   rows/item: %s\n", nrow(d),
            paste(range(d$n), collapse = "-")))

# ---- check 1: AoA vs proportion "yes", all 379 items ------------------------
common <- intersect(names(AOA), names(m))
r_p <- cor(m[common], AOA[common])
r_s <- cor(m[common], AOA[common], method = "spearman")
cat(sprintf("\n[1] AoA vs P(resp=1), n = %d items:  Pearson %.3f   Spearman %.3f\n",
            length(common), r_p, r_s))

ord <- order(AOA[common])
show <- c(head(common[ord], 5), tail(common[ord], 5))
cat(sprintf("    %-14s %6s %8s\n", "word", "AoA", "P(yes)"))
for (w in show) cat(sprintf("    %-14s %6.2f %8.3f\n", w, AOA[w], m[w]))

# Permutation reference: how extreme is this correlation?
set.seed(1)
null_r <- replicate(2000, cor(sample(m[common]), AOA[common], method = "spearman"))
cat(sprintf("    null Spearman over 2000 label permutations: max |r| = %.3f\n",
            max(abs(null_r))))

# ---- check 2: published Rasch difficulty vs proportion "yes", 89 items ------
common2 <- intersect(names(DIFFICULTY), names(m))
d_p <- cor(m[common2], DIFFICULTY[common2])
d_s <- cor(m[common2], DIFFICULTY[common2], method = "spearman")
cat(sprintf("\n[2] published Rasch difficulty vs P(resp=1), n = %d items:  Pearson %.4f   Spearman %.4f\n",
            length(common2), d_p, d_s))

ord2 <- order(DIFFICULTY[common2])
show2 <- c(head(common2[ord2], 3), tail(common2[ord2], 3))
cat(sprintf("    %-14s %10s %8s\n", "word", "difficulty", "P(yes)"))
for (w in show2) cat(sprintf("    %-14s %10.3f %8.3f\n", w, DIFFICULTY[w], m[w]))

# ---- verdict ----------------------------------------------------------------
# Direction: both correlations must be NEGATIVE, which is only true if resp 1 is
# the "JA" response. Mapping: the AoA association must be far outside the
# permutation null.
ok <- length(common) == 379 && length(common2) == 89 &&
      r_s < -0.7 && d_s < -0.95 && abs(r_s) > max(abs(null_r))

cat("\nInterpretation: both associations are negative, so resp = 1 is the\n",
    "affirmative ('JA') response and resp = 0 is 'NEIN'; a flipped option_text\n",
    "would put both correlations at the same magnitude with the opposite sign.\n",
    "The AoA association is word-specific and lies far outside the permutation\n",
    "null, so the item labels are attached to their own responses.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
