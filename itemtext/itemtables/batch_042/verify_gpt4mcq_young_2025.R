# verify_gpt4mcq_young_2025.R
#
# Claim under test: the item_text/option_text shipped for AIQ1..AIQ20 are the
# SPSS variable/value labels carried on the very columns the IRW codes come
# from ("ChatGPT IRT DATA_CLEAN.sav", OSF zq4eg), i.e. the administered items --
# and NOT the different 20-item AI block printed in the same deposit's
# "Reading and ChatGPT-Generated MCIs (Supplementary Materials 2).docx".
#
# The two candidate wordings put the keyed-correct option in different
# positions.  Under the .sav labels the correct alternative is value 1 for all
# 20 items (the generation prompt's format lists "Correct Response" first).
# Under the SM2 wording the correct alternative sits at the positions in
# SM2_KEY below.  Supplementary Materials 3 publishes the CTT P-value
# (proportion correct, N = 190) per item, so each candidate makes a falsifiable
# prediction about the live response data.

suppressMessages(library(irw))

TABLE <- "gpt4mcq_young_2025"
ITEMS <- paste0("AIQ", 1:20)

# Supplementary Materials 3 (OSF zq4eg), "Item Statistics Using CTT", P-value column.
PUBLISHED <- c(0.916, 0.889, 0.816, 0.926, 0.911, 0.937, 0.932, 0.932, 0.926, 0.889,
               0.889, 0.926, 0.947, 0.679, 0.832, 0.926, 0.937, 0.937, 0.500, 0.868)

# Position of the correct alternative under the SM2 (rejected) wording.
SM2_KEY <- c(3,3,2,2,1,2,4,3,3,3,3,4,3,2,3,4,4,4,1,4)

d <- irw::irw_fetch(TABLE)
d <- d[d$item %in% ITEMS, ]

p_sav <- sapply(ITEMS, function(i) mean(d$resp[d$item == i] == 1))
p_sm2 <- sapply(seq_along(ITEMS),
                function(k) mean(d$resp[d$item == ITEMS[k]] == SM2_KEY[k]))

cat(sprintf("%-7s %6s %6s %8s %8s\n",
            "item", "pub", "sav1", "diff", "SM2key"))
for (k in seq_along(ITEMS))
    cat(sprintf("%-7s %6.3f %6.3f %8.4f %8.3f\n",
                ITEMS[k], PUBLISHED[k], p_sav[k], p_sav[k] - PUBLISHED[k], p_sm2[k]))

worst <- max(abs(p_sav - PUBLISHED))
cat(sprintf("\nlargest |published - P(resp==1)| over 20 items: %.4f (tolerance 0.001)\n", worst))
cat(sprintf("mean P(correct) under .sav labels: %.3f ; under SM2 wording: %.3f\n",
            mean(p_sav), mean(p_sm2)))

# What this does NOT establish: several published P-values tie (0.926 four
# times, 0.937 three times, 0.889 three times), so this route cannot separate
# those items from one another on its own.  What separates them is that the
# label and the response column are the SAME .sav column and the IRW code IS
# that column name (data/gpt4mcq_young_2025.r selects starts_with("AIQ") with
# no rename), so no permutation is possible; the check above is what rules out
# the rival wording set published in the same deposit.

ok <- worst <= 0.001 && mean(p_sm2) < 0.3
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
