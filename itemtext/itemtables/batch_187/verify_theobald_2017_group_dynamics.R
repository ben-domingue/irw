# verify_theobald_2017_group_dynamics.R -- Step 5b, route 9 (response-frequency matching).
#
# Claim being verified: item Comfort = "I felt comfortable with my group." and item
# Dominator = "One group member dominated discussion during today's [topic] activity.",
# with resp 1..6 = Strongly Disagree, Disagree, Somewhat Disagree, Somewhat Agree,
# Agree, Strongly Agree for both.
#
# Published values: Theobald et al. (2017) PLOS ONE 12(7):e0181336, Table 1
# ("Questions on the survey and the percentage of responses", pooled across all three
# survey iterations, n = 1300 each). Counts hard-coded below in resp order 1..6
# (Strongly Disagree .. Strongly Agree).
#
# What would break: swapping the two item texts (the count vectors differ at every
# level), or reversing the anchor direction (neither vector is its own reverse).
# Table is ~2,600 rows, so the live fetch is negligible against the export cap.

suppressMessages(library(irw))

TABLE <- "theobald_2017_group_dynamics"
LEVELS <- c("Strongly Disagree", "Disagree", "Somewhat Disagree",
            "Somewhat Agree", "Agree", "Strongly Agree")

PUBLISHED <- list(
    # "I felt comfortable with my group. (NewEng19)"
    Comfort   = c(4, 13, 41, 151, 589, 502),
    # "One group member dominated discussion during today's [topic] activity. (NewEng22)"
    Dominator = c(86, 391, 291, 240, 195, 97)
)

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]

obs <- lapply(names(PUBLISHED), function(it)
    as.numeric(table(factor(d$resp[d$item == it], levels = 1:6))))
names(obs) <- names(PUBLISHED)

ok <- TRUE
for (it in names(PUBLISHED)) {
    cat(sprintf("\n%s (published Table 1 vs live), resp 1..6\n", it))
    cat(sprintf("  %-18s %5s %9s %6s\n", "option", "resp", "published", "live"))
    for (k in 1:6)
        cat(sprintf("  %-18s %5d %9d %6d\n", LEVELS[k], k,
                    PUBLISHED[[it]][k], obs[[it]][k]))
    m <- all(obs[[it]] == PUBLISHED[[it]])
    rev_m <- all(rev(obs[[it]]) == PUBLISHED[[it]])
    cat(sprintf("  exact match: %s | matches if anchors reversed: %s\n", m, rev_m))
    ok <- ok && m && !rev_m
}

# Swap test: would the published vectors also fit with the item texts exchanged?
swap <- all(obs$Comfort == PUBLISHED$Dominator) || all(obs$Dominator == PUBLISHED$Comfort)
cat(sprintf("\nswapped item texts would also match: %s\n", swap))
ok <- ok && !swap

cat("Establishes: which code carries which of the two questions, and the 1=Strongly Disagree\n",
    "..6=Strongly Agree direction, cell for cell (12/12). Does not establish the administered\n",
    "value of the [topic] placeholder, which Table 1 prints as a placeholder.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
