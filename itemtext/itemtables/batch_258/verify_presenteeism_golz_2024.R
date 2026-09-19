# verify_presenteeism_golz_2024.R -- Step 5b mapping check (batch_258).
#
# Claim: live var1..var6 = Golz et al. (2024, J Occup Rehabil 34:863-872, PMC11550221)
# Table 3 items 1..6 in order, and live resp 6 = "I was not ill" (the paper prints that
# option as 0; the OSF data.csv and the live table store it as 6).
#
# Route 1 (per-item descriptives). The paper excluded the 163 respondents who answered
# "not ill" and reports Table 3 on the remaining 324 (pairwise per item). Reproducing
# that subset from the live table requires resp 6 to be the "not ill" code: the count of
# respondents with any 6 must equal 163, and per-item M/SD on the rest must match
# Table 3. Items 1, 4 and 5 have near-tied means (2.64 / 2.60 / 2.63); their SDs
# (1.12 / 1.25 / 1.33) separate them, so M+SD jointly distinguish all six items.
# Also checks that all 15 pairwise swaps of the mapping fail.
suppressMessages(library(irw))
TABLE <- "presenteeism_golz_2024"
PUB_M  <- c(2.64, 2.11, 2.25, 2.60, 2.63, 2.72)
PUB_SD <- c(1.12, 1.20, 1.19, 1.25, 1.33, 1.24)
TOL <- 0.015

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
v <- w[, paste0("var", 1:6)]
anysix <- apply(v == 6, 1, function(r) any(r %in% TRUE))
cat(sprintf("respondents in live table: %d; with any resp==6: %d (paper: 163 'not ill' excluded)\n",
            nrow(v), sum(anysix)))
s <- v[!anysix, ]
cat(sprintf("remaining: %d (paper: 324)\n\n", nrow(s)))
m <- colMeans(s, na.rm = TRUE); sd <- apply(s, 2, sd, na.rm = TRUE)
cat(sprintf("%-6s %8s %8s %8s %8s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD"))
for (i in 1:6) cat(sprintf("%-6s %8.2f %8.3f %8.2f %8.3f\n", names(m)[i], PUB_M[i], m[i], PUB_SD[i], sd[i]))
ok_main <- all(abs(m - PUB_M) <= TOL & abs(sd - PUB_SD) <= TOL)

# every pairwise swap of the mapping must fail on M or SD
swaps_ok <- 0; n_sw <- 0
for (a in 1:5) for (b in (a + 1):6) {
  p <- 1:6; p[c(a, b)] <- p[c(b, a)]; n_sw <- n_sw + 1
  if (all(abs(m[p] - PUB_M) <= TOL & abs(sd[p] - PUB_SD) <= TOL)) swaps_ok <- swaps_ok + 1
}
cat(sprintf("\npairwise swaps that would also match: %d of %d\n", swaps_ok, n_sw))
cat("Does NOT establish: the wording of an overall instruction/recall stem (the paper prints none).\n")
cat(if (ok_main && swaps_ok == 0 && sum(anysix) == 163 && nrow(s) == 324) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
