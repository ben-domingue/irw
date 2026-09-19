# verify_taylorabdulai_2025_incentives.R -- copied from references/verify_template.R
#
# Claim: each IRW item code (the S1 xlsx column name) carries the Table 4 label
# shipped in item_text, and resp 1 = "Yes" (the option counted in Table 4).
#
# Falsifiable prediction: Taylor-Abdulai et al. (2025) PLOS ONE 10.1371/journal.pone.0319798,
# Table 4, block "What will make you accept COVID-19 vaccine", prints the frequency of each
# factor out of N = 377. Those seven frequencies are all distinct, so matching the live
# per-item count of resp == 1 against them pins every item to exactly one label, and a
# flipped resp direction would give 377 - f instead (none of which is in the published set).

suppressMessages(library(irw))

TABLE <- "taylorabdulai_2025_incentives"
N_PUB <- 377

# item code -> (shipped label, published Table 4 frequency)
PUBLISHED <- data.frame(
  item  = c("Covid_19_Financial_Incentive", "Covid_19_monetary_rewards",
            "Covid_19_free_of_charge", "Covid_19_adequate_info",
            "Covid_19_R_Travel", "Covid_19_employment_Condition",
            "Covid_19_positive_feedback"),
  label = c("Financial incentive", "Monetary rewards to health workers",
            "Vaccine given for free", "Adequate information about vaccine",
            "Requirement to travel", "Employment condition",
            "Positive feedback from vaccinated people"),
  freq  = c(40, 16, 63, 136, 47, 35, 75),
  stringsAsFactors = FALSE)

d <- irw::irw_fetch(TABLE)
yes <- tapply(d$resp == 1, d$item, sum)
n   <- tapply(d$resp, d$item, length)

PUBLISHED$live_yes <- as.numeric(yes[PUBLISHED$item])
PUBLISHED$live_n   <- as.numeric(n[PUBLISHED$item])
PUBLISHED$live_no  <- PUBLISHED$live_n - PUBLISHED$live_yes

cat(sprintf("%-30s %-42s %6s %8s %7s %6s\n", "item", "Table 4 label", "pub", "live=1", "live=0", "n"))
for (i in seq_len(nrow(PUBLISHED)))
  with(PUBLISHED[i, ], cat(sprintf("%-30s %-42s %6d %8d %7d %6d\n",
                                   item, label, freq, live_yes, live_no, live_n)))

exact      <- all(PUBLISHED$live_yes == PUBLISHED$freq)
all_n      <- all(PUBLISHED$live_n == N_PUB)
distinct   <- length(unique(PUBLISHED$freq)) == nrow(PUBLISHED)
# Would any permutation of labels also match? Only if two published counts were equal.
# Would a flipped resp direction match? Only if some 377 - f were in the published set.
flip_hits  <- sum((N_PUB - PUBLISHED$freq) %in% PUBLISHED$freq)

cat(sprintf("\nexact per-item match of live resp==1 counts to Table 4: %s\n", exact))
cat(sprintf("every item n == %d: %s\n", N_PUB, all_n))
cat(sprintf("published frequencies all distinct (route separates every item): %s\n", distinct))
cat(sprintf("published frequencies reproduced by a flipped (resp==0) reading: %d of 7\n", flip_hits))
cat("Note: this verifies code<->label and 1=Yes. It does not establish that the Table 4\n",
    "labels are the questionnaire's literal wording -- the questionnaire itself is unpublished.\n", sep = "")

cat(if (exact && all_n && distinct && flip_hits == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
