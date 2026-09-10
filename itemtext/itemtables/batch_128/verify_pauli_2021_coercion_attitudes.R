# verify_pauli_2021_coercion_attitudes.R
#
# CLAIM UNDER TEST (Step 5b). The item text shipped for coercion1..coercion15 is the
# per-variable label the study's own deposit carries for v6.1..v6.15, and the anchor
# words shipped for resp 0..5 run "fully disagree" (0) .. "fully agree" (5) -- i.e.
# the deposit codebook's direction, NOT the direction the paper's Methods states
# ("six-point approval scale ranging from 1 (= I fully agree) to 6 (= I don't agree
# at all)").
#
# Nothing here re-checks item/resp SETS -- validate_items.R did that. Three checks:
#
#  A. PROVENANCE OF THE LIVE TABLE. data/pauli_2021_ppos_d6.py melts the explicit
#     ordered list COERCION_COLS = v6.1..v6.15 and renames it coercion1..coercion15
#     (number-preserving), dropping the -99 sentinel. So if the live table really is
#     that melt of that file, per-item non-missing n and per-item observed min/max
#     must match the deposit column by column. A shifted or permuted column range
#     breaks it. On its own this pins 11 of 15 positions: n=329 is shared by items
#     2, 3 and 11 and n=324 by 5, 6 and 7, and only item 3 (min 1) and item 6
#     (max 4) are separated within their group by the range, so {2,11} and {5,7}
#     are NOT separated by this check. The complete tie is the codebook label plus
#     the script's explicit list; this is corroboration that the live data came
#     from that file.
#
#  B. ITEM CONTENT vs POLARITY PARTITION. The paper reports Cronbach's alpha = .778
#     for the 15-item index after "recoding those items that were reversed in the
#     original scale". Reversing exactly the six critically-worded items -- 3, 4, 8,
#     13, 14, 15, which is what the SHIPPED TEXT says those items are -- reproduces
#     it. This breaks if item_text were permuted across the two polarity classes.
#
#  C. ANCHOR DIRECTION. Under the shipped anchors (5 = fully agree), "More coercion
#     should be used in treatment" (item 6) must sit near the disagree floor and
#     "Use of coercion is necessary as protection in dangerous situations" (item 1)
#     above the midpoint. Under the paper's stated direction both readings invert
#     and become implausible for first-semester medical students.
#
suppressMessages({library(irw); library(readxl)})

TABLE <- "pauli_2021_coercion_attitudes"
URL   <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8667738/supplementaryFiles"
MEMBER <- "peerj-09-12604-s003.xlsx"
CACHE <- file.path(".cache", TABLE, MEMBER)

if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    z <- tempfile(fileext = ".zip")
    utils::download.file(URL, z, quiet = TRUE, mode = "wb")
    utils::unzip(z, files = MEMBER, exdir = dirname(CACHE))
}
raw <- as.data.frame(readxl::read_excel(CACHE, sheet = "PPOS-D6 raw dataset2"))
cols <- paste0("v6.", 1:15)
src  <- raw[, cols]
src[src == -99] <- NA

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
pi <- pi[match(paste0("coercion", 1:15), pi$item), ]

cat("== A. deposit column vs live item: n, min, max ==\n")
cat(sprintf("%-11s %-6s %6s %6s %4s %4s %4s %4s  %s\n",
            "live", "src", "n_live", "n_src", "lmin", "smin", "lmax", "smax", "ok"))
okA <- TRUE
for (i in 1:15) {
    x <- src[[i]]
    n_src <- sum(!is.na(x)); smin <- min(x, na.rm = TRUE); smax <- max(x, na.rm = TRUE)
    ok <- (pi$n[i] == n_src) && (pi$resp_min[i] == smin) && (pi$resp_max[i] == smax)
    okA <- okA && ok
    cat(sprintf("%-11s %-6s %6d %6d %4d %4d %4d %4d  %s\n",
                pi$item[i], cols[i], pi$n[i], n_src, pi$resp_min[i], smin,
                pi$resp_max[i], smax, if (ok) "OK" else "MISMATCH"))
}
cat(sprintf("live total rows %d vs deposit non-missing cells %d\n",
            s$n_rows, sum(!is.na(src))))
okA <- okA && (s$n_rows == sum(!is.na(src)))

cat("\n== B. alpha of the index implied by the shipped item wording ==\n")
alpha <- function(X) {
    k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}
cc <- src[stats::complete.cases(src), ]
crit <- c(3, 4, 8, 13, 14, 15)          # the six critically-worded items, per shipped text
X <- cc
for (i in setdiff(1:15, crit)) X[[i]] <- 5 - X[[i]]
a_ship <- alpha(X)
# a deliberately wrong partition: the canonical 5-item "coercion as offending" set
X2 <- cc
for (i in setdiff(1:15, c(3, 4, 8, 13, 15))) X2[[i]] <- 5 - X2[[i]]
a_alt <- alpha(X2)
cat(sprintf("complete cases: %d\n", nrow(cc)))
cat(sprintf("published alpha (paper, Methods)          : %.3f\n", 0.778))
cat(sprintf("alpha, reverse {3,4,8,13,14,15} (shipped) : %.3f\n", a_ship))
cat(sprintf("alpha, reverse {3,4,8,13,15}   (rival)    : %.3f\n", a_alt))
okB <- abs(a_ship - 0.778) < 0.02 && a_ship > a_alt

cat("\n== C. anchor direction ==\n")
m <- colMeans(src, na.rm = TRUE)
cat(sprintf("item 6  'More coercion should be used in treatment.'                  mean %.2f (max observed %d)\n",
            m[6], max(src[[6]], na.rm = TRUE)))
cat(sprintf("item 1  'Use of coercion is necessary as protection in dangerous...'   mean %.2f\n", m[1]))
cat(sprintf("item 15 'Coercion could have been much reduced, giving more time...'   mean %.2f\n", m[15]))
cat("Shipped anchors put 0 = fully disagree, 5 = fully agree, so item 6 is the floor\n")
cat("and items 1/15 sit above the 2.5 midpoint. The paper's stated 1 = 'I fully agree'\n")
cat("direction inverts all three and is rejected.\n")
okC <- m[6] < 2.5 && m[1] > 2.5 && m[15] > 2.5

cat("\nNOT ESTABLISHED BY CHECK A: it leaves {coercion2, coercion11} and\n")
cat("{coercion5, coercion7} mutually unseparated. The complete item-level tie is the\n")
cat("deposit codebook's per-variable labels plus the processing script's explicit\n")
cat("v6.1..v6.15 list (mapping_basis = data_labels), which A and B corroborate.\n\n")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
