# verify_matarboumosleh_2017_spai26.R
#
# CLAIM UNDER TEST: each of the 26 abbreviated column codes in the S1 Dataset
# (which the processing script uses verbatim as `item`) carries the full item
# wording assigned to it in itemtables/batch_096/matarboumosleh_2017_spai26__items.csv,
# taken from Table 2 of Matar Boumosleh & Jaalouk (2017), PLOS ONE 12(8):e0182239.
#
# THE FALSIFIABLE PREDICTION: Table 2 publishes, for each of the 26 item
# wordings, the number and percentage of participants endorsing it ("somewhat
# agree" or "strongly agree", i.e. resp >= 3). If any two item_texts were
# swapped, the endorsement count attached to those two codes would swap with
# them. This is an exact-count check, not a similarity check.
#
# The percentage denominator is the item's own non-missing n, which varies by
# item (614-674) -- so the (count, percent) PAIR separates even the two items
# that share a count of 230 (35.2% vs 35.8%) and the two that share 173
# (27.5% vs 27.7%).

suppressMessages(library(irw))

TABLE <- "matarboumosleh_2017_spai26"

# Paper Table 2: item code (as mapped) -> published n endorsing, published %.
PUB <- rbind(
  # Compulsive Behavior (9)
  c("SameTmeIntrnt_Ngtv_Relations",        249, 37.5),
  c("UpstStp_SmrtPhnUse",                  195, 29.6),
  c("LifeJoylss_NoSmrtPhn",                187, 29.9),
  c("DcreasdHobbies_SmrtPhnUse",           173, 27.5),
  c("SmrtPhnUse_MreTmeMny",                233, 35.4),
  c("Spnd_LsstimeSmrtPhn_EffortsUselss",   211, 33.8),
  c("Vig_SmrtPhnUse",                      260, 39.3),
  c("NgtvePhysHlthEffcts_SmrtPhnUse",      238, 38.5),
  c("FailCntrlImplse_smrtphnUse",          230, 35.2),
  # Functional Impairment (8)
  c("PainBckEye_ExcSmrtPhnUse",            283, 43.5),
  c("TiredDaytime_latenightSmrtPhnUse",    223, 35.9),
  c("DcreasdSlpTimeQulty_SmrtPhnUse",      234, 38.1),
  c("SlptLss4HrsMreTh1_SmrtPhnUse",        240, 35.8),
  c("NgtveSchlJob_SmrtPhnUse",             230, 35.8),
  c("FavorSmrtPhn_SpndTimefrnds",          136, 21.2),
  c("DcreasdFmlyIntrction_SmrtPhnUse",     258, 40.7),
  c("IncrsdTimeSmrtPhnUse_SameSatsfction", 173, 27.7),
  # Withdrawal (6)
  c("Rstlss_NoSmrtphn",                    268, 39.9),
  c("TnseStp_Smrtphn_Use",                 217, 32.4),
  c("CannotHveMeal_NosmrtPhn",             118, 18.9),
  c("FrstThghtSmrtphnUse_WakeUp",          409, 63.5),
  c("MissStp_SmrtPhnUse",                  294, 46.2),
  c("UrgeSmrtPhnUse_OnceStpUse",           267, 42.8),
  # Tolerance (3)
  c("hook_smrtPhn",                        330, 49.5),
  c("RcntSigIncTime_SmrtPhnUseWk",         269, 41.0),
  c("ExcessveSmrtPhn_Use",                 366, 54.3)
)
codes <- PUB[, 1]
pub_n <- as.numeric(PUB[, 2])
pub_p <- as.numeric(PUB[, 3])

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

obs_n <- sapply(codes, function(k) sum(d$resp[d$item == k] >= 3))
tot_n <- sapply(codes, function(k) sum(d$item == k))
obs_p <- round(100 * obs_n / tot_n, 1)

cat(sprintf("%-38s %7s %7s %7s %7s %6s\n",
            "item", "pub_n", "obs_n", "pub_%", "obs_%", "N"))
for (i in seq_along(codes))
  cat(sprintf("%-38s %7d %7d %7.1f %7.1f %6d\n",
              codes[i], pub_n[i], obs_n[i], pub_p[i], obs_p[i], tot_n[i]))

bad_n <- sum(obs_n != pub_n)
bad_p <- sum(abs(obs_p - pub_p) > 0.05)
cat(sprintf("\ncount mismatches: %d/26   percent mismatches (>0.05pp): %d/26\n",
            bad_n, bad_p))

cat("Note: this pins every one of the 26 item texts to its own code, because all 26\n",
    "(count, percent) pairs are distinct. It does NOT verify the option anchors\n",
    "(1=strongly disagree .. 4=strongly agree); those are taken from the paper's\n",
    "Methods text and are only corroborated by the endorsement direction implied by\n",
    "resp>=3 reproducing Table 2.\n", sep = "")

cat(if (bad_n == 0 && bad_p == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
