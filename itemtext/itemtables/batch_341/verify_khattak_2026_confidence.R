# verify_khattak_2026_confidence.R -- Step 5b route 1 (per-item published frequencies).
#
# CLAIM: confidence1..confidence4 are items 5-8 of "Section Four: Clinical Readiness &
# Emergency Response Capacity" in Khattak et al. (2026) PeerJ 10.7717/peerj.21098, in
# printed order (5 chest compressions, 6 AED, 7 choking, 8 recognizing cardiac arrest),
# and resp 1 = "Very confident", 2 = "Not confident".
#
# FALSIFIABLE PREDICTION: the paper's Table 3 publishes the Very confident / Not confident
# counts per item (N = 400), and all four Very-confident counts differ
# (164/114/264/166). If any two item_texts were swapped, or the 1/2 direction flipped,
# the observed per-item count of resp == 1 would land on the wrong published value.

suppressMessages(library(irw))

TABLE <- "khattak_2026_confidence"

# Khattak et al. 2026, PeerJ 21098, Table 3 rows 5-8: Very confident n / Not confident n.
PUB_VC <- c(confidence1 = 164, confidence2 = 114, confidence3 = 264, confidence4 = 166)
PUB_NC <- c(confidence1 = 236, confidence2 = 286, confidence3 = 136, confidence4 = 234)
LABEL  <- c(confidence1 = "chest compressions",
            confidence2 = "using an AED",
            confidence3 = "managing choking",
            confidence4 = "recognizing cardiac arrest")

d <- irw::irw_fetch(TABLE)
vc <- tapply(d$resp, d$item, function(x) sum(x == 1))[names(PUB_VC)]
nc <- tapply(d$resp, d$item, function(x) sum(x == 2))[names(PUB_VC)]

cat(sprintf("%-12s %-28s %7s %7s %7s %7s\n",
            "item", "item_text (abbrev.)", "pub_VC", "obs_1", "pub_NC", "obs_2"))
for (i in names(PUB_VC))
  cat(sprintf("%-12s %-28s %7d %7d %7d %7d\n",
              i, LABEL[i], PUB_VC[i], vc[i], PUB_NC[i], nc[i]))

ok <- all(vc == PUB_VC) && all(nc == PUB_NC)

# What this does NOT establish: nothing about the mapping is left open -- the four
# published counts are mutually distinct (closest pair 164 vs 166, confidence1 vs
# confidence4, separated by 2 exact counts), so every item is distinguished from every
# other, and the asymmetric counts also fix the 1/2 direction (a flip would give
# 236/286/136/234). It does not speak to which option wording respondents saw -- the
# questionnaire supplement's table header reads Yes/No over items 5-8.
flip_ok <- all(vc == PUB_NC)
cat(sprintf("\npublished VC counts distinct: %s; flipped direction would also match: %s\n",
            length(unique(PUB_VC)) == 4, flip_ok))
cat(if (ok && !flip_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
