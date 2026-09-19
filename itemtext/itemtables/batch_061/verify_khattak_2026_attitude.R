# Mapping verification for khattak_2026_attitude.
#
# Claim: attitude1/2/3/5 carry the four Section Three attitude statements of the
# study's own questionnaire (supplementary file peerj-14-21098-s004.docx, which
# annotates each answer option with its SPSS code), and resp 1 = Agree,
# 2 = Disagree.
#
# Falsifiable prediction: Table 2 of Khattak et al. (2026), PeerJ 13:e21098,
# prints Agree/Disagree n for each of the four statements, and all four counts
# are distinct. So the counts pin every item to exactly one statement AND fix
# the direction of the 1/2 coding at the same time.
#
# NOTE ON DIRECTION: the questionnaire's own header row annotates the attitude
# columns "Strongly Disagree (1) | Strongly Agree (2)". That annotation is wrong:
# the .sav value labels read 1 = "agree", 2 = "disagree", and the counts below
# only reconcile with the paper under the .sav direction. This script is what
# settles it.

suppressMessages(library(irw))

TABLE <- "khattak_2026_attitude"

# Paper Table 2, "Attitudes of dentists toward BLS/CPR", overall row (N = 400).
PUBLISHED <- list(
  attitude1 = c(Agree = 342, Disagree =  58),  # CPR is a critical skill for all dental professionals
  attitude2 = c(Agree = 362, Disagree =  38),  # I feel morally obligated to help during a medical emergency
  attitude3 = c(Agree = 296, Disagree = 104),  # BLS training should be mandatory for licensure
  attitude5 = c(Agree = 118, Disagree = 282)   # I believe BLS is not relevant in dental settings
)

d <- irw::irw_fetch(TABLE)              # 1,600 rows -- a negligible export
tab <- table(d$item, d$resp)

cat(sprintf("%-10s %14s %14s %14s %14s\n",
            "item", "pub Agree", "live resp==1", "pub Disagree", "live resp==2"))
ok <- TRUE
for (it in names(PUBLISHED)) {
  live1 <- as.integer(tab[it, "1"]); live2 <- as.integer(tab[it, "2"])
  p <- PUBLISHED[[it]]
  cat(sprintf("%-10s %14d %14d %14d %14d\n", it, p[["Agree"]], live1, p[["Disagree"]], live2))
  if (live1 != p[["Agree"]] || live2 != p[["Disagree"]]) ok <- FALSE
}

# The counts are distinct across items, so a permutation of item_text would break
# this check; show that explicitly rather than asserting it.
pub1 <- vapply(PUBLISHED, function(x) x[["Agree"]], numeric(1))
cat(sprintf("\ndistinct published Agree counts: %d of %d (%s)\n",
            length(unique(pub1)), length(pub1), paste(pub1, collapse = ", ")))

# And the reversed reading fails, which is what rules out the questionnaire's
# own (1)=Strongly Disagree annotation.
rev_ok <- all(vapply(names(PUBLISHED), function(it)
  as.integer(tab[it, "1"]) == PUBLISHED[[it]][["Disagree"]], logical(1)))
cat("reversed direction (1 = Disagree) also fits: ", rev_ok, "\n", sep = "")

cat("Note: this route distinguishes all four items from each other and fixes the\n",
    "1/2 coding direction. It does not check the wording itself, which is\n",
    "transcribed verbatim from supplementary file peerj-14-21098-s004.docx.\n", sep = "")

cat(if (ok && !rev_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
