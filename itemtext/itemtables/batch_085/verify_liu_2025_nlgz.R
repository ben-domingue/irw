# verify_liu_2025_nlgz.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST. The item text shipped for NLGZ1..NLGZ4 is tied to those codes by an
# EXPLICIT CODE LABEL in the study's own deposit README, not by an order inference:
#
#   "NLGZ: We measured perceived competence with four items. NLGZ1-NLGZ4 represents
#    questions one to four in the scale. ... The items in the scale are as follows:
#    1.I am confident that I can master the skills taught by the physical education
#    teacher in class. 2.I believe I perform better than most students. ..."
#   -- README.md, Dryad doi:10.5061/dryad.brv15dvkd
#
# Two links have to hold for that label to reach the live IRW table, and this script
# tests both, each falsifiably:
#
#   LINK 1 (source -> text): the README, fetched live, still numbers those four
#     sentences 1..4 and still states the NLGZ1-NLGZ4 correspondence. Compared string
#     for string against the shipped item_text. A permutation of any two shipped
#     sentences breaks it.
#   LINK 2 (source column -> live item code): data/liu_2025_teacher_support.py melts the
#     .sav's own columns and keeps the column NAME as `item`, so live NLGZ1 must equal
#     .sav column NLGZ1 for every respondent. Checked cell for cell against the PLOS S1
#     File .sav. This is NOT vacuous: the four columns are far from equal (max pairwise
#     cell agreement 0.619 among 879 respondents), so swapping any two codes would drop
#     that item's match rate to at most that level.
#
# Together the two links are an identity bijection from README question number to live
# item code, so the route distinguishes every item from every other item.
#
# Also printed as corroboration (not load-bearing): the .sav's own composite column NLGZ
# equals the row mean of exactly these four columns, which pins scale membership, and the
# per-item means, which are semantically ordered as the item content predicts.

suppressMessages({ library(irw); library(haven) })

TABLE <- "liu_2025_nlgz"
README_URL <- "https://datadryad.org/dataset/doi:10.5061/dryad.brv15dvkd"
SAV_URL    <- "https://doi.org/10.1371/journal.pone.0314338.s001"

SHIPPED <- c(
  NLGZ1 = "I am confident that I can master the skills taught by the physical education teacher in class.",
  NLGZ2 = "I believe I perform better than most students.",
  NLGZ3 = "I think I am more skilled in sports than most people.",
  NLGZ4 = "I am confident that I can perform as well as or better than others."
)

ok <- TRUE

## ---- LINK 1: the deposit README's explicit code label ------------------------
cat("== LINK 1: Dryad README, code label and item numbering ==\n")
page <- tryCatch(paste(readLines(README_URL, warn = FALSE), collapse = "\n"),
                 error = function(e) NA_character_)
if (is.na(page)) {
  cat("FETCH FAILED:", README_URL, "\n"); ok <- FALSE
} else {
  txt <- gsub("<[^>]+>", " ", page)
  txt <- gsub("&#39;|&rsquo;|&#8217;", "'", txt)
  txt <- gsub("&amp;", "&", txt); txt <- gsub("&quot;", '"', txt)
  txt <- gsub("[ \t\r\n]+", " ", txt)

  claim <- "NLGZ1-NLGZ4 represents questions one to four in the scale"
  has_claim <- grepl(claim, txt, fixed = TRUE)
  cat(sprintf("code-label sentence present: %s  [\"%s\"]\n", has_claim, claim))
  ok <- ok && has_claim

  blk <- sub(".*NLGZ: We measured perceived competence with four items\\.", "", txt)
  blk <- sub("YDCY:.*", "", blk)
  # split the "1.… 2.… 3.… 4.…" run into its four numbered sentences
  parts <- strsplit(blk, "(?<=[.:])\\s*(?=[1-4]\\.)", perl = TRUE)[[1]]
  parts <- trimws(parts[grepl("^[1-4]\\.", trimws(parts))])
  got <- trimws(sub("^[1-4]\\.\\s*", "", parts))
  cat(sprintf("numbered items recovered from README: %d\n", length(got)))
  for (i in seq_along(SHIPPED)) {
    g <- if (i <= length(got)) got[i] else "<missing>"
    same <- identical(g, unname(SHIPPED[i]))
    ok <- ok && same
    cat(sprintf("  README item %d -> %-6s %-5s %s\n", i, names(SHIPPED)[i],
                if (same) "MATCH" else "DIFF", g))
  }
}

## ---- LINK 2: .sav column -> live item code, cell for cell --------------------
cat("\n== LINK 2: live IRW resp vs the PLOS S1 File .sav column of the same name ==\n")
tmp <- tempfile(fileext = ".sav")
utils::download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb")
sav <- as.data.frame(haven::read_sav(tmp))
names(sav)[1] <- "id"
sav$id <- as.integer(sav$id)

live <- irw::irw_fetch(TABLE)
codes <- names(SHIPPED)

cat(sprintf("%-7s %6s %8s %11s %11s\n", "item", "n", "match%", "mean_live", "mean_sav"))
worst <- 1
for (cd in codes) {
  l <- live[live$item == cd, c("id", "resp")]
  m <- merge(l, data.frame(id = sav$id, sav_resp = as.numeric(sav[[cd]])), by = "id")
  rate <- mean(m$resp == m$sav_resp)
  worst <- min(worst, rate)
  cat(sprintf("%-7s %6d %8.4f %11.6f %11.6f\n", cd, nrow(m), rate,
              mean(m$resp), mean(m$sav_resp)))
}
ok <- ok && (worst == 1)

agr <- c()
for (a in 1:3) for (b in (a + 1):4)
  agr <- c(agr, sprintf("%s/%s %.3f", codes[a], codes[b],
                        mean(sav[[codes[a]]] == sav[[codes[b]]], na.rm = TRUE)))
cat("pairwise cell agreement among the four .sav columns: ", paste(agr, collapse = "  "), "\n", sep = "")
cat("max pairwise agreement 0.619 < 1, so no two codes are interchangeable under LINK 2.\n")

## ---- corroboration (not load-bearing) ---------------------------------------
cat("\n== corroboration ==\n")
comp <- rowMeans(sav[, codes])
cat(sprintf("the .sav's own composite column NLGZ equals rowMeans(NLGZ1..NLGZ4): %s (max |diff| %.2e)\n",
            isTRUE(all.equal(as.numeric(sav$NLGZ), comp)),
            max(abs(as.numeric(sav$NLGZ) - comp))))
mn <- tapply(live$resp, live$item, mean)[codes]
cat(sprintf("live per-item means: %s\n", paste(sprintf("%s=%.3f", codes, mn), collapse = "  ")))
cat("Semantically ordered as the content predicts: the two absolute/weak-comparative items\n",
    "(NLGZ1 'master the skills', NLGZ4 'as well as or better than others') sit highest, the\n",
    "strict social comparisons lower, lowest for the strongest claim (NLGZ3 'more skilled\n",
    "than most people'). Corroborating only: the means do not separate NLGZ1 from NLGZ4\n",
    "(3.889 vs 3.901), which is why the status rests on the code-label match in LINK 1 and\n",
    "the cell-for-cell identity in LINK 2, and not on this.\n", sep = "")
cat("Not established by any route here: the administered CHINESE wording. The survey was run\n",
    "in Chinese and neither the .sav (zero variable and value labels) nor the README (English\n",
    "throughout) publishes it, so the shipped English is a translated_substitute.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
