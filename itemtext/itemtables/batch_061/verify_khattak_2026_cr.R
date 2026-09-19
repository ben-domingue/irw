# verify_khattak_2026_cr.R -- Step 5b route 1 (per-item published frequencies).
#
# CLAIM: cr1..cr4 are the four "Clinical Readiness & Emergency Response Capacity"
# questions of Khattak et al. (2026) PeerJ 10.7717/peerj.21098, in the order the
# paper prints them (1 protocol, 2 emergency kit, 3 AED, 4 refresher interest).
#
# FALSIFIABLE PREDICTION: the paper's results table publishes the Yes count and
# percentage for each of the four items, and all four differ (178/44.5, 232/58.0,
# 30/7.5, 244/61.0). If any two item_texts were swapped, the observed per-item
# count of resp==1 ("Yes") would land on the wrong published value.

suppressMessages(library(irw))

TABLE <- "khattak_2026_cr"

# Khattak et al. 2026, PeerJ 21098, "Clinical Readiness & Emergency Response
# Capacity" table: Yes n (%) per item, N = 400.
PUB_N   <- c(cr1 = 178, cr2 = 232, cr3 = 30, cr4 = 244)
PUB_PCT <- c(cr1 = 44.5, cr2 = 58.0, cr3 = 7.5, cr4 = 61.0)
LABEL <- c(cr1 = "BLS/CPR protocol in clinic",
           cr2 = "emergency kit available",
           cr3 = "AED available",
           cr4 = "interested in refresher training")

d <- irw::irw_fetch(TABLE)
yes_n <- tapply(d$resp, d$item, function(x) sum(x == 1))
tot_n <- tapply(d$resp, d$item, length)
yes_n <- yes_n[names(PUB_N)]; tot_n <- tot_n[names(PUB_N)]
obs_pct <- 100 * yes_n / tot_n

cat(sprintf("%-5s %-34s %9s %9s %8s %8s\n",
            "item", "item_text (shipped, abbreviated)",
            "pub_yes_n", "obs_yes_n", "pub_%", "obs_%"))
for (i in names(PUB_N))
  cat(sprintf("%-5s %-34s %9d %9d %8.1f %8.1f\n",
              i, LABEL[i], PUB_N[i], yes_n[i], PUB_PCT[i], obs_pct[i]))

ok <- all(yes_n == PUB_N)

# What this does NOT establish: nothing -- the four published Yes counts are
# mutually distinct (178/232/30/244), so every item is separated from every
# other item by this route. It says nothing about the confidence items 5-8 of
# the same source section, which are a different IRW table.
cat(sprintf("\nall four counts distinct in the published table: %s\n",
            length(unique(PUB_N)) == 4))
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
