# verify_kim_2023_gad7.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes gad1..gad7 carry the canonical GAD-7
# item wording in canonical numbering (gad1 = "Feeling nervous, anxious or on
# edge" ... gad7 = "Feeling afraid as if something awful might happen").
# Neither the study's paper nor its SPSS deposit labels these columns, so the
# tie rests on the instrument's own 1-7 numbering and has to be tested against
# content.
#
# The test is cross-instrument. The same 202 respondents also completed the
# PHQ-9 and the PSS-10 in the same SPSS file, and two GAD-7 items have a
# near-unique content twin there:
#
#   gad5 "Being so restless that it is hard to sit still"
#        <-> PHQ9_8, the PHQ-9's only psychomotor item ("...being so fidgety
#            or restless that you have been moving around a lot more than usual")
#   gad6 "Becoming easily annoyed or irritable"
#        <-> PSS_9, the PSS-10's anger item ("been angered because of things
#            that were outside of your control"); irritability/anger is also the
#            GAD-7 content FURTHEST from psychomotor restlessness, so gad6 is
#            predicted to be the WEAKEST correlate of PHQ9_8.
#
# Predictions (all would break under a permutation of the item labels):
#   P1  argmax_i corr(gad_i, PHQ9_8) == gad5
#   P2  argmax_j corr(gad5, PHQ9_j) == PHQ9_8
#   P3  argmin_i corr(gad_i, PHQ9_8) == gad6
#   P4  argmax_i corr(gad_i, PSS_9)  == gad6
#
# Also printed, as corroboration rather than as a pass condition: the item
# means, whose ordering should put the generic worry item (gad3) at the top and
# gad5/gad7 at the bottom, the pattern GAD-7 samples routinely show.
#
# WHAT THIS DOES NOT ESTABLISH: it pins gad5 and gad6 only. It does not
# distinguish gad1, gad2, gad3, gad4 and gad7 from one another -- their content
# has no comparably specific twin in the PHQ-9 or PSS-10. The Step 5b status is
# therefore PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "kim_2023_gad7"
SAV   <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0278921.s001")

# --- live IRW data (the gad half) -------------------------------------------
d <- irw::irw_fetch(TABLE)
gad_items <- paste0("gad", 1:7)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", gad_items)]

# --- the study's SPSS deposit (the PHQ-9 / PSS-10 half) ---------------------
tf <- tempfile(fileext = ".sav")
utils::download.file(SAV, tf, quiet = TRUE, mode = "wb")
sav <- as.data.frame(haven::read_sav(tf))
sav$id <- as.numeric(sav$NUM)
phq_items <- paste0("PHQ9_", 1:9)
m <- merge(w, sav[, c("id", phq_items, "PSS_9")], by = "id")
for (v in c(phq_items, "PSS_9")) m[[v]] <- as.numeric(m[[v]])
cat(sprintf("merged n = %d respondents\n\n", nrow(m)))

r <- function(a, b) cor(m[[a]], m[[b]], use = "complete.obs")

# --- P1 / P3 -----------------------------------------------------------------
c8 <- sapply(gad_items, r, b = "PHQ9_8")
cat("corr(gad_i, PHQ9_8)  [PHQ-9's only psychomotor restlessness item]\n")
for (i in gad_items) cat(sprintf("  %-5s %6.3f\n", i, c8[i]))
top8 <- names(which.max(c8)); bot8 <- names(which.min(c8))
cat(sprintf("  -> strongest: %s (predicted gad5) ; weakest: %s (predicted gad6)\n\n",
            top8, bot8))

# --- P2 ----------------------------------------------------------------------
c5 <- sapply(phq_items, function(p) r("gad5", p))
cat("corr(gad5, PHQ9_j) across all nine PHQ-9 items\n")
for (p in phq_items) cat(sprintf("  %-7s %6.3f\n", p, c5[p]))
top5 <- names(which.max(c5))
cat(sprintf("  -> strongest: %s (predicted PHQ9_8)\n\n", top5))

# --- P4 ----------------------------------------------------------------------
c9 <- sapply(gad_items, r, b = "PSS_9")
cat("corr(gad_i, PSS_9)  [PSS-10's anger item]\n")
for (i in gad_items) cat(sprintf("  %-5s %6.3f\n", i, c9[i]))
top9 <- names(which.max(c9))
cat(sprintf("  -> strongest: %s (predicted gad6)\n\n", top9))

# --- corroboration only ------------------------------------------------------
mu <- sapply(gad_items, function(i) mean(m[[i]]))
cat("item means (corroborative, not a pass condition)\n")
for (i in names(sort(mu, decreasing = TRUE)))
    cat(sprintf("  %-5s %5.2f\n", i, mu[i]))
cat(sprintf("  -> highest %s (expected gad3, the generic worry item); ",
            names(which.max(mu))))
cat(sprintf("lowest %s (expected gad5 or gad7)\n\n", names(which.min(mu))))

ok <- c(P1 = top8 == "gad5", P2 = top5 == "PHQ9_8",
        P3 = bot8 == "gad6", P4 = top9 == "gad6")
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins gad5 and gad6 only. gad1/gad2/gad3/gad4/gad7 are NOT\n",
    "distinguished from one another by this route -- status PARTIAL.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
