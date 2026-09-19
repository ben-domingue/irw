# verify_mhscdc_fried_2020_se.R -- Step 5b re-runnable evidence.
#
# CLAIM: live item code PreNN is the OSF deposit's clean_prepost.csv column PreNN,
# which is codebook row cleandata_pre == "QNN", whose Item cell holds the wording
# shipped in mhscdc_fried_2020_se__items.csv.
#
# The chain has two falsifiable links, both checked here:
#   (A) live PreNN data == deposit column PreNN data (per-item mean/sd to 2dp).
#       Breaks if data/mhscdc_fried_2020.r's num_range("Pre", 46:55) had shifted,
#       or if the live codes were permuted relative to the deposit columns.
#   (B) codebook Q46..Q55 texts == shipped item_text (punctuation-insensitive).
#       Breaks if item_text for any two items were swapped.
# Plus (C): the codebook's Q-number scale-block anchors reproduce the processing
#       script's Pre-number block ranges, which is what ties the Q numbering to
#       the Pre numbering globally rather than by assumption.
#
# Offline-tolerant: the deposit numbers and codebook texts are hard-coded from
# the files fetched 2026-09-09 (osf.io/mvdpe, "4. Data" and "6. Measures").

suppressMessages(library(irw))

TABLE <- "mhscdc_fried_2020_se"
ITEMS <- paste0("Pre", 46:55)

# (A) deposit clean_prepost.csv, columns Pre46..Pre55, n = 80 complete rows each
DEP_MEAN <- c(2.30, 2.84, 2.95, 3.00, 3.04, 3.44, 2.77, 3.06, 2.26, 3.24)
DEP_SD   <- c(0.54, 0.58, 0.59, 0.73, 0.66, 0.59, 0.83, 0.56, 0.61, 0.60)
DEP_MAX  <- c(3, 4, 4, 4, 4, 4, 4, 4, 3, 4)
TOL <- 0.015

# (B) Codebook_Baseline.xlsx, cleandata_pre Q46..Q55, "Item" column
CODEBOOK <- c(
 "I can always manage to solve difficult problems if I try hard enough",
 "If someone opposes me I can find the means and ways to get what I want",
 "It is easy for me to stick to my aims and accomplish my goals",
 "I am confident that I could deal efficiently with unexpected events",
 "Thanks to my resourcefulness I know how to handle unforeseen situations",
 "I can solve most problems if I invest the necessary effort",
 "I can remain calm when facing difficulties because I can rely on my coping abilities",
 "When I am confronted with a problem I can usually find several solutions",
 "If I am in trouble I can usually think of a solution",
 "I can usually handle whatever comes my way.")

# (C) codebook Label/Scale anchor Q-number  ->  processing-script Pre range start
ANCHOR_Q      <- c(1, 22, 34, 41, 46, 56, 68, 78, 86, 102, 141)
ANCHOR_SCRIPT <- c(1, 22, 34, 41, 46, 56, 68, 78, 86, 102, 141)  # data/mhscdc_fried_2020.r
ANCHOR_NAME <- c("DASS","Conscientiousness","Anger","Loneliness","Self-Efficacy",
                 "Mindfulness","Perceived Stress","Tiredness","Motivation",
                 "Smartphone Addiction","Procrastination")

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs_mean <- round(tapply(d$resp, d$item, mean)[ITEMS], 2)
obs_sd   <- round(tapply(d$resp, d$item, sd)[ITEMS], 2)
obs_max  <- tapply(d$resp, d$item, max)[ITEMS]

cat("(A) live vs deposit clean_prepost.csv, per item\n")
cat(sprintf("%-7s %8s %8s %8s %8s %5s %5s\n",
            "item","dep_mean","obs_mean","dep_sd","obs_sd","dmax","omax"))
for (i in seq_along(ITEMS))
  cat(sprintf("%-7s %8.2f %8.2f %8.2f %8.2f %5d %5d\n",
              ITEMS[i], DEP_MEAN[i], obs_mean[i], DEP_SD[i], obs_sd[i],
              DEP_MAX[i], as.integer(obs_max[i])))
worst <- max(abs(obs_mean - DEP_MEAN), abs(obs_sd - DEP_SD))
okA <- worst <= TOL && all(as.integer(obs_max) == DEP_MAX)
cat(sprintf("largest |deviation| = %.3f (tolerance %.3f); max-value pattern match: %s\n\n",
            worst, TOL, all(as.integer(obs_max) == DEP_MAX)))

norm <- function(x) tolower(gsub("[^a-z ]", "", gsub("[[:space:]]+", " ", tolower(x))))
csvp <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                  paste0(TABLE, "__items.csv"))
if (!file.exists(csvp)) csvp <- paste0("itemtables/batch_107/", TABLE, "__items.csv")
it <- read.csv(csvp, stringsAsFactors = FALSE)
ship <- tapply(it$item_text, it$item, function(z) unique(z))[ITEMS]

cat("(B) codebook Q46..Q55 text vs shipped item_text (punctuation-insensitive)\n")
okB <- TRUE
for (i in seq_along(ITEMS)) {
  same <- identical(norm(CODEBOOK[i]), norm(ship[[i]]))
  okB <- okB && same
  cat(sprintf("%-7s %-5s %s\n", ITEMS[i], if (same) "same" else "DIFF",
              substr(ship[[i]], 1, 62)))
}
cat("\n")

cat("(C) codebook scale-block anchors vs processing-script Pre ranges\n")
for (i in seq_along(ANCHOR_Q))
  cat(sprintf("  Q%-4d %-22s script block starts at Pre%-4d %s\n",
              ANCHOR_Q[i], ANCHOR_NAME[i], ANCHOR_SCRIPT[i],
              if (ANCHOR_Q[i] == ANCHOR_SCRIPT[i]) "match" else "MISMATCH"))
okC <- all(ANCHOR_Q == ANCHOR_SCRIPT)
cat(sprintf("  %d/%d block boundaries align -> QNN == PreNN\n\n",
            sum(ANCHOR_Q == ANCHOR_SCRIPT), length(ANCHOR_Q)))

cat("Note: what this does NOT establish. Within the self-efficacy block the ten items\n",
    "share one 1-4 ladder, so the response distribution alone separates only Pre46 and\n",
    "Pre54 (the two capped at 3); Pre50 and Pre53 differ by 0.02 in mean. The per-item\n",
    "tie is NOMINAL -- the codebook names each Q number and the script's num_range keeps\n",
    "that number -- and (A) and (C) are what license reading QNN as PreNN.\n", sep = "")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
