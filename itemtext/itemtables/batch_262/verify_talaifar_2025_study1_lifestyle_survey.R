# verify_talaifar_2025_study1_lifestyle_survey.R -- batch_262
#
# Claim: ls_1..ls_93 carry the wording the study's own OSF codebook
# ("Study 1 - Actual Lifestyle Polarization/Survey Materials/Handbook_ Fall 2016
# Survey measures.pdf", osf.io/6k2cp; Spring 2017 handbook osf.io/3mtxr is
# identical for ls_1..ls_93) prints against each column name. The IRW code IS
# the source column name (data/talaifar_2025_lifestyle_polarization.py:
# ls_cols = [f"ls_{i}" for i in range(1, 94)], melted without renaming).
#
# Route 8 + cross-block pairing: the survey asks about the same behaviour
# in different blocks (activity / place / people), so the codebook's wording
# predicts SPECIFIC cross-block partners. If the text were shifted or
# permuted, these partners would not be each other's strongest correlate.
suppressMessages(library(irw))
TABLE <- "talaifar_2025_study1_lifestyle_survey"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
m <- cor(w[, -1], use = "pairwise.complete.obs"); diag(m) <- NA
mu <- tapply(d$resp, d$item, mean)

ok <- TRUE
# 1. predicted strongest partner (codebook text -> expected partner)
pairs <- rbind(
  c("ls_19", "ls_74", "religious service  <-> Religious facility"),
  c("ls_71", "ls_50", "Gym                <-> Exercise, do sports"),
  c("ls_92", "ls_56", "Significant other  <-> Go on dates"),
  c("ls_76", "ls_87", "Work (place)       <-> Co-workers"),
  c("ls_65", "ls_69", "Bar                <-> Fraternity/Sorority house"),
  c("ls_88", "ls_18", "Family (people)    <-> Spend time with your family"),
  c("ls_89", "ls_64", "Friends (people)   <-> Socialize in person with friends"))
cat("Predicted top correlate (codebook partner):\n")
for (i in seq_len(nrow(pairs))) {
  a <- pairs[i, 1]; b <- pairs[i, 2]
  top <- names(which.max(m[a, ]))
  hit <- top == b
  cat(sprintf("  %-6s -> %-6s r=%5.2f  observed top=%-6s %s  [%s]\n",
              a, b, m[a, b], top, if (hit) "OK" else "MISS", pairs[i, 3]))
  ok <- ok && hit
}
# 2. a signed prediction: Mac vs PC are substitutes
cat(sprintf("  ls_53 (Use a Mac) vs ls_54 (Use a PC): r=%.2f (predicted strongly negative)\n",
            m["ls_53", "ls_54"]))
ok <- ok && m["ls_53", "ls_54"] < -0.5
# 3. semantic coherence of means (10-point frequency scale)
cat("Means, predicted high: shower", round(mu["ls_16"], 2), " campus", round(mu["ls_68"], 2),
    " home", round(mu["ls_72"], 2), " social media", round(mu["ls_57"], 2), "\n")
cat("Means, predicted low : cigarette", round(mu["ls_24"], 2), " psychologist", round(mu["ls_31"], 2),
    " spa", round(mu["ls_36"], 2), " co-workers", round(mu["ls_87"], 2), "\n")
ok <- ok && min(mu[c("ls_16", "ls_68", "ls_72", "ls_57")]) > 8.5 &&
  max(mu[c("ls_24", "ls_31", "ls_36", "ls_87")]) < 4
cat("\nDoes NOT establish: order among items without a distinctive partner or\n",
    "distribution (e.g. ls_78..ls_85 situation items among themselves). The item\n",
    "codes are the codebook's own variable names, which is what ties those.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
