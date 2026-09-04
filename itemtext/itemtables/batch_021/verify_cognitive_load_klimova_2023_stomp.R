# verify_cognitive_load_klimova_2023_stomp.R
#
# STATUS: this table is BLOCKED -- no __items.csv was written. The only deposit
# (openICPSR 194063 v2, doi:10.3886/E194063V2) is Cloudflare-403 to every automated
# route and additionally login-gated, and the journal article (Field Methods 38(1):
# 46-61, doi:10.1177/1525822x251344709) is closed access with no repository copy.
# The 18 item codes are STOMPCONTRa..i / STOMPEXPa..i; the letters encode nothing,
# so even the canonical Short Test of Music Preferences (14 genres, STOMP-R 23,
# against 9 here, and administered in Russian) could not be tied to them.
#
# There is therefore no item_text<->item mapping to verify, and mapping_verification
# records status=NO_ROUTE. What this script re-runs is the weaker set of structural
# claims the block note actually makes about the live data:
#
#   (A) CONTR/EXP is the study's between-subjects labelling arm -- no id appears in
#       both arms.
#   (B) letter x denotes the SAME item in both arms -- each CONTR letter's response
#       distribution should match its own EXP letter better than any other letter's.
#   (C) resp = 6 behaves like an off-scale category, not the top of a 6-point
#       preference scale -- it is rare or absent per item while 1..5 are populated.
#
# PASS here means those three structural claims reproduce. It does NOT mean any
# item text was verified: none was shipped.

suppressMessages(library(irw))

TABLE <- "cognitive_load_klimova_2023_stomp"
d <- as.data.frame(irw::irw_fetch(TABLE))
stopifnot(nrow(d) > 0)

d$arm    <- ifelse(grepl("^STOMPCONTR", d$item), "CONTR", "EXP")
d$letter <- sub("^STOMP(CONTR|EXP)", "", d$item)
letters9 <- sort(unique(d$letter))

# ---- (A) arms are disjoint by id -------------------------------------------
per_id  <- tapply(d$arm, d$id, function(x) length(unique(x)))
n_both  <- sum(per_id > 1)
cat("(A) ids:", length(per_id),
    "| CONTR rows:", sum(d$arm == "CONTR"),
    "| EXP rows:", sum(d$arm == "EXP"),
    "| ids in BOTH arms:", n_both, "\n")

# ---- (B) same letter = same item across arms -------------------------------
# Means alone are too coarse here (five of the nine letters have CONTR means within
# 0.6 of each other), so the comparison is the full response-frequency profile over
# resp 1..6, matched by total variation distance.
prof <- function(a) {
  t(sapply(letters9, function(L) {
    x <- factor(d$resp[d$letter == L & d$arm == a], levels = 1:6)
    as.numeric(table(x)) / sum(table(x))
  }))
}
A <- prof("CONTR"); B <- prof("EXP")
rownames(A) <- rownames(B) <- letters9
TV <- outer(seq_along(letters9), seq_along(letters9),
            Vectorize(function(i, j) 0.5 * sum(abs(A[i, ] - B[j, ]))))
dimnames(TV) <- list(letters9, letters9)

cat("\n(B) total variation distance, CONTR letter (rows) vs EXP letter (cols)\n")
print(round(TV, 3))
own  <- diag(TV)
offd <- TV[row(TV) != col(TV)]
wins <- sum(sapply(seq_along(letters9), function(i) which.min(TV[i, ]) == i))
cat(sprintf("own-letter TVD %.3f-%.3f (mean %.3f); cross-letter TVD %.3f-%.3f (mean %.3f)\n",
            min(own), max(own), mean(own), min(offd), max(offd), mean(offd)))
cat(sprintf("identity is the closest EXP letter for %d of %d letters; the %d misses lose by <= %.3f\n",
            wins, length(letters9), length(letters9) - wins,
            max(c(0, sapply(seq_along(letters9), function(i)
              if (which.min(TV[i, ]) == i) 0 else own[i] - min(TV[i, ]))))))

set.seed(1)
perm_sums <- replicate(20000, sum(TV[cbind(seq_along(letters9), sample(length(letters9)))]))
cat(sprintf("total TVD under identity %.3f; 20,000 random pairings mean %.3f, min %.3f; p = %.5f\n",
            sum(own), mean(perm_sums), min(perm_sums),
            (1 + sum(perm_sums <= sum(own))) / (1 + length(perm_sums))))

# ---- (C) resp = 6 is an off-scale category ---------------------------------
tab <- table(d$item, d$resp)
cat("\n(C) count of resp==6 per item (out of that item's n)\n")
n6 <- tab[, "6"]
ni <- rowSums(tab)
for (i in seq_along(n6))
  cat(sprintf("%-13s %3d / %3d\n", rownames(tab)[i], n6[i], ni[i]))
cat(sprintf("resp==6 used %d-%d times per item (%d items never use it); resp 1-5 min per-item count %d\n",
            min(n6), max(n6), sum(n6 == 0), min(tab[, c("1","2","3","4","5")])))
share6 <- sum(n6) / sum(ni)
cat(sprintf("overall share of resp==6: %.3f\n", share6))

cat("\nWHAT THIS DOES NOT ESTABLISH: which genre (or any wording) letter a..i refers to,\n",
    "the response-option wording, the direction of the 1-5 scale, or the meaning of code 6.\n",
    "No item text was shipped for this table; mapping status is NO_ROUTE.\n", sep = "")

ok <- n_both == 0 &&
      wins >= 6 &&
      mean(own) < 0.5 * mean(offd) &&
      max(n6) < min(ni) / 4 &&
      share6 < 0.10
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
