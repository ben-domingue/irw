## dtmr_sim: simulated Diagnosing Teachers' Multiplicative Reasoning (DTMR) data
##
## Source: the dcmdata R package (Thompson, CRAN, MIT licence), objects
## dtmr_data / dtmr_qmatrix / dtmr_true_profiles / dtmr_true_items.
## https://cran.r-project.org/package=dcmdata , https://github.com/r-dcm/dcmdata
##
## Not the real DTMR responses. The package simulated them from the loglinear
## cognitive diagnostic model (LCDM): each of 990 respondents drew a mastery
## profile from the proportions in Izsak et al. (2019) Fig. 10, and responses to
## the 27 items came from the item parameters in Bradshaw et al. (2014) Table 1.
## What makes it worth a table is that the truth ships with it, at both levels:
##
##   cov_true_*         each respondent's true mastery (0/1) of the 4 attributes
##   itemcov_true_*     the generating LCDM item parameters (logit scale):
##                      intercept, main effects, and the one two-way interaction
##                      (referent_units x partitioning_iterating). NA means the
##                      term is not in that item's generating model, i.e. it
##                      contributes 0. Items 14 and 17 measure both
##                      referent_units and partitioning_iterating but carry the
##                      interaction in place of some main effects, as in
##                      Bradshaw et al. (2014), so "measured" does not imply a
##                      main effect.
##   qmatrix1..4        the Q-matrix, attributes in this order:
##                      1 referent_units, 2 partitioning_iterating,
##                      3 appropriateness, 4 multiplicative_comparison
##
## The structural parameters (16 latent-class proportions) are class-level, not
## person- or item-level, so they are not columns here; they are
## dcmdata::dtmr_true_structural.

library(dcmdata)
stopifnot(packageVersion("dcmdata") >= "0.2.0")

attrs <- c("referent_units", "partitioning_iterating",
           "appropriateness", "multiplicative_comparison")

x <- as.data.frame(dtmr_data)
stopifnot(nrow(x) == 990, ncol(x) == 28, !anyDuplicated(x$id))
items <- setdiff(names(x), "id")

## long
df <- data.frame(id   = rep(x$id, times = length(items)),
                 item = rep(items, each = nrow(x)),
                 resp = unlist(x[items], use.names = FALSE),
                 stringsAsFactors = FALSE)
stopifnot(all(df$resp %in% c(0, 1)))

## person truth
prof <- as.data.frame(dtmr_true_profiles)
stopifnot(setequal(prof$id, x$id), all(attrs %in% names(prof)))
for (a in attrs) df[[paste0("cov_true_", a)]] <- prof[[a]][match(df$id, prof$id)]

## item truth
ip <- as.data.frame(dtmr_true_items)
stopifnot(setequal(ip$item, items))
ip_cols <- setdiff(names(ip), "item")
for (cl in ip_cols) df[[paste0("itemcov_true_", cl)]] <- ip[[cl]][match(df$item, ip$item)]

## Q-matrix
q <- as.data.frame(dtmr_qmatrix)
stopifnot(setequal(q$item, items), identical(names(q)[-1], attrs))
for (k in seq_along(attrs)) df[[paste0("qmatrix", k)]] <- q[[attrs[k]]][match(df$item, q$item)]

## The parameters must agree with the Q-matrix: a main effect only on an
## attribute the item measures, the interaction only where it measures both,
## and every measured attribute enters through at least one term.
qk <- function(a) df[[paste0("qmatrix", match(a, attrs))]] == 1
inter <- !is.na(df$itemcov_true_referent_units__partitioning_iterating)
stopifnot(!any(inter & !(qk("referent_units") & qk("partitioning_iterating"))))
for (a in attrs) {
    has_main <- !is.na(df[[paste0("itemcov_true_", a)]])
    stopifnot(!any(has_main & !qk(a)))
    in_inter <- inter & a %in% c("referent_units", "partitioning_iterating")
    stopifnot(!any(qk(a) & !has_main & !in_inter))
}

stopifnot(nrow(df) == 990 * 27, !anyNA(df[c("id", "item", "resp")]))
out <- path.expand("~/.cache/irw-simsyn")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
write.csv(df, file.path(out, "dtmr_sim.csv"), quote = FALSE, row.names = FALSE, na = "")
