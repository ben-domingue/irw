# verify_hannachi_2025_eco_anxiety_cas.R
#
# CLAIM UNDER TEST: live item code cas<i> is the deposit's CCAS<i> column, whose
# French wording the deposit codebook ("code book for data.xlsx", sheet Feuil1)
# states row by row, and which the CC BY 4.0 French validation (Mouguiama-Daouda
# et al., 2022, Psychologica Belgica 62(1), supplementary pb-62-1-1137-s1.pdf)
# prints against the same item numbers. If item_text for any two items were
# swapped, the response-category profile below would land on the wrong code.
#
# The falsifiable prediction: the study's own Supplementary Table S5.1 publishes,
# per item code, the count of respondents in each response category 0..4. Those
# 13 x 5 count vectors are all distinct, so matching them cell for cell
# distinguishes EVERY item from every other item, and also fixes the direction of
# the resp axis (a flipped 0..4 coding would break every row).
#
# Data: the live IRW table only (6,942 rows -- a trivially small export).

suppressMessages(library(irw))

TABLE <- "hannachi_2025_eco_anxiety_cas"

# Hannachi & Somat (2025), Supplementary_Materials.docx, Table S5.1
# "Item means, standard deviations, skewness, and response category frequencies,
#  n (%). Response categories: 0 = not at all to 4 = completely. N = 534."
# rows: counts at resp 0,1,2,3,4 ; then the published mean.
PUB <- list(
  cas1  = list(c(258, 138,  66,  50,  22), 0.95),
  cas2  = list(c(303, 102,  66,  33,  30), 0.85),   # deposit column CCAS2/HEAS8
  cas3  = list(c(395,  82,  32,  17,   8), 0.43),
  cas4  = list(c(371,  78,  41,  24,  20), 0.58),
  cas5  = list(c(262, 127,  80,  47,  18), 0.94),
  cas6  = list(c(358,  92,  51,  24,   9), 0.57),
  cas7  = list(c(424,  55,  27,  19,   9), 0.38),
  cas8  = list(c(350,  95,  53,  27,   9), 0.60),
  cas9  = list(c(329, 109,  56,  32,   8), 0.65),   # deposit column CCAS9/HEAS9
  cas10 = list(c(160, 124, 100, 102,  48), 1.54),
  cas11 = list(c(344, 106,  46,  26,  12), 0.61),   # deposit column CCAS11/HEAS10
  cas12 = list(c(316,  90,  75,  36,  17), 0.78),
  cas13 = list(c(351,  82,  54,  30,  17), 0.65)
)

d  <- irw::irw_fetch(TABLE)
tb <- table(d$item, factor(d$resp, levels = 0:4))

cat(sprintf("%-6s %-28s %-28s %8s %8s\n",
            "item", "published n(0..4)", "observed n(0..4)", "pub M", "obs M"))
bad <- 0
for (it in names(PUB)) {
    pub <- as.integer(PUB[[it]][[1]])
    obs <- as.integer(tb[it, ])
    m   <- mean(d$resp[d$item == it])
    cat(sprintf("%-6s %-28s %-28s %8.2f %8.2f%s\n",
                it, paste(pub, collapse = ","), paste(obs, collapse = ","),
                PUB[[it]][[2]], m,
                if (identical(pub, obs)) "" else "   <-- MISMATCH"))
    if (!identical(pub, obs)) bad <- bad + 1
    if (abs(round(m, 2) - PUB[[it]][[2]]) > 0.005) bad <- bad + 1
}

cat(sprintf("\nitems with a mismatched category profile: %d of %d\n", bad, length(PUB)))

# Distinctness check: the route is only decisive if no two published profiles
# coincide.  Print that rather than assume it.
profiles <- sapply(PUB, function(x) paste(x[[1]], collapse = ","))
cat(sprintf("distinct published profiles: %d of %d\n",
            length(unique(profiles)), length(profiles)))

cat("What this does NOT establish: nothing about the wording itself beyond the\n",
    "code it hangs on -- the French text comes from the deposit codebook and the\n",
    "CC BY French validation, both of which key it to the same CCAS1..CCAS13\n",
    "numbering this script matches. It also says nothing about option_text, which\n",
    "is deliberately blank (the administered French anchors were never published).\n", sep = "")

cat(if (bad == 0 && length(unique(profiles)) == length(profiles))
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
