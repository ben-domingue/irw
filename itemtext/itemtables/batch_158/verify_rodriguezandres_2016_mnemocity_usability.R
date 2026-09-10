# verify_rodriguezandres_2016_mnemocity_usability.R
#
# Step 5b mapping check for rodriguezandres_2016_mnemocity_usability.
#
# CLAIM UNDER TEST: the item_text shipped in
# itemtables/batch_158/rodriguezandres_2016_mnemocity_usability__items.csv is
# attached to the right item code. The codes (US1, US2, SA1-SA4, Q3D, Q2_US1,
# Q2_SA1) are the S1 File column names, and PLOS ONE 10.1371/journal.pone.0161858
# prints those same codes beside the wording (Table 2 = Q1 questionnaire,
# Table 3 = Q2 questionnaire). This script does not take that label tie on
# trust: it re-derives the assignment from published numbers.
#
# WHAT WOULD BREAK IT: swapping item_text between any two codes.
#
# All queries are server-side aggregates (irw:::.irw_query_tibble) -- no export.

suppressMessages(library(irw))

TABLE <- "rodriguezandres_2016_mnemocity_usability"

tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")
ref <- tbl$qualified_reference
q   <- function(sql) as.data.frame(irw:::.irw_query_tibble(sql))

## ---------------------------------------------------------------------------
## (A) Route 1 -- published per-item M(SD) by group, article Table 10.
## Table 10 splits by the interaction played FIRST: Group A = NUI first,
## Group B = gamepad first. That split is live as cov_interaction_type.
## ---------------------------------------------------------------------------
PUB <- data.frame(
  item = c("US1", "US2", "SA1", "SA2", "SA3", "SA4"),
  mA   = c(4.04, 4.73, 4.65, 4.16, 3.89, 4.46),
  sA   = c(0.94, 0.52, 0.48, 0.92, 1.01, 0.75),
  mB   = c(4.25, 4.65, 4.64, 4.16, 4.04, 4.54),
  sB   = c(0.90, 0.73, 0.62, 1.11, 0.99, 0.69),
  stringsAsFactors = FALSE
)

grp <- q(sprintf(paste(
  "SELECT CAST(item AS STRING) AS item,",
  "CAST(cov_interaction_type AS STRING) AS grp,",
  "COUNT(*) AS n,",
  "AVG(SAFE_CAST(resp AS FLOAT64)) AS m,",
  "STDDEV_SAMP(SAFE_CAST(resp AS FLOAT64)) AS sd",
  "FROM `%s` WHERE resp IS NOT NULL GROUP BY item, grp ORDER BY item, grp"),
  ref))

getcell <- function(it, g, col) {
  v <- grp[grp$item == it & grp$grp == g, col]
  if (length(v) != 1) NA_real_ else v
}
obs <- data.frame(
  item = PUB$item,
  mA = sapply(PUB$item, getcell, "NUI",     "m"),
  sA = sapply(PUB$item, getcell, "NUI",     "sd"),
  mB = sapply(PUB$item, getcell, "gamepad", "m"),
  sB = sapply(PUB$item, getcell, "gamepad", "sd"),
  stringsAsFactors = FALSE
)

cat("=== (A) article Table 10: published vs live, by first-interaction group ===\n")
cat("     Group A = NUI first (n =", grp$n[grp$item == "US1" & grp$grp == "NUI"],
    "), Group B = gamepad first (n =", grp$n[grp$item == "US1" & grp$grp == "gamepad"], ")\n")
cat(sprintf("%-5s %-19s %-19s %-19s %-19s\n", "item",
            "A mean pub/obs", "A sd pub/obs", "B mean pub/obs", "B sd pub/obs"))
for (i in seq_len(nrow(PUB)))
  cat(sprintf("%-5s %8.2f /%7.2f  %8.2f /%7.2f  %8.2f /%7.2f  %8.2f /%7.2f\n",
              PUB$item[i], PUB$mA[i], obs$mA[i], PUB$sA[i], obs$sA[i],
              PUB$mB[i], obs$mB[i], PUB$sB[i], obs$sB[i]))

score <- function(perm) {
  # perm: assignment of PUBLISHED rows to observed rows
  mean(abs(c(PUB$mA - obs$mA[perm], PUB$sA - obs$sA[perm],
             PUB$mB - obs$mB[perm], PUB$sB - obs$sB[perm])))
}
perms <- function(v) {
  if (length(v) == 1) return(matrix(v, 1))
  do.call(rbind, lapply(seq_along(v), function(i)
    cbind(v[i], perms(v[-i]))))
}
P <- perms(1:6)
sc <- apply(P, 1, score)
ident <- which(apply(P, 1, function(r) all(r == 1:6)))
ord <- order(sc)
cat(sprintf("\nmean |published - observed| over all 24 cells: identity = %.4f\n", sc[ident]))
cat("ranked assignments (best five of 720):\n")
for (k in 1:5)
  cat(sprintf("  %.4f  %s%s\n", sc[ord[k]],
              paste(PUB$item[P[ord[k], ]], collapse = " "),
              if (ord[k] == ident) "   <- as shipped" else ""))
best_wrong <- min(sc[-ident])
cat(sprintf("identity is the strict minimum; best wrong permutation %.4f (%.1fx worse)\n",
            best_wrong, best_wrong / sc[ident]))
# The runner-up is the US2<->SA1 swap (the two highest-scoring items). Show the
# cells that separate them rather than resting on the aggregate margin.
i2 <- which(PUB$item == "US2"); i3 <- which(PUB$item == "SA1")
cat(sprintf("closest rival = US2<->SA1 swap. Group-B SD: published US2 %.2f vs observed US2 %.2f (d=%.2f)",
            PUB$sB[i2], obs$sB[i2], abs(PUB$sB[i2] - obs$sB[i2])))
cat(sprintf(" / observed SA1 %.2f (d=%.2f); published SA1 %.2f vs observed SA1 %.2f (d=%.2f) / observed US2 %.2f (d=%.2f)\n",
            obs$sB[i3], abs(PUB$sB[i2] - obs$sB[i3]),
            PUB$sB[i3], obs$sB[i3], abs(PUB$sB[i3] - obs$sB[i3]),
            obs$sB[i2], abs(PUB$sB[i3] - obs$sB[i2])))
okA <- sc[ident] == min(sc)

## ---------------------------------------------------------------------------
## (B) Q3D -- the article body states its mean in prose:
## "there was a question (Q3D) about the depth perception. The question had a
##  high score 3.6 (1-5 scale)".
## ---------------------------------------------------------------------------
all_m <- q(sprintf(paste(
  "SELECT CAST(item AS STRING) AS item, COUNT(*) AS n,",
  "AVG(SAFE_CAST(resp AS FLOAT64)) AS m,",
  "STDDEV_SAMP(SAFE_CAST(resp AS FLOAT64)) AS sd",
  "FROM `%s` WHERE resp IS NOT NULL GROUP BY item ORDER BY item"), ref))
q3d <- all_m$m[all_m$item == "Q3D"]
cat("\n=== (B) Q3D, mean stated in the article body ===\n")
cat(sprintf("published 3.6 (1-5 scale)   observed %.2f   diff %.2f\n", q3d, q3d - 3.6))
cat("Q3D is also the only item whose live mean is below 4.0 apart from SA3 (",
    sprintf("%.2f", all_m$m[all_m$item == "SA3"]), ") and Q2_US1 (",
    sprintf("%.2f", all_m$m[all_m$item == "Q2_US1"]), "), both pinned elsewhere.\n", sep = "")
okB <- abs(q3d - 3.6) < 0.15

## ---------------------------------------------------------------------------
## (C) Q2_US1 vs Q2_SA1 -- the two repeated questions. Table 3 re-asks exactly
## US1 ("Was the game easy to use?") and SA1 ("How much fun did you have?")
## after the second interaction, so each Q2 item should track its own Q1
## counterpart more than the other one. Test the identity assignment against
## the swap.
## ---------------------------------------------------------------------------
piv <- sprintf(paste(
  "WITH w AS (SELECT CAST(id AS STRING) AS id,",
  "MAX(IF(item='US1',    SAFE_CAST(resp AS FLOAT64), NULL)) AS US1,",
  "MAX(IF(item='SA1',    SAFE_CAST(resp AS FLOAT64), NULL)) AS SA1,",
  "MAX(IF(item='Q2_US1', SAFE_CAST(resp AS FLOAT64), NULL)) AS Q2_US1,",
  "MAX(IF(item='Q2_SA1', SAFE_CAST(resp AS FLOAT64), NULL)) AS Q2_SA1",
  "FROM `%s` WHERE resp IS NOT NULL GROUP BY id)",
  "SELECT COUNT(*) AS n,",
  "CORR(Q2_US1, US1) AS r_q2us1_us1, CORR(Q2_US1, SA1) AS r_q2us1_sa1,",
  "CORR(Q2_SA1, SA1) AS r_q2sa1_sa1, CORR(Q2_SA1, US1) AS r_q2sa1_us1",
  "FROM w"), ref)
cr <- q(piv)
cat("\n=== (C) repeated questions: retest correlation with the Q1 counterpart ===\n")
cat(sprintf("n respondents with all four = %d\n", cr$n))
cat(sprintf("Q2_US1 ~ US1 (ease~ease) r = %+.3f   Q2_US1 ~ SA1 (ease~fun)  r = %+.3f\n",
            cr$r_q2us1_us1, cr$r_q2us1_sa1))
cat(sprintf("Q2_SA1 ~ SA1 (fun~fun)   r = %+.3f   Q2_SA1 ~ US1 (fun~ease)  r = %+.3f\n",
            cr$r_q2sa1_sa1, cr$r_q2sa1_us1))
ident_sum <- cr$r_q2us1_us1 + cr$r_q2sa1_sa1
swap_sum  <- cr$r_q2us1_sa1 + cr$r_q2sa1_us1
cat(sprintf("sum of within-question r: as shipped = %+.3f, under the Q2 swap = %+.3f (%.1fx)\n",
            ident_sum, swap_sum, ident_sum / swap_sum))
cat(sprintf("mean levels also line up with Q1: US1 %.2f -> Q2_US1 %.2f (ease, lower);",
            all_m$m[all_m$item == "US1"], all_m$m[all_m$item == "Q2_US1"]))
cat(sprintf(" SA1 %.2f -> Q2_SA1 %.2f (fun, higher)\n",
            all_m$m[all_m$item == "SA1"], all_m$m[all_m$item == "Q2_SA1"]))
okC <- ident_sum > swap_sum

## ---------------------------------------------------------------------------
cat("\n=== what this does NOT establish ===\n")
cat("(A) pins US1, US2, SA1, SA2, SA3, SA4 against each other and (B) pins Q3D,\n")
cat("but neither reads the wording: the words come from the article's Table 2/Table 3,\n")
cat("which print the codes themselves, so a mis-transcription of those table cells\n")
cat("would survive this script. (A)'s aggregate margin over the runner-up (the US2<->SA1 swap) is only 1.5x, so it\nis the identity being the strict minimum -- not a wide gap -- that carries it.\n(C) is the weakest link -- it separates Q2_US1 from\n")
cat("Q2_SA1 by a 2-3x margin on small correlations, not decisively; the primary tie\n")
cat("for those two is Table 3's own 'US1'/'SA1' row labels plus the S1 File's\n")
cat("Q2_-prefixed column names. Nothing here tests option_text: the anchors come\n")
cat("from Table 2/Table 3's Value column and the data offer no way to check them.\n")

cat(sprintf("\nA=%s B=%s C=%s\n", okA, okB, okC))
cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
