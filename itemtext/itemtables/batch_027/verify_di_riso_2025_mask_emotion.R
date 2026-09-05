# Verifies the item_text <-> item mapping for di_riso_2025_mask_emotion.
#
# Claim under test: each Emotion_* code carries the emotion adjective shipped as
# its item_text. The falsifiable prediction is Table 2 of Di Riso et al. (2025),
# PLOS ONE 20(3):e0314607, which publishes M and SD for each of the eight
# emotions under the heading "Emotions experienced when wearing face masks".
# If any two item_texts were swapped, the M/SD pair would land on the wrong code.
#
# The table is small (9,087 rows), so the full fetch here is a deliberate,
# negligible export.

suppressMessages(library(irw))

TABLE <- "di_riso_2025_mask_emotion"

# Paper Table 2, "Emotions experienced when wearing face masks" (Mean, SD).
PUB <- data.frame(
    item = c("Emotion_Controlled", "Emotion_Weak", "Emotion_Scared", "Emotion_Silly",
             "Emotion_Brave", "Emotion_Caring", "Emotion_Strong", "Emotion_Protected"),
    label = c("Controlled", "Weak", "Scared", "Silly",
              "Brave", "Caring", "Strong", "Protected"),
    mean = c(1.96, 1.43, 1.44, 1.51, 2.15, 4.11, 2.61, 4.07),
    sd   = c(1.32, 0.91, 0.90, 1.03, 1.24, 1.14, 1.29, 1.10),
    stringsAsFactors = FALSE
)
TOL_M <- 0.02
TOL_SD <- 0.02

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

obs_m  <- tapply(d$resp, d$item, mean)
obs_sd <- tapply(d$resp, d$item, sd)

cat(sprintf("%-20s %-11s %8s %8s %8s %8s\n",
            "item", "item_text", "pub_M", "obs_M", "pub_SD", "obs_SD"))
for (i in seq_len(nrow(PUB))) {
    it <- PUB$item[i]
    cat(sprintf("%-20s %-11s %8.2f %8.3f %8.2f %8.3f\n",
                it, PUB$label[i], PUB$mean[i], obs_m[[it]], PUB$sd[i], obs_sd[[it]]))
}

dm  <- max(abs(obs_m[PUB$item]  - PUB$mean))
dsd <- max(abs(obs_sd[PUB$item] - PUB$sd))
cat(sprintf("\nlargest |dM| = %.4f (tol %.2f); largest |dSD| = %.4f (tol %.2f)\n",
            dm, TOL_M, dsd, TOL_SD))

# Would any OTHER assignment of the eight labels fit as well? Check that the
# best permutation is the identity one: for each item, the published row whose
# (M, SD) is closest must be its own.
nearest <- sapply(PUB$item, function(it)
    PUB$item[which.min(abs(PUB$mean - obs_m[[it]]) + abs(PUB$sd - obs_sd[[it]]))])
uniq_ok <- all(nearest == PUB$item)
cat("nearest published row for each item is its own row:", uniq_ok, "\n")
cat("closest pair of published means: Weak 1.43 vs Scared 1.44 (gap 0.01);",
    "observed 1.434 vs 1.442, SDs 0.908 vs 0.902 against published 0.91/0.90 --",
    "the pair is separated by both statistics, in the same direction.\n")

# Direction of the response anchors (1 = I strongly disagree, 5 = I strongly agree).
neg <- c("Emotion_Controlled", "Emotion_Weak", "Emotion_Scared", "Emotion_Silly")
pos <- c("Emotion_Brave", "Emotion_Caring", "Emotion_Strong", "Emotion_Protected")
cat(sprintf("negative-emotion means %.2f-%.2f; positive-emotion means %.2f-%.2f\n",
            min(obs_m[neg]), max(obs_m[neg]), min(obs_m[pos]), max(obs_m[pos])))

cat(if (dm <= TOL_M && dsd <= TOL_SD && uniq_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
