# verify_teicher_2015_mace_verbal.R -- copied from references/verify_template.R
#
# Claim: item codes Swore / Hurtful / Afraid / Leave (S9 File column names, used
# verbatim by data/teicher_2015_mace_items.py) carry the MACE-X wording of items
# 1 / 2 / 4 / 5, and resp 1 = "Yes", 0 = "No".
#
# Route 1 (primary): Teicher & Parigger (2015) PLOS ONE Table 5 (image,
# doi:10.1371/journal.pone.0117423.t005, "Rasch analysis of parental verbal abuse",
# n = 1050) prints % Yes per item against its wording: 30.8 / 41.0 / 30.0 / 13.9.
# Paper n equals live n (1050 per item), so each live %resp==1 must round to its
# OWN published value (tolerance 0.05 = half the printed precision). The tightest
# pair is Swore 30.8 vs Afraid 30.0 (0.8 apart = 8 respondents), which that
# tolerance separates; a Yes/No flip would give Leave 86.1.
#
# Route 2 (corroboration, for the Swore/Afraid pair): only form items 4-5 carry the
# "helpless or terrified" follow-up; the IRW distress tables hold those follow-ups
# under stems Afraid and Leave. Respondents rating distress on stem X must almost
# all have endorsed item X, and far fewer the other items.

suppressMessages(library(irw))

TABLE <- "teicher_2015_mace_verbal"
PUBLISHED <- c(
    Swore   = 30.8,  # 1 Swore at you, called you names, insulted
    Hurtful = 41.0,  # 2 Said hurtful things made you feel humiliated
    Afraid  = 30.0,  # 3 Acted in a way that made you feel afraid that you might be physically hurt
    Leave   = 13.9   # 4 Threatened to leave or abandon you
)
TOL <- 0.05

d <- as.data.frame(irw::irw_fetch(TABLE))
n_obs <- tapply(d$resp, d$item, length)
n_yes <- tapply(d$resp == 1, d$item, sum)
pct <- 100 * n_yes / n_obs

cat("Route 1: Table 5 % Yes vs live %resp==1\n")
cat(sprintf("%-8s %6s %6s %10s %10s %8s  %s\n", "item", "n", "yes", "published", "observed", "diff", "nearest"))
ok <- TRUE
for (it in names(PUBLISHED)) {
    nearest <- names(PUBLISHED)[which.min(abs(PUBLISHED - pct[[it]]))]
    dev <- pct[[it]] - PUBLISHED[[it]]
    cat(sprintf("%-8s %6d %6d %10.1f %10.3f %8.3f  %s\n", it, n_obs[[it]], n_yes[[it]],
                PUBLISHED[[it]], pct[[it]], dev, nearest))
    if (abs(dev) > TOL || nearest != it) ok <- FALSE
}
cat(sprintf("smallest gap between published values: %.1f points; tolerance %.2f\n",
            min(dist(PUBLISHED)), TOL))

cat("\nRoute 2: % endorsing each verbal item among respondents with distress=1 on a stem\n")
for (tb in c("teicher_2015_mace_distress_helpless", "teicher_2015_mace_distress_terrified")) {
    h <- as.data.frame(irw::irw_fetch(tb))
    for (st in c("Afraid", "Leave")) {
        ids <- unique(h$id[h$item == st & h$resp == 1])
        e <- sapply(names(PUBLISHED), function(k) 100 * mean(d$resp[d$item == k & d$id %in% ids] == 1))
        cat(sprintf("%-38s stem=%-6s n=%3d  %s\n", tb, st, length(ids),
                    paste(sprintf("%s=%.1f", names(e), e), collapse = " ")))
        if (names(which.max(e)) != st) ok <- FALSE
    }
}
cat("Route 1 distinguishes all four items from each other and fixes resp=1 as 'Yes';\n",
    "route 2 independently separates Afraid from Swore. Neither checks section_prompt\n",
    "wording or the online form's layout (only the formatted MACE-X .docx is published).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
