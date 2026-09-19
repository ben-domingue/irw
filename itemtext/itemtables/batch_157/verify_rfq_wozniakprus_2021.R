# verify_rfq_wozniakprus_2021.R
#
# Claim under test: the live item codes RFQ1..RFQ8 carry the CANONICAL RFQ-8 item
# numbering, i.e. RFQ1 = "People's thoughts are a mystery to me", RFQ2 = "I don't
# always know why I do what I do", RFQ3 = "When I get angry I say things without
# really knowing why I am saying them", RFQ4 = "...things that I later regret",
# RFQ5 = "If I feel insecure I can behave in ways that put others' backs up",
# RFQ6 = "Sometimes I do things without really knowing why", RFQ7 = "I always know
# what I feel" (the sole reverse-keyed item), RFQ8 = "Strong feelings often cloud
# my thinking".
#
# The source .sav carries NO variable labels for RFQ1..RFQ8, so the tie is made by
# published item numbering and must be checked against the data. Four falsifiable
# predictions follow from the canonical numbering; all four are computed below from
# the study's own Harvard Dataverse deposit (doi:10.7910/DVN/BMCC4C), which also
# ships the authors' derived scoring columns.
#
#   P1  Item 7 is the ONLY reverse-keyed item -> RFQ7 is the only column with
#       negative correlations against every other item.
#   P2  Item 1 is the weak item of the RFQ-8 (published standardised loadings
#       0.513 / 0.343 vs 0.766-0.884 for items 2-6 and 8; Horvath et al. 2023,
#       PLOS ONE 18(2):e0282000, Table 2) -> RFQ1 has the lowest corrected
#       item-total correlation, by a wide margin.
#   P3  Items 2 and 6 are near-synonyms ("I don't always know why I do what I do" /
#       "Sometimes I do things without really knowing why") -> {RFQ2,RFQ6} is the
#       highest-correlating pair in the matrix. Items 3 and 4 both begin "When I get
#       angry I say things..." -> {RFQ3,RFQ4} is the second-highest pair.
#   P4  The deposit's own derived columns reproduce the canonical RFQ-8 scoring key
#       exactly: RFQ_C over items 1-6 (1,2,3 -> 3,2,1; 4-7 -> 0) and RFQ_U over
#       items 2,4,5,6,7,8 (5,6,7 -> 1,2,3; 1-4 -> 0) with item 7 reversed. The key
#       is asymmetric, so it independently pins the CERTAINTY-only class {1,3},
#       the UNCERTAINTY-only class {7,8} and the shared class {2,4,5,6}.
#
# It does NOT separate RFQ2 from RFQ6: they are in the same key class and their
# corrected item-totals agree to three decimals. That pair rests on the published
# numbering alone, which is why the verification status is PARTIAL, not VERIFIED.
#
# Also checked: the .sav's value labels for RFQ8 read 1 = "strongly agree",
# 7 = "strongly disagree", the reverse of every other item. P5 shows that label is
# an error in the source file -- RFQ8 is scored and behaves exactly like the other
# uncertainty items -- which is why the shipped anchors run 1 = Strongly disagree
# ... 7 = Strongly agree for all eight items.

TAB <- "https://dataverse.harvard.edu/api/access/datafile/4289254"
f <- tempfile(fileext = ".tab")
utils::download.file(TAB, f, quiet = TRUE)
d <- utils::read.delim(f, stringsAsFactors = FALSE)

it <- paste0("RFQ", 1:8)
X  <- d[, it]
X  <- X[stats::complete.cases(X), ]
cat(sprintf("N complete cases: %d\n\n", nrow(X)))

ok <- logical(0)

## ---- P1: item 7 is the only reverse-keyed item -------------------------------
C <- stats::cor(X)
cat("Correlation matrix (live deposit):\n")
print(round(C, 3))
offdiag_neg <- sapply(it, function(v) all(C[v, setdiff(it, v)] < 0))
cat("\nP1 columns whose correlations with ALL others are negative: ",
    paste(it[offdiag_neg], collapse = ", "), "\n", sep = "")
p1 <- identical(it[offdiag_neg], "RFQ7")
cat(sprintf("P1 (RFQ7 and only RFQ7 is reverse-keyed): %s\n\n", ifelse(p1, "PASS", "FAIL")))
ok <- c(ok, p1)

## ---- P2: item 1 is the weak item ---------------------------------------------
Y <- X; Y$RFQ7 <- 8 - Y$RFQ7
tot <- rowSums(Y)
cit <- sapply(it, function(v) stats::cor(Y[[v]], tot - Y[[v]]))
cat("P2 corrected item-total correlations (RFQ7 reversed):\n")
for (v in it) cat(sprintf("   %-5s %.3f\n", v, cit[v]))
p2 <- (names(which.min(cit)) == "RFQ1") && (min(cit) < sort(cit)[2] - 0.10)
cat(sprintf("   lowest = %s (%.3f); next lowest = %s (%.3f)\n",
            names(which.min(cit)), min(cit),
            names(sort(cit))[2], sort(cit)[2]))
cat(sprintf("P2 (RFQ1 is the weak item, gap > 0.10): %s\n\n", ifelse(p2, "PASS", "FAIL")))
ok <- c(ok, p2)

## ---- P3: the two content pairs ------------------------------------------------
Cu <- C; Cu[lower.tri(Cu, diag = TRUE)] <- NA
prs <- which(!is.na(Cu), arr.ind = TRUE)
val <- Cu[prs]
o   <- order(-val)
cat("P3 top three item pairs by correlation:\n")
for (k in 1:3)
    cat(sprintf("   %s - %s  r = %.3f\n",
                it[prs[o[k], 1]], it[prs[o[k], 2]], val[o[k]]))
pair <- function(k) sort(c(it[prs[o[k], 1]], it[prs[o[k], 2]]))
p3 <- identical(pair(1), c("RFQ2", "RFQ6")) && identical(pair(2), c("RFQ3", "RFQ4"))
cat(sprintf("P3 (top pair = synonym pair {2,6}; second = anger pair {3,4}): %s\n\n",
            ifelse(p3, "PASS", "FAIL")))
ok <- c(ok, p3)

## ---- P4: the deposit's derived columns reproduce the canonical key -----------
recC <- function(x) c(3, 2, 1, 0, 0, 0, 0)[x]     # certainty recode
recU <- function(x) c(0, 0, 0, 0, 1, 2, 3)[x]     # uncertainty recode
D <- d[stats::complete.cases(d[, it]), ]
cat("P4 canonical RFQ-8 key reproduced against the deposit's own derived columns:\n")
p4 <- TRUE
for (i in 1:6) {
    got <- all(recC(D[[paste0("RFQ", i)]]) == D[[paste0("RFQc", i)]], na.rm = TRUE)
    cat(sprintf("   RFQc%d = certainty_recode(RFQ%d): %s\n", i, i, ifelse(got, "yes", "NO")))
    p4 <- p4 && got
}
for (i in c(2, 4, 5, 6, 8)) {
    got <- all(recU(D[[paste0("RFQ", i)]]) == D[[paste0("RFQu", i)]], na.rm = TRUE)
    cat(sprintf("   RFQu%d = uncertainty_recode(RFQ%d): %s\n", i, i, ifelse(got, "yes", "NO")))
    p4 <- p4 && got
}
got7r <- all(D$RFQ7R == 8 - D$RFQ7, na.rm = TRUE)
got7  <- all(recU(8 - D$RFQ7) == D$RFQu7, na.rm = TRUE)
cat(sprintf("   RFQ7R = 8 - RFQ7: %s\n", ifelse(got7r, "yes", "NO")))
cat(sprintf("   RFQu7 = uncertainty_recode(8 - RFQ7): %s\n", ifelse(got7, "yes", "NO")))
noC7 <- !any(c("RFQc7", "RFQc8") %in% names(d))
noU  <- !any(c("RFQu1", "RFQu3") %in% names(d))
cat(sprintf("   deposit has NO RFQc7/RFQc8 (items 7,8 outside certainty): %s\n", ifelse(noC7, "yes", "NO")))
cat(sprintf("   deposit has NO RFQu1/RFQu3 (items 1,3 outside uncertainty): %s\n", ifelse(noU, "yes", "NO")))
p4 <- p4 && got7r && got7 && noC7 && noU
cat(sprintf("P4 (canonical C={1..6}, U={2,4,5,6,7,8}, 7 reversed): %s\n\n",
            ifelse(p4, "PASS", "FAIL")))
ok <- c(ok, p4)

## ---- P5: the .sav's RFQ8 value label is wrong --------------------------------
uOthers <- c("RFQ2", "RFQ4", "RFQ5", "RFQ6")
r8 <- sapply(uOthers, function(v) C["RFQ8", v])
cat("P5 RFQ8 against the other non-reversed uncertainty items:\n")
for (v in uOthers) cat(sprintf("   r(RFQ8, %s) = %+.3f\n", v, r8[v]))
cat(sprintf("   r(RFQ8, RFQ7) = %+.3f   (RFQ7 is the reverse-keyed item)\n", C["RFQ8", "RFQ7"]))
p5 <- all(r8 > 0) && C["RFQ8", "RFQ7"] < 0
cat("P5 (RFQ8 runs in the SAME direction as the other U items, so the\n")
cat(sprintf("    .sav value label 1='strongly agree' for RFQ8 is an error): %s\n\n",
            ifelse(p5, "PASS", "FAIL")))
ok <- c(ok, p5)

## ---- what this does NOT establish --------------------------------------------
cat("NOT ESTABLISHED: RFQ2 vs RFQ6. Both sit in the same key class (certainty AND\n")
cat("uncertainty), and their corrected item-total correlations agree to three\n")
cat(sprintf("decimals (%.4f vs %.4f). A swap between them exchanges two near-synonymous\n",
            cit["RFQ2"], cit["RFQ6"]))
cat("sentences and is not detectable in these data; that pair rests on the published\n")
cat("RFQ-8 numbering (Horvath et al. 2023 Table 2; Zaal et al. 2023, PLOS ONE\n")
cat("18(6):e0287751 Table 2, which labels the same eight texts RFQ1..RFQ8 in this\n")
cat("exact order). Hence status = PARTIAL.\n\n")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
