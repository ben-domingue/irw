# verify_ajaykumar_2023_experience.R -- Step 5b mapping check (batch_440).
#
# Claim: item codes ExpRobots / ExpTech / ExpProg / ExpProgRob / ExpHands are the
# S6 Dataset column names (data/ajaykumar_2023_robot_curricula.py melts them
# unrenamed) and carry the S2 File codebook descriptions "experience with robots /
# technology / programming / programming robots / performing hands-on activities".
#
# Route 1 (per-item descriptive statistics): the article's Participants section
# (Ajaykumar et al. 2023, PLOS ONE 10.1371/journal.pone.0294786) reports, for the
# analysed N=27, experience with robots M=2.41 SD=1.12, technology M=4.15 SD=0.82,
# programming M=3.96 SD=0.94, programming robots M=2.30 SD=1.27. The check: for
# each published domain, the live item whose (M, SD) is nearest must be the code
# the shipped item_text claims, and it must match within rounding. A swap of any
# two of these four would break it (the four means are mutually >= 0.11 apart).
#
# What this does NOT establish directly: ExpHands (hands-on activities) has no
# published M/SD. It is pinned by elimination (the only remaining code) and by
# its self-describing name; its live mean 3.11 matches none of the four
# published values, which the script also checks.

suppressMessages(library(irw))
TABLE <- "ajaykumar_2023_experience"
PUB <- data.frame(
  claimed = c("ExpRobots", "ExpTech", "ExpProg", "ExpProgRob"),
  domain  = c("robots", "technology", "programming", "programming robots"),
  M  = c(2.41, 4.15, 3.96, 2.30),
  SD = c(1.12, 0.82, 0.94, 1.27), stringsAsFactors = FALSE)
TOL <- 0.006  # published to 2 dp

d <- irw::irw_fetch(TABLE)
obsM  <- tapply(d$resp, d$item, mean)
obsSD <- tapply(d$resp, d$item, sd)
cat("live per-item stats:\n")
print(round(data.frame(n = as.vector(table(d$item)[names(obsM)]), M = obsM, SD = obsSD), 3))

ok <- TRUE
cat(sprintf("\n%-20s %-11s %6s %6s %-11s %6s %6s\n", "published domain", "claimed", "pubM", "pubSD", "nearest", "obsM", "obsSD"))
for (i in seq_len(nrow(PUB))) {
  dist <- abs(obsM - PUB$M[i]) + abs(obsSD - PUB$SD[i])
  near <- names(which.min(dist))
  cat(sprintf("%-20s %-11s %6.2f %6.2f %-11s %6.3f %6.3f\n", PUB$domain[i], PUB$claimed[i],
              PUB$M[i], PUB$SD[i], near, obsM[near], obsSD[near]))
  if (near != PUB$claimed[i]) ok <- FALSE
  if (abs(obsM[near] - PUB$M[i]) > TOL || abs(obsSD[near] - PUB$SD[i]) > TOL) ok <- FALSE
}
hm <- obsM["ExpHands"]
cat(sprintf("\nExpHands (by elimination): obsM %.3f; min |diff| to any published mean %.3f\n",
            hm, min(abs(hm - PUB$M))))
if (min(abs(hm - PUB$M)) <= TOL) ok <- FALSE
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
