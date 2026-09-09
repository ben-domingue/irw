# verify_hayek_2022_attitude.R
#
# CLAIM: att1..att4 carry, in order, the four attitude items listed in Table 2 of
# Hayek et al. 2022 (PLOS ONE 17(3):e0265595):
#   att1 "Getting good grades is a good help for getting a good job"
#   att2 "Getting good grades will get me compliment from my parents"
#   att3 "Getting good grades means that I have to work too hard"
#   att4 "Getting good grades means will cause disapproval among my friends"
#
# FALSIFIABLE PREDICTION: Table 2 publishes a Spearman correlation between EACH of
# those four items and academic achievement at t3 (0.102, -0.015, 0.066, 0.020 --
# all distinct, so the four items are mutually distinguishable). Achievement
# (Gen_av.3) is not in the IRW table, so it is taken from the study's S1 Dataset
# and joined to the LIVE IRW responses on id. If item_text for any two items were
# swapped, the observed rhos would land in the wrong order.

suppressMessages(library(irw))

TABLE <- "hayek_2022_attitude"
PUBLISHED <- c(att1 = 0.102, att2 = -0.015, att3 = 0.066, att4 = 0.020)  # Table 2, rows in order
TOL <- 0.005

sav <- file.path(tempdir(), "hayek_s001.sav")
if (!file.exists(sav))
    download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0265595.s001",
                  sav, quiet = TRUE, mode = "wb")
raw <- haven::read_sav(sav)
ach <- data.frame(id = as.character(raw$ID), gen_av3 = as.numeric(raw$`Gen_av.3`))

d <- irw::irw_fetch(TABLE)
d$id <- as.character(d$id)
d <- merge(d[, c("id", "item", "resp")], ach, by = "id")

cat(sprintf("%-6s %10s %10s %9s %6s\n", "item", "published", "observed", "diff", "n"))
obs <- numeric(0)
for (it in names(PUBLISHED)) {
    s <- d[d$item == it, ]
    r <- suppressWarnings(cor(s$resp, s$gen_av3, method = "spearman", use = "complete.obs"))
    obs[it] <- r
    cat(sprintf("%-6s %10.3f %10.3f %+9.3f %6d\n", it, PUBLISHED[it], r, r - PUBLISHED[it], nrow(s)))
}
worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation: %.4f (tolerance %.3f)\n", worst, TOL))

# What this does NOT establish: the DIRECTION in which att3/att4 are stored. The
# published rho is computed on the same stored column, so it is invariant to how
# the shipped option_text anchors are oriented. The reverse-scored anchors on
# att3/att4 rest on the paper's Methods statement plus Tot_Att being the plain
# mean of the four stored columns (345/345 exact); see provenance.
cat("Note: pins item<->item_text for all 4 items; says nothing about the option_text\n",
    "anchor direction on att3/att4 (see provenance note).\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
