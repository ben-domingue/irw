# verify_pks_probability.R -- Step 5b mapping check for pks_probability (batch_430).
#
# Claim: IRW item bNNN carries the text the pks manual prints for problem pNNN.
# The pks 'probability' data ship BOTH the raw numeric answer each respondent gave
# (p101..p212) and the scored item (b101..b212, 1 = correct, 0 = error). Rescoring
# each raw-answer column pNNN against the correct answer the manual prints under
# that problem's wording must reproduce exactly one scored column -- bNNN -- and
# the live IRW table must be that scored column. If item_text for two problems
# were swapped, their keys would score the wrong raw column and agreement drops.
#
# Route: implied-parameter / rescoring (route 4) + live-vs-source reproduction.

suppressMessages({ library(irw); library(pks) })
data(probability); x <- probability
TABLE <- "pks_probability"
items <- c(sprintf("b1%02d", 1:12), sprintf("b2%02d", 1:12))
praw  <- sub("^b", "p", items)

# Keys as printed in the pks manual (Rd 'probability', pks 0.8.0) under each problem.
KEY <- c(p101=.40,p102=.65,p103=.55,p104=.32,p105=.75,p106=.80,p107=.70,p108=.50,
         p109=NA, p110=NA, p111=.12,p112=.48,p201=.20,p202=.75,p203=.80,p204=.07,
         p205=.75,p206=.70,p207=.80,p208=.50,p209=NA, p210=.12,p211=.28,p212=.15)
score <- function(j) {
  p <- x[[j]]
  if (j %in% c("p109","p209")) return(as.numeric(round(p, 2) == 0.06))   # "round to 0.06"
  if (j == "p110") return(as.numeric(abs(p - ifelse(x$mode == "lab", .28, .12)) < 1e-9)) # 0.12, lab: 0.28
  as.numeric(abs(p - KEY[[j]]) < 1e-9)
}
S <- sapply(praw, score)

# 1. live IRW table == package b columns (id = row index in data(probability))
d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[!is.na(d$resp), ]
live_ok <- sapply(items, function(i) { r <- d[d$item == i, ]; all(r$resp == x[as.integer(r$id), i]) })
cat(sprintf("live vs package b-columns: %d/24 items identical cell-for-cell (%d non-missing cells)\n",
            sum(live_ok), nrow(d)))

# 2. 24 x 24 agreement: rescored pNNN (columns) vs scored bMMM (rows)
A <- sapply(praw, function(j) sapply(items, function(i) {
  ok <- !is.na(S[, j]) & !is.na(x[[i]]); mean(S[ok, j] == x[[i]][ok]) }))
cat(sprintf("\n%-6s %8s %18s\n", "item", "own key", "best other problem"))
for (k in 1:24) {
  o <- A[k, -k]; cat(sprintf("%-6s %8.3f %12s %.3f\n", items[k], A[k, k], names(o)[which.max(o)], max(o)))
}
diag_exact <- all(abs(diag(A) - 1) < 1e-12)
unique_row <- all(sapply(1:24, function(k) A[k, k] > max(A[k, -k])))
unique_col <- all(sapply(1:24, function(k) A[k, k] > max(A[-k, k])))
cat(sprintf("\nown-key agreement exactly 1 for all 24: %s; max off-diagonal %.3f\n", diag_exact, max(A[row(A) != col(A)])))
cat(sprintf("own key is the unique best match in every row: %s, every column: %s\n", unique_row, unique_col))

# p110 two-wording check: the online key alone fails the lab respondents
lab <- x$mode == "lab"
cat(sprintf("p110: online key 0.12 reproduces b110 for lab %d/%d, lab key 0.28 for lab %d/%d; lab = ids %s\n",
    sum(as.numeric(abs(x$p110[lab]-.12)<1e-9) == x$b110[lab], na.rm = TRUE), sum(lab),
    sum(as.numeric(abs(x$p110[lab]-.28)<1e-9) == x$b110[lab], na.rm = TRUE), sum(lab),
    paste(range(which(lab)), collapse = "-")))
cat("Note: this pins every problem's key/wording to its own code; it cannot distinguish two\n",
    "problems with identical wording, of which there are none.\n", sep = "")

cat(if (all(live_ok) && diag_exact && unique_row && unique_col) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
