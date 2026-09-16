# verify_wang_2016_study1_authliving.R
#
# CLAIM UNDER TEST (Step 5b), in two parts:
#   (a) BLOCK + DIRECTION: the four codes authliving1..4 are the four Authentic
#       Living items of the 12-item Authenticity Scale (Wood et al., 2008) as the
#       study scored it, stored raw on an ASCENDING 1 = strongly disagree ..
#       5 = strongly agree coding (the shipped option_text).
#   (b) WITHIN-BLOCK ORDER: authliving1/2/3/4 correspond to AS items 1/8/9/11 in
#       that order.  This script CANNOT test (b) -- nothing in the data separates
#       the four items -- and it says so below.  Hence status PARTIAL.
#
# Falsifiable prediction for (a): summing the live authliving + authalien +
# authexternal tables per person must reproduce Wang (2016) PLOS ONE Table 1's
# Authenticity M = 42.49, SD = 6.18, and its r = .61 with the self-esteem total
# (M = 38.34, SD = 5.08) built from wang_2016_study1_se.  A block assigned to the
# wrong subscale tables, or a table stored on a reversed 1-5 coding, misses these
# by a wide margin (a reversed authliving block alone shifts the total by
# 2*(15.62) - 24 = 7.2 points of mean).

suppressMessages(library(irw))

PUB <- list(auth_m = 42.49, auth_sd = 6.18,
            se_m   = 38.34, se_sd   = 5.08,
            r      = 0.61)
TOL_M <- 0.05; TOL_SD <- 0.05; TOL_R <- 0.02

tot <- function(tabs) {
    d <- do.call(rbind, lapply(tabs, function(t) {
        x <- irw::irw_fetch(t); data.frame(id = as.character(x$id), resp = as.numeric(x$resp))
    }))
    s <- tapply(d$resp, d$id, sum)
    s[!is.na(s)]
}

auth <- tot(c("wang_2016_study1_authliving",
              "wang_2016_study1_authalien",
              "wang_2016_study1_authexternal"))
se   <- tot("wang_2016_study1_se")
common <- intersect(names(auth), names(se))
auth <- auth[common]; se <- se[common]

cat(sprintf("n persons (all three authenticity tables + se): %d\n\n", length(common)))
cat(sprintf("%-28s %10s %10s %8s\n", "quantity", "published", "observed", "diff"))
row <- function(lab, pub, obs) cat(sprintf("%-28s %10.2f %10.2f %8.3f\n", lab, pub, obs, obs - pub))
row("Authenticity total M",  PUB$auth_m,  mean(auth))
row("Authenticity total SD", PUB$auth_sd, sd(auth))
row("Self-esteem total M",   PUB$se_m,    mean(se))
row("Self-esteem total SD",  PUB$se_sd,   sd(se))
row("r(authenticity, SE)",   PUB$r,       cor(auth, se))

ok <- abs(mean(auth) - PUB$auth_m) <= TOL_M &&
      abs(sd(auth)   - PUB$auth_sd) <= TOL_SD &&
      abs(mean(se)   - PUB$se_m)   <= TOL_M &&
      abs(sd(se)     - PUB$se_sd)  <= TOL_SD &&
      abs(cor(auth, se) - PUB$r)   <= TOL_R

# Counterfactual: what the total would be if the authliving block were stored on
# the reversed coding the shipped option_text rules out.
al <- irw::irw_fetch("wang_2016_study1_authliving")
al_sum <- tapply(as.numeric(al$resp), as.character(al$id), sum)
rev_block <- 6 * 4 - mean(al_sum)
cat(sprintf("\nauthliving block sum: M = %.2f; reversed (6-x) it would be %.2f, moving the\n",
            mean(al_sum), rev_block))
cat(sprintf("  12-item total to %.2f against the published %.2f -- so the stored direction,\n",
            mean(auth) - mean(al_sum) + rev_block, PUB$auth_m))
cat("  and hence the shipped 1 = strongly disagree .. 5 = strongly agree anchors, is fixed.\n")

# What this does NOT establish.
w <- reshape(data.frame(id = as.character(al$id), item = al$item, resp = as.numeric(al$resp)),
             idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
m <- m[, c("authliving1","authliving2","authliving3","authliving4")]
cat("\nitem-rest correlations within the block (the only per-item signal available):\n")
for (j in 1:4)
    cat(sprintf("  %-13s r = %.3f\n", colnames(m)[j], cor(m[, j], rowSums(m[, -j]))))
cat("These do NOT identify which of AS items 1, 8, 9 and 11 each code is: the study\n",
    "publishes no per-item statistics, the source .sav (PLOS s001) carries no variable\n",
    "or value labels, and all four items are positively keyed, so no polarity, range or\n",
    "marker-item route separates them. Within-block order is inferred from the canonical\n",
    "Wood et al. (2008) subscale numbering and is NOT verified here.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
