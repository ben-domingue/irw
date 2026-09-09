# verify_kuehner_2017_mw_rumination.R -- Step 5b, route 1 (per-item descriptive statistics).
#
# CLAIM UNDER TEST: item "MW" carries the mind-wandering probe ("At the time of the
# beep, were you thinking about something other than what you were currently doing?",
# 1 = completely on task .. 7 = completely off task) and item "RUM" carries the
# uncontrollable-rumination item ("At the moment, I am stuck on negative thoughts and
# cannot disengage from them"). If the two texts were swapped, the numbers below flip.
#
# FALSIFIABLE PREDICTION: Kuehner, Welz, Reinhard & Alpers (2017), PLOS ONE 12(9):e0184488,
# Table 1 ("Ambulatory assessments") publishes, for the same five days of ambulatory
# assessment this table holds:
#     Mind wandering               M = 3.16, SD = 1.90, min 1, max 7
#     Uncontrollable rumination    M = 1.90, SD = 1.37, min 1, max 7
# The two means are 1.26 points apart on a 7-point scale, so they identify which code is
# which outright. (Table 1's values are person-aggregated; the pooled observation-level
# values below differ only in the second decimal.)

suppressMessages(library(irw))

TABLE <- "kuehner_2017_mw_rumination"
PUB_M  <- c(MW = 3.16, RUM = 1.90)
PUB_SD <- c(MW = 1.90, RUM = 1.37)
TOL_M  <- 0.05
TOL_SD <- 0.05

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]

obs_m  <- tapply(d$resp, d$item, mean)[names(PUB_M)]
obs_sd <- tapply(d$resp, d$item, stats::sd)[names(PUB_SD)]

cat(sprintf("%-5s %10s %10s %9s %10s %10s %9s\n",
            "item", "pub M", "obs M", "diff", "pub SD", "obs SD", "diff"))
for (i in names(PUB_M))
    cat(sprintf("%-5s %10.2f %10.2f %9.3f %10.2f %10.2f %9.3f\n",
                i, PUB_M[i], obs_m[i], obs_m[i] - PUB_M[i],
                PUB_SD[i], obs_sd[i], obs_sd[i] - PUB_SD[i]))

# Cross-check: the swapped assignment would have to be rejected, so show it explicitly.
swapped <- max(abs(obs_m[c("RUM", "MW")] - PUB_M))
cat(sprintf("\nfit under the SHIPPED assignment : largest |diff| in M = %.3f\n",
            max(abs(obs_m - PUB_M))))
cat(sprintf("fit under the SWAPPED assignment : largest |diff| in M = %.3f\n", swapped))

ok <- max(abs(obs_m - PUB_M)) <= TOL_M && max(abs(obs_sd - PUB_SD)) <= TOL_SD &&
      swapped > max(abs(obs_m - PUB_M))

cat("Note: with only two items this route separates every item from every other item,\n",
    "so it is decisive for item<->item_text. It says NOTHING about the option anchors:\n",
    "only resp 1 and 7 of MW are labelled in the paper, and the paper's statement that the\n",
    "scale runs 1 = completely on task to 7 = completely off task is the sole evidence for\n",
    "their direction; the observed mean of 3.15 is consistent with, but does not prove, it.\n", sep = "")

cat(if (isTRUE(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
