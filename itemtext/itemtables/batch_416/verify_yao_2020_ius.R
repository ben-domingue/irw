# verify_yao_2020_ius.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes ius1..ius27 carry the English IUS-27
# wording (Buhr & Dugas 2002, as distributed by PhenX PX650701) in its printed
# numbering 1..27, and resp 1..5 runs 1 = "Not at all characteristic of me" ..
# 5 = "Entirely characteristic of me".
#
# Nothing in the study ties ius1..ius27 to text. data/yao_2020_intolerance_
# uncertainty.py melts the deposit's own columns by name (regex 'ius\d+'), so
# the IRW code IS the source column name -- no positional step. What is
# inferred is what the NAME means: the .sav has no variable or value labels on
# any of its 126 columns, the .xlsx header row is the same bare codes, readme.txt
# says nothing about the IUS block, and the J Pers Assess paper is closed access.
# So the tie rests on the IUS form's printed numbering and is tested here.
#
# Predictions, each of which a relabelling would break:
#   P1  (content twin, cross-instrument) ius24 "Uncertainty keeps me from
#       sleeping soundly" is argmax_i corr(ius_i, bdi16) -- BDI item 16 is the
#       sleep item in both BDI-I and BDI-II, so no version assumption.
#   P2  (route 5, block structure) the published two-factor key (Factor 1 =
#       items 1,2,3,9,12,13,14,15,16,17,20,22,23,24,25; Factor 2 = the other 12)
#       separates the correlation matrix better than >= 99% of 10,000 random
#       15/12 partitions (statistic: mean within-block r minus mean
#       between-block r).
#   P3  (structural signature) the five items with the lowest mean inter-item
#       r are all Factor 2 items (chance ~ C(12,5)/C(27,5) = 0.0098).
#   P4  (option axis) every IUS item correlates POSITIVELY with the GAD-7 total
#       (0-3 per item, unambiguous severity coding) -- which holds only if
#       resp 5 = "Entirely characteristic of me". Live resp stored raw 1..5.
#
# REPORTED, NOT PASS CONDITIONS:
#   - the reciprocal of P1: over all 49 BAI/BDI/GAD items, ius24's strongest
#     correlate is NOT bdi16 (gad3/gad4 edge it, inside a general factor).
#   - the IUS-12 prospective/inhibitory split (Carleton 2007) does NOT beat
#     random partitions of those 12 items; the prospective items (10, 19, 21)
#     are weakly correlated with everything, which flattens that statistic.
#
# WHAT THIS DOES NOT ESTABLISH: P1 pins ius24 alone; P2/P3 pin factor
# MEMBERSHIP as a block, not the order of items within a factor. A swap of two
# items inside the same factor would pass. Status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "yao_2020_ius"
KEY   <- "94p8m47y58"
ius <- paste0("ius", 1:27)
F1  <- paste0("ius", c(1, 2, 3, 9, 12, 13, 14, 15, 16, 17, 20, 22, 23, 24, 25))

# --- live IRW data ----------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", ius)]

# --- the study's deposit (.sav), for the other instruments --------------------
meta <- jsonlite::fromJSON(
  sprintf("https://data.mendeley.com/public-api/datasets/%s", KEY))
f <- meta$files
url <- f$content_details$download_url[f$filename == "data upload_IU.sav"]
tf <- tempfile(fileext = ".sav")
utils::download.file(url, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(haven::zap_labels(haven::read_sav(tf)))
x[x == 999] <- NA
x$id <- seq_len(nrow(x))   # processing script: id = .sav row index

# id alignment (plumbing, not mapping evidence)
xm <- merge(w, x[, c("id", ius)], by = "id", suffixes = c("", ".sav"))
mism <- sum(as.matrix(xm[, ius]) != as.matrix(xm[, paste0(ius, ".sav")]), na.rm = TRUE)
cat(sprintf("id alignment: %d live respondents matched to .sav rows; %d cell mismatches\n\n",
            nrow(xm), mism))

oth <- grep("^(bai|bdi|gad)\\d+$", names(x), value = TRUE)
m <- merge(w, x[, c("id", oth)], by = "id")
r <- function(a, b) cor(m[[a]], m[[b]], use = "pairwise.complete.obs")

# --- P1 ---------------------------------------------------------------------
v <- sapply(ius, r, b = "bdi16")
o <- sort(v, decreasing = TRUE)[1:4]
cat("corr(ius_i, bdi16 sleep), top 4 of 27:",
    paste(sprintf("%s %.3f", names(o), o), collapse = ", "), "\n")
p1 <- names(o)[1] == "ius24"
rv <- sapply(oth, function(b) r("ius24", b)); ro <- sort(rv, decreasing = TRUE)[1:4]
cat("  (reported) corr(ius24, BAI/BDI/GAD item), top 4 of", length(oth), ":",
    paste(sprintf("%s %.3f", names(ro), ro), collapse = ", "), "\n\n")

# --- P2 ---------------------------------------------------------------------
R <- cor(w[, ius], use = "pairwise.complete.obs")
stat <- function(g, RR) { s <- outer(g, g, "=="); diag(s) <- NA
  mean(RR[s & !is.na(s)]) - mean(RR[!s & !is.na(s)]) }
g0 <- ifelse(ius %in% F1, 1, 2)
s0 <- stat(g0, R)
set.seed(20260924)
sp <- replicate(10000, stat(sample(g0), R))
pp <- mean(sp >= s0)
cat(sprintf("two-factor key: within-minus-between r = %.4f; random 15/12 partitions: max %.4f, 99th pct %.4f; p = %.4f\n",
            s0, max(sp), quantile(sp, .99), pp))
p2 <- pp < 0.01

idx <- paste0("ius", c(7, 8, 10, 11, 18, 19, 21, 9, 12, 15, 20, 25))
g12 <- rep(1:2, c(7, 5)); R12 <- R[idx, idx]
s12 <- stat(g12, R12); sp12 <- replicate(10000, stat(sample(g12), R12))
cat(sprintf("  (reported) IUS-12 split: stat %.4f, p = %.3f\n\n", s12, mean(sp12 >= s12)))

# --- P3 ---------------------------------------------------------------------
mr <- sapply(ius, function(i) mean(R[i, setdiff(ius, i)]))
low5 <- names(sort(mr))[1:5]
cat("lowest mean inter-item r:", paste(sprintf("%s %.3f%s", low5, mr[low5],
    ifelse(low5 %in% F1, "(F1)", "(F2)")), collapse = ", "), "\n\n")
p3 <- !any(low5 %in% F1)

# --- P4: option axis --------------------------------------------------------
m$gadtot <- rowSums(m[, paste0("gad", 1:7)])
cg <- sapply(ius, function(i) cor(m[[i]], m$gadtot, use = "pairwise.complete.obs"))
cat(sprintf("corr(ius_i, GAD-7 total): min %.3f (%s), max %.3f, n = %d with GAD\n",
            min(cg), names(which.min(cg)), max(cg), sum(!is.na(m$gadtot))))
mu <- tapply(d$resp, d$item, mean)[ius]
cat(sprintf("item means on 1-5: %.2f (%s) .. %.2f (%s)\n\n",
            min(mu), names(which.min(mu)), max(mu), names(which.max(mu))))
p4 <- all(cg > 0)

ok <- c(P1 = p1, P2 = p2, P3 = p3, P4 = p4)
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("\nScope: pins ius24, factor membership as blocks, and resp direction. Order\n",
    "WITHIN each factor is not established -- status PARTIAL.\n", sep = "")

cat(if (all(ok) && mism == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
