# verify_zautra_2015_tmms24.R -- Step 5b mapping check for zautra_2015_tmms24 (batch_246).
#
# Claim: live item TMMS24_<i> is the study's .sav column TMMS24_<i>pre (wave 1) /
# TMMS24_<i>post (wave 2) -- data/zautra_2015_social_intelligence_battery.py does a
# number-preserving rename -- and that column carries the Spanish TMMS-24 item the
# study's codebook (PLOS S2 File) prints against TMMS24_<i>, with subscales
# Attention = 1-8, Clarity = 9-16, Repair = 17-24.
#
# Route A (code <-> source column): per-item x per-level counts, live vs .sav,
#   cell for cell, both waves; duplicate count vectors within a wave are reported.
# Route B (published totals, paper Table 5 "EQ"): TMMS item-mean by group x wave
#   (Exp 3.09/3.19, Ctrl 3.18/3.20). Pins scale membership and raw scoring, not order.
# Route C (subscale block structure): each item's mean correlation with the rest of
#   its codebook subscale must exceed its mean correlation with each other subscale.
#   Pins subscale membership, not order within a subscale.
# NOT established by data: which wording within a subscale belongs to which column.
#   That rests on the codebook's explicit TMMS24_<i> labels (canonical TMMS-24 order).

suppressMessages({library(irw); library(haven)})
TABLE <- "zautra_2015_tmms24"
SAV_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0128638.s001"

tmp <- tempfile(fileext = ".sav")
download.file(SAV_URL, tmp, mode = "wb", quiet = TRUE)
s <- haven::zap_labels(haven::read_sav(tmp))
d <- as.data.frame(irw::irw_fetch(TABLE))

ok_counts <- TRUE; dups <- 0
cat("Route A: live TMMS24_<i> vs .sav TMMS24_<i>pre/post, counts of resp 1..5\n")
for (w in 1:2) {
  suf <- c("pre", "post")[w]; vecs <- character(0)
  for (i in 1:24) {
    it <- paste0("TMMS24_", i)
    lv <- tabulate(d$resp[d$item == it & d$wave == w], nbins = 5)
    x <- s[[paste0(it, suf)]]; x <- x[!is.na(x) & x %in% 1:5]
    sv <- tabulate(x, nbins = 5)
    vecs <- c(vecs, paste(sv, collapse = "/"))
    m <- identical(lv, sv); ok_counts <- ok_counts && m
    cat(sprintf("%-10s w%d live %-22s sav %-22s %s\n", it, w, paste(lv, collapse = "/"),
                paste(sv, collapse = "/"), m))
  }
  dups <- dups + sum(duplicated(vecs))
}
cat(sprintf("duplicate sav count vectors within a wave: %d (0 => route A separates every column)\n", dups))

cat("\nRoute B: TMMS item-mean by group x wave vs paper Table 5 (EQ)\n")
pub <- c(exp_pre = 3.09, exp_post = 3.19, ctl_pre = 3.18, ctl_post = 3.20)
pm <- aggregate(resp ~ id + wave, d, function(v) if (length(v) == 24) mean(v) else NA, na.action = na.pass)
wide <- reshape(pm, idvar = "id", timevar = "wave", direction = "wide")
wide <- wide[complete.cases(wide), ]
grp <- ifelse(startsWith(wide$id, "exp"), "exp", "ctl")
obs <- c(exp_pre = mean(wide$resp.1[grp == "exp"]), exp_post = mean(wide$resp.2[grp == "exp"]),
         ctl_pre = mean(wide$resp.1[grp == "ctl"]), ctl_post = mean(wide$resp.2[grp == "ctl"]))
cat(sprintf("complete pre+post cases: exp=%d ctl=%d\n", sum(grp == "exp"), sum(grp == "ctl")))
for (k in names(pub)) cat(sprintf("%-9s published %.2f observed %.3f diff %+.3f\n", k, pub[k], obs[k], obs[k] - pub[k]))
worst <- max(abs(obs - pub))
cat(sprintf("largest deviation %.3f (tolerance 0.05)\n", worst))

cat("\nRoute C: subscale block structure (wave 1, pairwise correlations)\n")
w1 <- d[d$wave == 1, ]
W <- reshape(w1[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(W) <- sub("^resp\\.", "", names(W))
items <- paste0("TMMS24_", 1:24)
R <- cor(W[, items], use = "pairwise.complete.obs")
sub <- rep(c("A", "C", "R"), each = 8); names(sub) <- items
hits <- 0
for (it in items) {
  m <- sapply(c("A", "C", "R"), function(g) { o <- setdiff(items[sub == g], it); mean(R[it, o]) })
  best <- names(which.max(m)); hit <- best == sub[it]; hits <- hits + hit
  cat(sprintf("%-10s assigned %s  meanr A=%.2f C=%.2f R=%.2f  best=%s %s\n", it, sub[it], m["A"], m["C"], m["R"], best, if (hit) "" else "<-- MISS"))
}
cat(sprintf("subscale hits: %d/24\n", hits))

cat("\nNot established: order WITHIN a subscale -- column -> wording there is the codebook's\n",
    "explicit TMMS24_<i> label tie, not data.\n", sep = "")
cat(if (ok_counts && dups == 0 && worst <= 0.05 && hits >= 22) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
