# verify_silva_2018_bsq.R -- batch_174
#
# STATUS OF THIS TABLE: BLOCKED on the item-wording rights rule (irw#1945); no
# __items.csv was written. This script banks the MAPPING evidence so that, if the
# BSQ rights position ever changes, the next round does not have to rebuild it.
# See notes_silva_2018_bsq.csv.
#
# Claim being checked: the live item codes BSQ5, BSQ11, ... are BSQ-34 item
# numbers (the S1 xlsx column names, melted unchanged by
# data/silva_2018_body_image.py), so BSQ<n> corresponds to item <n> of the
# unified Portuguese-language BSQ printed in Silva, Costa, Pimenta, Maroco &
# Campos (2016), Cad Saude Publica 32(7):e00133715, Table 2 (items numbered 1-34).
#
# Falsifiable prediction: that paper's Table 3 publishes per-item mean and SD for
# all 34 items in the same research programme's female university students
# (Brazil + Portugal, 2014, n = 526). The PLOS 2018 study's women (n = 1396, same
# ethics protocol C.A.A.E. 29896214.0.0000.5426) are a larger, overlapping
# sample, so exact agreement is NOT expected -- the test is whether the
# number-identity assignment is the best of all 8! = 40320 assignments of the
# 8 live codes to the 8 published BSQ-8B items on (mean, SD) jointly.

suppressMessages(library(irw))

TABLE <- "silva_2018_bsq"

# Cad Saude Publica 2016 Table 3, "Total" column (first of the three values).
PUB <- data.frame(
    num  = c(5, 11, 15, 20, 21, 22, 25, 28),
    mean = c(3.66, 1.70, 3.01, 2.42, 2.70, 3.04, 1.86, 2.69),
    sd   = c(1.50, 1.11, 1.49, 1.39, 1.66, 1.84, 1.34, 1.52)
)
PUB$item <- paste0("BSQ", PUB$num)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs_m <- tapply(d$resp, d$item, mean)[PUB$item]
obs_s <- tapply(d$resp, d$item, sd)[PUB$item]

cat(sprintf("%-6s %9s %9s %9s %9s %7s\n", "item", "pub_mean", "obs_mean", "pub_sd", "obs_sd", "n"))
nn <- table(d$item)[PUB$item]
for (i in seq_len(nrow(PUB)))
    cat(sprintf("%-6s %9.2f %9.2f %9.2f %9.2f %7d\n", PUB$item[i], PUB$mean[i], obs_m[i],
                PUB$sd[i], obs_s[i], as.integer(nn[i])))

# Cost of assigning live code i to published item j: squared distance in (mean, SD).
cost <- outer(seq_len(8), seq_len(8), function(i, j)
    (obs_m[i] - PUB$mean[j])^2 + (obs_s[i] - PUB$sd[j])^2)

perms <- function(v) {
    if (length(v) <= 1) return(list(v))
    out <- list()
    for (k in seq_along(v)) for (p in perms(v[-k])) out[[length(out) + 1]] <- c(v[k], p)
    out
}
P <- perms(1:8)
tot <- vapply(P, function(p) sum(cost[cbind(1:8, p)]), numeric(1))
ord <- order(tot)
best <- P[[ord[1]]]
identity_cost <- sum(diag(cost))
runner_up <- tot[ord[2]]

cat(sprintf("\nassignments tested: %d\n", length(P)))
cat(sprintf("identity (BSQ<n> -> item n) total cost: %.4f\n", identity_cost))
cat(sprintf("best assignment total cost:            %.4f  (is identity: %s)\n",
            tot[ord[1]], identical(best, 1:8)))
cat(sprintf("runner-up total cost:                  %.4f  (runner-up swaps: %s)\n", runner_up,
            paste(PUB$item[which(P[[ord[2]]] != 1:8)], collapse = ",")))
cat(sprintf("largest |mean diff| under identity: %.3f; largest |SD diff|: %.3f\n",
            max(abs(obs_m - PUB$mean)), max(abs(obs_s - PUB$sd))))

cat("\nWhat this does NOT establish: the samples differ (n=526 vs n=1396), so the\n",
    "runner-up margin, not the absolute fit, is the evidence; the closest pairs\n",
    "(BSQ15/BSQ22 and BSQ21/BSQ28, means within ~0.1) are separated mainly by SD.\n",
    "The primary tie is the code itself -- a BSQ-34 item number matching Table 2's\n",
    "numbering -- which this statistical check corroborates rather than replaces.\n", sep = "")

cat(if (identical(best, 1:8)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
