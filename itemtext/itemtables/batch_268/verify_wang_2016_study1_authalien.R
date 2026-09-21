# verify_wang_2016_study1_authalien.R
#
# CLAIM UNDER TEST (Step 5b), in two parts:
#   (a) BLOCK IDENTITY + STORED DIRECTION: the four codes authalien1..4 are the
#       four Self-Alienation items of the 12-item Authenticity Scale (Wood et al.,
#       2008), and they are stored ALREADY REVERSE-SCORED -- i.e. a stored 5 means
#       the respondent answered "strongly disagree" to the alienation statement,
#       which is why the shipped option_text puts "strongly agree" at resp = 1 and
#       "strongly disagree" at resp = 5, the OPPOSITE of the paper's stated
#       "1 (strongly disagree) to 5 (strongly agree)" administration coding and the
#       opposite of the anchors shipped for the sibling authliving table.
#   (b) WITHIN-BLOCK ORDER: authalien1/2/3/4 are AS items 2/7/10/12 in that order.
#       This script CANNOT test (b) -- all four items are the same polarity class,
#       share one 1-5 range, and the study publishes no per-item statistics -- and
#       it says so below.  Hence status PARTIAL.
#
# Falsifiable predictions for (a), all from live IRW tables only:
#   1. Every authalien item correlates POSITIVELY with the self-esteem total built
#      from wang_2016_study1_se.  Raw (unreversed) self-alienation -- "I feel
#      alienated from myself" -- must correlate NEGATIVELY with self-esteem.  The
#      self-esteem total's own direction is established in-script by showing all ten
#      of its items have positive item-rest correlations.
#   2. Summing the live authliving + authalien + authexternal tables per person
#      reproduces Wang (2016) PLOS ONE Table 1's Authenticity M = 42.49, SD = 6.18
#      and its r = .61 with the self-esteem total (published M = 38.34, SD = 5.08),
#      and Cronbach's alpha over those 12 stored columns reproduces the paper's
#      reported .81.  Under the rival "stored raw" reading the author's own total
#      would be a mixed-direction sum: flipping the alienation and external-influence
#      blocks (6 - x) moves the total to ~36.8 and alpha to ~.71.

suppressMessages(library(irw))

PUB <- list(auth_m = 42.49, auth_sd = 6.18, se_m = 38.34, se_sd = 5.08,
            r = 0.61, alpha = 0.81)
TOL_M <- 0.05; TOL_SD <- 0.05; TOL_R <- 0.02; TOL_A <- 0.01

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

aa <- wide("wang_2016_study1_authalien")
aa <- aa[, c("authalien1","authalien2","authalien3","authalien4")]
al <- wide("wang_2016_study1_authliving")
ao <- wide("wang_2016_study1_authexternal")
se <- wide("wang_2016_study1_se")

ids <- Reduce(intersect, list(rownames(aa), rownames(al), rownames(ao), rownames(se)))
aa <- aa[ids, ]; al <- al[ids, ]; ao <- ao[ids, ]; se <- se[ids, ]
cat(sprintf("n persons common to all four Study 1 tables: %d\n", length(ids)))
cat(sprintf("authalien items: %s\n\n", paste(colnames(aa), collapse = ", ")))

## --- direction of the self-esteem yardstick -------------------------------
se_tot <- rowSums(se)
cat("(i) the yardstick: item-rest r for each of the 10 self-esteem items\n")
ir <- sapply(seq_len(ncol(se)), function(j) cor(se[, j], rowSums(se[, -j, drop = FALSE])))
cat(sprintf("    %s\n", paste(sprintf("%s=%+.2f", colnames(se), ir), collapse = "  ")))
cat(sprintf("    min item-rest r = %+.3f -- all positive, so the total is keyed\n", min(ir)))
cat("    self-esteem-POSITIVE (higher = higher self-esteem).\n\n")
yardstick_ok <- min(ir) > 0

## --- prediction 1: sign of authalien vs self-esteem ------------------------
cat("(ii) r(authalien item, self-esteem total) -- positive iff stored reversed\n")
r_aa <- sapply(seq_len(ncol(aa)), function(j) cor(aa[, j], se_tot))
for (j in seq_along(r_aa))
    cat(sprintf("     %-11s r = %+.3f\n", colnames(aa)[j], r_aa[j]))
cat(sprintf("     min = %+.3f, max = %+.3f. Under the rival 'stored raw' reading these\n",
            min(r_aa), max(r_aa)))
cat(sprintf("     would be %+.3f .. %+.3f -- i.e. every one negative.\n\n",
            -max(r_aa), -min(r_aa)))
sign_ok <- all(r_aa > 0)

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

## counterfactual: alienation + external stored raw (i.e. flip them back)
Af <- cbind(al, 6 - aa, 6 - ao)
cat(sprintf("\n      counterfactual 'stored raw' (flip alien+external): total M = %.2f",
            mean(rowSums(Af))))
cat(sprintf(", alpha = %.3f\n", alpha(Af)))
cat(sprintf("      against the published %.2f / %.2f -- the stored coding is the one the\n",
            PUB$auth_m, PUB$alpha))
cat("      paper reports, so the alienation block is already reverse-scored.\n\n")

tot_ok <- abs(mean(auth) - PUB$auth_m)  <= TOL_M  &&
          abs(sd(auth)   - PUB$auth_sd) <= TOL_SD &&
          abs(mean(se_tot) - PUB$se_m)  <= TOL_M  &&
          abs(sd(se_tot)   - PUB$se_sd) <= TOL_SD &&
          abs(cor(auth, se_tot) - PUB$r) <= TOL_R &&
          abs(alpha(A) - PUB$alpha)      <= TOL_A

## --- what this does NOT establish -----------------------------------------
cat("(iv) what is NOT verified: which of AS items 2, 7, 10 and 12 each code is.\n")
for (j in seq_len(ncol(aa)))
    cat(sprintf("     %-11s item-rest r = %.3f, M = %.2f, SD = %.2f\n",
                colnames(aa)[j], cor(aa[, j], rowSums(aa[, -j, drop = FALSE])),
                mean(aa[, j]), sd(aa[, j])))
cat("     All four are one polarity class on one 1-5 range; the study publishes no\n")
cat("     per-item statistics and the source .sav (PLOS s001) carries no variable or\n")
cat("     value labels, so no route separates them. Within-block order is inferred\n")
cat("     from the canonical Wood et al. (2008) subscale numbering (2, 7, 10, 12\n")
cat("     ascending) and is NOT verified here.\n\n")

ok <- yardstick_ok && sign_ok && tot_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
