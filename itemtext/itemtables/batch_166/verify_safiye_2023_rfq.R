# verify_safiye_2023_rfq.R
#
# Claim under test: the live item codes RFQ1..RFQ8 carry the CANONICAL RFQ-8 item
# numbering, i.e. RFQ1 = "People's thoughts are a mystery to me", RFQ2 = "I don't
# always know why I do what I do", RFQ3 = "When I get angry I say things without
# really knowing why I am saying them", RFQ4 = "When I get angry I say things that I
# later regret", RFQ5 = "If I feel insecure I can behave in ways that put others'
# backs up", RFQ6 = "Sometimes I do things without really knowing why", RFQ7 = "I
# always know what I feel" (the sole reverse-keyed item), RFQ8 = "Strong feelings
# often cloud my thinking" -- and that resp 1..7 = the .sav value labels
# "Strongly disagree" .. "Strongly agree" for every item.
#
# Codes RFQ1..RFQ8 ARE the column names of the study's S1 Data .sav
# (data/safiye_2023_mbi_rfq.py melts them by name), but those columns carry NO
# variable labels, so the name->wording tie is the instrument's published numbering
# and has to be tested against the data. Predictions, computed on the deposit:
#
#   P1  Item 7 is the ONLY reverse-keyed item -> RFQ7 is the only column whose
#       correlations with every other item are negative.
#   P2  Item 1 is the weak non-reversed item of the RFQ-8 (published loadings
#       0.513/0.343 vs 0.753-0.888 for items 2-6 and 8; Horvath et al. 2023, PLOS
#       ONE 18(2):e0282000, Table 2) -> among the seven non-reversed items RFQ1 has
#       the lowest corrected item-total correlation, by a clear gap.
#   P3  Items 3/4 both begin "When I get angry I say things..." and items 2/6 are
#       near-synonyms -> {RFQ3,RFQ4} and {RFQ2,RFQ6} are the two highest-correlating
#       pairs in the matrix (either order).
#   P4  The deposit's own derived scoring columns reproduce the canonical RFQ-8 key
#       row for row: RFQc1..RFQc6 = certainty recode (1,2,3 -> 3,2,1; else 0) of the
#       same-numbered item; RFQu2/4/5/6/8 = uncertainty recode (5,6,7 -> 1,2,3; else 0);
#       RFQu7 = uncertainty recode of the REVERSED RFQ7; no RFQc7/RFQc8, no RFQu1/RFQu3.
#       The key is asymmetric: it pins certainty-only {1,3}, uncertainty-only {7,8}
#       and shared {2,4,5,6} independently of the correlations.
#   P5  (option axis, route 9) Live per-item value counts equal the deposit's
#       per-item counts of the numeric codes whose value labels are the shipped
#       option_text, for all 8 x 7 cells.
#
# Combined: P1 separates 7 from 8; P4+P3 put 3 (certainty-only) and 4 (shared) in the
# anger pair and 1 as the other certainty-only item; 5 is the shared item outside
# both pairs. NOT separated: RFQ2 vs RFQ6 (same key class, same content pair).

suppressMessages({ library(haven); library(irw) })

TABLE <- "safiye_2023_rfq"
SAV   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0279535.s001"
f <- tempfile(fileext = ".sav")
utils::download.file(SAV, f, quiet = TRUE, mode = "wb")
d <- haven::read_sav(f)

it <- paste0("RFQ", 1:8)
D  <- as.data.frame(lapply(d, function(z) if (is.numeric(z)) as.numeric(z) else z))
X  <- D[stats::complete.cases(D[, it]), it]
cat(sprintf("Deposit rows: %d; complete on RFQ1..RFQ8: %d\n\n", nrow(D), nrow(X)))
ok <- logical(0)

## P1 ---------------------------------------------------------------------------
C <- stats::cor(X)
cat("Correlation matrix (deposit):\n"); print(round(C, 3))
neg <- sapply(it, function(v) all(C[v, setdiff(it, v)] < 0))
p1 <- identical(it[neg], "RFQ7")
cat(sprintf("\nP1 columns negative against ALL others: %s -> %s\n\n",
            paste(it[neg], collapse = ","), ifelse(p1, "PASS", "FAIL")))
ok <- c(ok, p1)

## P2 ---------------------------------------------------------------------------
Y <- X; Y$RFQ7 <- 8 - Y$RFQ7
tot <- rowSums(Y)
cit <- sapply(it, function(v) stats::cor(Y[[v]], tot - Y[[v]]))
cat("P2 corrected item-total correlations (RFQ7 reversed):\n")
for (v in it) cat(sprintf("   %-5s %.3f\n", v, cit[v]))
nr <- sort(cit[setdiff(it, "RFQ7")])
p2 <- names(nr)[1] == "RFQ1" && (nr[2] - nr[1]) > 0.10
cat(sprintf("   non-reversed lowest = %s (%.3f), next = %s (%.3f), gap %.3f\n",
            names(nr)[1], nr[1], names(nr)[2], nr[2], nr[2] - nr[1]))
cat(sprintf("P2 (RFQ1 weakest non-reversed item, gap > 0.10): %s\n\n", ifelse(p2, "PASS", "FAIL")))
ok <- c(ok, p2)

## P3 ---------------------------------------------------------------------------
Cu <- C; Cu[lower.tri(Cu, diag = TRUE)] <- NA
prs <- which(!is.na(Cu), arr.ind = TRUE); val <- Cu[prs]; o <- order(-val)
cat("P3 top three pairs:\n")
for (k in 1:3) cat(sprintf("   %s - %s  r = %.3f\n", it[prs[o[k], 1]], it[prs[o[k], 2]], val[o[k]]))
pr <- function(k) paste(sort(c(it[prs[o[k], 1]], it[prs[o[k], 2]])), collapse = "-")
p3 <- setequal(c(pr(1), pr(2)), c("RFQ3-RFQ4", "RFQ2-RFQ6"))
cat(sprintf("P3 (top two pairs = {3,4} and {2,6}): %s\n\n", ifelse(p3, "PASS", "FAIL")))
ok <- c(ok, p3)

## P4 ---------------------------------------------------------------------------
recC <- function(x) c(3, 2, 1, 0, 0, 0, 0)[x]
recU <- function(x) c(0, 0, 0, 0, 1, 2, 3)[x]
p4 <- TRUE
cat("P4 deposit's derived columns vs canonical key (share of rows reproduced):\n")
for (i in 1:6) {
    s <- mean(recC(D[[paste0("RFQ", i)]]) == D[[paste0("RFQc", i)]])
    cat(sprintf("   RFQc%d = certainty_recode(RFQ%d): %.4f\n", i, i, s)); p4 <- p4 && s == 1
}
for (i in c(2, 4, 5, 6, 8)) {
    s <- mean(recU(D[[paste0("RFQ", i)]]) == D[[paste0("RFQu", i)]])
    cat(sprintf("   RFQu%d = uncertainty_recode(RFQ%d): %.4f\n", i, i, s)); p4 <- p4 && s == 1
}
s7  <- mean(recU(8 - D$RFQ7) == D$RFQu7)
s7n <- mean(recU(D$RFQ7) == D$RFQu7)
cat(sprintf("   RFQu7 = uncertainty_recode(8 - RFQ7): %.4f  (unreversed: %.4f)\n", s7, s7n))
absent <- !any(c("RFQc7", "RFQc8", "RFQu1", "RFQu3") %in% names(D))
cat(sprintf("   no RFQc7/RFQc8/RFQu1/RFQu3 columns: %s\n", absent))
p4 <- p4 && s7 == 1 && s7n < 1 && absent
cat(sprintf("P4 (C={1..6}, U={2,4,5,6,7,8}, 7 reversed): %s\n\n", ifelse(p4, "PASS", "FAIL")))
ok <- c(ok, p4)

## P5 (route 9) ------------------------------------------------------------------
shipped <- c("Strongly disagree", "I disagree", "I partially disagree",
             "I neither agree nor disagree", "I partially agree", "I agree", "Strongly agree")
lab_ok <- all(sapply(it, function(v) {
    lb <- attr(d[[v]], "labels"); identical(unname(names(lb)[match(1:7, lb)]), shipped)
}))
cat(sprintf("P5a .sav value labels 1..7 equal shipped option_text for all 8 items: %s\n", lab_ok))
live <- irw::irw_fetch(TABLE)
dep_tab  <- sapply(it, function(v) tabulate(X[[v]], 7))
live_tab <- sapply(it, function(v) tabulate(as.integer(live$resp[live$item == v]), 7))
cat("   deposit counts (rows = resp 1..7):\n"); print(dep_tab)
cat("   live counts:\n"); print(live_tab)
p5 <- lab_ok && identical(dep_tab, live_tab)
cat(sprintf("P5 (live counts == deposit counts, 56/56 cells): %s\n\n", ifelse(p5, "PASS", "FAIL")))
ok <- c(ok, p5)

cat("NOT ESTABLISHED: RFQ2 vs RFQ6. Same key class (certainty AND uncertainty), same\n")
cat(sprintf("content pair; corrected item-totals %.3f vs %.3f. RFQ6 > RFQ2 is in the same\n", cit["RFQ2"], cit["RFQ6"]))
cat("direction as Horvath 2023's loadings (item 6 0.854/0.888 vs item 2 0.832/0.753),\n")
cat("but that is a cross-sample comparison of a small gap, not a test; in the Polish\n")
cat("RFQ-8 deposit (batch_157) the two agree to 3 dp. A swap of these two\n")
cat("near-synonymous sentences is undetectable here and rests on the published RFQ-8\n")
cat("numbering (Horvath 2023 Table 2; Ruiz-Parra 2023 S1 Appendix). Status PARTIAL.\n\n")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
