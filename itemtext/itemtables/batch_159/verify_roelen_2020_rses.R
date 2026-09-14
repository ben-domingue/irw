#!/usr/bin/env Rscript
# verify_roelen_2020_rses.R -- Step 5b mapping verification.
#
# WHAT IS BEING VERIFIED
#   item axis : q_407..q_416 ARE the source .dta's own column names
#               (data/roelen_2020_haiti_battery.py melts RSES_COLS = q_407..q_416 by
#               name; no positional step), and the .dta carries a variable LABEL for
#               each one. So the item<->item_text tie is a label match at the source.
#               This script re-derives it mechanically: it re-reads the labels from the
#               deposited .dta and diffs them against the shipped item_text.
#   resp axis : THIS is where inference lived. The .dta stores 1=Strongly agree ..
#               4=Strongly disagree, while pandas.read_stata() decodes to the LABEL
#               STRINGS and the script re-encodes them Strongly disagree=1 .. Strongly
#               agree=4 -- i.e. the live integers run OPPOSITE to the .dta's own codes.
#               Verified by route 9 (response-frequency matching): all 10 items x 4
#               levels = 40 cell counts, raw vs live.
#   route 7   : the paper states 94.7% of respondents agreed/strongly agreed with
#               item 8 ("I wish I could have more respect for myself"). Under the
#               shipped mapping that is q_414 at resp 3+4. This pins one item AND the
#               resp direction independently of the .dta.
#
# Not plumbing: item counts / resp sets are validate_items.R's job and are not re-checked.

suppressMessages({library(redivis); library(haven)})

TBL <- "datapages.item_response_warehouse_3:5xaj:v6_0.roelen_2020_rses:v8eq"
DTA <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243457.s002"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                       "roelen_2020_rses__items.csv")

ok <- TRUE

## ---- source of truth: the deposited Stata file --------------------------------
tmp <- tempfile(fileext = ".dta")
utils::download.file(DTA, tmp, quiet = TRUE, mode = "wb")
raw <- haven::read_dta(tmp)
cols <- sprintf("q_%d", 407:416)

## ---- (A) item axis: shipped item_text vs the .dta variable labels --------------
shipped <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
ship_txt <- tapply(shipped$item_text, shipped$item, function(x) unique(x)[1])
cat("=== (A) item_text vs .dta variable labels ===\n")
n_ok <- 0
for (c in cols) {
  lab <- as.character(attr(raw[[c]], "label"))
  got <- as.character(ship_txt[[c]])
  same <- identical(lab, got)
  n_ok <- n_ok + same
  cat(sprintf("  %s  %-5s  label=%-78s shipped=%s\n", c, if (same) "MATCH" else "DIFF", lab, got))
}
cat(sprintf("  -> %d/10 exact string matches\n\n", n_ok))
if (n_ok != 10) ok <- FALSE

## ---- (B) resp axis: route 9, 40 cell counts raw vs live ------------------------
lab_of  <- c("Strongly agree", "Agree", "Disagree", "Strongly disagree")  # .dta codes 1..4
irw_of  <- c("Strongly disagree" = 1, "Disagree" = 2, "Agree" = 3, "Strongly agree" = 4)

rawc <- do.call(rbind, lapply(cols, function(c) {
  v <- as.integer(raw[[c]]); t <- table(v)
  data.frame(item = c,
             resp = as.integer(irw_of[lab_of[as.integer(names(t))]]),
             n_raw = as.integer(t), stringsAsFactors = FALSE)
}))

live <- redivis::query(sprintf(
  "SELECT item, resp, COUNT(*) AS n_live FROM `%s` GROUP BY item, resp", TBL))$to_data_frame()
live$resp <- as.integer(live$resp); live$n_live <- as.integer(live$n_live)

m <- merge(rawc, live, by = c("item", "resp"), all = TRUE)
m <- m[order(m$item, m$resp), ]
m$n_raw[is.na(m$n_raw)] <- 0L; m$n_live[is.na(m$n_live)] <- 0L
m$match <- m$n_raw == m$n_live
cat("=== (B) route 9: raw .dta counts re-coded to IRW resp vs live counts ===\n")
print(m, row.names = FALSE)
cat(sprintf("  -> %d/%d of the item x level cells match exactly\n\n", sum(m$match), nrow(m)))
if (!all(m$match) || nrow(m) != 40) ok <- FALSE

## ---- (C) route 7: the paper's marker statistic ---------------------------------
# Roelen et al. 2020, Discussion: "the large majority of respondents (94.7%) indicated
# to agree or strongly agree with this statement" -- RSES item 8, shipped as q_414.
q414 <- live[live$item == "q_414", ]
pct  <- 100 * sum(q414$n_live[q414$resp %in% c(3, 4)]) / sum(q414$n_live)
cat("=== (C) route 7: paper's 94.7% agree/strongly-agree on RSES item 8 ===\n")
cat(sprintf("  q_414 resp 3+4 = %d of %d = %.1f%%   (paper: 94.7%%)\n",
            sum(q414$n_live[q414$resp %in% c(3, 4)]), sum(q414$n_live), pct))
# every other item, for contrast
for (c in setdiff(cols, "q_414")) {
  s <- live[live$item == c, ]
  cat(sprintf("    %s = %.1f%%\n", c, 100 * sum(s$n_live[s$resp %in% c(3, 4)]) / sum(s$n_live)))
}
if (abs(pct - 94.7) > 0.1) ok <- FALSE
cat("\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
