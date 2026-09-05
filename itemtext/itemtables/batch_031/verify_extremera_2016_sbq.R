# verify_extremera_2016_sbq.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the four live item codes sbq1..sbq4 carry the SBQ-R's own
# item 1..4 wording (lifetime ideation/attempt; past-year ideation frequency;
# threat/told someone; likelihood of a future attempt), and each item's integer
# `resp` is the RAW option index in the instrument's printed order -- NOT the
# SBQ-R's collapsed scoring (which would be 1,2,3,3,4,4 for item 1 and 1,2,2,3,3
# for item 3).
#
# Falsifiable predictions, from the instrument alone (Osman et al. 2001; option
# counts and printed numbering, no per-item statistics are published for this
# sample):
#   sbq1  6 options numbered 1..6   -> live levels 1..6, 6 distinct
#   sbq2  5 options numbered 1..5   -> live levels 1..5, 5 distinct
#   sbq3  5 options numbered 1..5   -> live levels 1..5, 5 distinct
#   sbq4  7 options numbered 0..6   -> live levels 0..6, 7 distinct   <- unique 0-start
# Only item 1 has six options and only item 4 is numbered from 0, so this pins
# sbq1 and sbq4 outright. Items 2 and 3 are both 5-option 1..5 items and are NOT
# separated by this route; the second block below is the (softer) evidence for them.
#
# Live sets/ranges come from irw::irw_table_sets() -- server-side, no export.
# Distributions come from the study's own SPSS deposit (PLOS S1, .sav), whose
# per-item non-missing n is asserted equal to the live per-item n first.

suppressMessages(library(irw))
TABLE <- "extremera_2016_sbq"

EXPECTED <- data.frame(
    item      = c("sbq1", "sbq2", "sbq3", "sbq4"),
    n_options = c(6L, 5L, 5L, 7L),
    lo        = c(1L, 1L, 1L, 0L),
    hi        = c(6L, 5L, 5L, 6L),
    stringsAsFactors = FALSE)

s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
pi <- pi[match(EXPECTED$item, pi$item), ]

cat("== Block 1: per-item option structure, live vs instrument ==\n")
cat(sprintf("%-6s %10s %14s %10s %14s\n",
            "item", "opts(exp)", "range(exp)", "lvls(live)", "range(live)"))
for (i in seq_len(nrow(EXPECTED)))
    cat(sprintf("%-6s %10d %14s %10d %14s\n",
                EXPECTED$item[i], EXPECTED$n_options[i],
                sprintf("%d-%d", EXPECTED$lo[i], EXPECTED$hi[i]),
                pi$n_resp_levels[i],
                sprintf("%d-%d", pi$resp_min[i], pi$resp_max[i])))

# sbq3 carries 2 responses coded 0, outside its five printed options -- a known
# data defect, documented in notes/provenance. Allow it explicitly here.
ok1 <- pi$resp_max[1] == 6 && pi$resp_min[1] == 1 && pi$n_resp_levels[1] == 6 &&
       pi$resp_max[2] == 5 && pi$resp_min[2] == 1 && pi$n_resp_levels[2] == 5 &&
       pi$resp_max[3] == 5 &&
       pi$resp_max[4] == 6 && pi$resp_min[4] == 0 && pi$n_resp_levels[4] == 7
cat(sprintf("block 1: %s  (sbq1 is the only 6-option item; sbq4 the only 0-based, 7-level one)\n",
            if (ok1) "PASS" else "FAIL"))
cat("  note: sbq3 shows 6 levels 0-5 -- five printed options plus 2 responses coded 0,\n",
    "  a source data defect, not a mapping claim.\n", sep = "")

cat("\n== Block 2: raw option index, not SBQ-R scoring ==\n")
cat(sprintf("  sbq1 distinct live levels = %d (SBQ-R scoring would give 4)\n", pi$n_resp_levels[1]))
cat(sprintf("  sbq3 distinct live levels = %d (SBQ-R scoring would give 3)\n", pi$n_resp_levels[3]))
ok2 <- pi$n_resp_levels[1] == 6 && pi$n_resp_levels[3] >= 5
cat(sprintf("block 2: %s\n", if (ok2) "PASS" else "FAIL"))

cat("\n== Block 3: sbq2 vs sbq3, from the deposit ==\n")
ok3 <- NA
sav <- file.path(tempdir(), "extremera_s001.sav")
url <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0163656.s001")
got <- tryCatch({
    if (!file.exists(sav))
        utils::download.file(url, sav, quiet = TRUE, mode = "wb",
                             headers = c("User-Agent" = "IRW-itemtext/1.0"))
    haven::read_sav(sav)
}, error = function(e) {cat("  (deposit unreachable:", conditionMessage(e), ")\n"); NULL})

if (!is.null(got)) {
    d <- got[, c("sbq1", "sbq2", "sbq3")]
    n_live <- pi$n[match(c("sbq1","sbq2","sbq3"), pi$item)]
    n_sav  <- sapply(d, function(x) sum(!is.na(x)))
    cat(sprintf("  per-item non-missing n  sav: %s   live: %s\n",
                paste(n_sav, collapse = "/"), paste(n_live, collapse = "/")))
    stopifnot(all(n_sav == n_live))   # deposit is a faithful proxy for the live table

    base <- !is.na(d$sbq1) & d$sbq1 == 1        # "Never thought about or attempted"
    v2 <- sum(base & !is.na(d$sbq2) & d$sbq2 > 1)
    v3 <- sum(base & !is.na(d$sbq3) & d$sbq3 > 1)
    n0 <- sum(base)
    cat(sprintf("  among the %d who answered sbq1 = 1 (never ideated or attempted, lifetime):\n", n0))
    cat(sprintf("    sbq2 > 1 : %3d (%.1f%%)  <- shipped as PAST-YEAR IDEATION; >1 here is a strict contradiction\n",
                v2, 100*v2/n0))
    cat(sprintf("    sbq3 > 1 : %3d (%.1f%%)  <- shipped as TOLD SOMEONE; a threat without ideation is possible\n",
                v3, 100*v3/n0))
    t2 <- as.integer(table(factor(d$sbq2[!is.na(d$sbq2)], levels = 1:5)))
    t3 <- as.integer(table(factor(d$sbq3[!is.na(d$sbq3) & d$sbq3 > 0], levels = 1:5)))
    cat(sprintf("  level counts sbq2: %s   (frequency ladder -> monotone decline)\n", paste(t2, collapse = "/")))
    cat(sprintf("  level counts sbq3: %s   (options 2a/2b, 3a/3b are pairs -> flat tail)\n", paste(t3, collapse = "/")))
    ok3 <- v2 < v3 && t2[5] < t3[5]
    cat(sprintf("block 3: %s (direction as predicted: %s)\n",
                if (isTRUE(ok3)) "PASS" else "FAIL",
                if (isTRUE(ok3)) "yes" else "no"))
}

cat("\nWhat this does NOT establish: blocks 1-2 distinguish sbq1 and sbq4 from every\n",
    "other item outright, but sbq2 and sbq3 are structurally identical 5-option items\n",
    "and are separated only by block 3's directional/distributional argument, which is\n",
    "suggestive rather than decisive. Status is therefore PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok1 && ok2 && !isFALSE(ok3)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
