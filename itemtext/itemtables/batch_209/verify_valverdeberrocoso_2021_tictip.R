# verify_valverdeberrocoso_2021_tictip.R -- Step 5b, route 1 (per-item descriptives).
#
# Claim under test: TICTIP01..TICTIP28 in the IRW table are items 1..28 of
# Table 2 of Valverde-Berrocoso et al. (2021) PLOS ONE 16(9):e0256283, whose
# wording (Spanish original in S1 File, English in Table 2) is what shipped.
#
# Falsifiable prediction: the published M and DT for item k must reproduce from
# the live responses to TICTIP<k>. Any permutation of the text across items
# breaks it, provided the (M, SD) pairs are mutually distinguishable -- which the
# script also checks rather than assuming.

suppressMessages(library(irw))

TABLE <- "valverdeberrocoso_2021_tictip"

# Paper Table 2, "Regular teaching practice with ICT", items 1-28: M and DT.
PUB_M  <- c(5.06,5.31,4.90,4.13,4.01,4.29,3.88,4.43,4.31,3.25,4.29,3.56,4.25,3.58,
            4.05,3.34,3.75,3.75,3.65,3.57,4.30,4.53,3.71,4.23,4.35,5.41,5.15,3.41)
PUB_SD <- c(1.045,0.809,1.084,1.353,1.301,1.169,1.538,1.254,1.689,1.783,1.249,1.338,
            1.252,1.474,1.287,1.473,1.399,1.431,1.604,1.436,1.157,1.187,1.439,1.417,
            1.446,0.878,1.069,1.581)
TOL_M  <- 0.01
TOL_SD <- 0.01

items <- sprintf("TICTIP%02d", 1:28)
d <- irw::irw_fetch(TABLE)
obs_m  <- tapply(d$resp, d$item, mean)[items]
obs_sd <- tapply(d$resp, d$item, stats::sd)[items]

cat(sprintf("%-9s %8s %8s %7s   %8s %8s %7s\n",
            "item", "pub_M", "obs_M", "dM", "pub_SD", "obs_SD", "dSD"))
for (i in 1:28)
    cat(sprintf("%-9s %8.2f %8.2f %7.3f   %8.3f %8.3f %7.3f\n",
                items[i], PUB_M[i], obs_m[i], obs_m[i] - PUB_M[i],
                PUB_SD[i], obs_sd[i], obs_sd[i] - PUB_SD[i]))

worst_m  <- max(abs(obs_m  - PUB_M))
worst_sd <- max(abs(obs_sd - PUB_SD))
cat(sprintf("\nlargest |dM| = %.4f (tol %.2f); largest |dSD| = %.4f (tol %.2f)\n",
            worst_m, TOL_M, worst_sd, TOL_SD))

# Discrimination: how many of the 28 published (M, SD) pairs are unique, i.e. how
# many items this route can actually tell apart from every other item.
key <- paste(sprintf("%.2f", PUB_M), sprintf("%.3f", PUB_SD))
n_unique <- sum(table(key)[key] == 1)
cat(sprintf("published (M, SD) pairs unique to one item: %d of 28\n", n_unique))
dupM <- names(which(table(sprintf("%.2f", PUB_M)) > 1))
cat("items tied on M alone (separated here by SD): ",
    paste(items[sprintf("%.2f", PUB_M) %in% dupM], collapse = ", "), "\n", sep = "")

cat("Note: this route establishes the item_text<->item mapping for all 28 items.\n",
    "It does NOT establish the option_text<->resp mapping: the 1=Nunca..6=Siempre\n",
    "anchors are taken from the S1 File legend printed above the scale and from the\n",
    "paper's own '(1) Never ... (6) Always' statement, not from any per-level count.\n",
    sep = "")

ok <- worst_m <= TOL_M && worst_sd <= TOL_SD && n_unique == 28
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
