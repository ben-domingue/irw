# verify_esiason_2024_aaqii.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST: the REDCap column codes aaq1..aaq7 (which the IRW processing
# script melts straight through as `item`, data/esiason_2024_nmosd.py) carry the
# CANONICAL AAQ-II item numbering of Bond et al. (2011), i.e. aaq1 = "My painful
# experiences and memories...", aaq4 = "My painful memories prevent me...", etc.
# Neither the PLOS paper nor the S1/S2 workbooks state this: the workbooks carry
# no variable labels and the paper only cites the scale. So the numbering is an
# inference and this script is what tests it.
#
# DATA. This reads the study's own S1/S2 supplementary workbooks rather than
# irw_fetch(), for two reasons: (a) irw_fetch() exports the whole table against
# the 200GB/30-day account cap; (b) the live table is a strict subset of these
# same columns -- the processing script dropped every response of 6 or 7 via
# valid_range=(1,5) -- so the raw columns give the UNTRUNCATED correlations the
# structural test needs. The `item` codes are byte-identical either way: the
# script does df.melt(value_vars=["aaq1".."aaq7"], var_name="item").
#
# TEST 1 (route 5, content-block structure). The AAQ-II's seven items fall into
# three content blocks that every published internal-structure study recovers,
# most recently Nunez et al. (2025) PeerJ, doi:10.7717/peerj.19620 (CC BY), PMC12255244:
#   {1,4} painful memories | {2,3} fear/control of feelings | {5,6,7} interference
# If the numbering is canonical, that partition should separate the observed
# correlation matrix better than any rival partition of the same 2-2-3 shape.
# There are 105 such partitions; a wrong numbering has no reason to put the
# canonical one on top.
#
# TEST 2 (routes 1 and 7, marker item). Item 4 is the least-endorsed AAQ-II item
# across samples -- it needs the highest trait level to endorse (Nunez et al.
# 2025; Ong et al. 2019), and in the CC BY item table of Langer et al. (2024),
# BMC Psychology, doi:10.1186/s40359-024-01608-w (PMC10908082), AAQ4 has the
# lowest mean of the seven (2.75) with AAQ1 next (3.04). If the numbering is
# canonical, aaq4 should be the lowest-mean item here too, aaq1 second lowest.
#
# WHAT THIS DOES NOT ESTABLISH: it pins the three blocks and, within the first
# block, which of the two is item 4. It does NOT separate aaq2 from aaq3, nor
# order aaq5/aaq6/aaq7 within their block -- their observed means differ by
# <= 0.09 at N ~ 57, which is noise. Hence PARTIAL, not VERIFIED, in
# verification_esiason_2024_aaqii.csv.

suppressMessages(library(readxl))

UA <- "IRW-Finder/1.0 (ben.domingue@gmail.com)"
URLS <- c(
  patient   = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0300777.s001",
  caregiver = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0300777.s002")
COLS <- paste0("aaq", 1:7)

grab <- function(u) {
    f <- tempfile(fileext = ".xlsx")
    utils::download.file(u, f, quiet = TRUE, mode = "wb",
                         headers = c("User-Agent" = UA))
    d <- as.data.frame(readxl::read_excel(f, skip = 1))
    d[COLS]
}
d <- do.call(rbind, lapply(URLS, grab))
d[] <- lapply(d, function(x) suppressWarnings(as.numeric(x)))
cat(sprintf("respondents: %d (patients + caregivers)\n\n", nrow(d)))

## ---- TEST 2: item means -------------------------------------------------
PUB <- c(3.04, 3.39, 3.91, 2.75, 3.37, 3.67, 3.53)   # Langer et al. 2024, BMC Psychology, Table 1
m <- colMeans(d, na.rm = TRUE)
cat("per-item means (observed here vs. published AAQ-II sample):\n")
cat(sprintf("%-6s %8s %10s %6s %6s\n", "item", "obs", "published", "rk_o", "rk_p"))
for (i in 1:7)
    cat(sprintf("%-6s %8.3f %10.2f %6d %6d\n", COLS[i], m[i], PUB[i],
                rank(m)[i], rank(PUB)[i]))
rho <- suppressWarnings(cor(m, PUB, method = "spearman"))
cat(sprintf("\nSpearman(observed means, published means) = %.3f\n", rho))
lowest_is_4 <- which.min(m) == 4
second_is_1 <- order(m)[2] == 1
cat(sprintf("lowest-mean item is aaq%d (predicted aaq4): %s\n", which.min(m), lowest_is_4))
cat(sprintf("second-lowest is aaq%d (predicted aaq1): %s\n", order(m)[2], second_is_1))

## ---- TEST 1: content-block partition ------------------------------------
C <- cor(d, use = "pairwise.complete.obs")
delta <- function(blocks) {
    w <- c(); b <- c()
    for (i in 1:6) for (j in (i + 1):7) {
        same <- any(vapply(blocks, function(bl) i %in% bl && j %in% bl, logical(1)))
        if (same) w <- c(w, C[i, j]) else b <- c(b, C[i, j])
    }
    c(delta = mean(w) - mean(b), within = mean(w), between = mean(b))
}
parts <- list()
for (three in combn(7, 3, simplify = FALSE)) {
    rest <- setdiff(1:7, three)
    for (two in combn(rest, 2, simplify = FALSE)) {
        key <- list(sort(three), sort(two), sort(setdiff(rest, two)))
        key <- key[order(vapply(key, function(z) z[1], numeric(1)))]
        tag <- paste(vapply(key, paste, character(1), collapse = ","), collapse = "|")
        parts[[tag]] <- key
    }
}
sc <- vapply(parts, function(p) delta(p)["delta"], numeric(1))
sc <- sort(sc, decreasing = TRUE)
canon <- "1,4|2,3|5,6,7"
cat(sprintf("\n%d partitions of shape 2-2-3; canonical AAQ-II content blocks = %s\n",
            length(sc), canon))
cat("top 3:\n")
for (i in 1:3) cat(sprintf("  %d. %-16s delta = %.4f\n", i, names(sc)[i], sc[i]))
rk <- match(canon, names(sc))
dd <- delta(parts[[canon]])
cat(sprintf("canonical rank: %d of %d  (within r = %.3f, between r = %.3f, delta = %.4f)\n",
            rk, length(sc), dd["within"], dd["between"], dd["delta"]))

cat("\nNot established by either test: aaq2 vs aaq3, and the order of aaq5/aaq6/aaq7\n")
cat("within their block (observed means differ by <= 0.09 at N ~ 57).\n\n")

ok <- rk == 1 && lowest_is_4 && second_is_1
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
