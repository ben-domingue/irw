# verify_dalichaouche_2026_covid_knowledge.R -- Step 5b, re-runnable.
#
# Claim: live item Ck is the k-th question of section "II - Knowledge" in the deposit's
# 'Supplementary file 1-questionnaire.docx'. The item codes are the deposit workbook's own
# column names (C1..C6); each Ck column is immediately preceded by a column whose header is
# the French question stem (de-spaced) and whose cells hold the raw answer category.
#
# Two checks, both of which break if any two items' text were swapped:
#  (1) the French header preceding Ck contains the key words of English stem k, and the
#      raw categories in that column are the answer options English question k offers;
#  (2) scoring that raw column with question k's published key reproduces the LIVE
#      table's Ck vector respondent-by-respondent (live id = workbook row position,
#      per data/dalichaouche_2026_covid_kap.py), for all 300 respondents.
suppressMessages({library(irw); library(readxl)})
TABLE <- "dalichaouche_2026_covid_knowledge"
URL <- "https://ndownloader.figshare.com/files/63116881"   # Base de donnee_KAP_etudiant COVID-19.xlsx
tf <- tempfile(fileext = ".xlsx")
download.file(URL, tf, mode = "wb", quiet = TRUE, headers = c("User-Agent" = "Mozilla/5.0"))
x <- as.data.frame(read_excel(tf, .name_repair = "minimal"))

# English stem keywords (supplement) -> expected French header fragment, and the key
# pattern (the raw category the published key marks correct).
spec <- data.frame(
  item   = paste0("C", 1:6),
  en     = c("type of infectious disease", "main route of transmission", "incubation period",
             "main clinical manifestations", "severe forms", "prevented"),
  fr     = c("typedelamaladieinfectieuse", "principalevoiedetransmission", "incubation",
             "manifestationscliniques", "formesgraves", "Commentpr"),
  key    = c("^Virale$", "^Gouttelettes respiratoires", "^1~14 jours$", "^Fi.vre/Toux",
             "^Les vieux et/ou", "^Porter un masque"),
  stringsAsFactors = FALSE)

live <- irw::irw_fetch(TABLE)
ok <- TRUE
cat(sprintf("%-4s %-30s %-45s %6s %6s %8s\n", "item", "english stem kw", "preceding french header",
            "raw1s", "live1s", "id_agree"))
for (i in seq_len(nrow(spec))) {
  k <- spec$item[i]
  j <- match(k, names(x)); hdr <- names(x)[j - 1]
  raw <- x[[j - 1]]
  scored <- ifelse(!is.na(raw) & grepl(spec$key[i], raw), 1L, 0L)
  lv <- live[live$item == k, ]; lv <- lv[order(lv$id), ]
  agree <- sum(scored[lv$id] == lv$resp)
  hdr_ok <- grepl(spec$fr[i], hdr, fixed = TRUE)
  # a swapped mapping would show up as the key pattern hitting the wrong column
  other_hits <- sapply(setdiff(seq_len(nrow(spec)), i), function(m)
      sum(grepl(spec$key[m], x[[j - 1]])))
  cat(sprintf("%-4s %-30s %-45s %6d %6d %5d/%d  hdr_match=%s other_keys_in_col=%d\n",
              k, spec$en[i], substr(hdr, 1, 45), sum(scored), sum(lv$resp), agree, nrow(lv),
              hdr_ok, sum(other_hits)))
  if (!hdr_ok || agree != nrow(lv) || nrow(lv) != nrow(x) || sum(other_hits) > 0) ok <- FALSE
  cat("     raw categories:", paste(sort(unique(na.omit(raw))), collapse = " | "),
      sprintf("[blank: %d]\n", sum(is.na(raw))))
}
cat("\nEstablishes: each Ck's header is question k's French stem and its raw categories are question k's\n",
    "options; scoring with k's key reproduces live Ck for every respondent. Does NOT establish the\n",
    "French wording itself (headers are de-spaced/de-accented), nor the English supplement's fidelity\n",
    "to the French form.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
