# verify_kohlmann_2016_phq9.R -- Step 5b check for kohlmann_2016_phq9 (batch_434).
#
# Claim: live item phq9_n is PHQ-9 item n in the standard PHQ-9/PHQ-D order
# (1 anhedonia, 2 depressed mood, 3 sleep, 4 energy, 5 appetite, 6 failure,
# 7 concentration, 8 psychomotor, 9 suicidal ideation), with resp 0..3 =
# "Ueberhaupt nicht / Not at all" .. "Beinahe jeden Tag / Nearly every day".
#
# Evidence: Kohlmann et al. (2016) PLOS ONE 10.1371/journal.pone.0156167, Results,
# "Frequency and range of depressive symptoms": the percentage of patients
# reporting each symptom on "at least several of the last 14 days" (resp >= 1),
# given per NAMED symptom. The nine published rates are all distinct at one
# decimal (closest pair: feeling down 38.0 vs appetite change 37.7), so matching
# each live item's rate to exactly one published symptom pins every item.
# Also checks the published PHQ-9 total, Table 1 "Depression, mean (SD) 5.5 (4.6)".
#
# NOT established: the exact wording respondents read. The study did not
# publish its German form; item text is the standard German PHQ-D, assumed.

suppressMessages(library(irw))
TABLE <- "kohlmann_2016_phq9"
ok <- TRUE

PUB <- c(phq9_1 = 55.7,  # loss of interest
         phq9_2 = 38.0,  # feeling down
         phq9_3 = 69.4,  # sleeping problems
         phq9_4 = 74.9,  # loss of energy
         phq9_5 = 37.7,  # appetite change
         phq9_6 = 21.9,  # feelings of failure
         phq9_7 = 39.3,  # trouble concentrating
         phq9_8 = 25.6,  # psychomotor change
         phq9_9 = 14.1)  # suicidal ideations
LAB <- c("loss of interest","feeling down","sleeping problems","loss of energy",
         "appetite change","feelings of failure","trouble concentrating",
         "psychomotor change","suicidal ideations")
# Published values are rounded to one decimal. Tolerance 0.10, not 0.05: live
# phq9_6 is 291/1332 = 21.847%, which rounds to 21.8 while the paper prints 21.9;
# the paper's own 95% CI (17.7-26.0) is centred on 21.85, so the paper evidently
# rounded 21.85 up. Every other rate reproduces at 0.05. At 0.10 each live rate
# still falls within tolerance of exactly one published symptom (closest rival
# pair is 38.0 vs 37.7, 0.3 apart).
TOL <- 0.10

d <- irw::irw_fetch(TABLE)
obs <- tapply(d$resp >= 1, d$item, mean)[names(PUB)] * 100
n   <- tapply(d$resp, d$item, length)[names(PUB)]

cat(sprintf("%-7s %-22s %6s %9s %9s  %s\n", "item", "published symptom", "n",
            "pub %>=1", "obs %>=1", "published symptoms within tol"))
for (i in names(PUB)) {
  hits <- LAB[abs(PUB - obs[i]) <= TOL]
  cat(sprintf("%-7s %-22s %6d %9.1f %9.3f  %s\n", i, LAB[names(PUB) == i], n[i],
              PUB[i], obs[i], paste(hits, collapse = ", ")))
  if (length(hits) != 1 || hits != LAB[names(PUB) == i]) ok <- FALSE
}

w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item",
             direction = "wide")
tot <- rowSums(w[, paste0("resp.phq9_", 1:9)])
cat(sprintf("\nPHQ-9 total (complete cases n=%d): mean %.2f SD %.2f; published 5.5 (4.6)\n",
            sum(!is.na(tot)), mean(tot, na.rm = TRUE), sd(tot, na.rm = TRUE)))
if (round(mean(tot, na.rm = TRUE), 1) != 5.5 || round(sd(tot, na.rm = TRUE), 1) != 4.6) ok <- FALSE

cat("Does NOT establish the administered wording (German form unpublished; standard PHQ-D assumed).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
