# verify_liu_2023_brand_trust.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (mapping_basis = paper_order):
#   Item wording ships from S1 File (Annexure 1: Questionnaire items,
#   doi:10.1371/journal.pone.0295133.s002), which prints the 19 items in six
#   construct-headed blocks but NEVER prints the BT1..BT4 codes the data uses.
#   So the assignment
#       BT1 = "... are trustworthy."
#       BT2 = "... quality ... is reliable."
#       BT3 = "... quality ... is stable."
#       BT4 = "The Hulunbuir's regional public brands keep promise ..."
#   rests on (a) the block heading "Brand trust toward agricultural products'
#   regional public brand" pinning WHICH four sentences are the BT codes, and
#   (b) the annexure's listing order pinning the order WITHIN the block.
#
# This script tests (a) and the block-order premise behind (b). It does NOT
# test the within-block order -- nothing in the paper does -- so the recorded
# status is PARTIAL, not VERIFIED.
#
# Checks:
#   A. Live BT1..BT4 are cell-for-cell identical to the deposit's BT1..BT4.
#   B. Cronbach's alpha by block on the deposit reproduces all six published
#      alphas (Table 2), and the live BT alpha = published 0.875; i.e. the
#      annexure's block sequence/sizes (BT 4, ATT 3, SN 3, PBC 3, PI 3, PB 3)
#      are the workbook's column sequence.
#   C. Each BT item correlates more with its own block than any rival block.

suppressMessages(library(irw))

TABLE <- "liu_2023_brand_trust"
XLSX  <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0295133.s001")

# Liu & Wang (2023) PLOS ONE, Table 2 (image table), Cronbach's alpha per
# construct, in the paper's own order: BT, ATT, SN, PBC, PI, PB.
PUB_ALPHA <- c(BT = 0.875, ATT = 0.798, SN = 0.810, PBC = 0.852,
               PI = 0.809, PB = 0.863)
TOL <- 0.002

alpha <- function(M) {
    M <- M[complete.cases(M), , drop = FALSE]
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}

blocks <- list(BT  = paste0("BT",  1:4), ATT = paste0("ATT", 1:3),
               SN  = paste0("SN",  1:3), PBC = paste0("PBC", 1:3),
               PI  = paste0("PI",  1:3), PB  = paste0("PB",  1:3))

## --- deposit workbook -------------------------------------------------------
tmp <- tempfile(fileext = ".xlsx")
download.file(XLSX, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
names(raw)[1] <- "id"
cat(sprintf("deposit S1 Data: %d rows x %d cols; column order: %s\n",
            nrow(raw), ncol(raw), paste(names(raw)[-1], collapse = " ")))

## --- A. live vs deposit, cell for cell --------------------------------------
d <- irw::irw_fetch(TABLE)
W <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(W) <- sub("^resp\\.", "", names(W))
W <- W[order(as.numeric(as.character(W$id))), ]
live <- W[, blocks$BT]
dep  <- raw[order(raw$id), blocks$BT]
same <- all(mapply(function(a, b) identical(as.numeric(a), as.numeric(b)),
                   live, dep))
cat(sprintf("\nA. live BT columns vs deposit BT columns: %d x %d, identical = %s\n",
            nrow(live), ncol(live), same))

## --- B. alphas ---------------------------------------------------------------
cat("\nB. Cronbach's alpha by construct block (deposit workbook), vs paper Table 2\n")
cat(sprintf("%-5s %10s %10s %8s\n", "block", "published", "observed", "diff"))
obs_a <- sapply(blocks, function(cs) alpha(raw[, cs]))
for (b in names(blocks))
    cat(sprintf("%-5s %10.3f %10.3f %8.4f\n",
                b, PUB_ALPHA[[b]], obs_a[[b]], obs_a[[b]] - PUB_ALPHA[[b]]))
a_live <- alpha(live)
cat(sprintf("BT alpha computed on the LIVE IRW table: %.3f (published 0.875)\n", a_live))
worst <- max(abs(obs_a[names(PUB_ALPHA)] - PUB_ALPHA))

## --- C. discriminant ---------------------------------------------------------
cat("\nC. mean correlation of each BT item with its own block vs the best rival block\n")
R <- cor(raw[, unlist(blocks)], use = "complete.obs")
ok_disc <- TRUE
for (it in blocks$BT) {
    within <- mean(R[it, setdiff(blocks$BT, it)])
    rivals <- sapply(setdiff(names(blocks), "BT"),
                     function(b) mean(R[it, blocks[[b]]]))
    cat(sprintf("  %-4s within-BT %.3f | best rival %s %.3f\n",
                it, within, names(which.max(rivals)), max(rivals)))
    ok_disc <- ok_disc && within > max(rivals)
}

## --- what this does NOT establish -------------------------------------------
cat("\nNOT ESTABLISHED: the order WITHIN the BT block. Live means ",
    paste(sprintf("%.2f", sapply(live, mean, na.rm = TRUE)), collapse = " / "),
    " (SDs ", paste(sprintf("%.2f", sapply(live, sd, na.rm = TRUE)), collapse = " / "),
    ") differ, but the paper publishes no per-item means or wording-keyed\n",
    "statistics -- only CFA loadings keyed to the CODES (BT1 .798, BT2 .853,\n",
    "BT3 .776, BT4 .768), which say nothing about which sentence is which.\n",
    "The article quotes one BT item ('... are trustworthy.') but ties it to no\n",
    "code. BT1..BT4 = annexure sentences 1..4 rests on listing order alone.\n",
    "Status is PARTIAL.\n", sep = "")

cat(if (same && worst <= TOL && abs(a_live - 0.875) <= TOL && ok_disc) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
