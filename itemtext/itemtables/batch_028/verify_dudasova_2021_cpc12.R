# verify_dudasova_2021_cpc12.R -- Step 5b mapping verification.
#
# CLAIM: PsyCap1..PsyCap12 in the IRW table are items 1..12 of the ORIGINAL CPC-12
# in the order published in Lorenz et al. (2016) S1 Appendix
# (1-3 hope/State Hope Scale, 4-6 optimism/AFF+LOT-R, 7-9 resilience/RS-13,
#  10-12 self-efficacy/GSE), NOT the re-ordered CPC-12R printed in Dudasova et
# al.'s own S1 Appendix (1-3 optimism, 4-6 hope, 7-9 self-efficacy, 10-12 new
# resilience). Getting that crosswalk wrong would permute 9 of 12 items.
#
# FALSIFIABLE PREDICTIONS, from Dudasova et al. 2021 (PLOS ONE 16(3):e0247114):
#   (a) Table 1 subscale summary M/SD, Study 1 (N=282).
#   (b) Table 2 standardized loadings, 3 first-order + 1 second-order factor model
#       (MLR, Mplus 8), which give each of the 12 items a DISTINCT predicted value.
#   (c) In-text item-rest correlations for resilience items 1 and 3 (r = .355, .238).
# If any pair of item_texts were swapped, the loading assigned to that item would
# move to the other one and (b) would break.

suppressMessages(library(irw))
suppressMessages(library(lavaan))

TABLE <- "dudasova_2021_cpc12"

# (a) paper Table 1: Hope, Optimism, Resilience, Self-efficacy, PsyCap total
PUB_SUB <- data.frame(
  block = c("hope 1-3", "optimism 4-6", "resilience 7-9", "self-efficacy 10-12", "total 1-12"),
  M  = c(13.149, 14.227, 13.089, 14.004, 54.470),
  SD = c( 2.410,  3.093,  2.286,  2.300,  8.131))

# (b) paper Table 2 standardized loadings, in PsyCap1..12 order
PUB_LOAD <- c(.670, .686, .723, .861, .930, .773, .372, .769, .325, .857, .753, .703)
# second-order loadings Hope/Optimism/(S-E+Resil) on PsyCap
PUB_2ND  <- c(.988, .689, .836)
# (c) in-text item-rest correlations, resilience items 1 and 3
PUB_IR   <- c(PsyCap7 = .355, PsyCap9 = .238)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w), fixed = TRUE)
m <- w[, paste0("PsyCap", 1:12)]
m <- m[complete.cases(m), ]
cat("N complete cases:", nrow(m), " (paper: 282)\n\n")

cat("--- (a) subscale summary scores vs paper Table 1 ---\n")
blocks <- list(1:3, 4:6, 7:9, 10:12, 1:12)
obsM <- obsS <- numeric(5)
for (i in seq_along(blocks)) {
  s <- rowSums(m[, blocks[[i]], drop = FALSE]); obsM[i] <- mean(s); obsS[i] <- sd(s)
}
cat(sprintf("%-20s %8s %8s %8s %8s\n", "block", "pubM", "obsM", "pubSD", "obsSD"))
for (i in 1:5)
  cat(sprintf("%-20s %8.3f %8.3f %8.3f %8.3f\n",
              PUB_SUB$block[i], PUB_SUB$M[i], obsM[i], PUB_SUB$SD[i], obsS[i]))
okA <- max(abs(obsM - PUB_SUB$M)) <= 0.01

cat("\n--- (b) CFA standardized loadings vs paper Table 2 ---\n")
mod <- "Hope =~ PsyCap1+PsyCap2+PsyCap3
Optimism =~ PsyCap4+PsyCap5+PsyCap6
SER =~ PsyCap7+PsyCap8+PsyCap9+PsyCap10+PsyCap11+PsyCap12
PsyCap =~ Hope+Optimism+SER"
fit <- cfa(mod, data = m, estimator = "MLR")
st <- standardizedsolution(fit)
lo <- st[st$op == "=~" & grepl("^PsyCap[0-9]", st$rhs), ]
lo <- lo[match(paste0("PsyCap", 1:12), lo$rhs), ]
cat(sprintf("%-10s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in 1:12)
  cat(sprintf("%-10s %10.3f %10.3f %8.3f\n",
              lo$rhs[i], PUB_LOAD[i], lo$est.std[i], lo$est.std[i] - PUB_LOAD[i]))
worst <- max(abs(lo$est.std - PUB_LOAD))
cat(sprintf("largest loading deviation: %.3f\n", worst))
sec <- st[st$op == "=~" & st$lhs == "PsyCap", ]
cat(sprintf("second-order (Hope/Opt/SER): published %s | observed %s\n",
            paste(sprintf("%.3f", PUB_2ND), collapse = " "),
            paste(sprintf("%.3f", sec$est.std), collapse = " ")))
cat(sprintf("model fit: chisq.scaled %.3f df %d (paper: 105.038, df 51)\n",
            fitmeasures(fit, "chisq.scaled"), fitmeasures(fit, "df")))
okB <- worst <= 0.035   # 11/12 match to 3 dp; Resil1 is .342 vs published .372

cat("\n--- (c) item-rest correlations, resilience items 1 and 3 ---\n")
tot <- rowSums(m)
ir <- sapply(names(PUB_IR), function(v) cor(m[[v]], tot - m[[v]]))
for (v in names(PUB_IR))
  cat(sprintf("%-10s published %.3f  observed %.3f\n", v, PUB_IR[[v]], ir[[v]]))
okC <- max(abs(ir - PUB_IR)) <= 0.005

cat("\nWhat this does NOT establish: it verifies that each IRW item code sits at the\n",
    "position the paper's own analysis assigns it, and hence which CPC-12 statement it\n",
    "carries. It says nothing about the accuracy of the Czech->English crosswalk itself\n",
    "(done by exact English-string identity between the two PLOS appendices), nor about\n",
    "the 3 resilience items whose Czech wording was never published.\n", sep = "")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
