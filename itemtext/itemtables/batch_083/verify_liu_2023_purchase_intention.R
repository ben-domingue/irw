# verify_liu_2023_purchase_intention.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (mapping_basis = paper_order):
#   The item wording ships from S1 File (Annexure 1: Questionnaire items,
#   doi:10.1371/journal.pone.0295133.s002), which prints the 19 items in six
#   construct-headed blocks but NEVER prints the PI1/PI2/PI3 codes the data
#   uses. So the assignment
#       PI1 = "If I can, I would like to buy ..."
#       PI2 = "I would try to buy ..."
#       PI3 = "I would like to recommend ..."
#   rests on (a) the block heading "Purchase Intention toward agricultural
#   products' regional public brand" pinning WHICH three sentences belong to
#   the PI codes, and (b) the annexure's listing order pinning the order WITHIN
#   the block.
#
# This script tests (a) and the block-order premise behind (b). It does NOT
# test the within-block order -- nothing in the paper does, which is why the
# recorded status is PARTIAL, not VERIFIED.
#
# Checks:
#   A. The live IRW table's PI1/PI2/PI3 columns are cell-for-cell identical to
#      the deposit workbook's PI1/PI2/PI3 columns (ties the live code to the
#      source column end to end; the processing script melts by name).
#   B. Cronbach's alpha of the live PI block = the paper's published PI alpha
#      (Table 2: 0.809). Computed on the deposit workbook for all six blocks,
#      the same partition reproduces all six published alphas in the paper's
#      stated order -- i.e. the annexure's block sequence and sizes
#      (BT 4, ATT 3, SN 3, PBC 3, PI 3, PB 3) are the workbook's column
#      sequence, which is what licenses reading the PI heading onto PI1-PI3.
#   C. Discriminant check: each PI item correlates more with the other two PI
#      items than with any other construct's items.

suppressMessages(library(irw))

TABLE <- "liu_2023_purchase_intention"
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
live <- W[, blocks$PI]
dep  <- raw[order(raw$id), blocks$PI]
same <- all(mapply(function(a, b) identical(as.numeric(a), as.numeric(b)),
                   live, dep))
cat(sprintf("\nA. live PI columns vs deposit PI columns: %d x %d, identical = %s\n",
            nrow(live), ncol(live), same))

## --- B. alphas ---------------------------------------------------------------
cat("\nB. Cronbach's alpha by construct block (deposit workbook), vs paper Table 2\n")
cat(sprintf("%-5s %10s %10s %8s\n", "block", "published", "observed", "diff"))
obs_a <- sapply(blocks, function(cs) alpha(raw[, cs]))
for (b in names(blocks))
    cat(sprintf("%-5s %10.3f %10.3f %8.4f\n",
                b, PUB_ALPHA[[b]], obs_a[[b]], obs_a[[b]] - PUB_ALPHA[[b]]))
a_live <- alpha(live)
cat(sprintf("PI alpha computed on the LIVE IRW table: %.3f (published 0.809)\n", a_live))
worst <- max(abs(obs_a[names(PUB_ALPHA)] - PUB_ALPHA))

## --- C. discriminant ---------------------------------------------------------
cat("\nC. mean correlation of each PI item with its own block vs the best rival block\n")
R <- cor(raw[, unlist(blocks)], use = "complete.obs")
ok_disc <- TRUE
for (it in blocks$PI) {
    within <- mean(R[it, setdiff(blocks$PI, it)])
    rivals <- sapply(setdiff(names(blocks), "PI"),
                     function(b) mean(R[it, blocks[[b]]]))
    cat(sprintf("  %-4s within-PI %.3f | best rival %s %.3f\n",
                it, within, names(which.max(rivals)), max(rivals)))
    ok_disc <- ok_disc && within > max(rivals)
}

## --- what this does NOT establish -------------------------------------------
cat("\nNOT ESTABLISHED: the order WITHIN the PI block. The three live items are\n",
    "statistically near-identical -- means ",
    paste(sprintf("%.2f", sapply(live, mean, na.rm = TRUE)), collapse = " / "),
    " and SDs ",
    paste(sprintf("%.2f", sapply(live, sd, na.rm = TRUE)), collapse = " / "),
    " -- and the paper publishes no per-item means, SDs or wording-keyed\n",
    "statistics, only CFA loadings keyed to the CODES (PI1 .801, PI2 .738,\n",
    "PI3 .757), which say nothing about which sentence is which. So\n",
    "PI1/PI2/PI3 = annexure sentences 1/2/3 rests on the S1 File listing order\n",
    "alone. Status is PARTIAL.\n", sep = "")

cat(if (same && worst <= TOL && ok_disc) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
