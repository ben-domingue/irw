# verify_naja_2024_challenges.R
#
# Claim under test: each item code carries the challenge label shipped in
# item_text, and resp=1 means the respondent SELECTED that challenge.
#
# Falsifiable prediction: Naja et al. (2024) PLOS ONE 19(1):e0295904 report,
# in the Results ("job challenges during the pandemic ... as displayed in
# Fig 1"), the number of dieticians endorsing each challenge out of 371:
#   work-life balance 160 (43.1%), face-to-face counseling 147 (39.6%),
#   seeing enough patients 117 (31.5%), job security 99 (26.6%),
#   job satisfaction 75 (20.2%).
# All five counts are distinct, so this pins EVERY item against every other,
# and the direction of the 0/1 coding at the same time (a flipped coding would
# give 211/224/254/272/296).

suppressMessages(library(irw))

TABLE <- "naja_2024_challenges"

PUBLISHED <- c(work_life_balance = 160, face_to_face_counseling = 147,
               seeing_enough_patients = 117, job_security = 99,
               job_satisfaction = 75)

d <- irw::irw_fetch(TABLE)
obs <- tapply(d$resp, d$item, function(x) sum(x == 1))
obs <- obs[names(PUBLISHED)]
n   <- tapply(d$resp, d$item, length)[names(PUBLISHED)]

cat(sprintf("%-24s %10s %10s %8s %8s\n", "item", "published", "observed", "diff", "n"))
for (i in seq_along(obs))
    cat(sprintf("%-24s %10d %10d %8d %8d\n",
                names(obs)[i], PUBLISHED[i], obs[i], obs[i] - PUBLISHED[i], n[i]))

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation: %d selections (tolerance 0)\n", worst))

cat("Note: the five published counts are mutually distinct (160/147/117/99/75),\n",
    "so no permutation of the five labels reproduces them; the check also rules\n",
    "out a reversed 0/1 coding. It does NOT verify the exact wording shipped in\n",
    "item_text -- the paper's methods list four of the five choices verbatim and\n",
    "'Seeing enough patients' is taken from the S1 column header.\n", sep = "")

cat(if (worst == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
