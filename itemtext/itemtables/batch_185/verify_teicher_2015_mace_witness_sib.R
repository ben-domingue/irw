# verify_teicher_2015_mace_witness_sib.R -- copied from references/verify_template.R
#
# Claim under test. Each `item` is an S9 File column name (data/teicher_2015_mace_items.py
# melts them unchanged). item_text for 6 codes is the S3 File (MACE-X) wording at the
# position where the authors' MACEscore R/mace_x_names.R lists that code (MACE-X items
# 18-23); Attempt_sex_sib and Intercourse_sib ship blank because S3's items 24/25 ("Had or
# attempted to have any type of sexual intercourse ... with your sibling" / "Threatened to
# harm your sibling") are not what those columns hold.
#
# Checks:
#   A. Route 1: paper Table 11 (image, n=839) % Yes for MACE items 15-18 = Hit_sib,
#      Hit_sib_med, Sex_comment_sib, Fondled_sib; each live value must round to its own
#      published value and sit nearer its own value than any other Table 11 value.
#   B. Physical severity ladder implied by the shipped texts: Push_sib (push/grab/slap..)
#      > Hit_sib (left marks) > Hit_sib_med (medical attention), with Hit_sib_med nested
#      in Push_sib.
#   C. Cluster membership: the codes shipped with sexual wording (Touch_them_sib) and the
#      two blanked codes co-endorse with Sex_comment_sib far more than with Hit_sib_med --
#      so Intercourse_sib is a sexual item, not S3's "Threatened to harm your sibling".
#   D. Intercourse_sib nested in Attempt_sex_sib (separate attempted / actual items).
# What this does NOT establish: which of the three rare sexual codes Touch_them_sib /
# Attempt_sex_sib / Intercourse_sib the "touch their body" wording belongs to is tied by
# the self-describing code name and MACEscore position only (0.72 / 0.95 / 0.83 % Yes are
# not separable by any published statistic); Fondled_sib (0.95) and Attempt_sex_sib (0.95)
# are likewise tied numerically and separated only by code name; and character identity of
# S3 wording with the online form actually administered.

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_witness_sib"
PUBLISHED <- c(Hit_sib = 11.9, Hit_sib_med = 1.9, Sex_comment_sib = 1.7, Fondled_sib = 1.0)

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

pct <- sapply(split(d$resp, d$item), function(v) 100 * mean(v))
n   <- table(d$item)
cat("== live % Yes (n) ==\n")
for (s in names(pct)) cat(sprintf("  %-16s %6.2f  (n=%d)\n", s, pct[s], n[s]))

cat("\n== A. Table 11 % Yes vs live ==\n")
okA <- TRUE
for (s in names(PUBLISHED)) {
  o <- pct[s]; others <- PUBLISHED[names(PUBLISHED) != s]
  near_own <- abs(o - PUBLISHED[s]) < min(abs(o - others))
  rounds <- abs(round(o, 1) - PUBLISHED[s]) < 1e-9
  cat(sprintf("  %-16s published %5.1f live %6.2f  rounds-to-own=%s  nearest-own=%s\n",
              s, PUBLISHED[s], o, rounds, near_own))
  okA <- okA && rounds && near_own && n[s] == 839
}

co <- function(a, b) sum(w[[a]] == 1 & w[[b]] == 1, na.rm = TRUE)
ny <- function(a) sum(w[[a]] == 1, na.rm = TRUE)

cat("\n== B. physical ladder ==\n")
cat(sprintf("  Push_sib %.2f > Hit_sib %.2f > Hit_sib_med %.2f\n",
            pct["Push_sib"], pct["Hit_sib"], pct["Hit_sib_med"]))
cat(sprintf("  Hit_sib_med=1 also Push_sib=1: %d of %d; Hit_sib=1 also Push_sib=1: %d of %d\n",
            co("Hit_sib_med", "Push_sib"), ny("Hit_sib_med"), co("Hit_sib", "Push_sib"), ny("Hit_sib")))
okB <- pct["Push_sib"] > pct["Hit_sib"] && pct["Hit_sib"] > pct["Hit_sib_med"] &&
  co("Hit_sib_med", "Push_sib") / ny("Hit_sib_med") >= 0.9

cat("\n== C. cluster membership (co-endorsement share) ==\n")
okC <- TRUE
for (s in c("Touch_them_sib", "Attempt_sex_sib", "Intercourse_sib")) {
  sx <- co(s, "Sex_comment_sib") / ny(s); ph <- co(s, "Hit_sib_med") / ny(s)
  cat(sprintf("  %-16s n_yes=%d  with Sex_comment_sib %.2f  with Hit_sib_med %.2f  with Push_sib %.2f\n",
              s, ny(s), sx, ph, co(s, "Push_sib") / ny(s)))
  okC <- okC && sx >= 0.8 && sx > ph + 0.5
}

cat("\n== D. nesting ==\n")
cat(sprintf("  Intercourse_sib=1 also Attempt_sex_sib=1: %d of %d\n",
            co("Intercourse_sib", "Attempt_sex_sib"), ny("Intercourse_sib")))
okD <- co("Intercourse_sib", "Attempt_sex_sib") == ny("Intercourse_sib")

cat("\nNot established: Touch_them_sib vs Attempt_sex_sib vs Intercourse_sib, and Fondled_sib vs\n",
    "Attempt_sex_sib, are not separable numerically; those rest on code names + MACEscore order.\n", sep = "")
cat(sprintf("A=%s B=%s C=%s D=%s\n", okA, okB, okC, okD))
cat(if (okA && okB && okC && okD) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
