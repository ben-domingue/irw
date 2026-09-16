# verify_wu2026_novel.R -- Step 5b re-runnable evidence.
#
# CLAIM UNDER TEST: IRW item code Novel_k denotes ceramic vase stimulus k of
# Fig 1 (Wu, Yahaya, Tai & Ren 2026, PLOS ONE 21(4):e0342855), and the shipped
# option_text anchors run 1 = "Strongly Disagree" ... 7 = "Strongly Agree".
#
# All 10 items carry the SAME item_text ("This is a novel vase."), because the
# study used one single-item novelty statement per stimulus image. So the only
# thing that can be mis-mapped is which VASE each code denotes -- that is what
# this script falsifies.
#
# Falsifiable prediction: Fig 2 of the paper publishes the per-stimulus mean
# novelty rating for vases 1-10. A permuted code->stimulus mapping breaks it.

suppressMessages(library(irw))

TABLE <- "wu2026_novel"

# Paper Fig 2, "Novelty" row, vase1 .. vase10 (read off the published figure).
PUB_NOVELTY <- c(2.24, 3.60, 4.08, 4.41, 4.33, 4.48, 4.42, 5.13, 5.20, 4.56)
# Paper Fig 2, "Typicality" row -- used for the polarity/semantics check below.
PUB_TYPICALITY <- c(5.70, 4.23, 4.14, 3.29, 4.61, 3.12, 3.13, 2.81, 2.67, 2.16)
# Paper body text, Ceramic Vase Stimulus 2: "ranked ninth in novelty (M = 3.60, SD = 1.72)".
PUB_S2_MEAN <- 3.60; PUB_S2_SD <- 1.72
TOL <- 0.015

d <- irw::irw_fetch(TABLE)
codes <- paste0("Novel_", 1:10)
obs  <- tapply(d$resp, d$item, mean)[codes]
osd  <- tapply(d$resp, d$item, sd)[codes]

cat(sprintf("%-9s %10s %10s %8s\n", "item", "Fig2", "observed", "diff"))
for (i in seq_along(codes))
    cat(sprintf("%-9s %10.2f %10.4f %8.3f\n", codes[i], PUB_NOVELTY[i], obs[i],
                obs[i] - PUB_NOVELTY[i]))

worst <- max(abs(obs - PUB_NOVELTY))
cat(sprintf("\nlargest deviation from Fig 2: %.4f (tolerance %.3f)\n", worst, TOL))

# The two tight pairs are what a swap would show up in: 4.41/4.42 (vases 4,7)
# and 4.47/4.48 (vases 6,10 sit at 4.48/4.56, and Novel_6 vs Novel_7 at 4.47/4.42).
cat(sprintf("tight pair Novel_4 / Novel_7 observed: %.4f / %.4f (Fig 2: %.2f / %.2f)\n",
            obs["Novel_4"], obs["Novel_7"], PUB_NOVELTY[4], PUB_NOVELTY[7]))
swap47 <- abs(obs["Novel_4"] - PUB_NOVELTY[7]) + abs(obs["Novel_7"] - PUB_NOVELTY[4])
keep47 <- abs(obs["Novel_4"] - PUB_NOVELTY[4]) + abs(obs["Novel_7"] - PUB_NOVELTY[7])
cat(sprintf("  |error| as shipped = %.4f ; if 4 and 7 were swapped = %.4f\n", keep47, swap47))

cat(sprintf("\nStimulus 2 body-text check: published M=%.2f SD=%.2f ; observed M=%.4f SD=%.4f\n",
            PUB_S2_MEAN, PUB_S2_SD, obs["Novel_2"], osd["Novel_2"]))
s2_ok <- abs(obs["Novel_2"] - PUB_S2_MEAN) <= TOL && abs(osd["Novel_2"] - PUB_S2_SD) <= 0.01

# Anchor-direction check: novelty and typicality are rated on the same 1-7
# agreement scale, so if 1 = Strongly Disagree they must be negatively related
# across stimuli (a plain classic vase is typical and not novel).
r <- cor(obs, PUB_TYPICALITY)
cat(sprintf("\ncor(observed novelty mean, Fig 2 typicality mean) over 10 vases = %+.3f\n", r))
cat(sprintf("  vase 1 (plain classic form): typicality %.2f / novelty %.4f -- lowest novelty in the set\n",
            PUB_TYPICALITY[1], obs["Novel_1"]))
cat("  A reversed anchor reading (1 = Strongly Agree) would make the least\n",
    "  typical vases the LEAST novel, i.e. flip this correlation positive.\n", sep = "")
dir_ok <- r < -0.5 && which.min(obs) == 1

cat("\nWhat this does NOT establish: item_text is identical for all ten items by\n",
    "design, so no route can or needs to distinguish it per item; and the 2-6\n",
    "scale points are shipped blank because the source labels only the endpoints.\n", sep = "")

cat(if (worst <= TOL && s2_ok && dir_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
