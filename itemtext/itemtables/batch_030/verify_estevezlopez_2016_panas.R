# verify_estevezlopez_2016_panas.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST: panas_1..panas_20 carry the affect terms numbered 1..20 in
# Estevez-Lopez et al. (2016), PeerJ 4:e1822 (Fig. 1 and the item list in the
# Methods): 1 Interested, 2 Distressed, 3 Excited, 4 Upset, 5 Strong, 6 Guilty,
# 7 Scared, 8 Hostile, 9 Enthusiastic, 10 Proud, 11 Irritable, 12 Alert,
# 13 Ashamed, 14 Inspired, 15 Nervous, 16 Determined, 17 Attentive, 18 Jittery,
# 19 Active, 20 Afraid.
#
# The processing script assigns panas_N POSITIONALLY from the deposit's
# "Nth_item" columns, so two things need showing, and this script shows both:
#
#   PART A (plumbing-adjacent but not plumbing): live panas_N equals the
#     deposit's Nth_item column cell for cell. Confirms the positional rename
#     did not shift. Skipped with a message if the deposit cannot be fetched.
#   PART B (the mapping): re-fit the paper's best-fitting model 2b(3) -- two
#     correlated factors with the Zevon & Tellegen mood-subcategory residual
#     correlations plus distressed~~nervous -- on the LIVE data and compare
#     every standardised loading and every residual correlation with the values
#     printed on the item boxes of Figure 1. Those published values are
#     item-specific, so a permutation of the affect terms would break them.
#
# What Part B does NOT establish: panas_5 (Strong) vs panas_19 (Active) are not
# separated. Their published loadings are .58 and .59, they sit in the same
# Zevon & Tellegen subcategory, and they are each other's residual-correlation
# partner, so exchanging the two words is invisible to this route.

suppressMessages(library(irw))
TABLE <- "estevezlopez_2016_panas"
items <- paste0("panas_", 1:20)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

## ---- PART A: positional rename against the deposit -------------------------
partA <- NA
ok <- requireNamespace("readxl", quietly = TRUE)
if (!ok) {
    cat("PART A skipped: readxl not installed.\n\n")
} else {
    url <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4817417/supplementaryFiles"
    tmpz <- tempfile(fileext = ".zip")
    got <- tryCatch({
        utils::download.file(url, tmpz, quiet = TRUE,
                             headers = c("User-Agent" = "IRW-itemtext/1.0"))
        TRUE
    }, error = function(e) FALSE)
    if (!got || !file.exists(tmpz) || file.size(tmpz) < 1000) {
        cat("PART A skipped: could not fetch the Europe PMC supplementary zip.\n\n")
    } else {
        dir <- tempfile(); dir.create(dir)
        utils::unzip(tmpz, files = "peerj-04-1822-s001.xlsx", exdir = dir)
        x <- as.data.frame(readxl::read_excel(
            file.path(dir, "peerj-04-1822-s001.xlsx")))
        src <- names(x)[-1]                       # 1st_item .. 20th_item
        m <- match(w$id, x$Participant)
        cat("PART A -- live panas_N vs deposit column N, cell for cell\n")
        cat(sprintf("  participants matched: %d of %d\n", sum(!is.na(m)), nrow(w)))
        agree <- sapply(1:20, function(i)
            mean(w[[items[i]]] == x[m, src[i]], na.rm = TRUE))
        cat(sprintf("  %-9s %-11s agreement\n", "live", "deposit"))
        for (i in 1:20)
            cat(sprintf("  %-9s %-11s %.4f\n", items[i], src[i], agree[i]))
        partA <- all(!is.na(agree) & agree == 1) && sum(!is.na(m)) == nrow(w)
        cat(sprintf("  all 20 columns identical: %s\n\n", partA))
    }
}

## ---- PART B: Figure 1 of the paper, refit on the live data -----------------
if (!requireNamespace("lavaan", quietly = TRUE))
    stop("lavaan is required for PART B")
suppressMessages(library(lavaan))

mod <- "
PA  =~ panas_1+panas_12+panas_17+panas_3+panas_9+panas_14+panas_10+panas_16+panas_5+panas_19
NA_ =~ panas_4+panas_2+panas_15+panas_18+panas_6+panas_13+panas_8+panas_11+panas_7+panas_20
panas_1~~panas_12; panas_12~~panas_17; panas_1~~panas_17
panas_3~~panas_9;  panas_9~~panas_14;  panas_3~~panas_14
panas_10~~panas_16; panas_5~~panas_19
panas_4~~panas_2; panas_2~~panas_15; panas_15~~panas_18
panas_6~~panas_13; panas_8~~panas_11; panas_7~~panas_20
"
fit <- lavaan::cfa(mod, data = w, estimator = "MLM")
s <- lavaan::standardizedSolution(fit)

# Figure 1 published standardised loadings, keyed by item number.
PUB_L <- c(panas_1=.60, panas_12=.64, panas_17=.57, panas_3=.64, panas_9=.73,
           panas_14=.66, panas_10=.52, panas_16=.69, panas_5=.58, panas_19=.59,
           panas_4=.78, panas_2=.65, panas_15=.66, panas_18=.74, panas_6=.59,
           panas_13=.44, panas_8=.75, panas_11=.70, panas_7=.68, panas_20=.64)
WORD <- c("Interested","Distressed","Excited","Upset","Strong","Guilty","Scared",
          "Hostile","Enthusiastic","Proud","Irritable","Alert","Ashamed","Inspired",
          "Nervous","Determined","Attentive","Jittery","Active","Afraid")
names(WORD) <- items

L <- s[s$op == "=~", c("lhs", "rhs", "est.std")]
L$pub <- PUB_L[L$rhs]
L$diff <- L$est.std - L$pub
cat("PART B1 -- standardised loadings, live refit vs Figure 1\n")
cat(sprintf("  %-9s %-13s %-4s %8s %8s %7s\n",
            "item", "word", "fac", "Fig.1", "refit", "diff"))
for (i in seq_len(nrow(L)))
    cat(sprintf("  %-9s %-13s %-4s %8.2f %8.3f %7.3f\n",
                L$rhs[i], WORD[L$rhs[i]], L$lhs[i], L$pub[i], L$est.std[i], L$diff[i]))
worstL <- max(abs(L$diff))
cat(sprintf("  largest loading deviation: %.4f\n\n", worstL))

# Figure 1 published residual correlations, in the model's own order.
PUB_R <- c(.02, .02, .13, .27, .02, -.04, -.02, .36,
           -.01, .29, .32, .24, .36, .56)
R <- s[s$op == "~~" & s$lhs != s$rhs & grepl("^panas_", s$lhs),
       c("lhs", "rhs", "est.std")]
R$pub <- PUB_R
R$diff <- R$est.std - R$pub
cat("PART B2 -- residual correlations, live refit vs Figure 1\n")
for (i in seq_len(nrow(R)))
    cat(sprintf("  %-9s ~~ %-9s (%s ~~ %s)  Fig.1 %6.2f  refit %6.3f  diff %6.3f\n",
                R$lhs[i], R$rhs[i], WORD[R$lhs[i]], WORD[R$rhs[i]],
                R$pub[i], R$est.std[i], R$diff[i]))
worstR <- max(abs(R$diff))
fcor <- s$est.std[s$op == "~~" & s$lhs == "PA" & s$rhs == "NA_"]
cat(sprintf("  largest residual-correlation deviation: %.4f\n", worstR))
cat(sprintf("  PA~~NA factor correlation: Fig.1 -0.41  refit %.3f\n\n", fcor))

TOL <- 0.01
pass <- worstL <= TOL && worstR <= TOL && abs(fcor - (-0.41)) <= TOL &&
        (is.na(partA) || isTRUE(partA))

cat("Scope of this evidence: the loading and residual-correlation profile is\n",
    "item-specific and pins 19 of 20 affect terms uniquely. It does NOT separate\n",
    "panas_5 (Strong) from panas_19 (Active): published loadings .58 vs .59, same\n",
    "mood subcategory, and they are each other's residual partner, so swapping\n",
    "those two words would not move any number above. Status is PARTIAL for that\n",
    "reason, not because anything here failed.\n", sep = "")

cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
