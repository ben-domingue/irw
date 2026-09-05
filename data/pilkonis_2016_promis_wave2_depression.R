#!/usr/bin/env Rscript
# PROMIS 1 Wave 2 Depression -- Phase 1 (5 tables)
#
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZDIITC
# DOI: 10.7910/DVN/ZDIITC   (alias hdl:1902.1/21231)
# License: CC0 1.0
# IRW issue: https://github.com/ben-domingue/irw/issues/516
#
# Usage:
#   Rscript data/pilkonis_2016_promis_wave2_depression.R "/path/to/PROMIS Wave 2 Depression DI 20130522.sav"
#
# The source .sav must be passed as a command-line argument: Harvard Dataverse
# gates this dataset behind guestbook ID 110, so the file cannot be fetched
# non-interactively the way the rest of this pipeline fetches its inputs.
# Nothing about the source lives in the repository -- neither the .sav nor the
# accompanying codebook/protocol .doc files are copied in.
#
# Study design (from the study protocol, "Protocol 07-04 Version 1.4"):
# a joint Pittsburgh-depression / Seattle-pain PROMIS validation study. This
# file holds the Pittsburgh depression sample only (Arm 3 = Pain has 0 records),
# 194 participants x 3 visits = 568 person-visit records. The PROMIS banks were
# administered as computerized adaptive tests (CATs), so those item matrices are
# sparse by design (~4-6 items per bank per visit); the legacy instruments
# (CES-D, PHQ-9) were administered as fixed forms and are near-complete.
#
# INTENTIONALLY HELD, not processed here:
#   * PROMIS Fatigue (FATEXP/FATIMP/An/HI), Physical Function (PFA/PFB/PFC),
#     Social Participation (SRPSAT) and Sleep-Wake (Sleep*) -- each has an
#     unresolved instrument boundary. Fatigue and Physical Function span
#     several source prefixes whose membership in one bank is not documented in
#     the .sav, codebook or protocol; SRPSAT serves two distinct CATs (separate
#     SocialSatSR and SocialSatDSA T-scores exist) and Sleep* likewise serves
#     both Sleep Disturbance and Wake Disturbance, and the item-to-bank mapping
#     is in none of the three source files.
#   * All Phase 2 instruments (PAININ, PAINBE, MASQ, HRSD, PS, CGI, RMBDQ,
#     MOSSLP, ODI, BPI*, PAQ, CCI, PHHHQ, AQ, GRGH1, SRMCB1/SRMCL1, NASSPSI1).
#   * All derived scores (*_TScore, *_SE, CCITOT, HRSDTOT, WRAT4TOT),
#     demographics, administrative fields, free text and identifying fields.
#
# Response codes are written exactly as administered. No reverse scoring, no
# re-keying, no totals or T-scores, no label substitution, no imputation, no
# item text. Only system-missing values are treated as missing -- the file
# declares no SPSS user-defined missing values, confirmed against the codebook
# ("Missing Values: System" for every variable that has any). In particular:
# CES-D code 0 is the documented anchor "Rarely or none of the time (Less than
# 1 day)" and is retained, and Wave 1's `resp == 6 -> NA` rule
# (data/promis1wave1.R) is deliberately NOT carried over.

suppressPackageStartupMessages(library(haven))

# ---------------------------------------------------------------- paths -----

script_dir <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  f <- grep("^--file=", a, value = TRUE)
  if (length(f)) return(dirname(normalizePath(sub("^--file=", "", f[1]))))
  getwd()
}

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1L) {
  stop("usage: Rscript pilkonis_2016_promis_wave2_depression.R <path to .sav>",
       call. = FALSE)
}
SRC <- args[1]
if (!file.exists(SRC)) stop("source .sav not found: ", SRC, call. = FALSE)

OUT_DIR <- file.path(script_dir(), "..", "automated_finding", "irw_output")
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)
OUT_DIR <- normalizePath(OUT_DIR)

# ------------------------------------------------- structural columns -------

ID_COL   <- "login"   # computer-generated study id; used as-is, not renumbered
WAVE_COL <- "Asmnt"   # 1 = Baseline, 2 = 1 month follow-up, 3 = 3 month f/u
ARM_COL  <- "Arm"     # 1 = Depression (Late-life), 2 = Depression (Mid-life)

OUT_COLS <- c("id", "item", "resp", "wave", "cov_arm")

# ------------------------------- explicit per-table item whitelists ---------
# Hard-coded source variable names. Item sets are never derived by subtracting
# forbidden columns from the full column list.

SCALES <- list(
  pilkonis_2016_promis_depression = list(
    construct = "PROMIS Emotional Distress - Depression (CAT)",
    items = c("EDDEP04", "EDDEP05", "EDDEP06", "EDDEP09", "EDDEP17", "EDDEP19",
              "EDDEP21", "EDDEP22", "EDDEP23", "EDDEP26", "EDDEP28", "EDDEP29",
              "EDDEP30", "EDDEP31", "EDDEP35", "EDDEP36", "EDDEP39", "EDDEP41",
              "EDDEP42", "EDDEP44", "EDDEP45", "EDDEP46", "EDDEP50", "EDDEP54")
  ),
  pilkonis_2016_promis_anxiety = list(
    construct = "PROMIS Emotional Distress - Anxiety (CAT)",
    items = c("EDANX01", "EDANX02", "EDANX03", "EDANX05", "EDANX07", "EDANX12",
              "EDANX16", "EDANX18", "EDANX21", "EDANX26", "EDANX30", "EDANX33",
              "EDANX40", "EDANX41", "EDANX46", "EDANX47", "EDANX48", "EDANX49",
              "EDANX51", "EDANX53", "EDANX54")
  ),
  pilkonis_2016_promis_anger = list(
    construct = "PROMIS Emotional Distress - Anger (CAT)",
    items = c("EDANG01", "EDANG03", "EDANG05", "EDANG06", "EDANG09", "EDANG10",
              "EDANG11", "EDANG15", "EDANG16", "EDANG17", "EDANG18", "EDANG21",
              "EDANG25", "EDANG28", "EDANG30", "EDANG31", "EDANG35", "EDANG37",
              "EDANG45", "EDANG47", "EDANG48", "EDANG54", "EDANG55", "EDANG56")
  ),
  pilkonis_2016_cesd = list(
    construct = "CES-D (20-item, fixed form)",
    items = c("CESD1", "CESD2", "CESD3", "CESD4", "CESD5", "CESD6", "CESD7",
              "CESD8", "CESD9", "CESD10", "CESD11", "CESD12", "CESD13",
              "CESD14", "CESD15", "CESD16", "CESD17", "CESD18", "CESD19",
              "CESD20")
  ),
  pilkonis_2016_phq9 = list(
    construct = "PHQ-9 (fixed form)",
    items = c("PHQ1", "PHQ2", "PHQ3", "PHQ4", "PHQ5", "PHQ6", "PHQ7", "PHQ8",
              "PHQ9")
  )
)

# Documented response-code sets (from the .sav value labels, corroborated by
# the SPSS codebook). Any observed value outside its table's set is fatal.
CODES <- list(
  pilkonis_2016_promis_depression = 1:5,  # 1 Never .. 5 Always
  pilkonis_2016_promis_anxiety    = 1:5,  # 1 Never .. 5 Always
  pilkonis_2016_promis_anger      = 1:5,  # 1 Never .. 5 Always / Not at all .. Very much
  pilkonis_2016_cesd              = 0:3,  # 0 Rarely or none .. 3 Most or all of the time
  pilkonis_2016_phq9              = 1:4   # 1 Not at all .. 4 Nearly every day
)

# Expected results, taken from the completed preflight. Deviation is fatal.
EXPECTED <- list(
  pilkonis_2016_promis_depression = list(items = 24L, rows = 2699L, resp = c(1, 5)),
  pilkonis_2016_promis_anxiety    = list(items = 21L, rows = 2621L, resp = c(1, 5)),
  pilkonis_2016_promis_anger      = list(items = 22L, rows = 3696L, resp = c(1, 5)),
  pilkonis_2016_cesd              = list(items = 20L, rows = 11331L, resp = c(0, 3)),
  pilkonis_2016_phq9              = list(items = 9L,  rows = 5109L, resp = c(1, 4))
)

# Source fields that must never appear as an item or as an output column.
FORBIDDEN <- c(
  # identifying / administrative / free text
  "StudyID", "stcode", "Missing", "TXNOTE", "TXSRCE", "TXTYPE",
  # derived PROMIS scores
  "Anger_SE", "Anger_TScore", "Anxiety_SE", "Anxiety_TScore",
  "Depression_SE", "Depression_TScore", "Fatigue_SE", "Fatigue_TScore",
  "PainBe_SE", "PainBe_TScore", "PainInt_SE", "PainInt_TScore",
  "PhysF_SE", "PhysF_TScore", "SleepDis_SE", "SleepDis_TScore",
  "SocialSatDSA_SE", "SocialSatDSA_TScore", "SocialSatSR_SE",
  "SocialSatSR_TScore", "WakeDis_SE", "WakeDis_TScore",
  # other derived totals
  "CCITOT", "HRSDTOT", "WRAT4TOT",
  # demographics
  "Socio02", "Socio03", "Socio04", "Socio05", "Socio06", "Socio07", "Socio08",
  "Socio10", "Socio11", "fincome",
  "race_nhpi", "race_as", "race_ai", "race_aa", "race_wh",
  "FT_student", "PT_emp", "FT_emp", "loa", "disability", "retired", "unemp",
  "homemaker",
  "csmoke_pipe", "csmoke_cigar", "csmoke_cigt",
  "psmoke_pipe", "psmoke_cigar", "psmoke_cigt"
)
# Held instruments (unresolved Phase 1 candidates + all of Phase 2), by prefix.
HELD_PREFIX <- c("FATEXP", "FATIMP", "An", "HI", "PFA", "PFB", "PFC", "SRPSAT",
                 "Sleep", "PAININ", "PAINBE", "MASQ", "HRSD", "PS", "CGI",
                 "RMBDQ", "MOSSLP", "ODI", "BPI", "PAQ", "CCI", "PHHHQ", "AQ",
                 "GRGH", "SRMCB", "SRMCL", "NASSPSI")

fail <- function(...) stop("FATAL: ", ..., call. = FALSE)

check <- function(ok, ...) if (!isTRUE(ok)) fail(...) else invisible(TRUE)

# --------------------------------------------------------------- load -------

cat("source: ", SRC, "\n", sep = "")
raw <- read_sav(SRC)          # system-missing only; file declares no user-NA
cat(sprintf("read OK: %d rows x %d variables\n\n", nrow(raw), ncol(raw)))

check(all(c(ID_COL, WAVE_COL, ARM_COL) %in% names(raw)),
      "missing structural column(s) in source")

sid  <- as.integer(as.vector(raw[[ID_COL]]))
wave <- as.integer(as.vector(raw[[WAVE_COL]]))
arm  <- as.integer(as.vector(raw[[ARM_COL]]))

# Source-level structural checks, before anything is melted.
check(!any(is.na(sid)),  "NA in ", ID_COL)
check(!any(is.na(wave)), "NA in ", WAVE_COL)
check(!any(is.na(arm)),  "NA in ", ARM_COL)
check(length(unique(sid)) == 194L,
      "expected 194 unique ", ID_COL, ", got ", length(unique(sid)))
check(setequal(unique(wave), 1:3),
      "expected waves {1,2,3}, got {", paste(sort(unique(wave)), collapse = ","), "}")
check(!any(duplicated(data.frame(sid, wave))),
      "duplicate (", ID_COL, ",", WAVE_COL, ") pairs in source")
check(all(tapply(arm, sid, function(z) length(unique(z))) == 1L),
      ARM_COL, " is not invariant within ", ID_COL)

# ---------------------------------------------------- build (in memory) -----

build <- function(nm) {
  spec  <- SCALES[[nm]]
  items <- spec$items

  # whitelist integrity
  check(!any(duplicated(items)), nm, ": duplicated names in whitelist")
  check(all(items %in% names(raw)),
        nm, ": whitelist names absent from source: ",
        paste(setdiff(items, names(raw)), collapse = ", "))
  check(length(intersect(items, FORBIDDEN)) == 0L,
        nm, ": forbidden variable in whitelist: ",
        paste(intersect(items, FORBIDDEN), collapse = ", "))
  check(!any(grepl("(_SE|_TScore|TOT)$", items)),
        nm, ": derived-score name in whitelist")
  bad_held <- items[vapply(items, function(v) {
    p <- HELD_PREFIX[vapply(HELD_PREFIX, function(h) startsWith(v, h), logical(1))]
    length(p) > 0L
  }, logical(1))]
  check(length(bad_held) == 0L,
        nm, ": held-instrument variable in whitelist: ",
        paste(bad_held, collapse = ", "))
  check(!any(items %in% c(ID_COL, WAVE_COL, ARM_COL)),
        nm, ": structural column in whitelist")

  long <- do.call(rbind, lapply(items, function(v) {
    data.frame(id      = sid,
               item    = v,
               resp    = as.numeric(as.vector(raw[[v]])),
               wave    = wave,
               cov_arm = arm,
               stringsAsFactors = FALSE)
  }))
  # only system-missing responses are dropped; nothing else is filtered
  long <- long[!is.na(long$resp), , drop = FALSE]
  long <- long[order(long$id, long$item, long$wave), , drop = FALSE]
  rownames(long) <- NULL
  long
}

validate <- function(nm, long) {
  exp <- EXPECTED[[nm]]
  ok  <- CODES[[nm]]

  check(identical(names(long), OUT_COLS),
        nm, ": columns are {", paste(names(long), collapse = ","),
        "}, expected {", paste(OUT_COLS, collapse = ","), "}")
  check(length(intersect(names(long), FORBIDDEN)) == 0L,
        nm, ": forbidden output column")
  check(is.numeric(long$resp) && !any(is.na(long$resp)),
        nm, ": resp not numeric / contains NA")
  check(all(long$resp %in% ok),
        nm, ": resp outside documented set {", paste(ok, collapse = ","),
        "}: ", paste(sort(unique(setdiff(long$resp, ok))), collapse = ","))
  check(sum(duplicated(long[, c("id", "item", "wave")])) == 0L,
        nm, ": duplicate (id,item,wave) keys")
  check(length(unique(long$id)) == 194L,
        nm, ": ", length(unique(long$id)), " unique ids, expected 194")
  check(setequal(unique(long$wave), 1:3),
        nm, ": waves are not {1,2,3}")
  check(!any(is.na(long$cov_arm)),
        nm, ": NA in cov_arm")
  check(all(tapply(long$cov_arm, long$id, function(z) length(unique(z))) == 1L),
        nm, ": cov_arm not invariant within id")
  check(length(intersect(unique(long$item), FORBIDDEN)) == 0L,
        nm, ": forbidden variable present as an item")

  check(nrow(long) == exp$rows,
        nm, ": ", nrow(long), " rows, preflight expected ", exp$rows)
  check(length(unique(long$item)) == exp$items,
        nm, ": ", length(unique(long$item)), " observed items, preflight expected ",
        exp$items)
  check(min(long$resp) == exp$resp[1] && max(long$resp) == exp$resp[2],
        nm, ": resp range ", min(long$resp), "-", max(long$resp),
        ", preflight expected ", exp$resp[1], "-", exp$resp[2])
  invisible(TRUE)
}

# Deterministic spot-check: re-read the named cell straight out of the source
# frame and compare it to the melted value.
spotcheck <- function(nm, long, k = 3L) {
  idx <- unique(round(seq(1, nrow(long), length.out = k)))
  for (i in idx) {
    r   <- long[i, ]
    srow <- which(sid == r$id & wave == r$wave)
    check(length(srow) == 1L,
          nm, ": spot-check could not resolve a unique source row")
    rawv <- as.numeric(as.vector(raw[[r$item]]))[srow]
    check(identical(as.numeric(rawv), as.numeric(r$resp)),
          nm, ": spot-check mismatch at (", r$id, ",", r$item, ",", r$wave,
          "): output ", r$resp, " vs source ", rawv)
    cat(sprintf("    row %6d  (id=%d, item=%-8s wave=%d)  output resp=%s  <-  .sav row %d = %s  MATCH\n",
                i, r$id, r$item, r$wave, r$resp, srow, rawv))
  }
  invisible(TRUE)
}

# Build and validate everything first; write nothing until all five pass.
tables <- list()
for (nm in names(SCALES)) {
  tables[[nm]] <- build(nm)
  validate(nm, tables[[nm]])
  cat(sprintf("validated %-32s rows=%-6d ids=%-4d items=%-3d waves=%s resp={%s}\n",
              nm, nrow(tables[[nm]]),
              length(unique(tables[[nm]]$id)),
              length(unique(tables[[nm]]$item)),
              paste(sort(unique(tables[[nm]]$wave)), collapse = ","),
              paste(sort(unique(tables[[nm]]$resp)), collapse = ",")))
}
cat("\nall five tables validated in memory; writing output\n\n")

for (nm in names(tables)) {
  long <- tables[[nm]]
  out  <- file.path(OUT_DIR, paste0(nm, ".csv"))
  write.csv(long, out, row.names = FALSE)
  cat(sprintf("%s: rows=%d ids=%d items=%d waves=%s resp=%g-%g dup_keys=%d\n",
              nm, nrow(long), length(unique(long$id)),
              length(unique(long$item)),
              paste(sort(unique(long$wave)), collapse = "/"),
              min(long$resp), max(long$resp),
              sum(duplicated(long[, c("id", "item", "wave")]))))
  cat("  schema: ", paste(names(long), collapse = ","), "\n", sep = "")
  cat("  held-out items (whitelisted, zero responses): ",
      if (length(setdiff(SCALES[[nm]]$items, unique(long$item))))
        paste(setdiff(SCALES[[nm]]$items, unique(long$item)), collapse = ", ")
      else "none", "\n", sep = "")
  cat("  spot-check vs source .sav:\n")
  spotcheck(nm, long)
  cat("  ->", out, "\n\n")
}

cat("done: 5 tables,", sum(vapply(tables, nrow, integer(1))), "rows total\n")
