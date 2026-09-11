# verify_tsai_2017_treeit_h12_language.R -- Step 5b mapping check (batch_192).
#
# Claim: H12-1/H12-2/H12-3 carry, in that order, the three H12 statements of the
# study's S1 File (Appendix 1, Treeit Heuristic Evaluation, pone.0180102.s001):
#   H12-1 "Use standard meanings of words."
#   H12-2 "Specialized language for specialized groups."
#   H12-3 "User can define aliases."
# mapping_basis = paper_order: the IRW code IS the S3 xlsx column name (header row 2),
# but that column name carries no text, so column -> statement rests on the appendix
# listing its 3 statements in the same order as the xlsx's H12-1..H12-3 columns.
#
# Check A (code -> source column): live per-item response counts must equal the
# counts in the S3 xlsx columns of the same name (hard-coded below, read 2026-09-11
# from pone.0180102.s003, sha256 af427348...df18). All three count vectors differ, so
# this pins each live code to its source column.
# Check B (column -> statement, circumstantial): items 1 and 2 are both about the
# wording of language; item 3 is a user-customisation feature. Prediction: H12-3 is
# the odd one out -- r(H12-1,H12-2) exceeds both correlations with H12-3, and H12-3
# has the lowest mean / largest SD.
#
# What this does NOT establish: it cannot separate H12-1 from H12-2 (means 4.327 vs
# 4.297, 99/101 respondents give identical answers to both), and B is a semantic
# coherence argument, not a published per-item statistic -- the paper reports none
# for H12 (Table 3 gives only the H12 composite's loading 0.79). Status: PARTIAL.

suppressMessages(library(irw))

TABLE <- "tsai_2017_treeit_h12_language"

SOURCE_COUNTS <- list(
  "H12-1" = c(`3` = 12, `4` = 44, `5` = 45),
  "H12-2" = c(`3` = 13, `4` = 45, `5` = 43),
  "H12-3" = c(`2` = 5, `3` = 16, `4` = 29, `5` = 51)
)

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)

okA <- TRUE
cat("Check A: live per-item counts vs S3 xlsx column counts\n")
for (it in names(SOURCE_COUNTS)) {
  live <- table(d$resp[d$item == it])
  src <- SOURCE_COUNTS[[it]]
  lv <- as.numeric(live[names(src)]); lv[is.na(lv)] <- 0
  extra <- setdiff(names(live), names(src))
  same <- all(lv == src) && length(extra) == 0
  cat(sprintf("  %-6s source %-18s live %-18s %s\n", it,
              paste(names(src), src, sep = ":", collapse = " "),
              paste(names(live), as.numeric(live), sep = ":", collapse = " "),
              if (same) "MATCH" else "MISMATCH"))
  okA <- okA && same
}

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
r <- cor(w[, c("H12-1", "H12-2", "H12-3")], use = "pairwise.complete.obs")
m <- colMeans(w[, c("H12-1", "H12-2", "H12-3")], na.rm = TRUE)
s <- apply(w[, c("H12-1", "H12-2", "H12-3")], 2, sd, na.rm = TRUE)
agree12 <- sum(w[["H12-1"]] == w[["H12-2"]], na.rm = TRUE)

cat("\nCheck B: H12-3 (aliases) should be the odd one out\n")
cat(sprintf("  r(H12-1,H12-2) = %.3f   r(H12-1,H12-3) = %.3f   r(H12-2,H12-3) = %.3f\n",
            r[1, 2], r[1, 3], r[2, 3]))
cat(sprintf("  means: %.3f %.3f %.3f   SDs: %.3f %.3f %.3f\n",
            m[1], m[2], m[3], s[1], s[2], s[3]))
cat(sprintf("  identical answers H12-1 vs H12-2: %d of %d\n", agree12, nrow(w)))
okB <- r[1, 2] > max(r[1, 3], r[2, 3]) && which.min(m) == 3 && which.max(s) == 3

cat("\nNot established: order of H12-1 vs H12-2 (near-identical responses); B is\n",
    "semantic coherence only. Recorded as PARTIAL.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
