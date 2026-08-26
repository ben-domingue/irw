# Mapping verification for ALSECYPIAMH_WU_2022_PHQ (issue #1643).
#
# The anchor is documentary, not statistical: the paper administers the PHQ-2
# on a 0-3 scale and cites Liao et al. (2017), whose Chinese PHQ-2-C names
# item 1 as 做事情没什么兴趣 (little interest or pleasure in doing things) and
# item 2 as 感到沮丧、压抑或绝望 (feeling down, depressed or hopeless). The IRW
# codes are PHQ1 and PHQ2, so code number ties to instrument item number.
#
# The only falsifiable data-side prediction a 2-item scale supports is the
# replicated PHQ-2 endorsement asymmetry: the anhedonia item (item 1) is
# endorsed more often than the depressed-mood item (item 2) in community and
# adolescent samples. A swap would invert this.
#
# This is corroboration, not proof -- with two items the check has one degree
# of freedom. Hence PARTIAL.

options(irw.itemtext_disclaimer = FALSE)
suppressMessages(library(irw))

d <- as.data.frame(irw_fetch("ALSECYPIAMH_WU_2022_PHQ"))
stopifnot(setequal(unique(d$item), c("PHQ1", "PHQ2")))

endorse <- tapply(d$resp, d$item, function(v) mean(v >= 1))
mu      <- tapply(d$resp, d$item, mean)

cat("proportion endorsing at all (resp >= 1):\n"); print(round(endorse, 4))
cat("\nmean resp:\n"); print(round(mu, 4))
cat("\nfull distribution:\n"); print(table(d$item, d$resp))

ok <- endorse[["PHQ1"]] > endorse[["PHQ2"]] && mu[["PHQ1"]] > mu[["PHQ2"]]
cat("\nPHQ1 (anhedonia) endorsed more than PHQ2 (depressed mood), as predicted:",
    ok, "\n")
cat("NOT ESTABLISHED by this check: anything beyond the two items' relative order;",
    "the mapping rests on the Liao et al. (2017) PHQ-2-C item numbering.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
