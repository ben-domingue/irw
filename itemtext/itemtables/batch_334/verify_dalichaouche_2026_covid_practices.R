# verify_dalichaouche_2026_covid_practices.R -- Step 5b, re-runnable.
#
# Claim: live items P1..P6 are the xlsx score columns of the same name (the
# processing script melts ^P\d+$ columns by name); each score column is preceded by
# a label column whose header is that question's de-spaced French stem, which ties
# P_k to docx section IV question k; and each shipped (item, resp, option_text) row
# is the label every labelled source respondent at that score chose.
# Swapping the text of any two items breaks check 2 (stem keyword lands in the wrong
# header); a flipped/permuted option breaks check 3.

suppressMessages({library(irw); library(readxl)})
TABLE <- "dalichaouche_2026_covid_practices"
here <- tryCatch(dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))),
                 error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
ok <- TRUE

xl <- tempfile(fileext = ".xlsx")
download.file("https://ndownloader.figshare.com/files/63116881", xl, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "Mozilla/5.0 (IRW-research)"))
src <- as.data.frame(read_excel(xl))
live <- irw::irw_fetch(TABLE)
it <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
P <- paste0("P", 1:6)
labcol <- setNames(names(src)[match(P, names(src)) - 1], P)

# 1. live per-item x level counts vs source score columns (all six vectors distinct,
#    so this also pins live P_k to source column P_k and no other)
cat("== 1. live vs source score-column counts (resp 0/1/2) ==\n")
for (p in P) {
  lv <- table(factor(live$resp[live$item == p], 0:2)); sv <- table(factor(src[[p]], 0:2))
  cat(sprintf("%s live %s | source %s\n", p, paste(lv, collapse = "/"), paste(sv, collapse = "/")))
  if (!all(lv == sv)) ok <- FALSE
}

# 2. item <-> text: a keyword from each shipped English stem, as it appears in the
#    de-spaced French header, must hit that item's preceding header and no other.
kw <- c(P1 = "fivre", P2 = "contacts", P3 = "particip", P4 = "masque", P5 = "mains", P6 = "distanciation")
en <- c(P1 = "fever", P2 = "close contact", P3 = "participate", P4 = "mask", P5 = "wash your hands", P6 = "social distancing")
cat("\n== 2. stem keyword x preceding header (1 = header contains keyword) ==\n")
m <- t(sapply(P, function(k) sapply(P, function(h) as.integer(grepl(kw[k], tolower(labcol[h]), fixed = TRUE)))))
print(m)
for (k in P) cat(sprintf("%s header '%s'  shipped stem '%s'  en-keyword '%s' in stem: %s\n", k, labcol[k],
                         it$item_text[it$item == k][1], en[k],
                         grepl(en[k], tolower(it$item_text[it$item == k][1]), fixed = TRUE)))
en_ok <- all(sapply(P, function(k) grepl(en[k], tolower(it$item_text[it$item == k][1]), fixed = TRUE)))
if (!all(m == diag(6)) || !en_ok) { ok <- FALSE; cat("   -> item/stem tie not the identity\n") }

# 3. option <-> resp: share of labelled source respondents at each score who chose the shipped label
cat("\n== 3. option_text vs resp: labelled source respondents at that score choosing the shipped label ==\n")
for (i in seq_len(nrow(it))) {
  p <- it$item[i]; r <- it$resp[i]
  lab <- src[[labcol[p]]][src[[p]] == r]
  n_na <- sum(is.na(lab)); lab <- lab[!is.na(lab)]
  hit <- sum(lab == it$option_text[i])
  cat(sprintf("%s resp=%d  %3d/%3d  (+%d unanswered cells scored %d)  '%s'\n",
              p, r, hit, length(lab), n_na, r, it$option_text[i]))
  if (length(lab) == 0 || hit != length(lab)) ok <- FALSE
}
cat("Does NOT establish: the printed French stem wording (headers are de-spaced) -- a text question, not a mapping one.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
