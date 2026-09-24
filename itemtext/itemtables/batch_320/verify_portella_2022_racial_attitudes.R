# verify_portella_2022_racial_attitudes.R -- Step 5b, batch_320.
#
# Claim: item codes q9/q12/q57/q60 carry the codebook's statements (CODEBOOK.pdf,
# Dataverse doi:10.7910/DVN/ZHCTCK), and resp runs 1 = Strongly disagree ..
# 4 = Strongly agree for q12/q57/q60 but REVERSED for q9 (1 = Strongly agree ..
# 4 = Strongly disagree), as the authors' own 06_descriptive_en.R implies by
# building `reverse_q9` before tabulating under disagree->agree column labels.
#
# Falsifiable prediction: the paper's SI Table S4 ("Racial ideology among
# Brazilian students", PNAS 10.1073/pnas.2117956119 SI p.11) prints, per
# statement, the % Strongly disagrees / Disagrees / Agrees / Strongly agrees.
# Under the shipped mapping, the live per-item resp distribution (mapped to
# those labels via the shipped option_text) must reproduce each row. We also
# test all 24 item<->statement permutations and both q9 directions: only the
# shipped one may match.

suppressMessages(library(irw))
TABLE <- "portella_2022_racial_attitudes"

# SI Table S4 rows, columns = Strongly disagrees, Disagrees, Agrees, Strongly agrees
S4 <- rbind(
  dont_care   = c(0.79, 0.70,  9.94, 88.57),
  better_jobs = c(57.80, 28.10, 9.33, 4.78),
  democratic  = c(34.77, 33.23, 19.50, 12.50),
  less_work   = c(54.94, 33.34, 8.42, 3.29))
SHIPPED <- c(q9 = "dont_care", q12 = "better_jobs", q57 = "democratic", q60 = "less_work")
TOL <- 0.02

d <- irw::irw_fetch(TABLE)
pct <- function(x) round(100 * as.numeric(table(factor(x, levels = 1:4))) / length(x), 2)
# live distribution expressed in disagree->agree order, given a q9 direction
live_da <- function(item, q9_reversed) {
  p <- pct(d$resp[d$item == item])
  if (item == "q9" && q9_reversed) rev(p) else p
}

cat("Shipped mapping vs SI Table S4 (% SD / D / A / SA):\n")
worst <- 0
for (it in names(SHIPPED)) {
  obs <- live_da(it, TRUE); pub <- S4[SHIPPED[[it]], ]
  worst <- max(worst, abs(obs - pub))
  cat(sprintf("%-4s %-12s live %6.2f %6.2f %6.2f %6.2f | S4 %6.2f %6.2f %6.2f %6.2f\n",
              it, SHIPPED[[it]], obs[1], obs[2], obs[3], obs[4], pub[1], pub[2], pub[3], pub[4]))
}
cat(sprintf("largest abs deviation (shipped): %.3f pp (tol %.2f)\n\n", worst, TOL))

# Alternatives: every permutation of statements x both q9 directions
perms <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
n_match <- 0; shipped_ok <- FALSE
for (p in perms(rownames(S4))) for (rv in c(TRUE, FALSE)) {
  dev <- max(sapply(seq_along(p), function(k) max(abs(live_da(names(SHIPPED)[k], rv) - S4[p[k], ]))))
  if (dev <= TOL) {
    n_match <- n_match + 1
    if (identical(unname(p), unname(SHIPPED)) && rv) shipped_ok <- TRUE
  }
}
q9_unrev <- max(abs(live_da("q9", FALSE) - S4["dont_care", ]))
cat(sprintf("q9 read unreversed (1 = Strongly disagree): deviation %.2f pp\n", q9_unrev))
cat(sprintf("mappings (24 permutations x 2 q9 directions) matching S4 within tol: %d; shipped among them: %s\n",
            n_match, shipped_ok))
cat("Does NOT establish: the Portuguese item wording (not in the deposit or SI); only that each\n",
    "code carries the statement Table S4 attributes to its distribution, in the stated direction.\n", sep = "")
cat(if (worst <= TOL && n_match == 1 && shipped_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
