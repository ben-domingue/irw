# verify_anh_2026_finsocialization.R
#
# CLAIM UNDER TEST: item_text for FS1..FS7 (from PLOS ONE 10.1371/journal.pone.0340002
# Table 3, an image table that prefixes each item with its variable code) is attached to
# the right IRW item code.
#
# The falsifiable prediction: Table 3 publishes a distinct per-item VIF for each of the
# seven FS items. VIF is computed from the FS1..FS7 columns of the S1 File, which
# data/anh_2026_finwellbeing.py melts verbatim into the IRW item codes (the IRW code IS
# the source column name). So recomputing VIF per column and comparing to the published
# column pins each Table 3 ROW to a specific S1 COLUMN, i.e. to a specific IRW item.
# If the item_text of any two items were swapped, the published VIFs would land on the
# wrong columns and the permutation search below would prefer a non-identity permutation.
#
# NOTE ON QUOTA: this script deliberately does NOT call irw_fetch(). It uses
# irw::irw_table_sets() (server-side aggregates) to confirm the live table's item set,
# resp set and per-item n, and does the per-item statistics on the S1 File itself.

suppressMessages(library(irw))

TABLE <- "anh_2026_finsocialization"
S1 <- ("https://journals.plos.org/plosone/article/file"
       )
S1URL <- paste0(S1, "?type=supplementary&id=10.1371/journal.pone.0340002.s001")

# Published Table 3, Family financial socialisation block, VIF column (FS1..FS7).
PUB_VIF <- c(1.715, 1.869, 1.901, 1.761, 1.957, 2.133, 2.138)
# Published Table 3 outer loadings, same block.
PUB_LOAD <- c(0.732, 0.766, 0.781, 0.741, 0.785, 0.818, 0.817)
PUB_ALPHA <- 0.891

cols <- paste0("FS", 1:7)
d <- read.csv(S1URL)
stopifnot(all(cols %in% names(d)))
fs <- d[, cols]

## --- live-side sanity: the codes and levels this text is being attached to -------
ts <- irw::irw_table_sets(TABLE)
cat("live item set: ", paste(sort(unique(as.character(ts$items))), collapse = " "), "\n", sep = "")
cat("live resp set: ", paste(sort(unique(as.numeric(ts$resp))), collapse = " "), "\n", sep = "")
cat("live rows: ", ts$n_rows, " = 7 items x 306 respondents\n\n", sep = "")

## --- the mapping test -----------------------------------------------------------
vif <- sapply(seq_along(cols), function(i)
    1 / (1 - summary(lm(fs[, i] ~ ., data = fs[, -i]))$r.squared))

cat(sprintf("%-5s %10s %10s %9s\n", "item", "published", "observed", "diff"))
for (i in seq_along(cols))
    cat(sprintf("%-5s %10.3f %10.4f %+9.4f\n", cols[i], PUB_VIF[i], vif[i], vif[i] - PUB_VIF[i]))

worst <- max(abs(vif - PUB_VIF))
cat(sprintf("\nlargest VIF deviation: %.4f (published to 3 dp, so <=0.0005 is exact)\n", worst))

# Is the identity assignment the BEST of all 5040 permutations, and by how much?
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:7)
sse <- sapply(P, function(p) sum((vif[p] - PUB_VIF)^2))
o <- order(sse)
cat(sprintf("best permutation:   %s  SSE=%.3g\n", paste(P[[o[1]]], collapse = ""), sse[o[1]]))
cat(sprintf("runner-up:          %s  SSE=%.3g  (%.0fx worse)\n",
            paste(P[[o[2]]], collapse = ""), sse[o[2]], sse[o[2]] / sse[o[1]]))
identity_best <- identical(P[[o[1]]], 1:7)

## --- corroboration (not decisive on its own) ------------------------------------
itc <- sapply(seq_along(cols), function(i) cor(fs[, i], rowSums(fs[, -i])))
cat(sprintf("\ncorrected item-total r vs published loadings: Pearson %.2f, Spearman %.2f\n",
            cor(itc, PUB_LOAD), cor(itc, PUB_LOAD, method = "spearman")))
alpha <- local({ k <- ncol(fs); (k / (k - 1)) * (1 - sum(apply(fs, 2, var)) / var(rowSums(fs))) })
cat(sprintf("Cronbach's alpha: observed %.3f vs published %.3f\n", alpha, PUB_ALPHA))

## --- what this does NOT establish -----------------------------------------------
cat("\nNot established by this route: the Vietnamese wording respondents actually read\n",
    "(the deposit is English-coded and holds no Vietnamese; item_text is the English\n",
    "source wording per Table 3), and the response-option anchors, which come from the\n",
    "Methods text (1 = strongly disagree, 5 = strongly agree) and not from any per-item\n",
    "statistic.\n", sep = "")

cat(if (identity_best && worst <= 0.0005) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
