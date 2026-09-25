# verify_liu_2023_subjective_norm.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST (mapping_basis = paper_order): the three sentences shipped as item_text
# are the S1 File (pone.0295133.s002) "Subjective Norm toward agricultural products'
# regional public brand" block, assigned to SN1..SN3 in listing order. The IRW code IS the
# S1 Data (.s001 xlsx) column name (data/liu_2023_brand_trust.py selects ^SN\d+$ by name and
# melts), and the annex prints the block under its construct heading without codes. Links:
#   (a) block: live SN columns = the paper's Subjective Norm construct = the annex SN block;
#   (b) order: SN1/2/3 = the 1st/2nd/3rd sentence of that block.
#
# ROUTE 3 (published construct statistics) + Table 5 structural paths, for link (a).
# Liu & Wang (2023) PLOS ONE e0295133. Table 2 prints per-construct alpha / CR / AVE;
# Table 5 prints the standardized SEM paths. Refitting the paper's model must reproduce
# both, with the SN block landing on the published Subjective Norm row and nowhere else.
#
# Data: the live SN table is fetched from IRW (544 x 3, tiny) and checked cell-for-cell
# against the deposit's SN columns; the other five constructs (needed to refit the model)
# come from the deposit's S1 Data workbook, which is what the IRW sibling tables were
# built from.
#
# WHAT THIS DOES NOT ESTABLISH: link (b). The annex's three SN sentences are unnumbered and
# the paper publishes no wording-keyed per-item statistic (its per-item loadings are keyed to
# codes, and are in any case printed one row-block off -- the published "ATT1-3" loadings
# are the data's SN loadings). Order within the block rests on listing order. PARTIAL.

suppressMessages(library(irw))
suppressMessages(library(lavaan))
suppressMessages(library(readxl))

TABLE <- "liu_2023_subjective_norm"
live <- as.data.frame(irw::irw_fetch(TABLE)[, c("id", "item", "resp")])
lw <- reshape(live, idvar = "id", timevar = "item", direction = "wide")
names(lw) <- sub("^resp\\.", "", names(lw))

tf <- tempfile(fileext = ".xlsx")
download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0295133.s001",
              tf, mode = "wb", quiet = TRUE)
w <- as.data.frame(readxl::read_excel(tf))
idcol <- if ("id" %in% names(w)) "id" else names(w)[1]
w$id <- w[[idcol]]

m <- merge(lw, w[, c("id", "SN1", "SN2", "SN3")], by = "id", suffixes = c(".live", ".dep"))
same <- sapply(1:3, function(i) sum(m[[paste0("SN", i, ".live")]] == m[[paste0("SN", i, ".dep")]], na.rm = TRUE))
cat(sprintf("live SN rows %d; deposit rows %d; matched ids %d; identical cells SN1/SN2/SN3 = %s\n\n",
            nrow(lw), nrow(w), nrow(m), paste(same, collapse = "/")))
same_ok <- nrow(m) == nrow(lw) && all(same == nrow(m))
# refit on the live SN values
w <- merge(w[, setdiff(names(w), c("SN1", "SN2", "SN3"))], lw, by = "id")

cat("per-item descriptives (live SN)\n")
for (v in c("SN1", "SN2", "SN3"))
    cat(sprintf("  %s mean %.3f  sd %.3f  %%at5 %.1f\n", v, mean(w[[v]]), sd(w[[v]]), 100 * mean(w[[v]] == 5)))
cat("\n")

bl <- list(BT = paste0("BT", 1:4), ATT = paste0("ATT", 1:3), SN = paste0("SN", 1:3),
           PBC = paste0("PBC", 1:3), PI = paste0("PI", 1:3), PB = paste0("PB", 1:3))
meas <- paste(sapply(names(bl), function(k) paste0(k, " =~ ", paste(bl[[k]], collapse = " + "))),
              collapse = "\n")
f <- lavaan::sem(paste0(meas, "\nATT ~ BT + SN\nPI ~ BT + ATT + SN + PBC\nPB ~ BT + PI\n"), data = w)
ss <- lavaan::standardizedSolution(f)
L <- ss[ss$op == "=~", ]

alpha <- function(v) { k <- length(v); S <- cov(w[, v]); k / (k - 1) * (1 - sum(diag(S)) / sum(S)) }
obs <- t(sapply(names(bl), function(k) {
    l <- L$est.std[L$lhs == k]
    c(alpha = alpha(bl[[k]]), CR = sum(l)^2 / (sum(l)^2 + sum(1 - l^2)), AVE = mean(l^2))
}))
PUB <- rbind(BT = c(0.875, 0.876, 0.639), ATT = c(0.798, 0.799, 0.571),
             SN = c(0.810, 0.812, 0.591), PBC = c(0.852, 0.853, 0.660),
             PI = c(0.809, 0.809, 0.586), PB = c(0.863, 0.867, 0.687))

cat("ROUTE 3 -- live SN block (alpha, CR, AVE) against every published construct row\n")
cat(sprintf("  live SN: alpha %.3f  CR %.3f  AVE %.3f\n", obs["SN", 1], obs["SN", 2], obs["SN", 3]))
dev <- apply(PUB, 1, function(p) max(abs(obs["SN", ] - p)))
for (k in rownames(PUB))
    cat(sprintf("  vs published %-4s %.3f/%.3f/%.3f  max|diff| %.4f\n", k, PUB[k, 1], PUB[k, 2], PUB[k, 3], dev[k]))
best <- names(which.min(dev))
cat(sprintf("  best match: %s (%.4f); runner-up %s (%.4f)\n\n", best, min(dev),
            names(sort(dev))[2], sort(dev)[2]))

cat("Table 5 standardized paths (published vs live)\n")
PATHS <- data.frame(lhs = c("ATT", "PI", "PB", "PI", "ATT", "PI", "PI", "PB"),
                    rhs = c("BT", "BT", "BT", "ATT", "SN", "SN", "PBC", "PI"),
                    pub = c(0.428, 0.194, 0.417, 0.329, 0.342, 0.057, 0.373, 0.293))
R <- ss[ss$op == "~", ]
PATHS$obs <- sapply(seq_len(nrow(PATHS)), function(i)
    R$est.std[R$lhs == PATHS$lhs[i] & R$rhs == PATHS$rhs[i]])
for (i in seq_len(nrow(PATHS)))
    cat(sprintf("  %-3s -> %-3s  pub %.3f  live %.3f  diff %+.4f\n", PATHS$rhs[i], PATHS$lhs[i],
                PATHS$pub[i], PATHS$obs[i], PATHS$obs[i] - PATHS$pub[i]))
pdev <- max(abs(PATHS$obs - PATHS$pub))
cat(sprintf("  largest path deviation: %.4f\n\n", pdev))

cat("Block membership: each SN item's mean |r| with its own block vs best rival block\n")
C <- cor(w[, unlist(bl)])
for (v in bl$SN) {
    own <- mean(C[v, setdiff(bl$SN, v)])
    riv <- sapply(setdiff(names(bl), "SN"), function(k) mean(C[v, bl[[k]]]))
    cat(sprintf("  %s own %.3f  best rival %s %.3f\n", v, own, names(which.max(riv)), max(riv)))
}
cat("\n")

cat("SOURCE DEFECT -- Table 2 per-item loadings vs live loadings (3-item TPB blocks)\n")
PUBL <- list(ATT = c(0.742, 0.755, 0.807), SN = c(0.785, 0.838, 0.813), PBC = c(0.743, 0.796, 0.726))
for (k in names(PUBL)) {
    mm <- sapply(c("ATT", "SN", "PBC"), function(j) max(abs(L$est.std[L$lhs == j] - PUBL[[k]])))
    cat(sprintf("  published %-3s row %s -> matches live %s (max|diff| %.4f)\n", k,
                paste(sprintf("%.3f", PUBL[[k]]), collapse = "/"), names(which.min(mm)), min(mm)))
}
cat(sprintf("  live SN loadings: %s\n\n", paste(sprintf("%.3f", L$est.std[L$lhs == "SN"]), collapse = "/")))

cat("SCOPE. Establishes that live SN1-SN3 are the paper's Subjective Norm construct, so the annex's\n")
cat("Subjective Norm block is the right three sentences. Does NOT establish which sentence is SN1 vs\n")
cat("SN2 vs SN3: that rests on listing order. PARTIAL.\n")
# Separation: the published PI row (0.809/0.809/0.586) sits close to SN (0.810/0.812/0.591),
# so construct stats alone separate SN from PI by a factor (~6x), not by a wide margin; the
# Table 5 paths (all 8 within 0.0005, incl. SN->ATT 0.342 and SN->PI 0.057) are what make
# a SN/PI label swap untenable. Threshold: best == SN, <= 0.002, runner-up >= 3x best.
ok <- same_ok && best == "SN" && min(dev) <= 0.002 && sort(dev)[2] >= 3 * min(dev) && pdev <= 0.005
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
