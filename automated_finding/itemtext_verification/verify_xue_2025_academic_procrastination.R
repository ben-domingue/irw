# verify_xue_2025_academic_procrastination.R
#
# Step 5b mapping verification (backfill, 2026-09-03) for a table uploaded
# 2026-09-01 in batch `automated_finding` with mapping_basis = paper_explicit.
#
# WHAT IS ACTUALLY BEING CLAIMED, AND WHY IT NEEDS CHECKING
# ---------------------------------------------------------
# The PLOS deposit (S1 Data) names its item columns Q8_1..Q8_19, Q9_1..Q9_20,
# Q10_1..Q10_20. The S3 File ("Constructs and items") names its items
# AP1..AP19, AS1..AS20, CSS1..CSS20. The AP/AS/CSS codes appear NOWHERE in the
# data. data/xue_2025_academic_procrastination.py maps Q8_<i> -> AP<i>
# positionally, in order, inside the Q8 block.
#
# So `paper_explicit` is half right: the CODES are explicit in the paper, but
# their ATTACHMENT to data columns is an order inference. Step 5b's "explicit
# code labels in the paper" exemption does NOT apply here -- that exemption is
# for a label match (paper says "Q1: ..." and the data column is `Q1`), and
# this is not one. Hence this script.
#
# Two things can go wrong, and both are checked:
#   (A) BLOCK BOUNDARY -- one supplementary file lists three constructs in
#       sequence, so an off-by-one at a block edge would put AS wording on AP
#       codes. Checks 1 and 3 test this.
#   (B) ORDER WITHIN THE BLOCK -- whether Q8_7 really is the item S3 File
#       numbers AP7. Check 2 tests this as far as it can be tested.
#
# DATA SOURCING / QUOTA
# ---------------------
# irw_fetch() exports the whole table against a 200GB/30-day account-wide cap.
# There is no server-side aggregate endpoint in the irw package (fetch_resp.R
# has only the live-fetch and local-CSV routes), so exactly ONE fetch is made
# and every live statistic below is computed from it. The academic-stress
# totals needed for check 3 are read from the PLOS deposit over HTTP rather
# than by fetching the sibling IRW table xue_2025_academic_stress -- that would
# be a second export for no gain, since the deposit is the source both tables
# were built from.

suppressMessages(library(irw))

TABLE <- "xue_2025_academic_procrastination"
CODES <- paste0("AP", 1:19)

# ---- Published values, hard-coded from the article (PLOS ONE 10.1371/journal.pone.0338956) ----
PUB_ALPHA      <- 0.871                     # Table 2, "Academic Procrastination"
PUB_AP_HIGH    <- c(m = 63.864, s = 11.140) # Table 3, high-pressure group
PUB_AP_LOW     <- c(m = 51.387, s = 11.248) # Table 3, low-pressure group

# The four S3 File AP stems that are worded TOWARDS good study habits, i.e.
# against the procrastination construct. Read straight off the S3 File block:
#   AP8  "I make sure to organize my study materials so I can use them at any time."
#   AP13 "I have a detailed plan for preparing for exams."
#   AP18 "I have a study plan every day."
#   AP19 "I often check the tasks I should complete before entertainment or going to bed."
# Every other one of the 19 stems describes procrastinating. This is a
# prediction about WHICH FOUR OF NINETEEN POSITIONS behave differently.
POS_WORDED <- c("AP8", "AP13", "AP18", "AP19")

cat("=== ", TABLE, " -- Step 5b mapping verification ===\n\n", sep = "")

# ---------------- live data (ONE fetch) ----------------
d <- as.data.frame(irw::irw_fetch(TABLE))
if (is.null(d) || !nrow(d)) stop("irw_fetch returned no rows; nothing was checked.")
d$resp <- as.numeric(d$resp); d$id <- as.character(d$id); d$item <- as.character(d$item)

W <- as.data.frame(reshape(d[, c("id", "item", "resp")], idvar = "id",
                           timevar = "item", direction = "wide"))
names(W) <- sub("^resp\\.", "", names(W))
X <- as.matrix(W[, CODES])
rownames(X) <- as.character(W$id)
X <- X[stats::complete.cases(X), , drop = FALSE]
cat(sprintf("live respondents with all 19 AP items: %d\n\n", nrow(X)))

cronbach <- function(M) {
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, stats::var)) / stats::var(rowSums(M)))
}

# ---------------- CHECK 1: alpha, as stored ----------------
# Order-invariant, so this does not test within-block order. It tests the BLOCK
# BOUNDARY (is this exactly the 19-column set the paper called "Academic
# Procrastination"?) and the STORAGE DIRECTION (raw, or already reverse-keyed?).
a_raw <- cronbach(X)
Xr <- X; Xr[, POS_WORDED] <- 6 - Xr[, POS_WORDED]
a_rev <- cronbach(Xr)
cat("CHECK 1 -- Cronbach's alpha of the 19 shipped items, as stored\n")
cat(sprintf("  published (Table 2)              : %.3f\n", PUB_ALPHA))
cat(sprintf("  observed, items as stored (raw)  : %.3f   <-- must match\n", a_raw))
cat(sprintf("  observed, 4 pos-worded reversed  : %.3f   (would NOT match)\n", a_rev))
ok1 <- abs(a_raw - PUB_ALPHA) <= 0.002
cat(sprintf("  => %s\n\n", if (ok1) "match" else "MISMATCH"))

# ---------------- CHECK 2: keying polarity (Step 5b route 6) ----------------
# The item-level check. If the S3 File block were shifted by one, or its order
# permuted, the four non-conforming positions would move.
tot <- rowSums(X)
itc <- sapply(CODES, function(c_) stats::cor(X[, c_], tot - X[, c_]))
cat("CHECK 2 -- corrected item-total correlation vs. S3 File wording polarity\n")
cat(sprintf("  %-6s %8s  %s\n", "item", "r", "S3 File stem is worded"))
for (c_ in CODES)
    cat(sprintf("  %-6s %+8.3f  %s\n", c_, itc[c_],
                if (c_ %in% POS_WORDED) "PRO-study (expect r <= 0)" else "procrastinating (expect r > 0)"))
neg_set <- CODES[itc < 0.10]
cat(sprintf("\n  items with r < 0.10 observed : %s\n", paste(neg_set, collapse = ", ")))
cat(sprintf("  items predicted by S3 wording: %s\n", paste(POS_WORDED, collapse = ", ")))
cat(sprintf("  15 procrastination-worded items span r = %+.3f to %+.3f\n",
            min(itc[setdiff(CODES, POS_WORDED)]), max(itc[setdiff(CODES, POS_WORDED)])))
ok2 <- setequal(neg_set, POS_WORDED)
cat(sprintf("  chance of this 4-of-19 split under a random permutation: 1/%d = %.5f\n",
            choose(19, 4), 1 / choose(19, 4)))
cat(sprintf("  => %s\n\n", if (ok2) "exact 4/4 hit, 19/19 positions classified correctly" else "MISMATCH"))

# ---------------- CHECK 3: published subgroup totals (Step 5b route 3) ----------------
# Reproduces Table 3's academic-procrastination row. Needs the academic-stress
# total to form the groups; taken from the PLOS deposit, not from a second
# irw_fetch (see quota note in the header).
cat("CHECK 3 -- Table 3 subgroup totals, groups formed on academic-stress score\n")
ok3 <- NA
url <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0338956.s001")
xlsx <- file.path(tempdir(), "pone.0338956.s001.xlsx")
got <- tryCatch({
    if (!file.exists(xlsx)) utils::download.file(url, xlsx, mode = "wb", quiet = TRUE)
    stopifnot(requireNamespace("readxl", quietly = TRUE)); TRUE
}, error = function(e) FALSE)

if (!isTRUE(got)) {
    cat("  SKIPPED: deposit unreachable or readxl unavailable. Checks 1-2 stand alone.\n\n")
} else {
    raw <- as.data.frame(suppressMessages(readxl::read_excel(xlsx, col_names = FALSE, .name_repair = "minimal")))
    hdr <- as.character(unlist(raw[2, ]))
    src <- raw[-(1:2), , drop = FALSE]; names(src) <- hdr
    src[] <- lapply(src, function(v) suppressWarnings(as.numeric(v)))
    as_tot <- rowSums(src[, paste0("Q9_", 1:20)])
    names(as_tot) <- as.character(as.integer(src$index))

    ap_tot <- setNames(rowSums(X), rownames(X))
    common <- intersect(names(ap_tot), names(as_tot))
    cat(sprintf("  respondents joined live id <-> deposit index: %d\n", length(common)))
    a <- ap_tot[common]; s <- as_tot[common]
    hi <- a[s >  stats::quantile(s, 0.73)]
    lo <- a[s <= stats::quantile(s, 0.27)]
    cat(sprintf("  %-22s %10s %10s | %10s %10s\n", "", "pub mean", "obs mean", "pub sd", "obs sd"))
    cat(sprintf("  %-22s %10.3f %10.3f | %10.3f %10.3f  (n=%d)\n",
                "high-pressure group", PUB_AP_HIGH["m"], mean(hi), PUB_AP_HIGH["s"], stats::sd(hi), length(hi)))
    cat(sprintf("  %-22s %10.3f %10.3f | %10.3f %10.3f  (n=%d)\n",
                "low-pressure group",  PUB_AP_LOW["m"],  mean(lo), PUB_AP_LOW["s"],  stats::sd(lo),  length(lo)))
    ok3 <- abs(mean(hi) - PUB_AP_HIGH["m"]) <= 0.01 && abs(stats::sd(hi) - PUB_AP_HIGH["s"]) <= 0.01 &&
           abs(mean(lo) - PUB_AP_LOW["m"])  <= 0.01 && abs(stats::sd(lo) - PUB_AP_LOW["s"])  <= 0.01
    cat(sprintf("  => %s\n\n", if (ok3) "exact reproduction; the AP block is exactly Q8_1..Q8_19, summed raw" else "MISMATCH"))
}

# ---------------- what this does NOT establish ----------------
cat("WHAT THIS DOES NOT ESTABLISH\n")
cat("  Checks 1 and 3 are order-invariant: they pin the BLOCK (these 19 columns and no\n")
cat("  others are the paper's Academic Procrastination scale, stored raw), not the order\n")
cat("  inside it. Check 2 is the only item-level route and it separates the 4 pro-study\n")
cat("  stems from the 15 procrastination stems; it does NOT distinguish the 15 from each\n")
cat("  other, nor the 4 from each other. A permutation confined within either class --\n")
cat("  e.g. AP2 <-> AP5, or AP13 <-> AP18 -- would pass everything here. The paper\n")
cat("  publishes no per-item statistics (Tables 1-9 are scale-level throughout), the 19\n")
cat("  items share one 1-5 scale so the range fingerprint is flat, and Zhao (2007)'s\n")
cat("  subscale structure is not reported, so no route can close that gap. Status is\n")
cat("  therefore PARTIAL, not VERIFIED.\n\n")

pass <- isTRUE(ok1) && isTRUE(ok2) && !isFALSE(ok3)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
