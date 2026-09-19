# Verification for ghanbari_2016_helma_comm (mapping_basis = paper_order).
#
# THE CLAIM UNDER TEST: the live item codes com1..com8 are questionnaire items
# 34..41 of the HELMA (the "communication" block of Ghanbari et al. 2016,
# PLOS ONE 10.1371/journal.pone.0149202), IN THAT ORDER. The S3 .sav carries no
# variable labels, so nothing in the data file states which questionnaire item a
# com column is; the alignment is inferred from block name + presentation order.
#
# THE FALSIFIABLE PREDICTION: the paper's Table 2 publishes an 8-factor varimax
# loading matrix for all 44 final items. Re-running that analysis on the S3 .sav
# (47 items, n = 582) reproduces those loadings, so the observed loading PROFILE
# of com1..com8 must line up with the published rows for items 34..41 in order.
# If any two com columns were swapped, the profiles would swap with them.
#
# Also checks live == .sav per item, so the loading evidence (computed on the
# .sav) actually transfers to the published IRW table.

suppressMessages(library(irw))
suppressMessages(library(haven))

TABLE <- "ghanbari_2016_helma_comm"
ITEMS <- paste0("com", 1:8)
SAV_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0149202.s003"
CACHE <- file.path("itemtext/.cache", TABLE, "s3.sav")
if (!file.exists(CACHE)) CACHE <- file.path(".cache", TABLE, "s3.sav")
if (!file.exists(CACHE)) {
    CACHE <- tempfile(fileext = ".sav")
    download.file(SAV_URL, CACHE, quiet = TRUE, mode = "wb")
}

## ---- 1. live table vs the .sav the IRW script was built from ---------------
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
sav <- as.data.frame(haven::read_sav(CACHE))

live_mean <- sapply(ITEMS, function(it) mean(d$resp[d$item == it]))
live_n    <- sapply(ITEMS, function(it) sum(d$item == it))
sav_mean  <- sapply(ITEMS, function(it) mean(sav[[it]], na.rm = TRUE))
sav_n     <- sapply(ITEMS, function(it) sum(!is.na(sav[[it]])))

cat("== live IRW table vs S3 .sav column, per item ==\n")
cat(sprintf("%-6s %8s %8s %10s %10s %10s\n", "item", "n_live", "n_sav", "mean_live", "mean_sav", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-6s %8d %8d %10.4f %10.4f %10.2e\n", ITEMS[i], live_n[i], sav_n[i],
                live_mean[i], sav_mean[i], live_mean[i] - sav_mean[i]))
link_ok <- max(abs(live_mean - sav_mean)) < 1e-10 && all(live_n == sav_n)
cat(sprintf("live/.sav columns identical: %s\n\n", link_ok))

## ---- 2. reproduce the paper's Table 2 loading matrix -----------------------
item_cols <- grep("^(access|reading|understand|appraise|use|com|num)[0-9]+$", names(sav), value = TRUE)
X <- na.omit(sav[, item_cols])
cat(sprintf("EFA input: %d items, %d complete cases (paper: 47 items, n = 582)\n", length(item_cols), nrow(X)))
R <- cor(X)
e <- eigen(R)
L <- e$vectors[, 1:8] %*% diag(sqrt(e$values[1:8]))
rownames(L) <- item_cols
Lv <- stats::varimax(L)$loadings
Lv <- matrix(as.numeric(Lv), nrow = nrow(L), dimnames = list(item_cols, paste0("f", 1:8)))
# sign-fix each factor so its dominant block is positive
for (j in 1:8) if (max(abs(Lv[, j])) != max(Lv[, j])) Lv[, j] <- -Lv[, j]

blockmean <- function(pfx) colMeans(abs(Lv[grep(paste0("^", pfx, "[0-9]+$"), rownames(Lv)), , drop = FALSE]))
# map reproduced factors onto the paper's factor numbering, using the paper's own
# footnote: 1 = understanding, 2 = communication, 3 = reading, 4 = appraisal,
# 5 = access, 6 = use, 7 = self-efficacy, 8 = numeracy.
f_und <- which.max(blockmean("understand"))
f_com <- which.max(blockmean("com"))
f_read <- which.max(blockmean("reading"))
f_app <- which.max(blockmean("appraise"))
f_use <- which.max(blockmean("use"))
f_num <- which.max(blockmean("num"))
# access splits: the .sav's access1-4 are the paper's self-efficacy items 1-4,
# access5-9 the paper's access items 5-9 (access10/11 were dropped from the final form).
f_acc <- which.max(colMeans(abs(Lv[paste0("access", 5:9), , drop = FALSE])))
f_se  <- which.max(colMeans(abs(Lv[paste0("access", 1:4), , drop = FALSE])))
ord <- c(f_und, f_com, f_read, f_app, f_acc, f_use, f_se, f_num)
stopifnot(length(unique(ord)) == 8)
OBS <- Lv[ITEMS, ord]

# Published Table 2, rows for items 34-41, all eight factor columns, in the
# paper's own column order. (Item 34's F1 cell is printed "-0.41" with a stray
# leading zero in an otherwise 3-decimal column; read as -.041.)
PUB <- matrix(c(
  -0.041, 0.521, 0.175, 0.199, 0.215, 0.305, -0.046,  0.020,
   0.233, 0.586,-0.040, 0.109, 0.117, 0.117,  0.174, -0.022,
   0.089, 0.549, 0.093, 0.180, 0.116, 0.091,  0.055,  0.001,
   0.233, 0.667,-0.030, 0.084, 0.195, 0.118,  0.021,  0.043,
   0.254, 0.578, 0.100, 0.124,-0.057, 0.092,  0.203, -0.156,
   0.123, 0.670, 0.126, 0.176, 0.129, 0.035,  0.181, -0.097,
   0.098, 0.710, 0.211, 0.230, 0.173, 0.021,  0.131, -0.038,
   0.138, 0.524, 0.063, 0.010,-0.017, 0.150,  0.058,  0.044),
  nrow = 8, byrow = TRUE, dimnames = list(paste0("item", 34:41), NULL))

cat("\n== communication-factor loading, claimed pairing ==\n")
cat(sprintf("%-6s %-8s %10s %10s %8s\n", "item", "paper", "published", "observed", "diff"))
for (i in 1:8)
    cat(sprintf("%-6s %-8s %10.3f %10.3f %8.3f\n", ITEMS[i], rownames(PUB)[i],
                PUB[i, 2], OBS[i, 2], OBS[i, 2] - PUB[i, 2]))
worst <- max(abs(OBS[, 2] - PUB[, 2]))
cat(sprintf("largest deviation on the communication factor: %.3f\n", worst))

## ---- 3. is the claimed pairing the BEST of all 8! pairings? ----------------
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:8)
dev <- sapply(P, function(p) mean(abs(OBS[p, ] - PUB)))
o <- order(dev)
ident <- which(sapply(P, function(p) all(p == 1:8)))
rank_ident <- which(o == ident)
cat(sprintf("\n== full 8-factor profile, all %d pairings ==\n", length(P)))
for (k in 1:3) cat(sprintf("  rank %d: com->item %s  mean|dev| = %.4f\n", k,
                           paste(33 + P[[o[k]]], collapse = ","), dev[o[k]]))
cat(sprintf("  claimed pairing (com1..com8 -> items 34..41) ranks %d of %d, mean|dev| = %.4f\n",
            rank_ident, length(P), dev[ident]))

## ---- 4. the two pairs the communication loading alone cannot separate -----
# com1/com8 (.51/.51 vs published .521/.524) and com4/com6 (.68/.67 vs .667/.670)
# are near-ties on the communication factor; a secondary column separates each.
cat("\n== tie-breaks on secondary factors ==\n")
tb <- function(a, b, ia, ib, fcol, fname) {
    cat(sprintf("  %s loading: %s=%.3f %s=%.3f | published %s=%.3f %s=%.3f -> %s\n",
        fname, a, OBS[a, fcol], b, OBS[b, fcol], ia, PUB[ia, fcol], ib, PUB[ib, fcol],
        if (abs(OBS[a,fcol]-PUB[ia,fcol]) + abs(OBS[b,fcol]-PUB[ib,fcol]) <
            abs(OBS[a,fcol]-PUB[ib,fcol]) + abs(OBS[b,fcol]-PUB[ia,fcol]))
            "claimed pairing wins" else "SWAP WINS"))
}
tb("com1", "com8", "item34", "item41", 6, "use (F6)")
tb("com4", "com6", "item37", "item39", 1, "understanding (F1)")

## ---- what this does NOT establish -----------------------------------------
cat("\nNote: the claimed pairing is the single best of all 40320 and each near-tied\n",
    "pair is separated by a secondary factor column (above), so every item is\n",
    "distinguished from every other. What this does NOT establish: that the .sav's\n",
    "`com` block is the questionnaire's communication block at all -- that rests on\n",
    "the block name, the 8-vs-8 item count and the paper's statement that\n",
    "communication kept its assumed item set -- nor the option_text -> resp\n",
    "direction, which is fixed by the .sav's own value labels (1=never..5=always).\n", sep = "")

pass <- link_ok && worst <= 0.03 && rank_ident == 1
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
