# verify_kim_2025_isi.R -- Step 5b mapping check for kim_2025_isi.
#
# CLAIM UNDER TEST
#   ISI_1_1 = "Difficulty falling asleep"
#   ISI_1_2 = "Difficulty staying asleep"
#   ISI_1_3 = "Problems waking up too early"
#   ISI_2 = satisfaction, ISI_3 = interference, ISI_4 = noticeability to others,
#   ISI_5 = worry/distress.
#
# ISI_2..ISI_5 are pinned by the deposit's OWN per-column value labels (S1 File,
# legend rows 288-292), which name each item's construct outright -- Step 5b
# exemption 2 at the value-label level, nothing statistical needed.
#
# ISI_1_1/1_2/1_3 share one anchor set ("not at all".."very severe") and one 1-5
# range, so no label and no range fingerprint separates them. This script tests
# them against three sleep markers collected in the SAME file (the PSQI block),
# which is the falsifiable part: if any two of the three severity sub-items were
# swapped, the pattern below inverts.
#
#   onset markers  : PSQI_2 (sleep latency, minutes), PSQI_5_a ("cannot fall
#                    asleep within 30 min")           -> ISI_1_1 must top both
#   maintenance    : PSQI_5_b ("wake up in the middle of the night or early
#                    morning")                        -> ISI_1_2 must top it
#   early waking   : PSQI_3 (habitual wake CLOCK TIME) -> only ISI_1_3 may
#                    correlate NEGATIVELY (endorsing "waking up too early"
#                    means actually getting up earlier)
#
# LIVE-DATA TIE: data/kim_2025_presleep_arousal.py melts the S1 workbook with
# var_name="item", so the live IRW `item` code IS the source column name for all
# seven items (no positional assignment anywhere). The correlations computed here
# on the source columns are therefore correlations on the live items. That tie is
# re-asserted below against irw::irw_table_sets() (server-side; no export).

suppressMessages(library(irw))

TABLE <- "kim_2025_isi"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0333390.s001")

# ---- data -------------------------------------------------------------------
cache <- file.path("itemtext/.cache", TABLE, "s001.xlsx")
if (!file.exists(cache)) cache <- file.path(".cache", TABLE, "s001.xlsx")
if (!file.exists(cache)) {
    cache <- tempfile(fileext = ".xlsx")
    utils::download.file(SI_URL, cache, quiet = TRUE, mode = "wb")
}
suppressMessages(d <- as.data.frame(readxl::read_excel(cache)))
d <- d[!is.na(suppressWarnings(as.numeric(d$No))), , drop = FALSE]
cat(sprintf("source rows (respondents): %d\n", nrow(d)))

lead <- function(x) suppressWarnings(as.numeric(sub("^([0-9]+(\\.[0-9]+)?).*$", "\\1", trimws(as.character(x)))))
clock <- function(x) {
    s <- as.character(x)
    m <- regmatches(s, regexpr("[0-9]{1,2}:[0-9]{2}", s))
    out <- rep(NA_real_, length(s)); ok <- regexpr("[0-9]{1,2}:[0-9]{2}", s) > 0
    p <- do.call(rbind, strsplit(m, ":")); out[ok] <- as.numeric(p[,1]) + as.numeric(p[,2])/60
    out
}

ISI <- c("ISI_1_1","ISI_1_2","ISI_1_3","ISI_2","ISI_3","ISI_4","ISI_5")
X <- as.data.frame(lapply(d[ISI], lead)); names(X) <- ISI
mk <- data.frame(
    latency_min = lead(d$PSQI_2),
    onset_5a    = lead(d$PSQI_5_a),
    maint_5b    = lead(d$PSQI_5_b),
    wake_clock  = clock(d$PSQI_3))

# ---- plumbing tie (asserted, not the evidence) ------------------------------
s <- irw::irw_table_sets(TABLE, source = "core")
cat(sprintf("live item set == source ISI column names: %s\n",
            identical(sort(as.character(s$items)), sort(ISI))))

# ---- the evidence -----------------------------------------------------------
rho <- function(v) sapply(X, function(y) suppressWarnings(cor(y, v, method = "spearman", use = "complete.obs")))
R <- sapply(mk, rho)
cat("\nSpearman rho, ISI item x same-file PSQI marker (n = 286)\n")
print(round(R, 3))

sev <- c("ISI_1_1","ISI_1_2","ISI_1_3")
c1 <- which.max(R[, "onset_5a"])    == which(ISI == "ISI_1_1")   # over ALL 7 items
c2 <- which.max(R[, "latency_min"]) == which(ISI == "ISI_1_1")
c3 <- which.max(R[sev, "maint_5b"]) == 2                          # ISI_1_2 among the trio
c4 <- R["ISI_1_3", "wake_clock"] < 0 && all(R[c("ISI_1_1","ISI_1_2"), "wake_clock"] > R["ISI_1_3", "wake_clock"])
c5 <- which.max(R[, "maint_5b"])    == which(ISI == "ISI_1_2")

cat(sprintf("\n[%s] ISI_1_1 tops PSQI_5a 'cannot fall asleep within 30 min' over all 7 items (%.3f vs next %.3f)\n",
            ifelse(c1,"ok","FAIL"), max(R[,"onset_5a"]), sort(R[,"onset_5a"], decreasing=TRUE)[2]))
cat(sprintf("[%s] ISI_1_1 tops PSQI_2 sleep-latency minutes over all 7 items (%.3f vs next %.3f)\n",
            ifelse(c2,"ok","FAIL"), max(R[,"latency_min"]), sort(R[,"latency_min"], decreasing=TRUE)[2]))
cat(sprintf("[%s] ISI_1_2 tops PSQI_5b night/early waking among the severity trio (%.3f vs %.3f, %.3f)\n",
            ifelse(c3,"ok","FAIL"), R["ISI_1_2","maint_5b"], R["ISI_1_1","maint_5b"], R["ISI_1_3","maint_5b"]))
cat(sprintf("[%s] ISI_1_2 tops PSQI_5b over all 7 items\n", ifelse(c5,"ok","FAIL")))
cat(sprintf("[%s] ISI_1_3 is the ONLY severity item negatively correlated with habitual wake clock time (%.3f vs %+.3f, %+.3f)\n",
            ifelse(c4,"ok","FAIL"), R["ISI_1_3","wake_clock"], R["ISI_1_1","wake_clock"], R["ISI_1_2","wake_clock"]))

cat("\nWhat this does NOT establish: the WORDING. The seven English stems are\n",
    "third-party text (Lenderking et al. 2024, J Patient Rep Outcomes 8:65, CC BY 4.0,\n",
    "Table 4, co-authored by the ISI's copyright holder), not the Korean the 286\n",
    "respondents actually read -- no Korean wording exists in the deposit or the\n",
    "paper. It also does not test ISI_2..ISI_5 statistically; those rest on the\n",
    "S1 File's own per-column value labels, which name their constructs.\n", sep = "")

cat(if (all(c1, c2, c3, c4, c5)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
