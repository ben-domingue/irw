# verify_ibrahim_2015_sf36.R -- re-runnable evidence for the Step 5b mapping claim.
#
# CLAIM UNDER TEST (two axes):
#  (A) option_text <-> resp. The live integers were produced by
#      data/ibrahim_2015_ckd_personality_qol.py, which maps the label STRINGS
#      stored in the PLOS S1 .sav onto its own 1..N coding -- a coding that is
#      REVERSED relative to the .sav's own numeric codes for several sections.
#      If the shipped option_text were attached to the wrong resp integer (or a
#      whole scale were flipped), the per-item x per-level counts would not
#      match the live table. Checked cell for cell.
#  (B) item_text <-> item. Each item's own response-option set is a structural
#      signature that pins it to a block of the SF-36; the study's own reverse-
#      recode columns (*_R) pin the reverse-keyed POSITIONS inside blocks 9 and
#      11; and the ordinal gradients inside block 3 (walking distance, stairs)
#      are falsifiable predictions of the canonical item order.
#
# WHAT THIS DOES NOT ESTABLISH: it does not separate every item from every
# other. Within Q4a-d, Q5a-c, and within each polarity class of Q9 and Q11,
# nothing here distinguishes e.g. 9a "full of pep" from 9e "a lot of energy",
# or 4a from 4b. That ordering rests on the canonical SF-36 lettering the item
# codes themselves carry. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "ibrahim_2015_sf36"
SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?type=supplementary&id=10.1371/journal.pone.0129015.s001")
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=",
                 commandArgs(FALSE), value = TRUE)[1])),
                 "ibrahim_2015_sf36__items.csv")
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- "ibrahim_2015_sf36__items.csv"

ok <- TRUE

## ---- live per-item x per-resp counts, server-side (no table export) --------
live <- tryCatch({
    tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
    as.data.frame(irw:::.irw_query_tibble(sprintf(
        "SELECT item, resp, COUNT(*) n FROM `%s` GROUP BY item, resp", tbl$qualified_reference)))
}, error = function(e) {
    d <- irw::irw_fetch(TABLE)
    as.data.frame(stats::aggregate(list(n = d$resp), by = list(item = d$item, resp = d$resp), length))
})
live$resp <- as.integer(live$resp)

## ---- the source .sav ------------------------------------------------------
tf <- file.path(tempdir(), "ibrahim2015.sav")
if (!file.exists(tf)) curl::curl_download(SAV_URL, tf, quiet = TRUE)
sav <- haven::read_sav(tf)

items <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE, colClasses = c(resp = "integer"))

## ==== (A) route 9: label counts through the shipped mapping ================
cat("=== (A) option_text <-> resp: source label counts vs live resp counts ===\n")
cat(sprintf("%-9s %-26s %5s %8s %8s\n", "item", "option_text", "resp", "sav_n", "live_n"))
cellsA <- 0; badA <- 0
for (it in sort(unique(items$item))) {
    sub <- items[items$item == it, ]
    v <- sav[[it]]
    labs <- attr(v, "labels")                  # .sav's own code -> label
    txt  <- names(labs)[match(as.numeric(v), as.numeric(labs))]
    txt[is.na(txt) & !is.na(v)] <- "<unlabelled>"
    for (k in seq_len(nrow(sub))) {
        # the shipped option_text, counted in the raw file
        sav_n <- sum(txt == sub$option_text[k], na.rm = TRUE)
        # unlabelled raw 6.0 in SF36Q10 is kept by the processing script as "all the time"
        if (it == "SF36Q10" && sub$option_text[k] == "all the time")
            sav_n <- sav_n + sum(txt == "<unlabelled>" & as.numeric(v) == 6, na.rm = TRUE)
        lr <- live[live$item == it & live$resp == sub$resp[k], "n"]
        live_n <- if (length(lr)) as.integer(lr) else 0L
        cellsA <- cellsA + 1
        if (sav_n != live_n) { badA <- badA + 1; ok <- FALSE }
        cat(sprintf("%-9s %-26s %5d %8d %8d%s\n", it,
                    substr(sub$option_text[k], 1, 26), sub$resp[k], sav_n, live_n,
                    if (sav_n != live_n) "   <-- MISMATCH" else ""))
    }
}
cat(sprintf("\n(A) %d of %d item x option cells reconcile exactly.\n", cellsA - badA, cellsA))

## ==== (B1) each item's option set == the .sav's label set for that column ===
cat("\n=== (B1) shipped option set vs .sav value-label set, per item ===\n")
badB1 <- 0
for (it in sort(unique(items$item))) {
    shipped <- sort(items$option_text[items$item == it])
    labset  <- sort(names(attr(sav[[it]], "labels")))
    if (!identical(shipped, labset)) { badB1 <- badB1 + 1; ok <- FALSE
        cat(sprintf("  %-9s MISMATCH: shipped {%s} vs sav {%s}\n", it,
                    paste(shipped, collapse = "|"), paste(labset, collapse = "|"))) }
}
cat(sprintf("  %d of %d items have an option set identical to their .sav label set",
            length(unique(items$item)) - badB1, length(unique(items$item))))
cat(".\n  (SF36Q10 carries only its 5 labelled categories; the script's one unlabelled\n",
    "   raw 6.0 is folded into 'all the time' at resp 6 in check (A) above.)\n", sep = "")

## ==== (B2) the study's own reverse-recode columns == canonical SF-36 set ====
cat("\n=== (B2) study's *_R recode columns vs canonical SF-36 reversal set ===\n")
rcols <- sort(sub("_R$", "", grep("^SF36.*_R$", names(sav), value = TRUE)))
canon <- sort(paste0("SF36Q", c("1","2","6","7","8","9a","9d","9e","9h","11b","11d")))
cat("  study : ", paste(rcols, collapse = " "), "\n")
cat("  canon : ", paste(canon, collapse = " "), "\n")
if (!identical(rcols, canon)) { ok <- FALSE; cat("  MISMATCH\n") } else
    cat("  identical -- pins the reverse-keyed POSITIONS 9a/9d/9e/9h and 11b/11d\n")

## ==== (B3) ordinal gradients predicted by the canonical Q3 order ===========
cat("\n=== (B3) live means, block 3 (1 = limited a lot .. 3 = not limited) ===\n")
m <- tapply(live$resp * live$n, live$item, sum) / tapply(live$n, live$item, sum)
q3 <- paste0("SF36Q3", letters[1:10])
lab3 <- c("vigorous","moderate","groceries","several flights","one flight",
          "bending","walk >1 mile","walk several blocks","walk one block","bathing")
for (i in seq_along(q3)) cat(sprintf("  %-9s %-20s %.3f\n", q3[i], lab3[i], m[q3[i]]))
pred <- c(
  "3a vigorous is the most limiting"      = unname(m["SF36Q3a"] == min(m[q3])),
  "3j bathing is the least limiting"      = unname(m["SF36Q3j"] == max(m[q3])),
  "walking: 3g < 3h < 3i (mile<blocks<block)" =
      unname(m["SF36Q3g"] < m["SF36Q3h"] && m["SF36Q3h"] < m["SF36Q3i"]),
  "stairs: 3d < 3e (several flights < one flight)" = unname(m["SF36Q3d"] < m["SF36Q3e"]))
for (nm in names(pred)) { cat(sprintf("  [%s] %s\n", if (pred[nm]) "ok" else "FAIL", nm))
                          if (!pred[nm]) ok <- FALSE }

## ==== (B4) Q9 polarity classes =============================================
cat("\n=== (B4) live means, block 9 (1 = none of the time .. 6 = all the time) ===\n")
pos <- paste0("SF36Q9", c("a","d","e","h")); neg <- paste0("SF36Q9", c("b","c","f","g","i"))
cat("  positively worded (pep/calm/energy/happy): ",
    paste(sprintf("%s=%.2f", pos, m[pos]), collapse = "  "), "\n")
cat("  negatively worded (nervous/down/blue/worn/tired): ",
    paste(sprintf("%s=%.2f", neg, m[neg]), collapse = "  "), "\n")
if (min(m[pos]) > max(m[neg]))
    cat("  the four positives all exceed every negative -- polarity classes separate cleanly\n") else
    { ok <- FALSE; cat("  FAIL: polarity classes overlap\n") }

cat("\nThis pins blocks, polarity classes and the block-3 gradient; it does NOT\n",
    "distinguish 4a-4d, 5a-5c, or the items within a polarity class of Q9/Q11.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
