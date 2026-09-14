# verify_sinche_2017_skill_importance.R -- Step 5b mapping check (batch_176).
#
# Claim: skill_imp_i  <->  S1 File .sav column Employ_Skill_iR, whose SPSS variable
# label names skill i (the processing script data/sinche_2017_transferable_skills.py
# assigns the IRW code positionally: enumerate over [Employ_Skill_1R..15R] -> skill_imp_{i+1}).
#
# Two independent predictions, both hard-coded (neither source will change):
#  A. SOURCE: per-item 1..5 frequency vectors computed from the S1 File .sav
#     (10.1371/journal.pone.0185023.s001), column Employ_Skill_iR. Under the claimed
#     mapping each live item must reproduce its column's vector cell for cell, and
#     must match NO other column's vector (so the route separates every item).
#  B. PAPER: Table 3 "Employed Skill Mean" per named skill (2 dp).

suppressMessages(library(irw))
TABLE <- "sinche_2017_skill_importance"

SRC <- rbind(
  c(117, 229, 408, 1219, 1841),  #  1 Discipline-specific knowledge
  c(32, 54, 172, 1027, 2520),    #  2 Ability to gather and interpret information
  c(63, 209, 322, 1050, 2154),   #  3 Ability to analyze data
  c(50, 123, 294, 1051, 2276),   #  4 Ability to manage a project
  c(29, 40, 166, 1009, 2559),    #  5 Oral communication skills
  c(26, 74, 211, 1056, 2435),    #  6 Written communication skills
  c(43, 97, 316, 1067, 2272),    #  7 Ability to work on a team
  c(29, 37, 155, 1009, 2567),    #  8 Ability to make decisions and solve problems
  c(95, 307, 689, 1137, 1562),   #  9 Ability to manage others
  c(67, 141, 443, 1356, 1793),   # 10 Creativity/innovative thinking
  c(22, 28, 175, 1005, 2557),    # 11 Time management
  c(70, 142, 463, 1238, 1878),   # 12 Ability to set a vision and goals
  c(191, 469, 1050, 1091, 958),  # 13 Career planning and awareness skills
  c(41, 72, 276, 1190, 2207),    # 14 Ability to learn quickly
  c(74, 193, 476, 989, 2052)     # 15 Ability to work with people outside the organization
)
TABLE3 <- c(4.16, 4.56, 4.32, 4.42, 4.59, 4.53, 4.43, 4.59, 3.99, 4.23, 4.60, 4.24, 3.57, 4.44, 4.26)

d <- irw::irw_fetch(TABLE)
items <- paste0("skill_imp_", 1:15)
LIVE <- t(sapply(items, function(it) tabulate(d$resp[d$item == it], nbins = 5)))
obs_mean <- as.numeric(tapply(d$resp, d$item, mean)[items])

ok <- TRUE
cat(sprintf("%-13s %-32s %-32s %6s %6s %5s\n", "item", "live counts 1..5", "source col counts 1..5",
            "T3", "live", "match"))
for (i in 1:15) {
  exact <- all(LIVE[i, ] == SRC[i, ])
  others <- which(apply(SRC, 1, function(r) all(r == LIVE[i, ])))
  uniq <- identical(as.integer(others), as.integer(i))
  mean_ok <- abs(obs_mean[i] - TABLE3[i]) <= 0.005 + 1e-9
  cat(sprintf("%-13s %-32s %-32s %6.2f %6.3f %5s\n", items[i],
              paste(LIVE[i, ], collapse = "/"), paste(SRC[i, ], collapse = "/"),
              TABLE3[i], obs_mean[i],
              if (exact && uniq && mean_ok) "yes" else "NO"))
  if (!(exact && uniq && mean_ok)) ok <- FALSE
}
cat(sprintf("\nitems whose live vector matches its own source column and only that column: %d/15\n",
            sum(sapply(1:15, function(i) identical(as.integer(which(apply(SRC, 1, function(r) all(r == LIVE[i, ])))), i)))))
cat(sprintf("largest |live mean - Table 3|: %.4f (tolerance 0.005, rounding)\n", max(abs(obs_mean - TABLE3))))
cat("Does NOT establish: which wording respondents saw for scale points 2-4 (unpublished),\n",
    "nor resolve the .sav value labels (agree/disagree) vs the paper's anchors (importance);\n",
    "both directions are 1=lowest..5=highest, which Table 3's means confirm.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
