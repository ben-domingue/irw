# verify_komura_2026_gqs_animacy.R
#
# CLAIM UNDER TEST: the five live item codes gqs_animacy_1..5 carry the five
# numbered anchor pairs listed under "Animacy:" in the study's S2 File
# ("User Instructions for Frontend Interface", section 7 "Questionnaire Screens"):
#   1 Dead <-> Alive   2 Stagnant <-> Lively   3 Inactive <-> Active
#   4 Unresponsive <-> Responsive              5 Sleepy <-> Awake
# and that resp ascends from the LEFT adjective (1) to the RIGHT adjective (5).
#
# Three falsifiable checks, none of which is a count check:
#
# A. SUBSCALE IDENTITY (route 3). The paper's Table 3 publishes the Animacy
#    dimension mean (SD) per AI-strategy condition. Averaging exactly these five
#    live items per respondent must reproduce it. Breaks if any item belongs to
#    a different GQS dimension or is stored reverse-coded.
#
# B. DUPLICATE-ANCHOR PIN (route 9-style, cross-table). The S2 File prints
#    "Unresponsive <-> Responsive" TWICE -- as Animacy 4 and as Perceived
#    Intelligence 2. If item 4 really is that pair, gqs_animacy_4 must correlate
#    with gqs_perceived_intelligence_2 more strongly than any other animacy x
#    perceived-intelligence cell. Breaks if item_text for 4 is swapped with any
#    other animacy item.
#
# C. SCALE DIRECTION (option_text <-> resp axis). The S2 File annotates
#    Perceived Safety items 2 ("Calm <-> Agitated") and 3 ("Peaceful <->
#    Surprised") as "(reversed item)" and no others. If resp = 1 is the LEFT
#    adjective, then reverse-scoring exactly those two must reproduce the paper's
#    published Perceived Safety means, and leaving them raw must not. That fixes
#    the direction convention the animacy option_text assumes.
#
# What this does NOT establish: it does not distinguish items 2, 3 and 5
# ("Stagnant <-> Lively", "Inactive <-> Active", "Sleepy <-> Awake") from each
# other. Their means (3.67 / 3.61 / 3.64) and their correlations with every
# other GQS block are within noise of one another; no published statistic
# separates them. The basis for their order is the S2 File's own numbering
# against the identically-numbered source columns, which is not a statistic.
# Hence the recorded status is PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressWarnings(suppressMessages({library(readxl); library(httr)}))

TABLE <- "komura_2026_gqs_animacy"

## ---- live data ------------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
d$item <- as.character(d$item)
cond <- unique(d[, c("id", "cov_aitype")])
live <- reshape(d[, c("id", "item", "resp")], idvar = "id",
                timevar = "item", direction = "wide")
names(live) <- sub("^resp\\.", "", names(live))
live <- as.data.frame(live)
anim <- paste0("gqs_animacy_", 1:5)

## ---- source workbook (S3 File, PLOS, CC BY 4.0) ---------------------------
url <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0340449.s003")
tmp <- tempfile(fileext = ".xlsx")
ok <- tryCatch({
  httr::GET(url, httr::write_disk(tmp, overwrite = TRUE),
            httr::user_agent("IRW-itemtext/1.0"), httr::timeout(120))
  TRUE
}, error = function(e) FALSE)
src <- if (ok && file.exists(tmp) && file.size(tmp) > 1e4)
           as.data.frame(readxl::read_excel(tmp)) else NULL

## ---- A. subscale identity vs paper Table 3 --------------------------------
cat("=== A. Animacy subscale mean (SD) by condition, paper Table 3 vs live ===\n")
PUB <- data.frame(cond = c("vertical", "horizontal", "random"),
                  mean = c(3.68, 3.50, 3.45), sd = c(0.78, 0.78, 0.88))
okA <- NA
{
  m <- merge(live, cond, by = "id")
  # The paper's "Random" arm is `random` plus the 6 rows whose aitype is
  # recorded as `unknown` (n = 46 total, matching F(2,145) = df 147).
  m$cond <- ifelse(m$cov_aitype == "unknown", "random", m$cov_aitype)
  m$score <- rowMeans(m[, anim])
  cat(sprintf("%-12s %5s %14s %14s %8s\n", "condition", "n",
              "published", "live", "diff"))
  worstA <- 0
  for (i in seq_len(nrow(PUB))) {
    s <- m$score[m$cond == PUB$cond[i]]
    cat(sprintf("%-12s %5d %7.2f (%.2f) %7.2f (%.2f) %8.3f\n",
                PUB$cond[i], length(s), PUB$mean[i], PUB$sd[i],
                mean(s), sd(s), mean(s) - PUB$mean[i]))
    worstA <- max(worstA, abs(mean(s) - PUB$mean[i]))
  }
  cat(sprintf("  largest deviation: %.3f (tolerance 0.02)\n", worstA))
  okA <- worstA <= 0.02
}

## ---- B. duplicate-anchor pin ----------------------------------------------
cat("\n=== B. gqs_animacy_4 vs the perceived-intelligence block ===\n")
cat("    (animacy 4 and perceived intelligence 2 are the SAME printed pair,\n")
cat("     'Unresponsive <-> Responsive')\n")
okB <- NA
if (is.null(src)) {
  cat("  S3 File unavailable; check B skipped.\n")
} else {
  pi5 <- paste0("gqs_perceived_intelligence_", 1:5)
  m <- merge(live, src[, c("sessionId", pi5)], by.x = "id", by.y = "sessionId")
  cm <- cor(m[, anim], m[, pi5], use = "complete.obs")
  print(round(cm, 3))
  best <- which(cm == max(cm), arr.ind = TRUE)
  cat(sprintf("\n  matrix maximum r = %.3f at %s x %s\n", max(cm),
              anim[best[1, 1]], pi5[best[1, 2]]))
  okB <- anim[best[1, 1]] == "gqs_animacy_4" &&
         pi5[best[1, 2]] == "gqs_perceived_intelligence_2"
}

## ---- C. scale direction ----------------------------------------------------
cat("\n=== C. direction: resp 1 = LEFT adjective ===\n")
cat("    S2 File marks Perceived Safety 2 and 3 '(reversed item)'.\n")
PUB_PS <- c(vertical = 3.93, horizontal = 3.64, random = 3.61)
okC <- NA
if (is.null(src)) {
  cat("  S3 File unavailable; check C skipped.\n")
} else {
  ps <- paste0("gqs_perceived_safety_", 1:3)
  s <- src
  s$cond <- ifelse(s$aitype == "unknown", "random", s$aitype)
  raw <- rowMeans(s[, ps])
  rev <- rowMeans(cbind(s[[ps[1]]], 6 - s[[ps[2]]], 6 - s[[ps[3]]]))
  cat(sprintf("%-12s %10s %12s %12s\n", "condition", "published",
              "raw", "2,3 reversed"))
  worstR <- 0; worstRaw <- 0
  for (cd in names(PUB_PS)) {
    k <- s$cond == cd
    cat(sprintf("%-12s %10.2f %12.3f %12.3f\n", cd, PUB_PS[[cd]],
                mean(raw[k]), mean(rev[k])))
    worstR   <- max(worstR,   abs(mean(rev[k]) - PUB_PS[[cd]]))
    worstRaw <- max(worstRaw, abs(mean(raw[k]) - PUB_PS[[cd]]))
  }
  cat(sprintf("  reversed deviation %.3f vs raw deviation %.3f\n",
              worstR, worstRaw))
  okC <- worstR <= 0.02 && worstRaw > 0.5
}

cat("\nNot established by any check above: the order of items 2, 3 and 5\n",
    "among themselves (means 3.67 / 3.61 / 3.64, no published per-item stats).\n",
    "Recorded status is PARTIAL for that reason.\n", sep = "")

pass <- isTRUE(okA) && isTRUE(okB) && isTRUE(okC)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
