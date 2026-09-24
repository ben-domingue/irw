# verify_ai_fear_dong_2026_own_fear.R -- Step 5b mapping check (batch_330).
#
# Claim: the occupation prefix of each item code (Religious_, Care_, Journalist_,
# Manager_, Judge_, Doctor_) is tied to the matching occupation description in the
# study materials' own-fear block ("To what extent are you afraid of AI being ...?").
# The eight trait suffixes carry no separate question: own.fear was asked once per
# occupation and the long-format source repeats that answer on all eight trait rows.
#
# Falsifiable prediction: the SI of Dong et al. (OSF mb5nz, "SupplementaryMaterials_
# Cultural AI Fear.pdf", https://osf.io/download/6heq4/) Table S2 "Occupation average"
# row publishes M (SD) of own fear per occupation over all 10,000 respondents. The six
# means are all distinct (smallest gap 0.64, Manager vs Care worker), so matching them
# assigns every occupation prefix to exactly one description. Any swap of two
# occupation texts would break the match by >= 0.64.
#
# What this does NOT establish: which trait suffix is which -- there is nothing to
# establish, because within every id x occupation the 8 trait-coded rows are identical
# (printed below). That is a response-table defect, not a text-mapping question.

suppressMessages(library(irw))
TABLE <- "ai_fear_dong_2026_own_fear"

PUB_M  <- c(Judge = 63.62, Doctor = 62.67, Manager = 58.95, Care = 58.31,
            Religious = 55.94, Journalist = 55.22)
PUB_SD <- c(Judge = 31.86, Doctor = 31.81, Manager = 30.38, Care = 31.93,
            Religious = 33.75, Journalist = 31.63)
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
d$occ <- sub("_.*", "", d$item)

# One value per id x occupation: take the first trait row (all 8 are identical).
k <- aggregate(resp ~ id + occ, d, function(x) length(unique(x)))
cat(sprintf("id x occupation cells: %d; with >1 distinct resp across the 8 trait codes: %d\n\n",
            nrow(k), sum(k$resp > 1)))
one <- d[!duplicated(d[, c("id", "occ")]), ]

obs_m  <- tapply(one$resp, one$occ, mean)[names(PUB_M)]
obs_sd <- tapply(one$resp, one$occ, sd)[names(PUB_M)]
cat(sprintf("%-11s %8s %8s %8s | %8s %8s\n", "prefix", "pub_M", "obs_M", "diff", "pub_SD", "obs_SD"))
for (o in names(PUB_M))
    cat(sprintf("%-11s %8.2f %8.4f %8.4f | %8.2f %8.4f\n",
                o, PUB_M[o], obs_m[o], obs_m[o] - PUB_M[o], PUB_SD[o], obs_sd[o]))

worst_m  <- max(abs(obs_m - PUB_M))
worst_sd <- max(abs(obs_sd - PUB_SD))
gap <- min(diff(sort(PUB_M)))
cat(sprintf("\nlargest |mean diff| %.4f, largest |SD diff| %.4f (tol %.2f); smallest gap between published means %.2f\n",
            worst_m, worst_sd, TOL, gap))

ok <- worst_m <= TOL && worst_sd <= TOL && gap > 2 * TOL
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
