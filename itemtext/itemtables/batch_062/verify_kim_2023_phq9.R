# verify_kim_2023_phq9.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes PHQ9_1..PHQ9_9 carry the canonical PHQ-9
# wording in canonical numbering (PHQ9_1 = "Little interest or pleasure in doing
# things" ... PHQ9_9 = "Thoughts that you would be better off dead or of hurting
# yourself in some way"), and resp 0/1/2/3 = Not at all / Several days / More
# than half the days / Nearly every day in that ascending order.
#
# Neither the paper nor its SPSS deposit ties these columns to any text -- the
# .sav carries no variable labels and no value labels for PHQ9_1..PHQ9_9 -- so
# the tie rests on the PHQ-9 form's own printed numbering 1-9 matching the
# column names PHQ9_{i}, and has to be tested against content.
#
# Predictions (each would break under a permutation of the item labels):
#
#   P1  MARKER ITEM (Step 5b route 7). Item 9 is suicidal ideation; in any
#       non-clinical sample it must be the least endorsed item of the nine, by
#       both lowest mean and highest share of zero responses.
#         argmin_i mean(PHQ9_i) == PHQ9_9  AND  argmax_i pct0(PHQ9_i) == PHQ9_9
#
#   P2  MOST-ENDORSED ITEM. Item 4 is fatigue/low energy, the most commonly
#       endorsed PHQ-9 symptom in general and community samples.
#         argmax_i mean(PHQ9_i) == PHQ9_4
#
#   P3  SUBSCALE BLOCK STRUCTURE (Step 5b route 5). The PHQ-9's well-replicated
#       two-factor solution puts items 3, 4, 5 (sleep, energy, appetite) on the
#       SOMATIC factor and items 2, 6, 7, 8, 9 on the COGNITIVE/AFFECTIVE
#       factor; item 1 (anhedonia) cross-loads and is excluded from the test.
#       Prediction: mean within-block r exceeds mean cross-block r for both
#       blocks. This is a testable statement about WHICH codes sit together.
#
#   P4  RESPONSE-AXIS DIRECTION (the option_text <-> resp axis). In the study's
#       own SPSS deposit, PHQ9_T must equal the raw unreversed row sum of
#       PHQ9_1..PHQ9_9 (range 0-27, the total range the paper states), and
#       PHQ9_G must partition PHQ9_T at the PHQ-9's standard severity cut points
#       0-4 / 5-9 / 10-19 / 20-27 with its labels NO/MIL/MOD/SEV in ascending
#       order. Both fail if 0 and 3 are the other way round.
#
# WHAT THIS DOES NOT ESTABLISH: it pins PHQ9_9 and PHQ9_4 individually and pins
# block membership for {3,5} vs {2,6,7,8}. It does NOT separate PHQ9_3 from
# PHQ9_5 within the somatic block, does NOT separate PHQ9_2, PHQ9_6, PHQ9_7 and
# PHQ9_8 from one another within the cognitive/affective block, and does not
# pin PHQ9_1 at all. The Step 5b status is therefore PARTIAL, not VERIFIED.
#
# Deliberately NOT used: the cross-instrument restlessness link between PHQ9_8
# and the sibling table kim_2023_gad7's gad5. gad5's own identity was inferred
# from PHQ9_8 in verify_kim_2023_gad7.R, so using it here would be circular.

suppressMessages(library(irw))

TABLE <- "kim_2023_phq9"
IT    <- paste0("PHQ9_", 1:9)
SAV   <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0278921.s001")

# --- live IRW data -----------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, IT]
cat(sprintf("live table: %d respondents x %d items\n\n", nrow(w), ncol(w)))

mu   <- sapply(IT, function(i) mean(w[[i]], na.rm = TRUE))
pct0 <- sapply(IT, function(i) 100 * mean(w[[i]] == 0, na.rm = TRUE))

# --- P1 / P2 -----------------------------------------------------------------
cat("per-item mean and % at zero\n")
for (i in IT) cat(sprintf("  %-7s mean %5.3f   %%zero %5.1f\n", i, mu[i], pct0[i]))
lo <- names(which.min(mu)); z <- names(which.max(pct0)); hi <- names(which.max(mu))
cat(sprintf("  -> lowest mean: %s (predicted PHQ9_9); highest %%zero: %s (predicted PHQ9_9)\n",
            lo, z))
cat(sprintf("  -> highest mean: %s (predicted PHQ9_4)\n\n", hi))

# --- P3 ----------------------------------------------------------------------
R <- cor(w, use = "complete.obs")
SOM <- c("PHQ9_3", "PHQ9_4", "PHQ9_5")
COG <- c("PHQ9_2", "PHQ9_6", "PHQ9_7", "PHQ9_8", "PHQ9_9")
within <- function(g) mean(R[g, g][upper.tri(R[g, g])])
cross  <- mean(R[SOM, COG])
w_som <- within(SOM); w_cog <- within(COG)
cat("PHQ-9 two-factor block test (item 1 excluded, cross-loading)\n")
cat(sprintf("  mean r within somatic  {3,4,5}     = %.3f\n", w_som))
cat(sprintf("  mean r within cognitive{2,6,7,8,9} = %.3f\n", w_cog))
cat(sprintf("  mean r across the two blocks       = %.3f\n", cross))
cat(sprintf("  -> both within > cross: %s\n\n",
            if (w_som > cross && w_cog > cross) "yes" else "NO"))

# --- P4 ----------------------------------------------------------------------
tf <- tempfile(fileext = ".sav")
utils::download.file(SAV, tf, quiet = TRUE, mode = "wb")
sav <- as.data.frame(haven::read_sav(tf))
rs  <- rowSums(sapply(IT, function(i) as.numeric(sav[[i]])))
tot <- as.numeric(sav$PHQ9_T); grp <- as.numeric(sav$PHQ9_G)
dmax <- max(abs(rs - tot))
cat(sprintf("deposit: max |PHQ9_T - rowSum(PHQ9_1..9)| = %.3f ; sum range %d-%d\n",
            dmax, min(rs), max(rs)))
band <- cut(rs, c(-1, 4, 9, 19, 27), labels = 1:4)
tab  <- table(grp, band)
print(tab)
bands_ok <- dmax == 0 && sum(diag(as.matrix(tab))) == length(rs)
cat(sprintf("  -> PHQ9_G matches the standard 0-4/5-9/10-19/20-27 bands exactly: %s\n\n",
            if (bands_ok) "yes" else "NO"))

ok <- c(P1 = (lo == "PHQ9_9" && z == "PHQ9_9"),
        P2 = hi == "PHQ9_4",
        P3 = (w_som > cross && w_cog > cross),
        P4 = bands_ok)
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins PHQ9_9 and PHQ9_4 individually and pins somatic/cognitive block\n",
    "membership; does NOT separate PHQ9_3 from PHQ9_5, does NOT separate PHQ9_2,\n",
    "PHQ9_6, PHQ9_7, PHQ9_8 from one another, and does not pin PHQ9_1 -- PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
