# verify_enders_2022_victimhood.R -- Step 5b re-runnable check (batch_573)
#
# CLAIM. VICTIM_1..4 carry the S1 Appendix "Victimhood." statements 1..4 in printed order
# (Enders, Uscinski, Klofstad & Stoler 2022, PLOS ONE e0276082, pone.0276082.s001):
#   1 "I rarely get what I deserve in life."  2 "Great things never come to me."
#   3 "I usually have to settle for less."    4 "I never seem to get an extra break."
# and resp 1 = "strongly disagree", resp 5 = "strongly agree" (as the appendix prints).
#
# DERIVATION. data/enders_2022_conspiracy_vaccine.py keeps the Qualtrics names VICTIM_1..4
# (VICTIM_5, a constant embedded attention check, is dropped). Raw Data.csv has no
# question-text row and no codebook; the appendix numbers the statements but never names a
# code, so the wording->code tie is presentation order (mapping_basis = paper_order).
#
# ROUTE A (scale identity). Appendix: a=0.87, M=2.78, SD=0.97 (Analyses.do line 270,
#   alpha victim_1-victim_4, gen(victimhood) = row mean of available items).
# ROUTE B (resp direction). SI Table A2: Perceived Victimhood correlates +0.295 with beliefs in
#   COVID-19 misinformation and +0.281 with COVID-19 conspiracy beliefs. A reversed resp scale
#   would flip both signs.
# ROUTE C (item mapping, cross-sample, PARTIAL). The same four statements were fielded by
#   Armaly & Enders (2021, Political Behavior, doi 10.1007/s11109-020-09662-x) whose CC0
#   replication data (Harvard Dataverse doi:10.7910/DVN/9IZO5I, "25 March 2019.csv") holds them
#   as q2_1,q2_2,q2_3,q2_5. Their code->wording tie is pinned by (i) re-running their Table 1
#   two-factor CFA (published EGO loadings .803/.797/.736/.752, chi2(18)=40.58, n=1,012) and
#   (ii) their ESM Figure A2, whose histograms are labelled with the wording and whose bars
#   match the per-code % distributions printed below. Then all 24 assignments of the four
#   A&E-labelled statements to VICTIM_1..4 are scored on centred item means, one-factor
#   loadings and the 6 inter-item r (sum of squared differences). PASS needs the shipped
#   identity to rank 1 and the top 4 to be exactly the within-pair swaps of {1,2}|{3,4}.
#
# NOT ESTABLISHED: this is a cross-sample inference (2019 Lucid vs 2021 Qualtrics), not a
# label in the study's own files. It pins the partition {VICTIM_1,VICTIM_2} = {deserve, great
# things} vs {VICTIM_3,VICTIM_4} = {settle, extra break} by a wide margin, but the order WITHIN
# each pair wins only narrowly (see the printed runner-up totals).

suppressMessages({ library(irw); library(lavaan) })

wide <- function(tab) {
  d <- as.data.frame(irw::irw_fetch(tab))[, c("id", "item", "resp")]
  w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
  names(w) <- sub("^resp\\.", "", names(w)); w
}
V  <- paste0("VICTIM_", 1:4)
wv <- wide("enders_2022_victimhood")[, c("id", V)]
ok <- TRUE

# ---- Route A: scale totals ---------------------------------------------------------
X <- wv[, V]; Xc <- X[complete.cases(X), ]
k <- 4; R <- cor(Xc); alpha <- k * mean(R[upper.tri(R)]) / (1 + (k - 1) * mean(R[upper.tri(R)]))
S <- cov(Xc); alpha_raw <- k / (k - 1) * (1 - sum(diag(S)) / sum(S))
sc <- rowMeans(X, na.rm = TRUE); sc[is.nan(sc)] <- NA
cat(sprintf("Route A: alpha(raw) %.3f vs .87 | M %.3f vs 2.78 | SD %.3f vs 0.97 | n %d\n",
            alpha_raw, mean(sc, na.rm = TRUE), sd(sc, na.rm = TRUE), sum(!is.na(sc))))
ok <- ok && abs(alpha_raw - .87) < .006 && abs(mean(sc, na.rm = TRUE) - 2.78) < .006 &&
  abs(sd(sc, na.rm = TRUE) - .97) < .006
cat(sprintf("  reversed-scale mean would be %.3f\n", 6 - mean(sc, na.rm = TRUE)))

# ---- Route B: direction via SI Table A2 ---------------------------------------------
mis <- wide("enders_2022_covid_vax_misinfo"); cc <- wide("enders_2022_covid_conspiracy")
mm <- rowMeans(mis[, paste0("COVVAXINFO_", 1:5)], na.rm = TRUE)
cm <- rowMeans(cc[, paste0("COVCONS_", 2:7)], na.rm = TRUE)
d  <- merge(merge(data.frame(id = wv$id, vic = sc), data.frame(id = mis$id, mis = mm)),
            data.frame(id = cc$id, con = cm))
r1 <- cor(d$vic, d$mis, use = "pair"); r2 <- cor(d$vic, d$con, use = "pair")
cat(sprintf("Route B: r(victimhood, misinformation) %+.3f vs +0.295 | r(victimhood, COVID CT) %+.3f vs +0.281\n", r1, r2))
ok <- ok && abs(r1 - .295) < .01 && abs(r2 - .281) < .01

# ---- Route C: cross-sample structural match against Armaly & Enders 2019 ---------------
AE_URL <- "https://dataverse.harvard.edu/api/access/datafile/4160083"
AE_SHA <- "cadfee5da5f3fc4bed68446a5e8c7781b639697fa99315a61b35c5e0b68b9dca"
f <- file.path(tempdir(), "ae_25march2019.csv")
if (!file.exists(f)) download.file(AE_URL, f, mode = "wb", quiet = TRUE)
sha <- tryCatch(system2("sha256sum", f, stdout = TRUE), error = function(e) "")
cat("A&E file sha256 matches:", grepl(AE_SHA, sha), "\n")
a <- read.csv(f, stringsAsFactors = FALSE); names(a) <- tolower(names(a))
a <- a[!(a$distributionchannel %in% c("preview", "test")), ]
for (v in c(paste0("q2_", 1:5), paste0("q3_", 1:5))) a[[v]] <- suppressWarnings(as.numeric(a[[v]]))
AEC <- c("q2_1", "q2_2", "q2_3", "q2_5")
WORD <- c("rarely deserve", "great things", "settle for less", "extra break")
fit <- cfa('SYS =~ q3_1+q3_2+q3_3+q3_5
            EGO =~ q2_1+q2_2+q2_3+q2_5
            q3_1 ~~ q3_5', data = a, std.lv = TRUE)
s <- standardizedSolution(fit); egl <- s$est.std[s$op == "=~" & s$lhs == "EGO"]
cat(sprintf("A&E Table 1 EGO loadings: live %s vs published .803 .797 .736 .752 | chi2 %.2f vs 40.58, n %d\n",
            paste(sprintf("%.3f", egl), collapse = " "), fitMeasures(fit, "chisq"), nobs(fit)))
ok <- ok && max(abs(egl - c(.803, .797, .736, .752))) < .0015
cat("A&E per-code % at 1..5 (raw 15..19), cf. ESM Figure A2 panels labelled by wording:\n")
for (j in 1:4) { t <- table(factor(a[[AEC[j]]], 15:19)); cat(sprintf("  %s %-16s %s\n", AEC[j], WORD[j],
  paste(sprintf("%5.1f", 100 * t / sum(t)), collapse = ""))) }

feat <- function(X) { X <- as.data.frame(X); names(X) <- paste0("x", 1:4)
  f <- cfa("F =~ x1+x2+x3+x4", data = X, std.lv = TRUE); l <- standardizedSolution(f)
  list(m = colMeans(X, na.rm = TRUE), l = l$est.std[l$op == "=~"], r = cor(X, use = "pair")) }
fe <- feat(Xc); fa <- feat(sapply(a[AEC], function(x) x - 14))
cat(sprintf("Enders VICTIM_1..4: means %s | loadings %s\n", paste(sprintf("%.3f", fe$m), collapse = " "),
            paste(sprintf("%.3f", fe$l), collapse = " ")))
cat(sprintf("A&E  (%s): means %s | loadings %s\n", paste(WORD, collapse = "/"),
            paste(sprintf("%.3f", fa$m), collapse = " "), paste(sprintf("%.3f", fa$l), collapse = " ")))
perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:4)
sc24 <- t(sapply(P, function(p) {
  dm <- (fe$m - mean(fe$m)) - (fa$m[p] - mean(fa$m)); dl <- fe$l - fa$l[p]
  ra <- fa$r[p, p]; ut <- upper.tri(ra)
  c(mean = sum(dm^2), load = sum(dl^2), r = sum((fe$r[ut] - ra[ut])^2)) }))
res <- data.frame(assign = sapply(P, paste, collapse = ""), sc24); res$total <- rowSums(sc24)
res <- res[order(res$total), ]; rownames(res) <- NULL
cat("All 24 assignments (digit k = A&E statement given to VICTIM_k; 1234 = shipped), best 6:\n")
print(format(head(res, 6), digits = 3))
top4 <- sort(res$assign[1:4])
cat(sprintf("shipped rank %d; top-4 set {%s}; 5th-best total %.3f vs 4th %.3f\n",
            which(res$assign == "1234"), paste(top4, collapse = ","), res$total[5], res$total[4]))
ok <- ok && res$assign[1] == "1234" && identical(top4, sort(c("1234", "2134", "1243", "2143")))
cat("NOT established: order WITHIN {VICTIM_1,VICTIM_2} and within {VICTIM_3,VICTIM_4} -- the\n",
    "within-pair swaps rank 2-4 with small margins; that order rests on the appendix listing order.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
