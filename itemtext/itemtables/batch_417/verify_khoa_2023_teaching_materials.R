# verify_khoa_2023_teaching_materials.R -- batch_417, Step 5b.
#
# Claim: live item codes TEM1..TEM4 carry the wording that Khoa & Huynh (2023),
# Data in Brief 49:109454 (doi 10.1016/j.dib.2023.109454, PMC10415701) print
# against those same codes ("TEM1 Knowledge gained via ...", ... "TEM4 From my
# perspective ..."). That tie is a label match in the paper (explicit-code
# exemption). What this script checks is that the LIVE codes are the paper's
# codes -- i.e. no rename/shift between the paper's variables and IRW's -- by
# matching the paper's code-labelled descriptive table (mean, SD per item) against
# the live data, and requiring each live item's nearest published (mean, SD) row to
# be its own code.
#
# Does NOT establish: that the questionnaire respondents saw was in English (the
# deposit's Questionnaire.pdf is English; the paper does not state the administered
# language). TEM1 and TEM2 means differ by only 0.01, so the SD column is what
# separates them (1.060 vs 1.052).

suppressMessages(library(irw))
TABLE <- "khoa_2023_teaching_materials"

# Data in Brief 2023, descriptive-statistics table (Mean, Std. deviation), rows TEM1-TEM4.
PUB <- data.frame(item = paste0("TEM", 1:4),
                  mean = c(3.86, 3.85, 3.94, 3.80),
                  sd   = c(1.060, 1.052, 0.999, 1.046))

d <- irw::irw_fetch(TABLE)
obs <- data.frame(item = PUB$item,
                  mean = as.numeric(tapply(d$resp, d$item, mean)[PUB$item]),
                  sd   = as.numeric(tapply(d$resp, d$item, sd)[PUB$item]))

cat(sprintf("%-6s %8s %8s %8s %8s %-8s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD", "nearest"))
ok <- TRUE
for (i in seq_len(nrow(PUB))) {
  # distance of live item i to every published row, SD weighted so 0.001 counts
  dist <- abs(obs$mean[i] - PUB$mean) / 0.01 + abs(obs$sd[i] - PUB$sd) / 0.001
  nearest <- PUB$item[which.min(dist)]
  good <- nearest == PUB$item[i] &&
          abs(obs$mean[i] - PUB$mean[i]) <= 0.005 &&
          abs(obs$sd[i] - PUB$sd[i]) <= 0.0006
  ok <- ok && good
  cat(sprintf("%-6s %8.2f %8.3f %8.3f %8.3f %-8s %s\n", PUB$item[i], PUB$mean[i],
              obs$mean[i], PUB$sd[i], obs$sd[i], nearest, if (good) "ok" else "MISMATCH"))
}
cat("\nEach live code reproduces the paper's code-labelled mean (to 2 dp) and SD (to 3 dp),\n",
    "and its nearest published row is its own code; the paper prints each item's wording\n",
    "against that same code, so code->text is a label match, not an order inference.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
