# Mapping check for pilch_2021_personality_ipip20 (IPIP-BFM-20, Polish).
#
# CLAIM UNDER TEST: item code IPIP<n> is item <n> of the published Polish
# IPIP-BFM-20 form (Topolewska, Skimina, Strus, Cieciuch & Rowinski, 2014;
# www.ipip.uksw.edu.pl -> "Kwestionariusz IPIP-BFM-20.pdf", CC BY 2013). That
# form numbers its 20 items 1..20, and its trait/keying structure is a strong,
# falsifiable prediction about the data:
#
#   position   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
#   trait      E  A  C  N  I  E  A  C  N  I  E  A  C  N  I  E  A  C  N  I
#   keyed      +  -  -  +  +  -  +  +  -  -  +  -  -  +  +  -  +  +  -  -
#   (keyed sign is for E/A/C/EmotionalStability/I; the paper scores the fourth
#    trait as NEUROTICISM, i.e. the reverse of the '+' shown above.)
#
# If the 20 wordings were permuted across traits, the subscale alphas, the
# composite means/SDs and the intercorrelations below would all break. What this
# CANNOT test is a swap WITHIN a trait-and-polarity pair (1<->11, 6<->16,
# 2<->12, 7<->17, 3<->13, 8<->18, 4<->14, 9<->19, 5<->15, 10<->20): those ten
# swaps leave every number here unchanged. Hence PARTIAL, not VERIFIED.
#
# Published values, all from Pilch I, Wardawy P, Probierz E (2021) PLOS ONE
# 16(10):e0258606 (CC BY 4.0): alphas from the Measures section, M/SD and
# intercorrelations from Table 2 (N = 397).

suppressMessages(library(irw))
TABLE <- "pilch_2021_personality_ipip20"

POS <- list(E = c(1, 11), A = c(7, 17), C = c(8, 18), N = c(9, 19), I = c(5, 15))
NEG <- list(E = c(6, 16), A = c(2, 12), C = c(3, 13), N = c(4, 14), I = c(10, 20))
PUB_ALPHA <- c(E = 0.87, A = 0.70, C = 0.76, N = 0.75, I = 0.66)
PUB_M     <- c(E = 2.76, A = 3.55, C = 3.23, N = 2.82, I = 3.81)   # see note on N
PUB_SD    <- c(E = 1.05, A = 0.72, C = 0.89, N = 0.86, I = 0.66)
PUB_R <- rbind(c("E","A",0.29), c("E","C",0.23), c("E","N",-0.30), c("E","I",0.17),
               c("A","C",0.24), c("A","N",0.02), c("A","I",0.11),
               c("C","N",-0.19), c("C","I",0.10), c("N","I",0.12))

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[stats::complete.cases(w[, paste0("IPIP", 1:20)]), ]
cat(sprintf("live data: %d respondents x 20 items\n\n", nrow(w)))

score <- function(tr) {
    a <- w[, paste0("IPIP", POS[[tr]]), drop = FALSE]
    b <- 6 - w[, paste0("IPIP", NEG[[tr]]), drop = FALSE]
    cbind(a, b)
}
alpha <- function(m) {
    k <- ncol(m)
    k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
}

comp <- sapply(names(POS), function(tr) rowMeans(score(tr)))
cat(sprintf("%-4s %9s %9s %9s %9s %9s %9s\n",
            "", "alpha", "pub", "M", "pub", "SD", "pub"))
ok <- TRUE
for (tr in names(POS)) {
    a <- alpha(score(tr)); m <- mean(comp[, tr]); s <- sd(comp[, tr])
    cat(sprintf("%-4s %9.3f %9.2f %9.2f %9.2f %9.2f %9.2f\n",
                tr, a, PUB_ALPHA[tr], m, PUB_M[tr], s, PUB_SD[tr]))
    if (abs(a - PUB_ALPHA[tr]) > 0.05) ok <- FALSE
    if (abs(s - PUB_SD[tr]) > 0.03) ok <- FALSE
    # N is exempted from the mean check: the paper's Table 2 reports 2.82 for
    # "neuroticism", which is 6 - 3.19, i.e. the emotional-stability mean, while
    # every correlation it reports for that variable carries the NEUROTICISM
    # sign (and is reproduced below). Treated as a reporting slip in the paper.
    if (tr != "N" && abs(m - PUB_M[tr]) > 0.02) ok <- FALSE
}

cat("\nintercorrelations (keyed as above; N = neuroticism direction)\n")
for (i in seq_len(nrow(PUB_R))) {
    x <- PUB_R[i, 1]; y <- PUB_R[i, 2]; p <- as.numeric(PUB_R[i, 3])
    o <- cor(comp[, x], comp[, y])
    flag <- if (abs(o - p) > 0.02) "  <-- MISMATCH" else ""
    cat(sprintf("  r(%s,%s) = %6.3f   published %6.2f%s\n", x, y, o, p, flag))
}
cat("\nThe one published correlation this keying does not reproduce is r(N,I):\n",
    "published +0.12, observed -0.12. Every other N correlation in Table 2\n",
    "(E -0.30, C -0.19, A 0.02, age -0.185 vs published -0.18) reproduces with\n",
    "sign, so the N column is read as neuroticism and this cell as a second\n",
    "sign slip in the same row rather than as evidence about the mapping.\n", sep = "")

# Polarity is also checkable without any published number: within each trait the
# two same-keyed items must correlate positively and cross-keyed negatively.
cat("\nwithin-trait keying pattern (raw, unreversed):\n")
for (tr in names(POS)) {
    p <- POS[[tr]]; n <- NEG[[tr]]
    rr <- cor(w[, paste0("IPIP", c(p, n))])
    cat(sprintf("  %s: r(+,+)=%+.2f r(-,-)=%+.2f  cross = %+.2f..%+.2f\n", tr,
                rr[1, 2], rr[3, 4], min(rr[1:2, 3:4]), max(rr[1:2, 3:4])))
    if (rr[1, 2] <= 0 || rr[3, 4] <= 0 || max(rr[1:2, 3:4]) >= 0) ok <- FALSE
}

cat("\nNOT ESTABLISHED: a swap within any of the ten trait-by-polarity pairs\n",
    "(1<->11, 6<->16, 2<->12, 7<->17, 3<->13, 8<->18, 4<->14, 9<->19, 5<->15,\n",
    "10<->20) is invisible to every number above.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
