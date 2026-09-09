# verify_jutte_2024_personality.R
#
# CLAIM UNDER TEST (Step 5b):
#   (a) each live item code (Extraversion_w2 ... Openness_w2) carries the Big Five
#       item wording printed against that construct in Table 1 of PLOS ONE
#       10.1371/journal.pone.0296423, and
#   (b) option_text is anchored 0 = "strongly disagree" ... 6 = "strongly agree",
#       i.e. the paper's stated 1-7 agreement scale stored with a -1 offset and
#       NOT reversed.
#
# The falsifiable predictions:
#   1. The same deposit's loneliness composite, +1, must reproduce the paper's
#      published means (2.69 pre / 2.56 during). That pins the -1 storage offset.
#   2. Under the claimed direction, the item "I easily get nervous and insecure"
#      (Neuroticism_w2) must be the strongest POSITIVE correlate of loneliness and
#      "I am outgoing and social" (Extraversion_w2) must correlate negatively --
#      the signs the paper itself reports (neuroticism +, openness -). A flipped
#      anchor direction inverts every one of these signs.

suppressMessages(library(irw))
suppressMessages(library(haven))

TABLE <- "jutte_2024_personality"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0296423.s003")

f <- tempfile(fileext = ".sav")
download.file(SI, f, quiet = TRUE, mode = "wb",
              headers = c("User-Agent" = "IRW-Finder/1.0 (ben.domingue@gmail.com)"))
sav <- haven::read_sav(f)

# --- 1. storage offset, from the published loneliness means -------------------
PUB <- c(pre = 2.69, during = 2.56)
lon_w1 <- rowMeans(sav[, c("Loneliness_I1_w1","Loneliness_I2_w1","Loneliness_I3_w1")], na.rm = TRUE)
lon_w2 <- rowMeans(sav[, c("Loneliness_I1_w2","Loneliness_I2_w2","Loneliness_I3_w2")], na.rm = TRUE)
obs <- c(pre = mean(lon_w1) + 1, during = mean(lon_w2) + 1)
cat("-- storage offset check (raw + 1 vs paper) --\n")
for (k in names(PUB))
  cat(sprintf("  %-7s published %.2f   observed %.4f   diff %+.4f\n",
              k, PUB[k], obs[k], obs[k] - PUB[k]))
offset_ok <- max(abs(obs - PUB)) < 0.02

# --- 2. live item codes are the source columns, verbatim ----------------------
d <- irw::irw_fetch(TABLE)
ITEMS <- c("Extraversion_w2","Agreeableness_w2","Conscientiousness_w2",
           "Neuroticism_w2","Openness_w2")
TEXT <- c("I am outgoing and social.",
          "I am entrusting and belief in the good in man.",
          "I handle all tasks thoroughly.",
          "I easily get nervous and insecure.",
          "I am fanciful and have an active imagination.")
live_mean <- tapply(d$resp, d$item, mean)[ITEMS]
sav_mean  <- sapply(ITEMS, function(x) mean(as.numeric(sav[[x]]), na.rm = TRUE))
cat("\n-- live item mean vs same-named source column mean --\n")
for (i in seq_along(ITEMS))
  cat(sprintf("  %-22s live %.4f   .sav %.4f   diff %.2e\n",
              ITEMS[i], live_mean[i], sav_mean[i], live_mean[i] - sav_mean[i]))
cols_ok <- max(abs(live_mean - sav_mean)) < 1e-9

# --- 3. anchor DIRECTION, via the sign pattern against loneliness -------------
cat("\n-- correlation with the w2 loneliness composite (higher = lonelier) --\n")
r <- sapply(ITEMS, function(x) cor(as.numeric(sav[[x]]), lon_w2, use = "complete.obs"))
for (i in seq_along(ITEMS))
  cat(sprintf("  %-22s r = %+0.3f   \"%s\"\n", ITEMS[i], r[i], TEXT[i]))
dir_ok <- r["Neuroticism_w2"] > 0.2 &&
          which.max(r) == which(ITEMS == "Neuroticism_w2") &&
          r["Extraversion_w2"] < 0 && r["Openness_w2"] < 0

cat("\nWhat this does NOT establish: the intermediate scale points 1-5 carry no\n",
    "published labels, so they ship with option_text blank and nothing here tests\n",
    "them; and the shipped English is the paper's own rendering of a German\n",
    "administration, which no number can check.\n", sep = "")

cat(sprintf("\noffset_ok=%s cols_ok=%s dir_ok=%s\n", offset_ok, cols_ok, dir_ok))
cat(if (offset_ok && cols_ok && dir_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
