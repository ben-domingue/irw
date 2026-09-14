# verify_simsalRbim_Mice_LargeValence.R
#
# What is at stake. item_text and option_text are blank by design (subjects are
# mice; the "items" are liquids in a two-bottle test and no wording exists), so
# the only mapping claims this table makes are:
#   (1) each item code names the liquid it looks like (AlmondMilk, AppleJuice,
#       HCl, quinine, water) -- i.e. data/simsalRbim.R paired optionA with
#       quantityA and optionB with quantityB, so each count sits under the
#       liquid it was recorded for; and
#   (2) resp is that liquid's count of corner visits with licks, higher =
#       preferred (the shipped `instructions` quote the paper saying so).
# A swap of two codes, or a crossed A/B pairing, would break both checks below.
#
# Check A: per-item n / sum / sum of squares, hard-coded from the source file
#   github.com/mytalbot/simsalRbim_data Mice_LargeValence.txt
#   (sha256 4a6507b22c7bd6c8003ce89641e31f2e16fc986b7c61532da77ba972684b9a1f),
#   computed as optionA->quantityA, optionB->quantityB.
# Check B: within each `trial` (one binary test = 2 rows), share of tests each
#   liquid "won" (more licked visits than its partner). Pfefferle et al. (2025)
#   Behav Res Methods 57:193 report for the high-valence mouse set: almond milk
#   most preferred, followed by apple juice; quinine and HCl avoided; HCl at
#   rank 4 (Fig. 3). So the predicted order is
#   AlmondMilk > AppleJuice > water > HCl > quinine.

suppressMessages(library(irw))
TABLE <- "simsalRbim_Mice_LargeValence"
pass <- TRUE

d <- as.data.frame(irw::irw_fetch(TABLE))
cat("live rows:", nrow(d), "\n\n")

RAW <- data.frame(item = c("AlmondMilk", "AppleJuice", "HCl", "quinine", "water"),
                  n    = c(88, 88, 88, 88, 88),
                  sum  = c(3504, 3360, 1031, 228, 2027),
                  ss   = c(174998, 175056, 43167, 5222, 74407))

cat("=== A. per-item stats: source file vs live ===\n")
obs <- do.call(rbind, lapply(RAW$item, function(i) {
    r <- d$resp[d$item == i]
    data.frame(item = i, n = length(r), sum = sum(r), ss = sum(r^2))
}))
cmp <- merge(RAW, obs, by = "item", suffixes = c("_raw", "_live"))
print(cmp, row.names = FALSE)
okA <- with(cmp, all(n_raw == n_live & sum_raw == sum_live & ss_raw == ss_live))
cat("exact match:", okA, "\n")
# how many of the 120 relabellings of the 5 codes reproduce the source sums?
perms <- function(v) if (length(v) <= 1) list(v) else
    do.call(c, lapply(seq_along(v), function(k) lapply(perms(v[-k]), function(p) c(v[k], p))))
P <- perms(1:5)
nA <- sum(sapply(P, function(p) all(RAW$sum[p] == obs$sum & RAW$ss[p] == obs$ss)))
cat("relabellings reproducing source sums+ss:", nA, "of", length(P), "(1 = only the shipped one)\n\n")
pass <- pass && okA && nA == 1

cat("=== B. within-test win share vs the paper's ranking ===\n")
tr <- split(d, d$trial)
sizes <- sapply(tr, nrow)
cat("trials:", length(tr), "| rows per trial:", paste(unique(sizes), collapse = ","), "\n")
pass <- pass && all(sizes == 2) && all(sapply(tr, function(t) length(unique(t$item)) == 2))
w <- do.call(rbind, lapply(tr, function(t) data.frame(item = t$item,
                                                      win = t$resp > rev(t$resp))))
ws <- tapply(w$win, w$item, mean)
ws <- sort(ws, decreasing = TRUE)
print(round(ws, 3))
PAPER <- c("AlmondMilk", "AppleJuice", "water", "HCl", "quinine")
okB <- identical(names(ws), PAPER)
cat("observed order:", paste(names(ws), collapse = " > "), "\n")
cat("paper order:   ", paste(PAPER, collapse = " > "), "\n")
cat("match:", okB, "\n")
gap <- min(-diff(as.numeric(ws)))
cat(sprintf("smallest gap between adjacent win shares: %.3f (>0 means the order is strict,\n", gap),
    "so exactly 1 of the 120 relabellings matches the paper order)\n", sep = "")
pass <- pass && okB && gap > 0

cat("\nNOT established: the paper's worth values / consensus error (16.36%) were not\n",
    "recomputed (simsalRbim is GitHub-only); the paper's rank order is a text claim\n",
    "(almond milk first, apple juice second, HCl fourth, quinine/HCl avoided), and\n",
    "water-3 / quinine-5 is inferred from it. Check A is what separates every code\n",
    "from every other exactly.\n", sep = "")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
