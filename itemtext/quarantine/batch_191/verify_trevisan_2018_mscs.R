# verify_trevisan_2018_mscs.R -- Step 5b mapping check for trevisan_2018_mscs (batch_191).
#
# Claim: live item MSCS_n carries the wording of item n on the MSCS Self Report form
# (PLOS ONE 10.1371/journal.pone.0206800, S1 File), and resp is the RAW response on
# that form's scale (1 = Not True or Almost Never True ... 5 = Very True or Almost
# Always True) for EVERY item, including the 32 reverse-keyed ones -- whose .sav
# value labels say the opposite (value 1 = "5- very true or always true").
#
# Routes (none of them re-checks item counts; validate_items.R did that):
#   A. Subscale membership: summing live items into the paper's Table 1 domains
#      (reverse items as 6 - resp) must reproduce the study's own composite columns
#      MSCS_SM1 .. MSCS_ER1 in the S2 .sav, respondent by respondent.
#   B. Keying polarity: each raw item must correlate with its keyed rest-of-domain
#      score negatively iff it is reverse-keyed (32 items), positively otherwise --
#      with item 41 negative, the anomaly the paper itself reports. This also fixes
#      option_text direction: if resp were already reversed the signs would flip.
#   C. The 11 / 20 / 30 triple, where the paper's Table 1 prints a different number
#      against each wording than S1 does. 20 is settled by B (negative, so "I do not
#      offer to help people"). 11 vs 30 (both positive empathic-concern items) is
#      settled by content: "I appear visibly upset when I see people suffering" should
#      track emotional reactivity (18,21,44,46) and a larger female-male gap, while
#      "I give compliments to people" should track social motivation (2,19,57,65).
#
# What this does NOT establish: order WITHIN a domain x polarity cell beyond the
# 11/20/30 triple and item 41. The code number = form number tie is the .sav's own
# variable label ("MSCS Question n"), which is what carries the rest.

suppressMessages(library(irw))
TABLE <- "trevisan_2018_mscs"

DOMAINS <- list(
  SM1  = c(1, 2, 10, 14, 19, 22, 42, 57, 65, 69, 76),
  SI1  = c(3, 13, 24, 28, 40, 45, 52, 54, 59, 67, 77),
  DEC1 = c(5, 9, 11, 16, 20, 27, 30, 39, 48, 55, 64),
  SK1  = c(26, 31, 33, 43, 47, 53, 58, 71, 72, 73, 75),
  VCS1 = c(6, 7, 8, 12, 37, 38, 50, 56, 61, 63, 74),
  NSS1 = c(17, 23, 29, 32, 34, 35, 49, 51, 62, 66, 70),
  ER1  = c(4, 15, 18, 21, 25, 36, 41, 44, 46, 60, 68))
REV <- c(1, 6, 7, 8, 12, 13, 14, 18, 20, 21, 22, 27, 29, 36, 37, 38, 40, 42, 44, 46,
         51, 52, 59, 60, 61, 62, 63, 67, 68, 69, 70, 74)   # Table 1 asterisks = the .sav's *_R columns

ok <- TRUE
d <- as.data.frame(irw::irw_fetch(TABLE))
d$n <- as.integer(sub("^MSCS_", "", d$item))
W <- reshape(d[, c("id", "n", "resp")], idvar = "id", timevar = "n", direction = "wide")
W <- W[order(W$id), ]
X <- as.matrix(W[, paste0("resp.", 1:77)]); colnames(X) <- 1:77
K <- X; K[, REV] <- 6 - K[, REV]
dom_of <- setNames(rep(names(DOMAINS), lengths(DOMAINS)), unlist(DOMAINS))

## --- Route A -----------------------------------------------------------------
cat("== Route A: domain sums vs the study's own composite columns (S2 .sav) ==\n")
sav <- tempfile(fileext = ".sav")
got <- tryCatch({
  utils::download.file("https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0206800.s002",
                       sav, mode = "wb", quiet = TRUE); TRUE }, error = function(e) FALSE)
if (!got) { cat("could not download S2 .sav -- route A not run\n"); ok <- FALSE } else {
  S <- haven::read_sav(sav)
  ids <- W$id   # processing script: id = row position in the .sav
  for (a in names(DOMAINS)) {
    s <- rowSums(K[, as.character(DOMAINS[[a]])])
    comp <- as.numeric(S[[paste0("MSCS_", a)]])[ids]
    cmp <- !is.na(s) & !is.na(comp)
    agree <- sum(abs(s[cmp] - comp[cmp]) < 1e-6)
    # a wrong membership is visible: swap in the neighbouring domain's first item
    alt <- DOMAINS[[a]]; other <- DOMAINS[[names(DOMAINS)[(match(a, names(DOMAINS)) %% 7) + 1]]][1]; alt[1] <- other
    s2 <- rowSums(K[, as.character(alt)]); agree2 <- sum(abs(s2[cmp] - comp[cmp]) < 1e-6)
    cat(sprintf("%-5s items %-38s exact %4d / %4d   (with item %d swapped for %d: %4d / %4d)\n",
                a, paste(DOMAINS[[a]], collapse = ","), agree, sum(cmp), DOMAINS[[a]][1], other, agree2, sum(cmp)))
    if (sum(cmp) < 1100 || agree != sum(cmp)) ok <- FALSE
  }
}

## --- Route B -----------------------------------------------------------------
cat("\n== Route B: raw item vs keyed rest-of-domain correlation sign ==\n")
r <- sapply(1:77, function(i) {
  rest <- setdiff(DOMAINS[[dom_of[as.character(i)]]], i)
  cor(X[, i], rowSums(K[, as.character(rest)]), use = "complete.obs") })
expected <- ifelse(1:77 %in% c(REV, 41), -1, 1)
cat(sprintf("reverse-keyed items: r range %.2f .. %.2f (expected all negative)\n", min(r[REV]), max(r[REV])))
fwd <- setdiff(1:77, c(REV, 41))
cat(sprintf("forward-keyed items (excl. 41): r range %.2f .. %.2f (expected all positive)\n", min(r[fwd]), max(r[fwd])))
cat(sprintf("item 41 (paper reports negative loading): r = %.2f\n", r[41]))
mism <- which(sign(r) != expected)
cat("sign mismatches:", if (length(mism)) paste(mism, collapse = ",") else "none", sprintf("(%d of 77 as predicted)\n", 77 - length(mism)))
if (length(mism)) ok <- FALSE
cat(sprintf("floor-sensitive reverse items raw means: 36 'act out ... hit, or shove' %.2f, 70 'flat, monotonous tone' %.2f, 61 'dominate conversations' %.2f\n",
            mean(X[, "36"], na.rm = TRUE), mean(X[, "70"], na.rm = TRUE), mean(X[, "61"], na.rm = TRUE)))

## --- Route C -----------------------------------------------------------------
cat("\n== Route C: the 11 / 20 / 30 triple (S1 numbering vs paper Table 1 numbering) ==\n")
mr <- function(i, js) mean(sapply(js, function(j) cor(X[, as.character(i)], X[, as.character(j)], use = "complete.obs")))
sex <- tapply(d$cov_sex, d$id, function(v) v[1])[as.character(W$id)]
gap <- function(i) mean(X[sex == 1, as.character(i)], na.rm = TRUE) - mean(X[sex == 0, as.character(i)], na.rm = TRUE)
for (i in c(11, 30)) cat(sprintf("MSCS_%d: mean r with reactivity {18,21,44,46} = %.3f; with social motivation {2,19,57,65} = %.3f; female-male gap = %.2f\n",
                                 i, mr(i, c(18, 21, 44, 46)), mr(i, c(2, 19, 57, 65)), gap(i)))
cat(sprintf("MSCS_20: rest-of-domain r = %.2f (negative => the reverse-worded 'I do not offer to help people', as S1 numbers it)\n", r[20]))
c_ok <- mr(11, c(18, 21, 44, 46)) > mr(30, c(18, 21, 44, 46)) &&
        mr(30, c(2, 19, 57, 65)) > mr(11, c(2, 19, 57, 65)) &&
        gap(11) > gap(30) && r[20] < 0
cat("11 = 'visibly upset', 30 = 'compliments', 20 = 'do not offer to help' supported:", c_ok, "\n")
if (!c_ok) ok <- FALSE

cat("\nNot established: order within a domain x polarity cell other than items 11/20/30 and 41.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
