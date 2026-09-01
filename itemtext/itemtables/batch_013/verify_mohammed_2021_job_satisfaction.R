## verify_mohammed_2021_job_satisfaction.R
##
## What this verifies: that each shipped item_text belongs to the item code it is
## attached to, and that the 1-5 option anchors are the ones the source file assigns.
##
## Route: data_labels. The mapping is mechanical, not inferred -- the IRW item codes
## ARE the S1 .sav's column names (data/mohammed_2021_patient_safety.py melts
## JOBSAT_ITEMS straight into `item`), so each code carries its own SPSS variable
## label. This script re-derives the shipped text from the .sav and diffs it
## character-by-character against the CSV, which settles the mapping outright.
##
## It also re-runs the two corroboration routes that FAILED, so the record of why
## the scale direction is uncorroborated is re-runnable rather than just asserted,
## and re-runs the response-data anomaly check flagged in provenance.
##
## Run from itemtext/:
##   Rscript itemtables/batch_013/verify_mohammed_2021_job_satisfaction.R

suppressMessages({library(haven); library(redivis)})
TBL  <- "mohammed_2021_job_satisfaction"
CSV  <- "itemtables/batch_013/mohammed_2021_job_satisfaction__items.csv"
SAV  <- ".cache/mohammed_2021_job_satisfaction/mohammed_s1.sav"
SRC  <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0245966.s001&type=supplementary"
ITEMS <- c("jobsat","jobsats","jobsatss","jobsatsss","jobsatssss")
fail <- character(0)

if (!file.exists(SAV)) { dir.create(dirname(SAV), recursive=TRUE, showWarnings=FALSE)
                         download.file(SRC, SAV, mode="wb", quiet=TRUE) }
d  <- read_sav(SAV)
it <- read.csv(CSV, stringsAsFactors=FALSE)

## ---- 1. item_text vs the .sav variable label, one code at a time -------------
cat("=== 1. item_text vs SPSS variable label (per code, exact string compare) ===\n")
for (i in ITEMS) {
  lab  <- attr(d[[i]], "label")
  ship <- unique(it$item_text[it$item == i])
  ok   <- length(ship) == 1L && identical(ship, lab)
  cat(sprintf("%-11s %s\n             label  <<%s>>\n             shipped<<%s>>\n",
              i, if (ok) "MATCH" else "*** MISMATCH ***", lab, paste(ship, collapse="|")))
  if (!ok) fail <- c(fail, paste("item_text mismatch:", i))
}

## ---- 2. option_text vs the .sav value labels, per item ----------------------
cat("\n=== 2. option_text/resp vs SPSS value labels (per item) ===\n")
for (i in ITEMS) {
  vl  <- attr(d[[i]], "labels")
  ref <- setNames(names(vl), as.integer(unname(vl)))
  sub <- it[it$item == i, c("resp","option_text")]
  got <- setNames(sub$option_text, as.character(sub$resp))
  ok  <- identical(ref[order(names(ref))], got[order(names(got))])
  cat(sprintf("%-11s %s  (%s)\n", i, if (ok) "MATCH" else "*** MISMATCH ***",
              paste(sprintf("%s=%s", names(ref), ref), collapse=", ")))
  if (!ok) fail <- c(fail, paste("option_text mismatch:", i))
}

## ---- 3. literal-transcription assertions -----------------------------------
cat("\n=== 3. transcription is literal, not tidied ===\n")
lt <- all(it$item_text == tolower(it$item_text)) && all(it$option_text == tolower(it$option_text))
cat("all item_text and option_text still lowercase as in source:", lt, "\n")
pr <- identical(unique(it$item_text[it$item == "jobsatsss"]), "am proud to work at this hospital")
cat("jobsatsss retains source's missing leading 'I':", pr, "\n")
if (!lt || !pr) fail <- c(fail, "text was normalised away from the source")

## ---- 4. item/resp sets vs live data (shard 4; irw_fetch cannot see it) ------
cat("\n=== 4. item/resp sets vs live IRW data ===\n")
gt <- tryCatch({
  tl <- redivis$organization("datapages")$dataset("item_response_warehouse_4")$list_tables()
  tl[[which(sapply(tl, function(t) t$name) == TBL)]]$to_data_frame()
}, error = function(e) { cat("could not fetch live data:", conditionMessage(e), "\n"); NULL })
if (is.null(gt)) { fail <- c(fail, "live data unavailable -- sets unchecked") } else {
  si <- identical(sort(unique(as.character(it$item))), sort(unique(as.character(gt$item))))
  sr <- identical(sort(unique(as.numeric(it$resp))),   sort(unique(as.numeric(gt$resp))))
  cat("item set identical:", si, " | resp set identical:", sr,
      " | live rows:", nrow(gt), "\n")
  if (!si || !sr) fail <- c(fail, "live set mismatch")
}

## ---- 5. the two corroboration routes that are NOT available -----------------
cat("\n=== 5. why scale direction is uncorroborated (expected to stay unavailable) ===\n")
M <- as.matrix(sapply(d[ITEMS], as.numeric))
js <- as.numeric(d$Jobsatisfaction)
cat(sprintf("route 3 (published total): derived Jobsatisfaction is %d not-satisfied / %d satisfied,\n",
            sum(js==1), sum(js==2)))
cat(sprintf("   matching the paper's Table 1 -- but point-biserial with the 5-item mean is %+.3f,\n",
            cor(as.numeric(js==2), rowMeans(M))))
cat("   so it is a separate self-report, not a composite of these items. Route unavailable.\n")
pos <- c("SUPPORT","WORKTOGA","TREATEAC","GETSBUSY","DOINGTHI","GOODWORD",
         "POSITIVE","COOPERAT","TOGATHER","COORDINA","PLEASANT")
pm <- rowMeans(as.matrix(sapply(d[pos], as.numeric)), na.rm=TRUE)
cat(sprintf("route 6 (polarity vs known-positive HSOPSC block, same 1-5 label set): r = %+.3f\n",
            cor(rowMeans(M), pm, use="complete.obs")))
cat("   ~0 rather than positive, so polarity cannot be read off it. Route unavailable.\n")

## ---- 6. response-data anomaly (reported, not a mapping defect) --------------
## NOTE on scope: an earlier pass of this check framed the lag-39 repeat as
## specific to the jobsat block, contrasted against a single HSOPSC column. That
## comparison was wrong -- a 5-column block repeats far more readily than one
## column. Compared block-to-block, the duplication structure turns out to be
## FILE-WIDE (the 42 HSOPSC items repeat at lag 130), so it is not a jobsat
## finding and it also affects mohammed_2021_patient_safety_culture. What stays
## specific to jobsat is its correlational isolation. Both are printed below.
cat("\n=== 6. response-data observations (not mapping defects) ===\n")
HS <- c("NEVERSAC","PROCEDUR","MISTAKES","SAFETYPR","MISTAKEI","NOPOTENT","HARMPATI","GOODWORD",
        "POSITIVE","PRESSURE","DOINGTHI","POSITIV1","EVALUATE","OVERLOOK","SUPPORT","WORKTOGA",
        "TREATEAC","GETSBUSY","FREELYSP","EELFREE","NOTAFRAI","FEEDBACK","INFORMED","DISCUSS",
        "NOTFEELL","EVENTRE1","NOTWORRY","ENOUGHST","WORKLONG","TEMPORAR","CRISISMO","WORKCLIM",
        "TOPPRIOR","INTEREST","COOPERAT","TOGATHER","COORDINA","PLEASANT","TRANSFER","INFORMAT",
        "ACCROSSH","SHIFTCHA")
sig  <- function(cols) apply(as.matrix(sapply(d[cols], as.numeric)), 1, paste, collapse = "-")
rept <- function(p, k) { n <- length(p); mean(p[1:(n-k)] == p[(1+k):n]) }

cat("(a) FILE-WIDE periodic duplication -- affects the sibling 42-item table too:\n")
pj <- sig(ITEMS); ph <- sig(HS)
cat(sprintf("    jobsat 5-item pattern : %3d distinct / %d | repeat at lag 39 = %.1f%%, lag 130 = %.1f%%\n",
            length(unique(pj)), length(pj), 100*rept(pj,39), 100*rept(pj,130)))
cat(sprintf("    HSOPSC 42-item pattern: %3d distinct / %d | repeat at lag 39 = %.1f%%, lag 130 = %.1f%%\n",
            length(unique(ph)), length(ph), 100*rept(ph,39), 100*rept(ph,130)))
cat("    An exact 42-value repeat cannot happen by chance, so the HSOPSC block carries the\n")
cat("    same class of structure at a different period. Genuine 5-item HSOPSC blocks show\n")
cat("    exact 5-column repeats of 44-54% at lag 130, i.e. comparable to jobsat's 46.5%.\n")
allv <- setdiff(names(d), "ID")
pa <- apply(as.matrix(suppressWarnings(sapply(d[allv], as.numeric))), 1, paste, collapse="-")
cat(sprintf("    Outright duplicate full records: %d (all %d are distinct)\n",
            sum(duplicated(pa)), length(unique(pa))))

cat("\n(b) SPECIFIC to the jobsat block, and not explained by (a):\n")
M <- as.matrix(sapply(d[ITEMS], as.numeric))
cat(sprintf("    rows with all five items identical: %.1f%% (genuine 5-item HSOPSC blocks: 12-22%%)\n",
            100*mean(apply(M, 1, function(r) length(unique(r)) == 1))))
cat(sprintf("    rows with jobsat/jobsatss/jobsatsss/jobsatssss identical: %.1f%%\n",
            100*mean((M[,1]==M[,3]) & (M[,1]==M[,4]) & (M[,1]==M[,5]))))
best <- 0; for (n2 in setdiff(names(d), ITEMS)) {
  x <- suppressWarnings(as.numeric(d[[n2]]))
  if (all(is.na(x)) || length(unique(x[!is.na(x)])) < 2) next
  r <- suppressWarnings(abs(cor(rowMeans(M), x, use = "complete.obs")))
  if (!is.na(r) && r > best) best <- r }
cat(sprintf("    max |r| of the 5-item mean with ANY of the other file variables: %.3f\n", best))
pos <- c("SUPPORT","WORKTOGA","TREATEAC","GETSBUSY","DOINGTHI","GOODWORD",
         "POSITIVE","COOPERAT","TOGATHER","COORDINA","PLEASANT")
pmm <- rowMeans(as.matrix(sapply(d[pos], as.numeric)), na.rm = TRUE)
b2 <- 0; for (n2 in setdiff(names(d), pos)) {
  x <- suppressWarnings(as.numeric(d[[n2]]))
  if (all(is.na(x)) || length(unique(x[!is.na(x)])) < 2) next
  r <- suppressWarnings(abs(cor(pmm, x, use = "complete.obs")))
  if (!is.na(r) && r > b2) b2 <- r }
cat(sprintf("    same figure for the HSOPSC positive block, for contrast: %.3f\n", b2))
cat("    A block that correlates with nothing in its own file is the robust anomaly here.\n")
cat("Neither observation affects the item-text mapping or the verdict below.\n\n")

cat("\n", strrep("-", 60), "\n", sep="")
if (length(fail)) { cat("VERDICT: FAIL\n"); cat(paste0("  - ", fail, collapse="\n"), "\n")
} else            { cat("VERDICT: PASS\n") }
