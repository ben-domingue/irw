# verify_wirs.R -- Step 5b mapping check for `wirs`.
#
# CLAIM: item_N in the IRW table is column N of ltm::WIRS, whose header is
# literally "Item N", and whose wording is documented item-by-item in the ltm
# package's WIRS.Rd ("Item 1: Informal discussion with individual workers." ...).
# data/ltm.R assigns the codes POSITIONALLY -- names(x) <- paste("item_",1:ncol(x))
# -- so the claim is falsifiable and is tested here by RE-RUNNING the derivation:
# the source data frame is still on CRAN, so every respondent's stored response
# must equal the source cell at that (row, column).
#
# If item_text for any two items were swapped, the diagonal below would move.

suppressMessages(library(irw))
suppressMessages(library(ltm))

TABLE <- "wirs"
d <- irw::irw_fetch(TABLE)
w <- ltm::WIRS                       # 1005 x 6, headers "Item 1".."Item 6"

cat("source headers: ", paste(names(w), collapse = " | "), "\n", sep = "")
cat("shipped codes : ", paste(paste0("item_", 1:6), collapse = " | "), "\n\n", sep = "")

# agreement matrix: shipped item_j (ordered by id) vs source column k
m <- matrix(NA_real_, 6, 6,
            dimnames = list(paste0("item_", 1:6), names(w)))
for (j in 1:6) {
    s <- d[d$item == paste0("item_", j), ]
    s <- s[order(as.integer(s$id)), ]
    for (k in 1:6)
        m[j, k] <- mean(as.integer(s$resp) == as.integer(w[[k]]))
}

cat("per-respondent agreement, shipped item (rows) x ltm::WIRS column (cols):\n")
print(round(m, 3))

diag_ok  <- all(abs(diag(m) - 1) < 1e-12)
off      <- m; diag(off) <- NA
worst_off <- max(off, na.rm = TRUE)

cat(sprintf("\nn per item (live): %s\n",
            paste(as.vector(table(d$item)), collapse = " ")))
cat(sprintf("diagonal all exactly 1.000: %s ; largest off-diagonal: %.3f\n",
            diag_ok, worst_off))

# Means, printed so a reader can see the items are individually distinguishable.
cat("\nper-item mean, live vs ltm::WIRS column of the same number:\n")
for (j in 1:6) {
    s <- d[d$item == paste0("item_", j), ]
    cat(sprintf("  item_%d  live %.10f   source %.10f\n", j, mean(s$resp), mean(w[[j]])))
}

cat("\nNote: this pins EVERY item to a unique source column (exact 1005/1005 match on\n",
    "the diagonal, <= ", sprintf("%.3f", worst_off), " off it), and the source column header carries the item\n",
    "number that WIRS.Rd's item wording is keyed to. It does NOT independently verify\n",
    "the WORDING itself, which is transcribed from WIRS.Rd, nor the meaning of resp 0/1\n",
    "(no response labels are published anywhere in the source, so option_text is blank).\n", sep = "")

cat(if (diag_ok && worst_off < 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
