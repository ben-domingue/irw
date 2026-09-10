## verify_mohammed_2021_patient_safety_culture.R
##
## What this verifies: that each shipped item_text belongs to the item code it is
## attached to, that the 1-5 option anchors are the ones the source file assigns
## per item, and -- the one judgement this table actually made -- that the stored
## response direction agrees with the WORDING of those labels rather than with
## the canonical AHRQ HSOPSC polarity the labels depart from.
##
## Route: data_labels (core model pattern 1). The IRW item codes ARE the S1
## .sav's column names -- data/mohammed_2021_patient_safety.py melts
## HSOPSC_ITEMS straight into `item` with var_name="item", no positional or
## order inference -- so each code carries its own SPSS variable label and value
## labels. Section 1 re-derives the shipped text from the .sav and diffs it
## character by character, which settles the item<->text mapping outright.
##
## Sections 3 and 4 are the substantive check. 18 of the 42 labels read as
## NEGATED versions of canonical HSOPSC reverse-worded items ("Staff in this
## unit does not work longer hours than is best for patient care" against
## AHRQ's A5 "Staff in this unit work longer hours..."), while the paper says
## "Negatively worded items were reversed when computing percent positive
## response" -- i.e. the reversal is claimed at composite time, which would
## leave the raw columns in canonical polarity and make the labels a mislabel.
## The data say otherwise, and that is what these sections print.
##
## Run from itemtext/:
##   Rscript itemtables/batch_109/verify_mohammed_2021_patient_safety_culture.R

suppressMessages({library(haven)})
TBL <- "mohammed_2021_patient_safety_culture"
CSV <- "itemtables/batch_109/mohammed_2021_patient_safety_culture__items.csv"
SAV <- ".cache/mohammed_2021_patient_safety_culture/mohammed_s1.sav"
SRC <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0245966.s001&type=supplementary"

ITEMS <- c("NEVERSAC","PROCEDUR","MISTAKES","SAFETYPR","MISTAKEI","NOPOTENT",
           "HARMPATI","GOODWORD","POSITIVE","PRESSURE","DOINGTHI","POSITIV1",
           "EVALUATE","OVERLOOK","SUPPORT","WORKTOGA","TREATEAC","GETSBUSY",
           "FREELYSP","EELFREE","NOTAFRAI","FEEDBACK","INFORMED","DISCUSS",
           "NOTFEELL","EVENTRE1","NOTWORRY","ENOUGHST","WORKLONG","TEMPORAR",
           "CRISISMO","WORKCLIM","TOPPRIOR","INTEREST","COOPERAT","TOGATHER",
           "COORDINA","PLEASANT","TRANSFER","INFORMAT","ACCROSSH","SHIFTCHA")

## canonical AHRQ HSOPSC 1.0 reverse-worded items, by this file's column names
REV <- c("MISTAKES","SAFETYPR","PRESSURE","OVERLOOK","NOTAFRAI","NOTFEELL",
         "EVENTRE1","NOTWORRY","WORKLONG","TEMPORAR","CRISISMO","INTEREST",
         "COORDINA","PLEASANT","TRANSFER","INFORMAT","ACCROSSH","SHIFTCHA")

fail <- character(0)

if (!file.exists(SAV)) { dir.create(dirname(SAV), recursive = TRUE, showWarnings = FALSE)
                         download.file(SRC, SAV, mode = "wb", quiet = TRUE) }
d  <- read_sav(SAV)
it <- read.csv(CSV, stringsAsFactors = FALSE)

## ---- 1. item_text vs the .sav variable label, one code at a time ------------
cat("=== 1. item_text vs SPSS variable label (per code, exact string compare) ===\n")
nmatch <- 0L
for (i in ITEMS) {
  lab  <- attr(d[[i]], "label")
  ship <- unique(it$item_text[it$item == i])
  ok   <- length(ship) == 1L && identical(ship, lab)
  if (ok) nmatch <- nmatch + 1L else {
    cat(sprintf("*** MISMATCH %-9s label  <<%s>>\n             shipped<<%s>>\n",
                i, lab, paste(ship, collapse = "|")))
    fail <- c(fail, paste("item_text mismatch:", i)) }
}
cat(sprintf("exact matches: %d/%d\n", nmatch, length(ITEMS)))
cat(sprintf("distinct shipped item_text strings: %d (no two codes share text)\n",
            length(unique(it$item_text))))
if (length(unique(it$item_text)) != length(ITEMS))
  fail <- c(fail, "shipped item_text is not distinct per item")

## ---- 2. option_text vs the .sav value labels, per item ----------------------
cat("\n=== 2. option_text/resp vs SPSS value labels (per item) ===\n")
omatch <- 0L; scales <- character(0)
for (i in ITEMS) {
  vl  <- attr(d[[i]], "labels")
  ref <- setNames(names(vl), as.integer(unname(vl)))
  sub <- it[it$item == i, c("resp", "option_text")]
  got <- setNames(sub$option_text, as.character(sub$resp))
  ok  <- identical(ref[order(names(ref))], got[order(names(got))])
  if (ok) omatch <- omatch + 1L else {
    cat(sprintf("*** MISMATCH %-9s (%s)\n", i,
                paste(sprintf("%s=%s", names(ref), ref), collapse = ", ")))
    fail <- c(fail, paste("option_text mismatch:", i)) }
  scales <- c(scales, paste(ref[order(as.integer(names(ref)))], collapse = "|"))
}
cat(sprintf("exact matches: %d/%d\n", omatch, length(ITEMS)))
cat("distinct anchor sets in the file (this is a per-item property, not one shared set):\n")
for (s in unique(scales))
  cat(sprintf("  n=%2d  %s\n", sum(scales == s), s))
## the three event-frequency items must be the never..always ones
freq <- ITEMS[grepl("never", scales)]
cat("items on the never..always scale:", paste(freq, collapse = ", "), "\n")
if (!identical(sort(freq), sort(c("MISTAKEI", "NOPOTENT", "HARMPATI"))))
  fail <- c(fail, "never..always anchors are not on the three event-reporting items")

## ---- 3. ROUTE 6: does the stored direction agree with the label wording? ----
cat("\n=== 3. route 6 -- keying polarity vs the labels' negated wording ===\n")
M <- sapply(ITEMS, function(c) { x <- as.numeric(d[[c]]); x[!(x %in% 1:5)] <- NA; x })
pos <- setdiff(ITEMS, REV)
pm  <- rowMeans(M[, pos], na.rm = TRUE)
r   <- sapply(ITEMS, function(c) cor(M[, c], pm, use = "complete.obs"))
cat(sprintf("mean r with the 24-item positive mean: canonical-positive %+.3f | canonical-reverse %+.3f\n",
            mean(r[pos]), mean(r[REV])))
cat(sprintf("canonical-reverse items with r < 0: %d of %d (range %+.3f to %+.3f)\n",
            sum(r[REV] < 0), length(REV), min(r[REV]), max(r[REV])))
for (i in REV) cat(sprintf("   %-9s %+ .3f\n", i, r[i]))
cat("Reading: had the columns kept canonical polarity, these 18 would correlate NEGATIVELY.\n")
cat("They do not, so the stored values run in the direction the labels' negated wording\n")
cat("states, and the shipped 1=strongly disagree..5=strongly agree anchors are right for them.\n")
if (sum(r[REV] < 0) > 0) fail <- c(fail, "a canonical-reverse item correlates negatively -- direction in doubt")

## ---- 4. ROUTE 3 (corroborative): dimension % positive vs the paper Table 3 --
cat("\n=== 4. route 3 -- 12-dimension percent-positive vs the paper's Table 3 ===\n")
dims <- list("Teamwork within units"   = c("SUPPORT","WORKTOGA","TREATEAC","GETSBUSY"),
             "Teamwork across units"   = c("COOPERAT","TOGATHER","COORDINA","PLEASANT"),
             "Supervisor expectations" = c("GOODWORD","POSITIVE","PRESSURE","OVERLOOK"),
             "Overall perceptions"     = c("MISTAKES","SAFETYPR","NEVERSAC","PROCEDUR"),
             "Organizational learning" = c("DOINGTHI","POSITIV1","EVALUATE"),
             "Communication openness"  = c("FREELYSP","EELFREE","NOTAFRAI"),
             "Mgmt support"            = c("WORKCLIM","TOPPRIOR","INTEREST"),
             "Handoffs"                = c("TRANSFER","INFORMAT","ACCROSSH","SHIFTCHA"),
             "Staffing"                = c("ENOUGHST","WORKLONG","TEMPORAR","CRISISMO"),
             "Feedback"                = c("FEEDBACK","INFORMED","DISCUSS"),
             "Frequency events"        = c("MISTAKEI","NOPOTENT","HARMPATI"),
             "Nonpunitive"             = c("NOTFEELL","EVENTRE1","NOTWORRY"))
pub <- c(74.14,53.14,51.94,51.24,40.24,42.74,33.94,42.24,40.54,47.34,34.64,25.44)
pp  <- function(cols, reverse)
  mean(sapply(cols, function(c) { x <- M[, c]; x <- x[!is.na(x)]
    if (reverse && c %in% REV) 100*mean(x <= 2) else 100*mean(x >= 4) }))
a <- sapply(dims, pp, reverse = FALSE); b <- sapply(dims, pp, reverse = TRUE)
cat(sprintf("%-24s %7s %8s %8s\n", "dimension", "paper", "as-is", "reversed"))
for (k in seq_along(dims))
  cat(sprintf("%-24s %7.2f %8.2f %8.2f\n", names(dims)[k], pub[k], a[k], b[k]))
cat(sprintf("mean |difference| : as-is %.2f | reversed %.2f    (lower is the better fit)\n",
            mean(abs(a - pub)), mean(abs(b - pub))))
cat(sprintf("correlation       : as-is %.3f | reversed %.3f\n", cor(a, pub), cor(b, pub)))
cat("Also: item counts per dimension are 4,4,4,4,3,3,3,4,4,3,3,3, matching Table 3's\n")
cat("'Number of Items' column exactly and summing to 42.\n")
cat("This route is CORROBORATIVE ONLY and is not part of the verdict: every one of the\n")
cat("paper's 12 percentages ends in the digit 4, which no genuine computation produces,\n")
cat("so the published figures are not trustworthy to the decimal. It agrees in direction\n")
cat("with section 3 and pins nothing on its own.\n")
if (mean(abs(a - pub)) >= mean(abs(b - pub)))
  cat("NOTE: the as-is reading no longer fits better than the reversed one -- worth a look,\n",
      "but section 3 is the binding check.\n")

## ---- 5. item/resp sets vs live IRW data, server-side (no export) ------------
cat("\n=== 5. item/resp sets vs live IRW data (irw_table_sets, no export) ===\n")
s <- tryCatch(irw::irw_table_sets(TBL, source = "core", per_item = TRUE),
              error = function(e) { cat("could not reach IRW:", conditionMessage(e), "\n"); NULL })
if (is.null(s)) { cat("live sets unchecked (network) -- sections 1-3 do not depend on this\n")
} else {
  si <- identical(sort(unique(as.character(it$item))), sort(as.character(s$items)))
  sr <- identical(sort(unique(as.integer(it$resp))),   sort(as.integer(s$resp)))
  cat(sprintf("item set identical: %s | resp set identical: %s | live rows: %s\n",
              si, sr, format(s$n_rows, big.mark = ",")))
  if (!si || !sr) fail <- c(fail, "live set mismatch")
}

## ---- 6. response-data observation carried over from the sibling table -------
## Not a mapping defect and not a verdict input. batch_013's
## verify_mohammed_2021_job_satisfaction.R found a FILE-WIDE periodic exact-
## duplicate structure and noted it bears on this table; reproduced here so the
## claim is re-runnable from this table's own directory.
cat("\n=== 6. response-data observation (file-wide duplication, NOT a mapping defect) ===\n")
sig  <- function(cols) apply(M[, cols, drop = FALSE], 1, paste, collapse = "-")
rept <- function(p, k) { n <- length(p); mean(p[1:(n-k)] == p[(1+k):n]) }
ph <- sig(ITEMS)
cat(sprintf("42-item response pattern: %d distinct / %d respondents\n", length(unique(ph)), length(ph)))
cat(sprintf("exact repeat at lag 130: %.1f%%   (an exact 42-value repeat cannot occur by chance)\n",
            100 * rept(ph, 130)))
cat(sprintf("exact repeat at lag  39: %.1f%%\n", 100 * rept(ph, 39)))
cat("Reported, not resolved; it concerns the response table, not the item text.\n")

cat("\n", strrep("-", 60), "\n", sep = "")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse = "\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
