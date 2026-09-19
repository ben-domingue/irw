# verify_gilbert_meta_55.R -- Step 5b mapping verification.
#
# CLAIM: `e1_item1`..`e1_item15` in the IRW table are, in that order, questions
# 1..15 of the endline assessment test printed in Table A4 of the paper's
# appendix (Wang, Vlassopoulos, Islam & Hassan 2024; IZA DP 15920 / J-PAL WP4445).
#
# FALSIFIABLE PREDICTION: the paper's Table B3 publishes, per question, the
# proportion of children answering correctly in the full sample AND the marks
# assigned to that question. If the item codes were permuted relative to the
# paper's numbering, neither vector would line up.
#
# Route 1 (per-item published statistics) + the "marks assigned" column, which
# is what separates the two items whose published proportion ties at 0.67.

suppressMessages(library(irw))

TABLE <- "gilbert_meta_55"
ITEMS <- paste0("e1_item", 1:15)

# --- Published values, appendix Table B3 (col. 5 "Total sample", col. 3 "Marks assigned")
PUB_P     <- c(0.92, 0.76, 0.67, 0.57, 0.63, 0.35, 0.61, 0.67, 0.68, 0.41,
               0.82, 0.84, 0.72, 0.45, 0.65)
PUB_MARKS <- c(5, 5, 5, 5, 6, 6, 4, 4, 4, 6, 6, 6, 6, 6, 6)
TOL <- 0.005   # published to 2 dp

# --- Part 1: live per-item proportion correct vs published Table B3 ---------
d <- irw::irw_fetch(TABLE)   # 26,445 rows -- small table, deliberate export
d$resp <- as.numeric(d$resp)
obs <- tapply(d$resp, d$item, mean, na.rm = TRUE)[ITEMS]

cat("Part 1 -- proportion correct, live vs paper Table B3 (total sample)\n")
cat(sprintf("%-10s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-10s %10.2f %10.4f %8.4f\n",
                ITEMS[i], PUB_P[i], obs[i], obs[i] - PUB_P[i]))
worst1 <- max(abs(round(obs, 2) - PUB_P))
cat(sprintf("largest |rounded observed - published|: %.4f (tolerance %.3f)\n\n",
            worst1, TOL))

# --- Part 2: marks assigned, recovered from the source .dta -----------------
# The study's IVR_Data.dta holds both the scored 0/1 variables (e1_item1..15,
# which the IRW table carries verbatim) and the raw mark variables
# (e1_cog_1..4, 9..14, 15..19). Each e1_cog takes only {0, max}, and
# e1_cog/max == e1_item exactly, so max(e1_cog) IS that question's marks.
DTA_URL <- "https://dataverse.harvard.edu/api/access/datafile/8123867?format=original"
cache   <- file.path("..", "..", ".cache", TABLE, "IVR_Data.dta")
if (!file.exists(cache)) {
    cache <- tempfile(fileext = ".dta")
    utils::download.file(DTA_URL, cache, quiet = TRUE, mode = "wb")
}
ok2 <- FALSE
if (requireNamespace("haven", quietly = TRUE) && file.exists(cache)) {
    raw <- haven::read_dta(cache)
    cog <- paste0("e1_cog_", c(1:4, 9:14, 15:19))
    cat("Part 2 -- marks assigned, live-vs-source item identity and paper Table B3\n")
    cat(sprintf("%-10s %-11s %6s %6s %10s %10s\n",
                "item", "source cog", "marks", "pub", "mean(live)", "mean(.dta)"))
    exact <- logical(15); marks <- numeric(15)
    for (i in 1:15) {
        cv <- raw[[cog[i]]]; iv <- raw[[ITEMS[i]]]
        keep <- !is.na(cv) & !is.na(iv)
        marks[i] <- max(cv[keep])
        exact[i] <- all(cv[keep] / marks[i] == iv[keep]) &&
                    abs(mean(iv[keep]) - obs[i]) < 1e-10
        cat(sprintf("%-10s %-11s %6d %6d %10.6f %10.6f\n",
                    ITEMS[i], cog[i], as.integer(marks[i]),
                    as.integer(PUB_MARKS[i]), obs[i], mean(iv[keep])))
    }
    ok2 <- all(exact) && all(marks == PUB_MARKS)
    cat(sprintf("all 15 e1_cog/max == e1_item and mean(live)==mean(.dta) to 1e-10: %s\n",
                all(exact)))
    cat(sprintf("marks vector matches paper Table B3: %s\n\n", all(marks == PUB_MARKS)))
} else {
    cat("Part 2 skipped -- haven unavailable or .dta could not be fetched.\n\n")
}

# --- What this does and does not establish ---------------------------------
cat("Pins: all 15 items. The published proportions alone tie e1_item3 and e1_item8\n",
    "at 0.67; the marks column (5 vs 4, Bangla- vs English-literacy block) separates\n",
    "them, and the (proportion, marks) pair is unique for every one of the 15 items.\n",
    "Does NOT establish which of the three grade-level variants any individual child\n",
    "received -- the IRW table carries no grade column, which is why item_text ships\n",
    "all three Level 1/2/3 wordings from Table A4.\n", sep = "")

cat(if (worst1 <= TOL && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
