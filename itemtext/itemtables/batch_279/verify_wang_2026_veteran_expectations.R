# verify_wang_2026_veteran_expectations.R
#
# Claim under test: each IRW item code B1/B2/B3 carries the wording shipped for
# it, and sits on the identically-named column of Wang & Zhang's S1 File.
# Two links, re-derived here from the source deposit and the live table:
#
#   LINK 1  code -> live column. Per-item counts of resp 1..7 in the live IRW
#           table vs the same-named column of the deposit .xlsx. Route 9. The
#           three count vectors are pairwise distinct, so any permutation of the
#           three codes would break the match.
#   LINK 2  code -> wording. The paper's Table 1 (the questionnaire itself,
#           published as an image asset) prints each item with the data's own
#           code as a literal label -- "B1. I hope that participation in
#           grassroots governance can provide substantial income." Step 5b
#           exemption 2. Table 1 is an IMAGE, so it cannot be re-scraped as
#           text; the transcription is hard-coded below and the check that can
#           be automated is that the shipped item_text still equals it.
#   LINK 3  corroboration, route 1. Table 5 publishes per-class means of B1/B2/B3
#           for the three latent classes with their class shares; the implied
#           grand means are compared with the live means.
#
# Deliberately NOT evidence: item counts / set membership (validate_items.R
# already checks those).

suppressMessages(library(irw))

TABLE <- "wang_2026_veteran_expectations"
S1 <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0351162.s001&type=supplementary"
UA <- "Mozilla/5.0"   # no email is sent to any outside service

# Transcribed from the paper's Table 1 image asset
# https://journals.plos.org/plosone/article/figure/image?size=large&id=10.1371/journal.pone.0351162.t001
SHIPPED <- c(
  B1 = "I hope that participation in grassroots governance can provide substantial income.",
  B2 = "I hope to improve the community’s respect for me through participation.",
  B3 = "I hope to improve management skills through participation")

# Paper Table 5: per-class means and class shares.
CLASS_SHARE <- c(0.513, 0.238, 0.249)
CLASS_MEANS <- rbind(B1 = c(6.2, 4.5, 4.7),
                     B2 = c(3.8, 5.5, 4.9),
                     B3 = c(3.9, 4.4, 5.2))

ok <- TRUE

## ---- LINK 1: live per-level counts vs the deposit column of the same name ----
xlsx <- file.path(tempdir(), "pone0351162_s001.xlsx")
got <- tryCatch({
  download.file(S1, xlsx, quiet = TRUE, mode = "wb", headers = c("User-Agent" = UA))
  file.exists(xlsx) && file.size(xlsx) > 10000
}, error = function(e) FALSE)

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d); d$resp <- as.numeric(d$resp)
live <- table(factor(d$item, levels = names(SHIPPED)), factor(d$resp, levels = 1:7))

cat("LINK 1 -- per-item counts of resp 1..7, live IRW vs deposit column\n")
if (got && requireNamespace("readxl", quietly = TRUE)) {
  raw <- as.data.frame(readxl::read_excel(xlsx, sheet = "Sheet1"))
  dep <- sapply(names(SHIPPED), function(cl)
    as.integer(table(factor(suppressWarnings(as.numeric(raw[[cl]])), levels = 1:7))))
  dep <- t(dep)
  for (it in names(SHIPPED)) {
    l <- as.integer(live[it, ]); s <- as.integer(dep[it, ])
    cat(sprintf("  %-3s live %-28s deposit %-28s %s\n", it,
                paste(l, collapse = ","), paste(s, collapse = ","),
                if (identical(l, s)) "MATCH" else "DIFFER"))
    if (!identical(l, s)) ok <- FALSE
  }
  # how many of the 9 cross comparisons are equal -- must be exactly 3 (diagonal)
  eq <- sum(outer(1:3, 1:3, Vectorize(function(i, j)
    identical(as.integer(live[i, ]), as.integer(dep[j, ])))))
  cat(sprintf("  cross-comparisons equal: %d of 9 (3 = diagonal only, i.e. the three\n", eq))
  cat("  count vectors are pairwise distinct and the assignment is unique)\n")
  if (eq != 3) ok <- FALSE
} else {
  cat("  deposit unavailable (download failed or readxl missing) -- LINK 1 not re-run\n")
  ok <- FALSE
}

## ---- LINK 2: the shipped wording still equals the Table 1 transcription ------
csv <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                 paste0(TABLE, "__items.csv"))
cat("\nLINK 2 -- shipped item_text vs the Table 1 transcription\n")
if (file.exists(csv)) {
  it <- read.csv(csv, stringsAsFactors = FALSE)
  for (code in names(SHIPPED)) {
    shipped <- unique(it$item_text[it$item == code])
    same <- length(shipped) == 1 && identical(shipped, unname(SHIPPED[code]))
    cat(sprintf("  %-3s %s | %s\n", code, if (same) "MATCH " else "DIFFER", shipped))
    if (!same) ok <- FALSE
  }
} else {
  cat("  items CSV not found beside this script -- LINK 2 not re-run\n"); ok <- FALSE
}

## ---- LINK 3: route 1 corroboration from Table 5 ------------------------------
cat("\nLINK 3 -- implied grand means from Table 5 vs live means\n")
obs <- tapply(d$resp, d$item, mean)[names(SHIPPED)]
imp <- as.vector(CLASS_MEANS %*% CLASS_SHARE)
for (i in 1:3)
  cat(sprintf("  %-3s Table5-implied %.2f   live %.3f   diff %+.3f\n",
              names(SHIPPED)[i], imp[i], obs[i], obs[i] - imp[i]))
cat(sprintf("  rank order: Table 5 %s | live %s\n",
            paste(names(SHIPPED)[order(-imp)], collapse = ">"),
            paste(names(obs)[order(-obs)], collapse = ">")))
if (!identical(order(-imp), order(-obs))) {
  cat("  rank order DIFFERS -- corroboration fails\n"); ok <- FALSE
}

cat("\nWHAT THIS DOES NOT ESTABLISH: that the authors' own column labelling in the\n",
    "deposit is correct (a mislabel inside the deposit would satisfy both links);\n",
    "and nothing about the Chinese wording respondents actually read -- the shipped\n",
    "text is the authors' English questionnaire from Table 1.\n", sep = "")
cat("Note: Table 5's implied means are rounded to 1 dp and describe the paper's 525\n",
    "analysed respondents, while the deposit and the live table hold 624 -- LINK 3 is\n",
    "corroboration of direction only. LINK 1 is the decisive, exact comparison.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
