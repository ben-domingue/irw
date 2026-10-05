# verify_bled_2021_imagery_use.R -- Step 5b check, batch_438.
#
# Claim 1 (code <-> source column): the IRW codes are the source S1 Data CSV
#   headers with the bracketed value-label suffix stripped (name-preserving rename in
#   data/bled_2021_pheno_imagery.py). If any column had been shuffled, the per-item
#   0/1/2 counts would not reproduce. Source counts below were tabulated from
#   journal.pone.0255039.s001 (119 rows with a numeric id) and are hard-coded.
# Claim 2 (code <-> item_text): each code names the everyday situation of one
#   questionnaire item (S1 Appendix items 5-11); the shipped English text for each
#   code must contain that situation's keyword and no other item's keyword.
# Claim 3 (resp <-> option_text): header value labels are
#   [0=words_only; 1=images/words; 2=imges_only]; shipped option_text must follow.

suppressMessages(library(irw))
TABLE <- "bled_2021_imagery_use"

SRC <- list(use_recollection   = c(8, 61, 50),
            use_comprehension  = c(17, 52, 50),
            use_anticipation   = c(17, 35, 67),
            use_planification  = c(34, 40, 45),
            use_problemSolving = c(32, 50, 37),
            use_decision       = c(14, 39, 66),
            use_memorization   = c(34, 48, 37))
KEY <- c(use_recollection = "remember", use_comprehension = "understand",
         use_anticipation = "anticipate", use_planification = "planning",
         use_problemSolving = "problem", use_decision = "decision",
         use_memorization = "memorize")

ok <- TRUE
d <- irw::irw_fetch(TABLE)
cat(sprintf("%-20s %-14s %-14s\n", "item", "source 0/1/2", "live 0/1/2"))
for (it in names(SRC)) {
  live <- as.integer(table(factor(d$resp[d$item == it], levels = 0:2)))
  m <- identical(as.numeric(live), SRC[[it]])
  ok <- ok && m
  cat(sprintf("%-20s %-14s %-14s %s\n", it, paste(SRC[[it]], collapse = "/"),
              paste(live, collapse = "/"), if (m) "match" else "MISMATCH"))
}

f <- "itemtables/batch_438/bled_2021_imagery_use__items.csv"
x <- read.csv(f, stringsAsFactors = FALSE)
cat("\nkeyword check on item_text_translated:\n")
for (it in names(KEY)) {
  txt <- unique(x$item_text_translated[x$item == it])
  hits <- names(KEY)[sapply(KEY, function(k) grepl(k, txt, ignore.case = TRUE))]
  m <- identical(hits, it)
  ok <- ok && m
  cat(sprintf("%-20s keyword '%s' -> hits: %s %s\n", it, KEY[[it]], paste(hits, collapse = ","),
              if (m) "ok" else "BAD"))
}

opt <- unique(x[, c("resp", "option_text_translated")])
opt <- opt[order(opt$resp), ]
want <- c("words only", "images and words", "images only")
m <- nrow(opt) == 3 && identical(opt$option_text_translated, want) && identical(as.integer(opt$resp), 0:2)
ok <- ok && m
cat("\noption map:", paste(opt$resp, opt$option_text_translated, sep = "=", collapse = "; "),
    if (m) "ok" else "BAD", "\n")

cat("Note: every item has a distinct 0/1/2 count vector, so the count route separates all 7 items;\n",
    "the paper publishes no per-item statistics, so there is no second, independent numeric route.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
