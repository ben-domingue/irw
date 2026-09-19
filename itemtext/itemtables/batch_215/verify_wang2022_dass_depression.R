# verify_wang2022_dass_depression.R
#
# CLAIM UNDER TEST (Step 5b), in two independent parts.
#
#  (a) WHICH DEPOSIT COLUMN EACH LIVE ITEM IS.  The shipped mapping says
#      dass_dep_1..7 are, in order, columns DASS3, DASS5, DASS10, DASS13,
#      DASS16, DASS17, DASS21 of the study's own deposit (figshare 19158812,
#      Data_Sheet_1.xlsx, CC BY 4.0) -- the seven canonical DASS-21 DEPRESSION
#      positions in ascending order.  Falsifiable two ways, both run below:
#      the live item's whole sorted response vector must be IDENTICAL to the
#      claimed column's, and it must be identical to NO OTHER of the 21 DASS
#      columns.  Any permutation inside the subscale breaks it.
#
#  (b) WHICH SUBSCALE THE SEVEN ITEMS ARE.  The shipped item_text is the
#      canonical DASS-21 depression wording, which requires that
#      {DASS3,5,10,13,16,17,21} really is the depression block of this
#      administration.  Two published predictions, neither of which the other
#      two subscales satisfy:
#        - Cronbach's alpha of the three canonical triples must reproduce the
#          paper's 0.87 / 0.84 / 0.86 (Wang et al. 2022, Measures), each to its
#          own value;
#        - the paper's Table 1 prints per-gender M +/- SD for all three
#          subscales (Depression 0.37 +/- 0.55 male, 0.49 +/- 0.64 female;
#          Anxiety 0.57/0.64 and 0.66/0.67; Stress 0.62/0.67 and 0.76/0.72).
#          All twelve cells must reproduce to the printed 2 decimals, and each
#          triple must match ITS OWN pair of cells.
#
#  WHAT THIS DOES NOT ESTABLISH, hence PARTIAL: that the deposit's header
#  numbers DASS1..DASS21 follow the canonical DASS-21 item order WITHIN the
#  depression subscale.  (b) pins the block, (a) pins live-item-to-column, but
#  which canonical depression SENTENCE the column "DASS3" carries rests on the
#  header's numbering convention, which neither the deposit nor the paper
#  states.  Unlike the anxiety subscale there is not even an underpowered
#  within-block structural test available: Lovibond & Lovibond assign the seven
#  depression items one content facet each (dysphoria, hopelessness,
#  devaluation of life, self-deprecation, lack of interest, anhedonia, inertia),
#  so there are no facet blocks whose intercorrelations could be compared.  A
#  permutation of the seven sentences among the seven columns would be
#  undetectable from the data.

suppressMessages({library(irw); library(readxl)})

TABLE <- "wang2022_dass_depression"
CLAIM <- c(dass_dep_1 = 3, dass_dep_2 = 5, dass_dep_3 = 10, dass_dep_4 = 13,
           dass_dep_5 = 16, dass_dep_6 = 17, dass_dep_7 = 21)
CANON <- list(depression = c(3,5,10,13,16,17,21),
              anxiety    = c(2,4,7,9,15,19,20),
              stress     = c(1,6,8,11,12,14,18))
PUB_ALPHA <- c(depression = 0.87, anxiety = 0.84, stress = 0.86)      # Measures
PUB_T1 <- list(                                                       # Table 1
    depression = c(male_m = 0.37, male_sd = 0.55, female_m = 0.49, female_sd = 0.64),
    anxiety    = c(male_m = 0.57, male_sd = 0.64, female_m = 0.66, female_sd = 0.67),
    stress     = c(male_m = 0.62, male_sd = 0.67, female_m = 0.76, female_sd = 0.72))
TOL_ALPHA <- 0.01
TOL_T1    <- 0.005          # printed to 2 dp, so a correct value rounds onto it

## ---- deposit ---------------------------------------------------------------
cache <- file.path("itemtext", ".cache", TABLE)
if (!dir.exists(cache)) cache <- file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)
xlsx <- file.path(cache, "data.xlsx")
if (!file.exists(xlsx))
    download.file("https://ndownloader.figshare.com/files/34038791", xlsx, quiet = TRUE)
raw <- suppressMessages(as.data.frame(read_excel(xlsx, sheet = 1)))
D <- sapply(1:21, function(k) suppressWarnings(as.numeric(raw[[paste0("DASS", k)]])))
colnames(D) <- paste0("DASS", 1:21)
gender <- suppressWarnings(as.numeric(raw[[2]]))    # header is the Chinese for "gender"
cat(sprintf("deposit: %d respondents x 21 DASS columns\n", nrow(D)))

## ---- live ------------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
cat(sprintf("live   : %d rows, %d ids, %d items\n",
            nrow(d), length(unique(d$id)), length(unique(d$item))))

## ---- (a) exact-distribution identification ---------------------------------
cat("\n-- (a) each live item's sorted response vector vs all 21 deposit columns --\n")
cat(sprintf("%-11s %-7s %5s %-22s %-28s %s\n",
            "item", "claim", "n", "live 0/1/2/3", "columns identical to it", "ok"))
ok_a <- TRUE
for (it in names(CLAIM)) {
    x <- sort(d$resp[d$item == it])
    hits <- colnames(D)[apply(D, 2, function(y) identical(sort(y[!is.na(y)]), x))]
    pass <- identical(hits, paste0("DASS", CLAIM[[it]]))
    ok_a <- ok_a && pass
    cat(sprintf("%-11s %-7s %5d %-22s %-28s %s\n",
                it, paste0("DASS", CLAIM[[it]]), length(x),
                paste(as.vector(table(factor(x, 0:3))), collapse = "/"),
                paste(hits, collapse = ","),
                if (pass) "yes" else "NO"))
}
cat(sprintf("all seven uniquely identical to their claimed column: %s\n", ok_a))

## ---- (b1) subscale alphas --------------------------------------------------
alpha <- function(M) {
    M <- M[complete.cases(M), , drop = FALSE]
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}
cat("\n-- (b1) Cronbach's alpha of the canonical triples in this deposit --\n")
cat(sprintf("%-11s %9s %9s %8s\n", "subscale", "published", "observed", "diff"))
ok_b1 <- TRUE
for (nm in names(CANON)) {
    a <- alpha(D[, paste0("DASS", CANON[[nm]])])
    ok_b1 <- ok_b1 && abs(a - PUB_ALPHA[[nm]]) <= TOL_ALPHA
    cat(sprintf("%-11s %9.2f %9.4f %8.4f\n", nm, PUB_ALPHA[[nm]], a, a - PUB_ALPHA[[nm]]))
}
a_live <- {
    w <- tapply(d$resp, list(as.character(d$id), as.character(d$item)), mean)
    alpha(w[, names(CLAIM), drop = FALSE])
}
cat(sprintf("live %s table, alpha = %.4f (published depression 0.87)\n", TABLE, a_live))
cat(sprintf("all three alphas within %.2f: %s\n", TOL_ALPHA, ok_b1))

## ---- (b2) Table 1 per-gender cells -----------------------------------------
# The deposit codes gender 1/2 without a label; the assignment below is read OFF
# the paper (all three subscales agree that code 2 = male), so it is one bit of
# freedom, not three -- and it cannot rescue a wrong subscale assignment, which
# is what is being tested.
cat("\n-- (b2) paper Table 1 per-gender M +/- SD, complete cases per subscale --\n")
cat(sprintf("%-11s %-7s %7s %7s %7s %7s %s\n",
            "subscale", "sex", "pub M", "obs M", "pub SD", "obs SD", "ok"))
ok_b2 <- TRUE
for (nm in names(CANON)) {
    M  <- D[, paste0("DASS", CANON[[nm]])]
    cc <- complete.cases(M)
    s  <- rowMeans(M)
    for (sex in c("male", "female")) {
        g  <- if (sex == "male") 2 else 1
        sel <- cc & !is.na(gender) & gender == g
        om <- mean(s[sel]); osd <- sd(s[sel])
        pm <- PUB_T1[[nm]][[paste0(sex, "_m")]]; psd <- PUB_T1[[nm]][[paste0(sex, "_sd")]]
        pass <- abs(om - pm) <= TOL_T1 && abs(osd - psd) <= TOL_T1
        ok_b2 <- ok_b2 && pass
        cat(sprintf("%-11s %-7s %7.2f %7.4f %7.2f %7.4f %s\n",
                    nm, sex, pm, om, psd, osd, if (pass) "yes" else "NO"))
    }
}
cat(sprintf("all twelve Table 1 cells reproduce within %.3f: %s\n", TOL_T1, ok_b2))

## ---- cross-check: would a rival subscale assignment pass (b2)? -------------
cat("\n-- cross-check: depression's published cells vs the OTHER triples' observed --\n")
for (nm in c("anxiety", "stress")) {
    M <- D[, paste0("DASS", CANON[[nm]])]; cc <- complete.cases(M); s <- rowMeans(M)
    om <- mean(s[cc & gender == 2]); of <- mean(s[cc & gender == 1])
    cat(sprintf("  %s triple would give male %.4f / female %.4f against depression's published 0.37 / 0.49\n",
                nm, om, of))
}

cat("\nNot established (see header): item order WITHIN the depression block.\n")
cat(if (ok_a && ok_b1 && ok_b2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
