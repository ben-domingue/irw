# Step 5b mapping verification for pakseresht_2021_gmfood_risk_ranking.
#
# Claim under test, two parts:
#   (a) item code -> ranked aspect: environmental=Environmental aspects,
#       health=Human health aspects, economic=Socio-economic aspects,
#       ethical=Ethical aspects (S1 File Appendix V, Box 2 option order).
#   (b) resp -> option_text direction: 1 = "Least relevant", 4 = "Most relevant"
#       (S1 File Box 2), NOT the reverse. data/pakseresht_2021_gmfood_ranking.py's
#       header comment asserts the opposite ("1=highest concern"), so this is a
#       live disagreement between two sources and has to be settled with numbers.
#
# Falsifiable prediction: the paper (Results, section 4.1) reports how many
# participants named each dimension their MAIN concern -- health 252,
# environmental 141, ethical 74, socio-economic 61 (n = 528, after 7 drops
# from the 535 in the S6 data file). If 4 = Most relevant, the count of
# resp == 4 per item must reproduce those four numbers (up to the 7 drops).
# If 1 = Most relevant, the resp == 1 counts would instead have to match --
# they do not, and are wrong by hundreds. A swapped item mapping breaks it too:
# the four counts are far apart (62..254), so any permutation is visible.

suppressMessages(library(irw))

TABLE <- "pakseresht_2021_gmfood_risk_ranking"

# Pakseresht et al. 2021 PLOS ONE 16(6):e0252580, Results: "health risks were
# the most relevant risk type (n = 252), followed by environmental risks
# (n = 141), ethical risks (n = 74), and socio-economic risks (n = 61)".
PUBLISHED_TOP <- c(health = 252, environmental = 141, ethical = 74, economic = 61)
ITEMS <- names(PUBLISHED_TOP)
TOL <- 7   # the 7 participants the paper discarded after this question

d <- irw::irw_fetch(TABLE)
top <- table(d$item[d$resp == 4])[ITEMS]
bot <- table(d$item[d$resp == 1])[ITEMS]

cat(sprintf("%-14s %12s %12s %8s %12s\n",
            "item", "published", "n(resp==4)", "diff", "n(resp==1)"))
for (i in ITEMS)
    cat(sprintf("%-14s %12d %12d %8d %12d\n",
                i, PUBLISHED_TOP[[i]], top[[i]],
                top[[i]] - PUBLISHED_TOP[[i]], bot[[i]]))

worst_top <- max(abs(as.integer(top) - as.integer(PUBLISHED_TOP)))
worst_bot <- max(abs(as.integer(bot) - as.integer(PUBLISHED_TOP)))
cat(sprintf("\nresp==4 largest deviation: %d (tolerance %d)\n", worst_top, TOL))
cat(sprintf("resp==1 largest deviation: %d  <- the reversed reading, for contrast\n",
            worst_bot))

# Permutation check: is the assignment we ship the ONLY one that fits?
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
fits <- 0
for (p in perms(ITEMS)) {
    if (max(abs(as.integer(top[p]) - as.integer(PUBLISHED_TOP))) <= TOL) fits <- fits + 1
}
cat(sprintf("permutations of the 4 item codes fitting the published counts within %d: %d of 24\n",
            TOL, fits))

cat("Note: this route pins all four items and the scale direction outright; it does\n",
    "not speak to the exact English wording, which is the study's own translation\n",
    "of a Swedish administration (S1 File: 'translated from Swedish').\n", sep = "")

cat(if (worst_top <= TOL && worst_bot > TOL && fits == 1)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
