# verify_SCS_Suh_2023_SCS.R -- Step 5b mapping check for SCS_Suh_2023_SCS (batch_170).
#
# CLAIM: live item SCS_n carries item n of Singelis's 30-item Self-Construal Scale as
# numbered in Singelis's own distribution letter ("latest version of the SCS",
# singelis_update_singelis_2007_english.pdf). The deposit's .sav files carry NO variable
# or value labels, so the tie code-number -> text is the instrument's printed numbering.
#
# ROUTE 5 (subscale block structure), with a PRE-REGISTERED partition: the letter's
# SCORING section assigns independent = #1,2,5,7,9,10,13,15,18,20,22,24,25,27,29 and
# interdependent = the other 15. The study's own OSF syntax (SCS_CFA syntax.R, Model3,
# "2 factors based on Singles (30 item)") uses exactly this partition on SCS_1..SCS_30,
# and its Model4 (24 item) drops exactly the letter's six added items (5,7,24 / 12,14,30).
# Test: each item should correlate more, on average, with its own subscale than with the
# other. A text permutation across subscales breaks this; a 2000-draw label permutation
# gives the null.
#
# CORROBORATION (not pre-registered -- the pairs were named from item content after the
# correlation matrix had been viewed during exploration, so treat as supporting only):
# nine near-paraphrase content pairs should sit in each other's top-3 correlates.
#
# DOES NOT ESTABLISH: order within a subscale in general. A swap between two
# same-subscale items with no content twin (e.g. SCS_5 <-> SCS_15, SCS_11 <-> SCS_12)
# or within a twin pair (SCS_20 <-> SCS_29) would still pass. Status is PARTIAL.

suppressMessages(library(irw))
TABLE <- "SCS_Suh_2023_SCS"

d <- as.data.frame(irw::irw_fetch(TABLE))
d$pid <- paste(d$group, d$id)
w <- reshape(d[, c("pid", "group", "item", "resp")], idvar = c("pid", "group"),
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
it <- paste0("SCS_", 1:30)
cat("persons:", nrow(w), " (by group:", paste(names(table(w$group)), table(w$group), collapse = ", "), ")\n\n")

R <- cor(w[, it], use = "pairwise.complete.obs"); diag(R) <- NA

IND <- c(1, 2, 5, 7, 9, 10, 13, 15, 18, 20, 22, 24, 25, 27, 29)
lab <- ifelse(1:30 %in% IND, 1L, 2L)
own_oth <- function(lab) t(sapply(1:30, function(i) {
    s <- which(lab == lab[i]); o <- which(lab != lab[i])
    c(own = mean(R[i, setdiff(s, i)], na.rm = TRUE), oth = mean(R[i, o]))
}))
oo <- own_oth(lab)
cat("Route 5 -- Singelis independent/interdependent partition\n")
cat(sprintf("%-7s %4s %7s %7s\n", "item", "sub", "own_r", "other_r"))
for (i in 1:30) cat(sprintf("%-7s %4s %7.3f %7.3f%s\n", it[i], c("IND", "INT")[lab[i]],
                            oo[i, 1], oo[i, 2], if (oo[i, 1] <= oo[i, 2]) "  <-- misfit" else ""))
score <- function(lab) { m <- own_oth(lab); sum(m[, 1] > m[, 2]) }
obs <- score(lab)
set.seed(1)
null <- replicate(2000, score(sample(lab)))
cat(sprintf("\nitems closer to own subscale: %d/30; permutation null (2000): mean %.1f, 99th pct %.0f, max %d\n",
            obs, mean(null), quantile(null, 0.99), max(null)))
cat(sprintf("mean r within IND %.3f, within INT %.3f, between %.3f\n\n",
            mean(R[IND, IND], na.rm = TRUE), mean(R[-IND, -IND], na.rm = TRUE), mean(R[IND, -IND])))

pairs <- list(c(20, 29), # act the same no matter who I am with / at home and at school
              c(9, 13),  # say "No" directly / direct and forthright
              c(2, 18),  # talk openly with an older stranger / speaking up in class
              c(26, 28), # respect group decisions / maintain group harmony
              c(25, 27), # take care of myself primary / personal identity independent
              c(8, 23),  # sacrifice self interest for group / stay in group if they need me
              c(17, 21), # relationships > accomplishments / happiness depends on others
              c(24, 25), # do what is best for me / take care of myself
              c(3, 30))  # avoid an argument / go along with what others want
top3 <- function(i) order(R[i, ], decreasing = TRUE, na.last = TRUE)[1:3]
cat("Corroboration -- content-twin pairs (r, rank of partner among 29)\n")
hits <- 0
for (p in pairs) {
    a <- p[1]; b <- p[2]
    ra <- rank(-R[a, -a])[which((1:30)[-a] == b)]
    rb <- rank(-R[b, -b])[which((1:30)[-b] == a)]
    ok <- (b %in% top3(a)) && (a %in% top3(b))
    hits <- hits + ok
    cat(sprintf("SCS_%-3d SCS_%-3d r=%.3f  rank %2.0f / %2.0f %s\n", a, b, R[a, b], ra, rb,
                if (ok) "mutual top-3" else ""))
}
cat(sprintf("mutual top-3 pairs: %d/9\n\n", hits))

# Anchor direction (letter: 1 = STRONGLY DISAGREE ... 7 = STRONGLY AGREE), printed only.
m <- sapply(c("US", "Korea"), function(g) colMeans(w[w$group == g, it], na.rm = TRUE))
cat(sprintf("SCS_1 'I enjoy being unique...': US mean %.2f, Korea mean %.2f (largest US-Korea gap of 30: %s)\n",
            m["SCS_1", "US"], m["SCS_1", "Korea"], it[which.max(abs(m[, 1] - m[, 2]))]))
cat("Not established: order within a subscale beyond the twin pairs; see header.\n")

pass <- obs >= 28 && obs > max(null) && hits >= 6
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
