# Step 5b verification for direkvand_2022_mjsi (batch_026).
#
# CLAIM UNDER TEST: the IRW item codes carry the MJSI's dimension in their prefix
# (C*, pr*, R*, p*, s*) and the paper's within-dimension item number in their suffix,
# so item_text was taken from PLOS ONE 10.1371/journal.pone.0262665 Table 4 / S4 File
# in that order.
#
# WHAT THIS SCRIPT CHECKS: the DIMENSION half of that claim, against the paper's own
# published Cronbach alphas (Results, para. "To determine internal consistency"):
#   whole tool 0.71, communications 0.73, professional 0.85,
#   responsibility 0.96, physical-mental 0.98, social 0.88.
# If the five code prefixes did not correspond to the paper's five dimensions, the
# alpha of the prefix-defined blocks would not reproduce the published values.
#
# WHAT IT DOES NOT CHECK: the ORDER of items WITHIN a dimension. Nothing in the data
# distinguishes, say, pr3 from pr4. See verification_direkvand_2022_mjsi.csv (PARTIAL)
# and provenance note: the paper's own S5 Persian questionnaire orders the professional
# and physical-mental blocks differently from its Table 4, and the two cannot both be right.
#
# WHAT THE VERDICT ACTUALLY RESTS ON (corrected at triage, 2026-09-04). Four of the
# five published subscale alphas do NOT reproduce from the deposited minimal dataset:
# professional 0.85 vs 0.580, responsibility 0.96 vs 0.161, physical-mental 0.98 vs
# 0.354, social 0.88 vs 0.464. Only communications (0.73 vs 0.733) and the whole tool
# (0.71 vs 0.705) come back. An earlier version of this comment named only two of the
# four, which understated how much of the stated test is not met.
#
# So the verdict is carried by three things, not by the alpha table as a whole: the
# communications alpha, the whole-tool alpha, and every item correlating positively
# with the mean of its own prefix block (weakest pr7 = 0.19). Those support the
# DIMENSION assignment; they do not reproduce the paper's per-subscale internal
# consistency, and the gap is large enough that the paper's own subscale alphas look
# unreliable -- 0.96 on a 2-item block implies an inter-item r near 0.92, against the
# ~0.09 the deposited data give. That is a fact about the source, not about this
# extraction: no option text is shipped for this table and the item wording comes from
# Table 4 / the S4 File, neither of which depends on the alphas.

suppressMessages(library(irw))
TABLE <- "direkvand_2022_mjsi"

PUB <- c(Communications = 0.73, Professional = 0.85, Responsibility = 0.96,
         `Physical-Mental` = 0.98, Social = 0.88, `WHOLE TOOL` = 0.71)

BLOCKS <- list(
  Communications  = c("C1","C2","C3","C4","c5","c6","c7"),
  Professional    = paste0("pr", 1:10),
  Responsibility  = c("R1","R2"),
  `Physical-Mental` = paste0("p", 1:4),
  Social          = c("s1","s2"))

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]),
             idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
BLOCKS[["WHOLE TOOL"]] <- unlist(BLOCKS, use.names = FALSE)

alpha <- function(x) {
  x <- x[complete.cases(x), , drop = FALSE]
  k <- ncol(x)
  k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))
}

cat(sprintf("%-16s %5s %10s %10s %8s\n", "block", "k", "published", "observed", "diff"))
obs <- numeric(0)
for (b in names(PUB)) {
  a <- alpha(w[, BLOCKS[[b]], drop = FALSE])
  obs[b] <- a
  cat(sprintf("%-16s %5d %10.2f %10.3f %8.3f\n", b, length(BLOCKS[[b]]), PUB[b], a, a - PUB[b]))
}

cat("\nItem-block correlations (each item vs the mean of its own prefix block):\n")
allpos <- TRUE
for (b in names(BLOCKS)) {
  if (b == "WHOLE TOOL") next
  its <- BLOCKS[[b]]
  bm <- rowMeans(w[, its, drop = FALSE], na.rm = TRUE)
  rs <- sapply(its, function(i) cor(w[[i]], bm, use = "complete.obs"))
  allpos <- allpos && all(rs > 0)
  cat(sprintf("  %-16s %s\n", b, paste(sprintf("%s=%.2f", its, rs), collapse = " ")))
}

okC <- abs(obs["Communications"] - PUB["Communications"]) <= 0.01
okT <- abs(obs["WHOLE TOOL"] - PUB["WHOLE TOOL"]) <= 0.01
cat(sprintf("\ncommunications alpha within 0.01 of published: %s\n", okC))
cat(sprintf("whole-tool alpha within 0.01 of published:      %s\n", okT))
cat(sprintf("every item correlates positively with its own block: %s\n", allpos))
cat("Note: this pins each item's DIMENSION, not its position within that dimension.\n")

cat(if (okC && okT && allpos) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
