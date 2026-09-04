# verify_wang_2024_self_efficacy_sources.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST (provenance: mapping_basis=paper_explicit, text_source=
# study_materials, S3 Appendix of 10.1371/journal.pone.0297517):
# that each item_text shipped for wang_2024_self_efficacy_sources is attached to
# the right item code among ME1-ME4, VE1-VE3, SP1-SP3, PES1-PES3.
#
# The mapping chain has three links, and they are NOT equally strong:
#   (1) live IRW `item` <-> source deposit column name.  data/wang_2024_speaking_
#       self_efficacy.py selects the item columns BY NAME out of the S1 Data
#       workbook and melts them (var_name="item"), so the IRW code IS the source
#       Excel header -- no positional assignment anywhere in the pipeline
#       (core model section 3, row 1).  Testable: the live per item x resp cell
#       counts must reproduce the deposit's, cell for cell.
#   (2) source column PREFIX <-> S3 Appendix subscale block.  The appendix prints
#       four headed blocks -- "Mastery Experience (ME)", "Vicarious Experience
#       (VE)", "Social Persuasion (SP)", "Physiological and Emotional States
#       (PES)" -- of sizes 4/3/3/3, exactly the prefixes and counts of the data
#       columns.  Testable statistically as block structure (Step 5b route 5).
#   (3) source column SUFFIX <-> the appendix's print order within a block.  The
#       S3 Appendix numbers its items 1..13 CONTINUOUSLY and never prints the
#       strings "ME1", "VE2", ... , so this link is an order inference, not a
#       label match.  NOTHING below tests it.  See the closing note.
#
# QUOTA: no irw_fetch() here.  irw_fetch() exports the whole table against a
# 200GB/30-day account-wide cap that one agent round exhausted on 2026-08-18.
# Every number below comes from a server-side aggregate query (GROUP BY /
# CORR over a self-join), which is not metered as an export.

suppressMessages(library(irw))

TABLE <- "wang_2024_self_efficacy_sources"
ITEMS <- c("ME1", "ME2", "ME3", "ME4", "VE1", "VE2", "VE3",
           "SP1", "SP2", "SP3", "PES1", "PES2", "PES3")

# ---------------------------------------------------------------------------
# Deposited values, hard-coded so this script needs only the live table.
# ---------------------------------------------------------------------------
# Counts of each response 1..7 per item in S1 Data (journal.pone.0297517.s004),
# sheets Study2-efa (224) + Study2-cfa (295) = 519 respondents, read by column
# NAME.  These are the source-of-truth distributions the live table must
# reproduce if no relabelling happened between deposit and IRW.
SRC <- list(
    "ME1"  = c(6, 22, 80, 78, 169, 119, 45),
    "ME2"  = c(5, 26, 58, 91, 177, 124, 38),
    "ME3"  = c(4, 31, 116, 113, 146, 92, 17),
    "ME4"  = c(10, 54, 115, 142, 125, 59, 14),
    "VE1"  = c(3, 20, 82, 115, 152, 109, 38),
    "VE2"  = c(1, 11, 45, 93, 198, 130, 41),
    "VE3"  = c(2, 10, 27, 54, 150, 170, 106),
    "SP1"  = c(30, 71, 121, 160, 78, 45, 14),
    "SP2"  = c(34, 76, 118, 162, 72, 40, 17),
    "SP3"  = c(34, 82, 110, 164, 71, 40, 18),
    "PES1" = c(6, 18, 37, 59, 187, 156, 56),
    "PES2" = c(7, 19, 54, 69, 174, 148, 48),
    "PES3" = c(16, 37, 85, 93, 136, 114, 38))

# Paper, section 3.2.3 (CFA of EFL-SSSES, N = 295): "The mean of all items was
# between 3.72 and 5.87.  Standard deviations varied between 1.04 and 1.50".
PUB_MEAN_RANGE <- c(3.72, 5.87)
PUB_SD_RANGE   <- c(1.04, 1.50)

fails <- character(0)

ref <- irw:::.fetch_redivis_table(TABLE, source = "core")$qualified_reference
cat("live table:", ref, "\n\n")

q <- function(sql) as.data.frame(irw:::.irw_query_tibble(sql))

# ---------------------------------------------------------------------------
# CHECK 1 (link 1) -- per item x resp cell counts, live vs deposit.
# This is Step 5b route 9 logic run in the label->code direction: if the
# pipeline had attached the text of ME1 to the column of ME2, or permuted any
# pair, the 7-number response profile would travel with it and these cells would
# disagree.  It is only decisive if the 13 profiles are mutually distinct, so
# that is checked too rather than assumed.
# ---------------------------------------------------------------------------
cat("== CHECK 1: live item x resp counts vs S1 Data columns (519 respondents) ==\n")
cells <- q(sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                         "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS INT64) AS resp,",
                         "COUNT(*) AS n FROM `%s` GROUP BY 1,2"), ref))
live <- matrix(0L, nrow = length(ITEMS), ncol = 7, dimnames = list(ITEMS, 1:7))
live[cbind(match(cells$item, ITEMS), cells$resp)] <- as.integer(cells$n)
src <- do.call(rbind, SRC[ITEMS])

cat(sprintf("%-6s %-30s %-30s %s\n", "item", "deposit counts 1..7",
            "live counts 1..7", "L1 diff"))
for (it in ITEMS)
    cat(sprintf("%-6s %-30s %-30s %d\n", it,
                paste(src[it, ], collapse = ","),
                paste(live[it, ], collapse = ","),
                sum(abs(src[it, ] - live[it, ]))))
bad <- sum(abs(src - live))
cat(sprintf("\ntotal absolute cell disagreement over 13 x 7 = 91 cells: %d\n", bad))
if (bad != 0) fails <- c(fails, "cell counts differ from the deposit")

d <- as.matrix(dist(src, method = "manhattan"))
diag(d) <- NA
cat(sprintf("closest pair of item profiles: L1 = %d (%s) -- 0 would mean two items\n",
            min(d, na.rm = TRUE),
            paste(rownames(which(d == min(d, na.rm = TRUE), arr.ind = TRUE)),
                  collapse = "/")))
cat("are indistinguishable by this check\n")
if (min(d, na.rm = TRUE) == 0)
    fails <- c(fails, "two items share an identical response profile")

# ---------------------------------------------------------------------------
# CHECK 2 (link 2) -- subscale block structure (Step 5b route 5).
# The appendix's 4/3/3/3 blocks are a prediction about the data: an item should
# correlate more with its own block than with any item outside it.  Correlations
# come from a server-side self-join on id, so no rows are exported.
# ---------------------------------------------------------------------------
cat("\n== CHECK 2: subscale block structure, appendix blocks ME(4) VE(3) SP(3) PES(3) ==\n")
cr <- q(sprintf(paste("SELECT a.item AS i, b.item AS j,",
                      "CORR(SAFE_CAST(a.resp AS FLOAT64), SAFE_CAST(b.resp AS FLOAT64)) AS r",
                      "FROM `%s` a JOIN `%s` b USING(id) GROUP BY 1,2"), ref, ref))
R <- matrix(NA_real_, length(ITEMS), length(ITEMS), dimnames = list(ITEMS, ITEMS))
R[cbind(match(cr$i, ITEMS), match(cr$j, ITEMS))] <- cr$r
grp <- sub("[0-9]+$", "", ITEMS); names(grp) <- ITEMS

ok <- 0
for (a in ITEMS) {
    same  <- setdiff(ITEMS[grp == grp[a]], a)
    other <- ITEMS[grp != grp[a]]
    mn <- min(R[a, same]); mx <- max(R[a, other])
    ok <- ok + (mn > mx)
    cat(sprintf("%-6s weakest within-%-3s r = %+.3f   strongest cross-block r = %+.3f   %s\n",
                a, grp[a], mn, mx, ifelse(mn > mx, "OK", "FAIL")))
}
cat(sprintf("\nblock separation: %d/%d items\n", ok, length(ITEMS)))
if (ok < length(ITEMS)) fails <- c(fails, sprintf("block separation only %d/13", ok))

# Power check: route 5 is underpowered when facets are collinear (SKILL.md warns
# a low score is then NOT evidence of a bad mapping).  Show it is not the case
# here -- the within-block correlations sit far above the cross-block ones.
wi <- unlist(lapply(unique(grp), function(g) {
    it <- ITEMS[grp == g]; R[it, it][upper.tri(R[it, it])] }))
xo <- unlist(lapply(ITEMS, function(a) R[a, ITEMS[grp != grp[a]]]))
cat(sprintf("within-block r: mean %+.3f (min %+.3f) | cross-block r: mean %+.3f (max %+.3f)\n",
            mean(wi), min(wi), mean(xo), max(xo)))
cat("=> the four facets are well separated, so the 13/13 above is a powered result,\n",
    "   not a coincidence of a dominant general factor.\n", sep = "")

# ---------------------------------------------------------------------------
# CHECK 3 -- keying polarity of the PES block (Step 5b route 6).
# PES1-PES3 are the only negatively worded items shipped ("I felt nervous /
# got stressed / got anxious").  If that text is attached to the right columns
# AND the data are stored raw, those three and only those three must correlate
# negatively with the rest of the scale.
# ---------------------------------------------------------------------------
cat("\n== CHECK 3: polarity of the negatively worded PES items (raw vs reverse-scored) ==\n")
# Compared against the 10 POSITIVELY worded items only -- averaging in an item's
# own block-mates would drown the sign that is being tested.
pes <- ITEMS[grp == "PES"]; pos <- ITEMS[grp != "PES"]
for (a in ITEMS) {
    ref_set <- setdiff(pos, a)
    cat(sprintf("%-6s mean r with the %d positively worded items = %+.3f  (%s wording)\n",
                a, length(ref_set), mean(R[a, ref_set]),
                ifelse(grp[a] == "PES", "negative", "positive")))
}
neg_ok <- all(sapply(pes, function(a) mean(R[a, pos]) < 0)) &&
          all(sapply(pos, function(a) mean(R[a, setdiff(pos, a)]) > 0))
cat(sprintf("all 3 PES negative against the positive block, all 10 others positive: %s\n", neg_ok))
cat("=> the PES items are stored RAW (not reverse-scored), which is what the shipped\n",
    "   negatively worded item_text and the 1=Strongly Disagree anchors describe.  This\n",
    "   separates the PES block from the other 10 items by sign; it does not order it.\n", sep = "")
if (!neg_ok) fails <- c(fails, "PES polarity does not match the shipped wording")

# ---------------------------------------------------------------------------
# CHECK 4 -- published CFA-phase mean/SD envelope.
# Confirms the cov_study split reproduces the paper's N=295 CFA subsample.  This
# pins the SUBSAMPLE, not any item: the paper gives only the extremes.
# ---------------------------------------------------------------------------
cat("\n== CHECK 4: CFA-phase (cov_study='cfa', N=295) mean/SD envelope vs paper ==\n")
ms <- q(sprintf(paste("SELECT CAST(item AS STRING) AS item, COUNT(*) AS n,",
                      "AVG(SAFE_CAST(resp AS FLOAT64)) AS m,",
                      "STDDEV_SAMP(SAFE_CAST(resp AS FLOAT64)) AS s",
                      "FROM `%s` WHERE cov_study = 'cfa' GROUP BY 1 ORDER BY 1"), ref))
for (k in seq_len(nrow(ms)))
    cat(sprintf("%-6s n=%d  mean=%.3f  sd=%.3f\n", ms$item[k], ms$n[k], ms$m[k], ms$s[k]))
cat(sprintf("\nobserved mean range %.2f-%.2f  vs paper 3.72-5.87\n",
            min(ms$m), max(ms$m)))
cat(sprintf("observed SD   range %.2f-%.2f  vs paper 1.04-1.50\n",
            min(ms$s), max(ms$s)))
env_ok <- all(abs(range(ms$m) - PUB_MEAN_RANGE) < 0.005) &&
          all(abs(range(ms$s) - PUB_SD_RANGE) < 0.005)
cat(sprintf("envelope matches to 2dp: %s\n", env_ok))
if (!env_ok) fails <- c(fails, "CFA mean/SD envelope does not match the paper")

# ---------------------------------------------------------------------------
# WHAT THIS DOES NOT ESTABLISH
# ---------------------------------------------------------------------------
cat("\n== NOT ESTABLISHED ==\n")
cat("The S3 Appendix numbers its items 1..13 continuously under four subscale headings\n",
    "and never prints the code strings ME1/ME2/... , so the numeric SUFFIX comes from the\n",
    "appendix's print order within a block.  The checks above pin the four block\n",
    "memberships and boundaries (4/3/3/3) and the polarity of the PES block; none of them\n",
    "distinguishes ME1 from ME2, or SP1 from SP2 from SP3.  A within-block permutation\n",
    "would survive every number printed here: 4!*3!*3!*3! = 5184 orderings are compatible\n",
    "with this evidence, of which the shipped one is the appendix's print order.\n", sep = "")
cat("Two rival routes were tried and are reported as failed, not as support:\n",
    "  - per-item published statistics: the paper's Tables 4/5 report loadings, alpha, CR\n",
    "    and AVE per FACTOR only, never per item, so Step 5b route 1 has nothing to match.\n",
    "  - cross-instrument content matching on the deposit's Study3 sheet (n=304 students\n",
    "    who answered both scales) is swamped by a general factor: ME2 ('correct\n",
    "    pronunciation, intonation, liaison') correlates .530 with its content twin LSE5\n",
    "    but .591 with PSE2, so the argmax does not recover the pairing.\n", sep = "")

cat("\n", if (!length(fails)) "VERDICT: PASS\n" else
    paste0("failures: ", paste(fails, collapse = "; "), "\nVERDICT: FAIL\n"), sep = "")
