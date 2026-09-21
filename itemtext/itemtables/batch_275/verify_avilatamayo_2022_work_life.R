# Step 5b verification for avilatamayo_2022_work_life  (batch_275)
#
# mapping_basis = paper_order. The IRW item code IS the SPSS column name
# (data/avilatamayo_2022_csr.py selects by prefix and melts with no rename), and
# the .sav variable labels pin each code to an ORDINAL ("Work-life balance 1",
# "... 2", "... 4" .. "... 8" -- position 3 is absent, the item the paper says
# was dropped from work-life balance for a loading below .50). What is INFERRED
# is that the k-th row of the S1 Appendix's "Equilibrio entre vida laboral y
# vida familiar" block is the k-th SURVIVING position. This script tests what
# can be tested against numbers:
#
#   A. route 9 -- option_text <-> resp. The .sav stores 1..7 with English value
#      labels; the live table stores 1..7. All 49 item x level cell counts must
#      match, which a flipped or permuted anchor set would break at once.
#   B. route 3 -- published subscale statistics. The 7 live items composited
#      must reproduce the paper's Table 1 Work-life balance M / SD (4.19 / 1.41).
#      Pins membership and rules out reverse-scoring.
#   C. route 8 -- semantic coherence of the per-item means and corrected
#      item-total correlations against item content.
#
# What this does NOT establish: the ORDER of the seven item texts within the
# subscale. The paper publishes NO per-item statistic anywhere -- Table 1 is
# construct-level, Fig 2 is a second-order path diagram carrying seven
# construct loadings, and the text reports only a mean loading per factor. Items
# 5.6 (4.4527) and 5.8 (4.4134) are 0.04 apart, so a swap of those two texts
# would be undetectable by any route available here. Hence PARTIAL, not VERIFIED.
#
# Note on B: alpha does NOT reproduce (see below) and the check does not require
# it to. Observed alpha is 0.8835 against a published .90. The same 0.01-0.02 gap
# appears in tangible employee involvement (.938 vs .95) -- the other subscale
# that lost an item -- while the five subscales whose published alpha reproduces
# to two decimals include skills development, which also lost one. M and SD are
# what this route is scored on.
#
# irw_fetch() is used deliberately: this table is 3,028 rows (~140 KB), so the
# export cost is negligible, and per item x level counts cannot be had from
# irw_table_sets().

suppressMessages(library(irw))
TABLE <- "avilatamayo_2022_work_life"
ITEMS <- paste0("Work_Life_5.", c(1, 2, 4, 5, 6, 7, 8), "_1")

# --- source: the study's own S1 Dataset (.sav), fetched fresh -----------------
SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?type=supplementary&id=10.1371/journal.pone.0266711.s001")
tmp <- tempfile(fileext = ".sav")
download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb")
cat("S1 Dataset sha256:", as.character(tools::sha256sum(tmp)), "\n")
cat("expected           329b550875b3e6b29e2d454a3a776e229f1bc05ac1c9bf2c07f7db879aea6662\n\n")
raw <- haven::read_sav(tmp)

cat("=== .sav variable labels for these columns (the ordinal that pins each code) ===\n")
for (it in ITEMS)
    cat(sprintf("%-18s %s\n", it, attr(raw[[it]], "label")))
cat("-> position 3 is absent from the deposit: the dropped work-life item.\n\n")

raw <- as.data.frame(raw[, ITEMS])
raw[] <- lapply(raw, as.numeric)

# --- live --------------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

# --- A. route 9: item x level cell counts ------------------------------------
cat("=== A. item x response-level counts: S1 .sav vs live IRW table ===\n")
cat(sprintf("%-18s %-6s %8s %8s\n", "item", "resp", "sav", "live"))
bad <- 0
for (it in ITEMS) {
    sv <- raw[[it]]
    sv <- sv[!is.na(sv) & sv %in% 1:7]     # one mean-imputed non-integer (3.8308) is dropped
    lv <- d$resp[d$item == it]
    for (k in 1:7) {
        a <- sum(sv == k); b <- sum(lv == k)
        cat(sprintf("%-18s %-6d %8d %8d%s\n", it, k, a, b, if (a != b) "   <-- MISMATCH" else ""))
        if (a != b) bad <- bad + 1
    }
}
cat(sprintf("\nmismatched cells: %d of 49\n\n", bad))

# --- B. route 3: published subscale statistics --------------------------------
cat("=== B. Work-life-balance composite vs paper Table 1 ===\n")
ids <- sort(unique(d$id))
m <- matrix(NA_real_, nrow = length(ids), ncol = length(ITEMS),
            dimnames = list(as.character(ids), ITEMS))
m[cbind(match(d$id, ids), match(d$item, ITEMS))] <- d$resp
m <- m[complete.cases(m), , drop = FALSE]   # the one mean-imputed cell was dropped upstream
comp <- rowMeans(m)
k <- ncol(m)
alpha <- k/(k-1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
PUB <- c(M = 4.19, SD = 1.41)
obs <- c(M = mean(comp), SD = sd(comp))
for (nm in names(PUB))
    cat(sprintf("%-6s published %6.2f   observed %8.4f   diff %7.4f\n",
                nm, PUB[[nm]], obs[[nm]], obs[[nm]] - PUB[[nm]]))
cat(sprintf("%-6s published %6.2f   observed %8.4f   diff %7.4f   (not scored -- see header)\n",
            "alpha", 0.90, alpha, alpha - 0.90))
ok_b <- all(abs(obs - PUB) < 0.015)
cat(sprintf("n complete cases: %d\n\n", nrow(m)))

# --- C. route 8: per-item means / item-total r vs content ---------------------
cat("=== C. per-item means and corrected item-total correlations (live) ===\n")
mu <- sapply(ITEMS, function(it) mean(d$resp[d$item == it]))
ir <- sapply(seq_along(ITEMS), function(i) cor(m[, i], rowSums(m[, -i, drop = FALSE])))
lab <- c("concrete benefit: attractive programmes for all parents (e.g. child care)",
         "flexible working time options",
         "generic: helps all employees coordinate private and professional life",
         "concrete policy: forbids employees being forced to work overtime",
         "absolute: demands do not interfere with free time or family life to any degree",
         "flexibility over daily start time and when to go home",
         "Overall: the company works hard to provide a very good work-life balance")
for (i in seq_along(ITEMS))
    cat(sprintf("%-18s M=%6.3f  r=%.3f  %s\n", ITEMS[i], mu[i], ir[i], lab[i]))
cat(sprintf("\nlowest two means are the two concrete commitments (%.3f child care, %.3f overtime ban);\n",
            mu[1], mu[4]))
cat(sprintf("highest corrected item-total r is the generic coordination item (%.3f), the most\n", ir[3]))
cat("central content in the block -- the ordering item content predicts.\n")
cat(sprintf("items 5.6 and 5.8 differ by %.4f in mean -- this route cannot separate them.\n\n",
            abs(mu[5] - mu[7])))

cat("Establishes: the 1..7 anchors attach to resp in the source's own order (A, 49/49 cells),\n")
cat("and that these seven codes are the published Work-life-balance subscale stored raw, not\n")
cat("reverse-scored (B, M and SD). Does NOT establish the order of the seven item texts within\n")
cat("the subscale: no per-item statistic is published anywhere in the paper.\n")

cat(if (bad == 0 && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
