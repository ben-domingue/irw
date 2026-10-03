# verify_ritzel_2020_farmer_burden.R -- Step 5b mapping check (batch_437).
#
# Claim: item codes y1..y9, x1..x4 carry the content the paper's Table 2 assigns
# to them (Ritzel et al. 2020, PLOS ONE 10.1371/journal.pone.0241075), and the
# German wording/anchors shipped come from the matching questions of the study's
# own questionnaire (Mack, Stoinescu & Heitkaemper 2019, Agroscope Science 92,
# Anhang 1). Three checks, all against published numbers hard-coded below:
#   A. per-item mean and SD (1 dp) vs paper Table 2 -- distinguishes every
#      item except x1 (recoded 8->6 in the paper); x2 vs x4 tie on mean (4.6)
#      and are separated by SD (1.4 vs 1.3).
#   B. response-category percentages vs the Agroscope report's figures
#      (Abb 12 admin row for y1, Abb 16 for y3, Abb 20 for y4, Abb 21 for y5,
#      section 2.2 text for x1) -- pins the option<->resp order for y4, y5, x1
#      and pins y1 to the admin-activities row (not total / office rows).
#   C. keying: y6-y8 are administered POSITIVELY in German but stored in the
#      paper's negated direction; they must correlate + with y9 (feel restricted)
#      and - with x2/x3 (well informed). This is what justifies shipping their
#      German anchors reversed (1 = "sehr stark", 7 = "ueberhaupt nicht").
# Sample note: IRW/S1 has 802 respondents; paper/report describe 808, so small
# residuals (<~1 pp, <0.05 in 1-dp rounding) are expected.

suppressMessages(library(irw))
TABLE <- "ritzel_2020_farmer_burden"
d <- irw::irw_fetch(TABLE)
ok <- TRUE

# ---- A. Table 2 means/SDs --------------------------------------------------
pub <- data.frame(
  item = c("y1","y2","y3","y4","y5","y6","y7","y8","y9","x2","x3","x4"),
  mean = c(4.9, 5.2, 4.2, 2.0, 4.1, 4.4, 3.8, 4.3, 4.5, 4.6, 4.8, 4.6),
  sd   = c(1.6, 1.3, 1.5, 0.9, 1.2, 1.6, 1.6, 1.7, 1.9, 1.4, 1.3, 1.3))
cat("A. paper Table 2 vs live (1-dp rounding tolerance 0.05)\n")
cat(sprintf("%-4s %6s %8s %6s %8s\n", "item", "pubM", "liveM", "pubSD", "liveSD"))
for (i in seq_len(nrow(pub))) {
  r <- d$resp[d$item == pub$item[i]]
  m <- mean(r); s <- sd(r)
  hit <- abs(m - pub$mean[i]) <= 0.0501 && abs(s - pub$sd[i]) <= 0.0501
  if (!hit) ok <- FALSE
  cat(sprintf("%-4s %6.1f %8.3f %6.1f %8.3f %s\n", pub$item[i], pub$mean[i], m,
              pub$sd[i], s, if (hit) "" else "<-- MISMATCH"))
}
# any swap among the 12 would break A? count pairs whose (mean,sd) pub values coincide
pk <- paste(pub$mean, pub$sd)
cat(sprintf("distinct published (mean,sd) pairs: %d of %d\n", length(unique(pk)), nrow(pub)))
if (length(unique(pk)) != nrow(pub)) ok <- FALSE

# ---- B. category percentages vs Agroscope Science 92 figures ----------------
pct <- function(it, bins) {
  r <- d$resp[d$item == it]
  sapply(bins, function(b) 100 * mean(r %in% b))
}
cmp <- function(label, it, bins, published, tol = 1.2) {
  obs <- pct(it, bins)
  dev <- max(abs(obs - published))
  cat(sprintf("%-38s live %s | pub %s | max dev %.2f\n", label,
              paste(sprintf("%5.1f", obs), collapse = ""),
              paste(sprintf("%5.1f", published), collapse = ""), dev))
  dev <= tol
}
cat("\nB. response-category % vs Agroscope Science 92\n")
bB <- c(
  cmp("y1 vs Abb12 admin row (1-3/4/5-7)", "y1", list(1:3, 4, 5:7), c(19, 18, 63)),
  cmp("y3 vs Abb16 (1-2/3/4/5/6-7)", "y3", list(1:2, 3, 4, 5, 6:7), c(13, 21, 25, 18, 22)),
  cmp("y4 vs Abb20 (<2h,2-4,4-6,>6)", "y4", as.list(1:4), c(36, 40, 15, 9)),
  cmp("y5 vs Abb21 (6 bins)", "y5", as.list(1:6), c(0.8, 8.9, 23.4, 30.3, 19.6, 17.1)),
  cmp("x1 vs sec.2.2 text (8 levels)", "x1", as.list(1:8), c(6, 0.51, 5, 43, 20, 15, 7, 4)))
# y1 must NOT match the other two rows of Abb12 (total: 34/26/39, office: 25/21/54)
o1 <- pct("y1", list(1:3, 4, 5:7))
alt <- c(total = max(abs(o1 - c(34, 26, 39))), office = max(abs(o1 - c(25, 21, 54))))
cat(sprintf("y1 vs Abb12 total row max dev %.1f, office row max dev %.1f (must be large)\n",
            alt["total"], alt["office"]))
# reversing the y4/y5/x1 option order must break the match
rev_dev <- c(y4 = max(abs(rev(pct("y4", as.list(1:4))) - c(36, 40, 15, 9))),
             y5 = max(abs(rev(pct("y5", as.list(1:6))) - c(0.8, 8.9, 23.4, 30.3, 19.6, 17.1))),
             x1 = max(abs(rev(pct("x1", as.list(1:8))) - c(6, 0.51, 5, 43, 20, 15, 7, 4))))
cat(sprintf("reversed-order max dev: y4 %.1f, y5 %.1f, x1 %.1f (must be large)\n",
            rev_dev["y4"], rev_dev["y5"], rev_dev["x1"]))
if (!all(bB) || any(alt < 5) || any(rev_dev < 5)) ok <- FALSE

# ---- C. keying of y6-y8 ------------------------------------------------------
w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cc <- function(a, b) cor(w[[a]], w[[b]], use = "pairwise.complete.obs")
cat("\nC. keying of y6-y8 (administered positively, stored negated)\n")
kc <- c()
for (v in c("y6", "y7", "y8")) {
  r9 <- cc(v, "y9"); r2 <- cc(v, "x2"); r3 <- cc(v, "x3")
  cat(sprintf("%s: r(y9 restricted)=%+.2f  r(x2 informed)=%+.2f  r(x3 informed)=%+.2f\n", v, r9, r2, r3))
  kc <- c(kc, r9 > 0 && r2 < 0 && r3 < 0)
}
if (!all(kc)) ok <- FALSE

cat("\nNot established: x1's item identity rests on its unique 1-8 range and the\n",
    "education frequencies, not on Table 2 (paper collapses x1 to 6 levels, 3.6/1.2;\n",
    "live 8-level 4.60/1.51). y2 (Q1.6 'burden vs 5 years ago') is pinned by Table 2\n",
    "mean/SD only; the report prints no figure for Q1.6.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
