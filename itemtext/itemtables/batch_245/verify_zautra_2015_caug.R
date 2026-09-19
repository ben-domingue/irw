# verify_zautra_2015_caug.R -- Step 5b mapping check for zautra_2015_caug (batch_245).
#
# Claim: live item caug<i> is the study's .sav column caug<i>pre (wave 1) /
# caug<i>post (wave 2) -- data/zautra_2015_social_intelligence_battery.py does a
# number-preserving rename -- and that column carries the Spanish GSE item that
# the study's codebook (PLOS S2 File, table "Variable | Item in English | Item in
# Spanish") prints against CAUG<i>.
#
# Route A (decisive for code <-> source column): per-item x per-level response
#   counts in the live table vs the .sav columns, cell for cell, both waves. Any
#   shift or permutation of the rename breaks it UNLESS two columns have the same
#   count vector, which is also checked.
# Route B (published totals, paper Table 5): GSE item-mean by group x wave
#   (Exp 3.01/3.15, Ctrl 3.12/3.08). Pins scale membership and raw (not
#   reversed) scoring, not order.
# NOT established by data: the link from source column caug<i> to its wording.
#   That rests on the codebook's labels, whose Spanish column follows the
#   published Spanish GSE order while its English column swaps CAUG2/CAUG8; the
#   data cannot separate those two (pre means 3.437 vs 3.419, near-synonymous).

suppressMessages({library(irw); library(haven)})
TABLE <- "zautra_2015_caug"
SAV_URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0128638.s001"

tmp <- tempfile(fileext = ".sav")
download.file(SAV_URL, tmp, mode = "wb", quiet = TRUE)
s <- haven::zap_labels(haven::read_sav(tmp))
d <- irw::irw_fetch(TABLE)

ok_counts <- TRUE
cat("Route A: live caug<i> vs .sav caug<i>pre/post, counts of resp 1..4\n")
cat(sprintf("%-7s %-5s %-18s %-18s %s\n", "item", "wave", "live", "sav", "match"))
sav_vecs <- list()
for (w in 1:2) {
  suf <- c("pre", "post")[w]
  for (i in 1:10) {
    it <- paste0("caug", i)
    lv <- tabulate(d$resp[d$item == it & d$wave == w], nbins = 4)
    x <- s[[paste0(it, suf)]]; x <- x[x %in% 1:4]
    sv <- tabulate(x, nbins = 4)
    sav_vecs[[paste(w, i)]] <- paste(sv, collapse = "/")
    m <- identical(lv, sv); ok_counts <- ok_counts && m
    cat(sprintf("%-7s %-5d %-18s %-18s %s\n", it, w, paste(lv, collapse = "/"),
                paste(sv, collapse = "/"), m))
  }
}
dups <- sum(duplicated(unlist(sav_vecs[paste(1, 1:10)]))) + sum(duplicated(unlist(sav_vecs[paste(2, 1:10)])))
cat(sprintf("duplicate sav count vectors within a wave: %d (0 => route A separates every column)\n", dups))

cat("\nRoute B: GSE item-mean by group x wave vs paper Table 5 (complete pre+post cases)\n")
pub <- c(exp_pre = 3.01, exp_post = 3.15, ctl_pre = 3.12, ctl_post = 3.08)
wide <- reshape(aggregate(resp ~ id + wave, d, function(v) if (length(v) == 10) mean(v) else NA,
                          na.action = na.pass), idvar = "id", timevar = "wave", direction = "wide")
wide <- wide[complete.cases(wide), ]
grp <- ifelse(startsWith(wide$id, "exp"), "exp", "ctl")
obs <- c(exp_pre = mean(wide$resp.1[grp == "exp"]), exp_post = mean(wide$resp.2[grp == "exp"]),
         ctl_pre = mean(wide$resp.1[grp == "ctl"]), ctl_post = mean(wide$resp.2[grp == "ctl"]))
cat(sprintf("n exp=%d ctl=%d (paper: 207/87 complete on all outcomes)\n", sum(grp == "exp"), sum(grp == "ctl")))
for (k in names(pub)) cat(sprintf("%-9s published %.2f observed %.3f diff %+.3f\n", k, pub[k], obs[k], obs[k] - pub[k]))
worst <- max(abs(obs - pub))
cat(sprintf("largest deviation %.3f (tolerance 0.03)\n", worst))

cat("\nNot established: column caug<i> -> wording is the codebook's label tie, not data;\n",
    "caug2 vs caug8 in particular rests on the codebook's Spanish column alone.\n", sep = "")
cat(if (ok_counts && dups == 0 && worst <= 0.03) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
