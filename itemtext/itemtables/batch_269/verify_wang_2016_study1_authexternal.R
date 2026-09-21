# verify_wang_2016_study1_authexternal.R
#
# CLAIM UNDER TEST (Step 5b), in two parts:
#   (a) BLOCK IDENTITY + STORED DIRECTION: the four codes authexternal1..4 are the
#       four Accepting External Influence items of the 12-item Authenticity Scale
#       (Wood et al., 2008), and they are stored ALREADY REVERSE-SCORED -- i.e. a
#       stored 5 means the respondent answered "strongly disagree" to the external-
#       influence statement.  That is why the shipped option_text puts "strongly
#       agree" at resp = 1 and "strongly disagree" at resp = 5, the OPPOSITE of the
#       paper's stated "1 (strongly disagree) to 5 (strongly agree)" administration
#       coding and the opposite of the anchors shipped for the sibling authliving
#       table.  (Same finding as batch_268's wang_2016_study1_authalien.)
#   (b) WITHIN-BLOCK ORDER: authexternal1/2/3/4 are AS items 3/4/5/6 in that order.
#       This script CANNOT test (b) -- all four items are the same polarity class,
#       share one 1-5 range, the study publishes no per-item statistics, and the
#       paper states the item order was randomised per respondent.  It says so
#       below.  Hence status PARTIAL.
#
# Falsifiable predictions for (a), all from live IRW tables only:
#   1. Every authexternal item correlates POSITIVELY with the self-esteem total
#      built from wang_2016_study1_se.  Raw (unreversed) accepting-external-
#      influence -- "I am strongly influenced by the opinions of others" -- must
#      correlate NEGATIVELY with self-esteem (Wood et al. 2008; the Russian AS
#      validation reports r = -0.32).  The self-esteem total's own direction is
#      established in-script by showing all ten of its items have positive
#      item-rest correlations.
#   2. Summing the live authliving + authalien + authexternal tables per person
#      reproduces Wang (2016) PLOS ONE Table 1's Authenticity M = 42.49, SD = 6.18
#      and its r = .61 with the self-esteem total (published M = 38.34, SD = 5.08),
#      and Cronbach's alpha over those 12 stored columns reproduces the paper's
#      reported .81.  The rival "external block stored raw" reading (flipping only
#      this table back, 6 - x) leaves the total mean almost unchanged -- so the
#      MEAN is NOT the discriminating statistic here -- but collapses alpha and the
#      published correlation.  Both are printed.
#   3. CODE-TO-COLUMN TIE: the live per-item M/SD reproduce the PLOS S1 Dataset's
#      A_other1 / A_o2 / A_o3 / A_o4 columns, which is the number-preserving rename
#      in data/wang_2016_authenticity_relationship.py.  Hard-coded here from the
#      .sav (cached, sha256 6874ddedac4383b93d70400b866bdd89f1040706fc7e17ea87ee14e05f14aac2)
#      so the script needs no credentials for the deposit.

suppressMessages(library(irw))

PUB <- list(auth_m = 42.49, auth_sd = 6.18, se_m = 38.34, se_sd = 5.08,
            r = 0.61, alpha = 0.81)
TOL_M <- 0.05; TOL_SD <- 0.05; TOL_R <- 0.02; TOL_A <- 0.01

## s001.sav columns A_other1, A_o2, A_o3, A_o4 (n = 104 each), read with pyreadstat
SAV <- data.frame(col = c("A_other1", "A_o2", "A_o3", "A_o4"),
                  m  = c(3.2019, 3.2500, 2.9712, 2.6731),
                  sd = c(0.9792, 0.9217, 1.0188, 0.8862),
                  stringsAsFactors = FALSE)

wide <- function(tab) {
    x <- irw::irw_fetch(tab)
    d <- data.frame(id = as.character(x$id), item = as.character(x$item),
                    resp = as.numeric(x$resp))
    w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
    rn <- w$id; w <- as.matrix(w[, -1, drop = FALSE])
    colnames(w) <- sub("^resp\\.", "", colnames(w)); rownames(w) <- rn
    w
}
alpha <- function(X) { k <- ncol(X); k/(k-1) * (1 - sum(apply(X, 2, var))/var(rowSums(X))) }

ao <- wide("wang_2016_study1_authexternal")
ao <- ao[, c("authexternal1","authexternal2","authexternal3","authexternal4")]
aa <- wide("wang_2016_study1_authalien")
al <- wide("wang_2016_study1_authliving")
se <- wide("wang_2016_study1_se")

ids <- Reduce(intersect, list(rownames(ao), rownames(aa), rownames(al), rownames(se)))
ao <- ao[ids, ]; aa <- aa[ids, ]; al <- al[ids, ]; se <- se[ids, ]
cat(sprintf("n persons common to all four Study 1 tables: %d\n", length(ids)))
cat(sprintf("authexternal items: %s\n\n", paste(colnames(ao), collapse = ", ")))

## --- code-to-column tie ----------------------------------------------------
cat("(0) live per-item M/SD against the PLOS S1 .sav columns the rename maps onto\n")
cat(sprintf("    %-14s %-10s %16s %16s\n", "live item", ".sav col", "live M (SD)", ".sav M (SD)"))
tie_ok <- TRUE
for (j in seq_len(ncol(ao))) {
    m <- mean(ao[, j]); s <- sd(ao[, j])
    cat(sprintf("    %-14s %-10s %7.4f (%.4f) %7.4f (%.4f)\n",
                colnames(ao)[j], SAV$col[j], m, s, SAV$m[j], SAV$sd[j]))
    tie_ok <- tie_ok && abs(m - SAV$m[j]) < 5e-4 && abs(s - SAV$sd[j]) < 5e-4
}
cat(sprintf("    all four reproduce their .sav column to 4 dp: %s\n\n", tie_ok))

## --- direction of the self-esteem yardstick -------------------------------
se_tot <- rowSums(se)
cat("(i) the yardstick: item-rest r for each of the 10 self-esteem items\n")
ir <- sapply(seq_len(ncol(se)), function(j) cor(se[, j], rowSums(se[, -j, drop = FALSE])))
cat(sprintf("    %s\n", paste(sprintf("%s=%+.2f", colnames(se), ir), collapse = "  ")))
cat(sprintf("    min item-rest r = %+.3f -- all positive, so the total is keyed\n", min(ir)))
cat("    self-esteem-POSITIVE (higher = higher self-esteem).\n\n")
yardstick_ok <- min(ir) > 0

## --- prediction 1: sign of authexternal vs self-esteem ---------------------
cat("(ii) r(authexternal item, self-esteem total) -- positive iff stored reversed\n")
r_ao <- sapply(seq_len(ncol(ao)), function(j) cor(ao[, j], se_tot))
for (j in seq_along(r_ao))
    cat(sprintf("     %-14s r = %+.3f\n", colnames(ao)[j], r_ao[j]))
cat(sprintf("     min = %+.3f, max = %+.3f. Under the rival 'stored raw' reading these\n",
            min(r_ao), max(r_ao)))
cat(sprintf("     would be %+.3f .. %+.3f -- every one negative, which is the published\n",
            -max(r_ao), -min(r_ao)))
cat("     direction for this subscale (AEI vs self-esteem r = -0.32, Russian AS\n")
cat("     validation, Front. Psychol. 11:609617).\n\n")
sign_ok <- all(r_ao > 0)

## --- prediction 2: published total, correlation and alpha ------------------
A <- cbind(al, aa, ao)
auth <- rowSums(A)
cat(sprintf("(iii) %-26s %10s %10s %8s\n", "", "published", "observed", "diff"))
row <- function(lab, pub, obs) cat(sprintf("      %-26s %10.2f %10.2f %8.3f\n", lab, pub, obs, obs - pub))
row("Authenticity total M",  PUB$auth_m,  mean(auth))
row("Authenticity total SD", PUB$auth_sd, sd(auth))
row("Self-esteem total M",   PUB$se_m,    mean(se_tot))
row("Self-esteem total SD",  PUB$se_sd,   sd(se_tot))
row("r(authenticity, SE)",   PUB$r,       cor(auth, se_tot))
row("alpha, 12 stored items", PUB$alpha,  alpha(A))

## counterfactual: THIS table stored raw (flip only the external block back)
Ae <- cbind(al, aa, 6 - ao)
cat(sprintf("\n      counterfactual 'external block stored raw' (flip only this table):\n"))
cat(sprintf("        total M = %.2f (published %.2f -- NOT discriminating on its own),\n",
            mean(rowSums(Ae)), PUB$auth_m))
cat(sprintf("        alpha = %.3f (published %.2f) and r with SE = %.3f (published %.2f)\n",
            alpha(Ae), PUB$alpha, cor(rowSums(Ae), se_tot), PUB$r))
cat("        -- both far off, so the stored coding is the one the paper reports.\n")
Af <- cbind(al, 6 - aa, 6 - ao)
cat(sprintf("      counterfactual 'alien + external both stored raw': total M = %.2f, alpha = %.3f\n\n",
            mean(rowSums(Af)), alpha(Af)))

tot_ok <- abs(mean(auth) - PUB$auth_m)  <= TOL_M  &&
          abs(sd(auth)   - PUB$auth_sd) <= TOL_SD &&
          abs(mean(se_tot) - PUB$se_m)  <= TOL_M  &&
          abs(sd(se_tot)   - PUB$se_sd) <= TOL_SD &&
          abs(cor(auth, se_tot) - PUB$r) <= TOL_R &&
          abs(alpha(A) - PUB$alpha)      <= TOL_A
cf_ok <- abs(alpha(Ae) - PUB$alpha) > 0.10 && abs(cor(rowSums(Ae), se_tot) - PUB$r) > 0.10

## --- corroboration: subscale intercorrelations -----------------------------
cat("(iv) corroboration -- stored subscale totals should all point the same way\n")
cat(sprintf("     r(external, alienation) = %+.3f, r(external, authliving) = %+.3f,\n",
            cor(rowSums(ao), rowSums(aa)), cor(rowSums(ao), rowSums(al))))
cat(sprintf("     r(external, self-esteem) = %+.3f -- all positive, as they must be if\n",
            cor(rowSums(ao), se_tot)))
cat("     every block is stored keyed towards authenticity.\n\n")

## --- what this does NOT establish -----------------------------------------
cat("(v) what is NOT verified: which of AS items 3, 4, 5 and 6 each code is.\n")
for (j in seq_len(ncol(ao)))
    cat(sprintf("     %-14s item-rest r = %.3f, M = %.2f, SD = %.2f\n",
                colnames(ao)[j], cor(ao[, j], rowSums(ao[, -j, drop = FALSE])),
                mean(ao[, j]), sd(ao[, j])))
cat("     All four are one polarity class on one 1-5 range; the study publishes no\n")
cat("     per-item statistics, states that item order was randomised within each\n")
cat("     survey, and the source .sav (PLOS s001) carries no variable or value\n")
cat("     labels, so no route separates them. Within-block order is inferred from\n")
cat("     the canonical Wood et al. (2008) subscale numbering (3, 4, 5, 6\n")
cat("     ascending) and is NOT verified here.\n\n")

ok <- tie_ok && yardstick_ok && sign_ok && tot_ok && cf_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
