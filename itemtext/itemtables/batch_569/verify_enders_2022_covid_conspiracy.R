# verify_enders_2022_covid_conspiracy.R -- Step 5b re-runnable check (batch_569)
#
# CLAIM. COVCONS_1..7 carry:
#   COVCONS_1  (not published; do-file name `cexaggerate`, outside the published scale) -- item_text blank
#   COVCONS_2  "Coronavirus was purposely created and released as part of a conspiracy."          (Table 1 row 2, 25%)
#   COVCONS_3  "The number of deaths related to the coronavirus has been exaggerated."            (Table 1 row 1, 29%)
#   COVCONS_4  "The coronavirus is being used to force a dangerous and unnecessary vaccine ..."   (Table 1 row 3, 20%)
#   COVCONS_5  "5G cell phone technology is responsible for the spread of the coronavirus."       (Table 1 row 6,  9%)
#   COVCONS_6  "Bill Gates is behind the coronavirus pandemic."                                   (Table 1 row 5, 11%)
#   COVCONS_7  "The coronavirus is being used to install tracking devices inside our bodies."     (Table 1 row 4, 12%)
# Table 1 of Enders et al. (2022, PLOS ONE e0276082) is sorted by % agreeing, NOT by code:
# its "(Item 1)".."(Item 6)" labels are rank positions and do not match the COVCONS suffixes.
#
# DERIVATION. data/enders_2022_conspiracy_vaccine.py keeps the Qualtrics column names
# (COVCONS_1..7) as `item`; the deposit's Raw Data.csv has no question-text row and no codebook.
# The study's own Analyses.do (OSF 6a7et) renames them cexaggerate, cpurpose, deaths, covidvaxx,
# cellphone, billgates, tracking (lines 178-190) and builds the published scale as
# `alpha cpurpose-tracking` = COVCONS_2..7 (line 200) -- mnemonics, not wording.
#
# ROUTE (independent of the do-file names).
#  (a) Published scale stats (alpha .90, M 2.20, SD 1.04, 6 items): computed for every
#      leave-one-out 6-item subset of COVCONS_1..7; only the subset dropping COVCONS_1 must match
#      at 2 dp. This pins COVCONS_1 as the unpublished 7th item.
#  (b) Published % agree ("agree"/"strongly agree", i.e. resp >= 4) for the six items:
#      29/25/20/12/11/9, all distinct integers. Each of COVCONS_2..7 must round to its claimed
#      value, and the claim must be the ONLY assignment of the six texts to COVCONS_2..7 that
#      reproduces all six rounded percentages.

suppressMessages(library(irw))

TABLE <- "enders_2022_covid_conspiracy"
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
it <- paste0("COVCONS_", 1:7)

# (a) which 6-item subset is the published scale?
PUB_SCALE <- c(M = 2.20, SD = 1.04, alpha = 0.90)
al <- function(X) {
  X <- X[complete.cases(X), ]; k <- ncol(X); s <- rowMeans(X)
  c(M = mean(s), SD = sd(s), alpha = k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))))
}
cat("(a) published 6-item scale: M 2.20, SD 1.04, alpha .90\n")
match_a <- logical(7)
for (k in 1:7) {
  s <- al(w[, it[-k]])
  match_a[k] <- all(round(s, 2) == PUB_SCALE)
  cat(sprintf("  drop %-9s  M %.4f  SD %.4f  alpha %.4f  %s\n", it[k], s["M"], s["SD"], s["alpha"],
              if (match_a[k]) "<- matches at 2 dp" else ""))
}
ok_a <- sum(match_a) == 1 && match_a[1]

# (b) % agree per item vs Table 1
TXT <- c("deaths exaggerated", "purposely created", "force vaccine", "tracking devices", "Bill Gates", "5G")
PUB_PCT <- c(29, 25, 20, 12, 11, 9)                      # Table 1 rows 1..6
CLAIM <- c(COVCONS_2 = 2, COVCONS_3 = 1, COVCONS_4 = 3, COVCONS_5 = 6, COVCONS_6 = 5, COVCONS_7 = 4)
obs <- sapply(it, function(i) 100 * mean(w[[i]] >= 4, na.rm = TRUE))
cat("\n(b) % agree (resp >= 4), live vs Table 1 under the claim\n")
cat(sprintf("  %-9s %8.3f  (not in Table 1; rounds to %d, which collides with 'purposely created' 25 -- (a) is what separates it)\n",
            "COVCONS_1", obs[1], round(obs[1])))
for (i in names(CLAIM))
  cat(sprintf("  %-9s %8.3f  -> %2d   Table 1: %-20s %2d\n", i, obs[i], round(obs[i]), TXT[CLAIM[i]], PUB_PCT[CLAIM[i]]))
ok_claim <- all(round(obs[names(CLAIM)]) == PUB_PCT[CLAIM])

library(utils)
perms <- as.matrix(expand.grid(rep(list(1:6), 6))); perms <- perms[apply(perms, 1, function(z) length(unique(z)) == 6), ]
fits <- apply(perms, 1, function(p) all(round(obs[names(CLAIM)]) == PUB_PCT[p]))
cat(sprintf("\n  assignments of the 6 texts to COVCONS_2..7 reproducing all six rounded %%: %d of %d\n",
            sum(fits), nrow(perms)))
ok_b <- ok_claim && sum(fits) == 1 && all(perms[which(fits), ] == CLAIM)

cat("\nNOT established: the wording of COVCONS_1 (it is shipped blank); the within-{4,5} order\n",
    "(the footnote names 'agree' and 'strongly agree' but the >=4 cut only shows those two are 4 and 5\n",
    "together; 5 = strongly agree follows the ascending convention and higher-is-more-belief).\n", sep = "")
cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
