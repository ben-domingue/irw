# verify_rdatasets_gssabortion.R
#
# mapping_basis is data_labels and the code derivation is pattern 1 (the IRW item
# code IS the source column name: data/Rdatasets.R does `item = names(x)[i]` over
# the GSS mnemonics), so Step 5b is exempt and this script is not required. It is
# written anyway because the exemption can be corroborated against numbers the GSS
# publishes itself, and the option axis (resp 0/1 -> "No"/"Yes") is a recode the
# Rdatasets port performed rather than something any label states.
#
# The falsifiable prediction: the share of resp==1 per item in the live IRW table
# must track the GSS's own published yes/(yes+no) marginals for that mnemonic --
# in rank order across all seven items, and within a couple of points in level.
# A swapped pair of item codes, or a flipped Yes/No coding, breaks it immediately.

suppressMessages(library(irw))

TABLE <- "rdatasets_gssabortion"

# GSS published counts by year, summed over 1972-2024, from the codebook pages at
# https://kjhealy.github.io/gssrdoc/reference/<var>.html (source: GSS, NORC).
YES <- c(abhlth = 43538, abrape = 39237, abdefect = 38428,
         abpoor = 23164, abnomore = 22063, absingle = 21745, abany = 17933)
NO  <- c(abhlth =  4950, abrape =  8783, abdefect =  9806,
         abpoor = 24941, abnomore = 26077, absingle = 26358, abany = 23465)
PUB <- 100 * YES / (YES + NO)

TOL <- 3.0   # points; the live port stops short of 2024, so a small gap is expected

d   <- irw::irw_fetch(TABLE)
d   <- d[!is.na(d$resp), ]
obs <- 100 * tapply(d$resp, d$item, mean)
n   <- tapply(d$resp, d$item, length)
obs <- obs[names(PUB)]; n <- n[names(PUB)]

cat(sprintf("%-9s %8s %10s %10s %8s\n", "item", "n", "published", "live %1", "diff"))
for (i in seq_along(PUB))
    cat(sprintf("%-9s %8d %10.2f %10.2f %8.2f\n",
                names(PUB)[i], n[i], PUB[i], obs[i], obs[i] - PUB[i]))

worst <- max(abs(obs - PUB))
rho   <- cor(obs, PUB, method = "spearman")
same_order <- identical(order(obs), order(PUB))

cat(sprintf("\nlargest deviation: %.2f points (tolerance %.1f)\n", worst, TOL))
cat(sprintf("rank order identical across all 7 items: %s (Spearman %.3f)\n", same_order, rho))
cat(sprintf("flipped-coding check: abhlth would read %.2f%% against a published %.2f%%\n",
            100 - obs[["abhlth"]], PUB[["abhlth"]]))

cat("Note: this route alone does not separate abnomore from absingle -- they differ by\n",
    "0.6 published points and ~0.4 live, about 1 SE at these n. The identity bijection in\n",
    "data/Rdatasets.R is what distinguishes every item from every other; this is corroboration.\n", sep = "")

cat(if (worst <= TOL && same_order) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
