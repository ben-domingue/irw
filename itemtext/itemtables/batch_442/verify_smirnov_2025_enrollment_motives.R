# verify_smirnov_2025_enrollment_motives.R -- Step 5b, route 1 (per-item descriptive statistics).
#
# Claim: each deposit column (IRW item code) carries the Fig 1 option wording shipped as its
# item_text. Fig 1 of Smirnov & Tarasova (2025, PLOS ONE 10.1371/journal.pone.0330679) prints the
# option wording against a selection percentage but no code, so the prediction is that each
# item's live selection rate (mean of 0/1 resp) reproduces the percentage printed beside the
# wording we attached to it. All eleven published percentages are distinct (87,64,48,44,40,29,
# 28,18,12,9,4), so any swap of item_text between two items breaks at least two comparisons.
# The deferment option is annotated "(male only)" in Fig 1 and its 29% is the rate among men;
# the live table carries cov_gender, so that item is compared on the male subsample.

suppressMessages(library(irw))
TABLE <- "smirnov_2025_enrollment_motives"

PUBLISHED <- c(   # Fig 1 wording -> printed percentage
  motive_recieve_degree     = 87,  # To receive PhD degree
  motive_research_skills    = 64,  # To develop research skills
  motive_teaching_skills    = 48,  # To develop teaching skills
  motive_keep_topic         = 44,  # To continue research in the field of interest
  motive_career_academic    = 40,  # To move forward in academic career
  motive_deferment          = 29,  # To get the deferment from the army (male only)
  motive_work_university    = 28,  # To employ in the university / scientific organization
  motive_career_nonacademic = 18,  # To move forward in non-academic career
  motive_travel             = 12,  # To get an opportunity to travel abroad
  motive_recieve_diploma    =  9,  # To receive the diploma without defending the thesis
  motive_dormitory          =  4)  # To get a place in a dormitory

d <- as.data.frame(irw::irw_fetch(TABLE))
obs <- sapply(names(PUBLISHED), function(i) {
  s <- d[d$item == i, ]
  if (i == "motive_deferment") s <- s[s$cov_gender == "male", ]
  100 * mean(s$resp)
})

cat(sprintf("%-27s %9s %9s %7s\n", "item", "published", "observed", "diff"))
for (i in names(PUBLISHED))
  cat(sprintf("%-27s %9d %9.2f %7.2f\n", i, PUBLISHED[[i]], obs[[i]], obs[[i]] - PUBLISHED[[i]]))
cat(sprintf("deferment over ALL respondents (not the Fig 1 base): %.2f\n",
            100 * mean(d$resp[d$item == "motive_deferment"])))

ok_round <- all(abs(obs - PUBLISHED) <= 0.5 + 1e-9)
# Distinguishability: nearest-published-value assignment must recover the shipped pairing for every item.
nearest <- sapply(obs, function(o) names(PUBLISHED)[which.min(abs(PUBLISHED - o))])
ok_assign <- all(nearest == names(obs))
cat(sprintf("\nall within rounding (|diff| <= 0.5): %s; nearest-percentage assignment reproduces all 11 pairings: %s\n",
            ok_round, ok_assign))
cat("Does NOT establish: that the English Fig 1 wording is what respondents read (survey was Russian);\n",
    "it establishes only which printed option each code is.\n", sep = "")
cat(if (ok_round && ok_assign) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
