# verify_herrera_2018_se_d_items.R -- Step 5b check for batch_436.
#
# Claim: SE1..SE4 are the four state-EMPATHY adjectives and D1..D4 the four
# PERSONAL-DISTRESS adjectives of Herrera et al. (2018) Study 2 (S2 Appendix,
# "Empathy and Personal Distress"), and within each block the code number follows
# the questionnaire's presentation order.
#
# Route 3 (published subscale totals) + route 5 (block structure):
#   * Paper Table 4 (Study 2): Empathy M 5.09 SD 1.22 alpha .88;
#     Personal Distress M 4.15 SD 1.43 alpha .85.
#   * Every within-block correlation should exceed every cross-block one.
# Structural check on within-block order (not statistical): the S5 .xlsx column
# order SE1,SE2,D1,D2,D3,SE3,D4,SE4 reproduces the questionnaire's interleave
# Softhearted,Touched,Uneasy,Trouble,Distressed,Sympathetic,Disturbed,Compassionate
# (E,E,D,D,D,E,D,E) position for position.
#
# NOT established: which adjective within a block carries which number beyond that
# positional reading -- no per-item statistics are published, and the four
# adjectives within each block are near-synonyms.

suppressMessages(library(irw))
TABLE <- "herrera_2018_se_d_items"

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
SE <- paste0("SE", 1:4); D <- paste0("D", 1:4)

alpha <- function(x) { x <- na.omit(x); k <- ncol(x)
  k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x))) }

se <- rowMeans(w[, SE]); pd <- rowMeans(w[, D])
obs <- rbind(Empathy = c(mean(se), sd(se), alpha(w[, SE])),
             Distress = c(mean(pd), sd(pd), alpha(w[, D])))
pub <- rbind(Empathy = c(5.09, 1.22, .88), Distress = c(4.15, 1.43, .85))
cat(sprintf("%-9s %6s %6s | %6s %6s | %6s %6s\n", "block", "M_pub", "M_obs",
            "SD_pub", "SD_obs", "a_pub", "a_obs"))
for (r in rownames(obs))
  cat(sprintf("%-9s %6.2f %6.3f | %6.2f %6.3f | %6.2f %6.3f\n", r,
              pub[r, 1], obs[r, 1], pub[r, 2], obs[r, 2], pub[r, 3], obs[r, 3]))
ok_totals <- all(abs(obs - pub) <= c(0.02, 0.02, 0.02))

# Swapped-block counterfactual: would the SE/D labels reversed also fit?
cat(sprintf("swapped blocks would give Empathy M %.3f vs published 5.09 -> %s\n",
            mean(pd), if (abs(mean(pd) - 5.09) > 0.02) "rejected" else "NOT rejected"))

cm <- cor(w[, c(SE, D)], use = "pairwise")
within <- c(cm[SE, SE][upper.tri(cm[SE, SE])], cm[D, D][upper.tri(cm[D, D])])
cross <- as.vector(cm[SE, D])
cat(sprintf("within-block r: min %.2f max %.2f ; cross-block r: min %.2f max %.2f\n",
            min(within), max(within), min(cross), max(cross)))
ok_blocks <- min(within) > max(cross)

# Positional interleave of the S5 header against the questionnaire (hard-coded from
# journal.pone.0204494.s005 sheet "Main" cols 47-54 and s002.docx Table 6).
hdr  <- c("SE1", "SE2", "D1", "D2", "D3", "SE3", "D4", "SE4")
qset <- c("E", "E", "D", "D", "D", "E", "D", "E")
ok_interleave <- identical(ifelse(grepl("^SE", hdr), "E", "D"), qset)
cat("S5 header block pattern:", ifelse(grepl("^SE", hdr), "E", "D"),
    "\nquestionnaire pattern:  ", qset, "\n")

cat("NOT established: order within each block beyond the positional reading.\n")
cat(if (ok_totals && ok_blocks && ok_interleave) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
