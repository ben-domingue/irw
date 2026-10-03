# verify_personalitychange_kramer_2025_si.R -- Step 5b check for batch_519.
# Copied from references/verify_template.R and adapted (pattern of batch_518's
# verify_personalitychange_kramer_2025_sa.R, the self-acceptance sibling).
#
# Claim: each IRW item code (sb05, sb07_01, ...) IS the authors' own column of the
# same name in their deposited analysis files (OSF zevcs, reproduce.zip ->
# data/df_sbsa.rda [Study 1] + data/df_sbsa2.rda [Study 2]), and the study codebook
# (OSF zevcs, 'Codebook Personality Change Intervention Study.pdf', pp. 16-22)
# prints the item text against exactly those codes (SB05, SB07_01 "Sociable", ...).
#
# Checks:
#  (1) code->column tie: per-item (n, sum, sum of squares) of the live table must
#      reproduce the same-named deposit column, and that fingerprint must be unique
#      among all numeric sb* columns (so a shifted range/swap would break it).
#  (2) facet pairing between the pre block (sb07_k, "want to change") and the post
#      block (sb12_k, "have changed"), same pid: if the 15 facet labels are in the
#      same order in both blocks, r(sb07_k, sb12_k) should be the largest entry in
#      row k of the 15x15 cross-block correlation matrix. In practice this is
#      underpowered (a general perceived-change factor dominates sb12), so only the
#      aggregate "mean diagonal r > mean off-diagonal r" is gated; the per-row hit
#      count is printed for the record. A permutation applied identically to both
#      blocks would survive it in any case.
#  (3) option direction: sb06_01 mean higher for sb05=1 (yes) than sb05=2 (no);
#      r(sb04 frequency mean, sb12 perceived-change mean) > 0.
# NOT established: the absolute column->wording tie rests on the codebook printing
# each code beside its text (explicit-code-label exemption).
suppressMessages(library(irw))
TABLE <- "personalitychange_kramer_2025_si"

d <- as.data.frame(irw::irw_fetch(TABLE))
items <- sort(unique(d$item))

td <- tempfile(); dir.create(td)
zip <- file.path(td, "reproduce.zip")
download.file("https://osf.io/download/6xv7f/", zip, mode = "wb", quiet = TRUE)
unzip(zip, files = c("reproduce/data/df_sbsa.rda", "reproduce/data/df_sbsa2.rda"), exdir = td)
ld <- function(f) { e <- new.env(); load(f, envir = e); as.data.frame(get(ls(e)[1], e)) }
s1 <- ld(file.path(td, "reproduce/data/df_sbsa.rda"))
s2 <- ld(file.path(td, "reproduce/data/df_sbsa2.rda"))
for (nm in c("s1","s2")) { x <- get(nm); for (c in names(x)) if (is.numeric(x[[c]])) x[[c]][x[[c]] %in% -9] <- NA; assign(nm, x) }

fp <- function(x) { x <- x[!is.na(x)]; c(n = length(x), sum = sum(x), ss = sum(x^2)) }
src_cols <- union(grep("^sb", names(s1), value = TRUE), grep("^sb", names(s2), value = TRUE))
src_cols <- src_cols[sapply(src_cols, function(c) is.numeric(c(s1[[c]], s2[[c]])))]
src <- t(sapply(src_cols, function(c) fp(c(if (c %in% names(s1)) s1[[c]], if (c %in% names(s2)) s2[[c]]))))
live <- t(sapply(items, function(i) fp(d$resp[d$item == i])))

cat("(1) code->column fingerprints (n, sum, sum of squares)\n")
cat(sprintf("%-8s %6s %7s %8s | %6s %7s %8s  %s\n", "item", "n_live", "sum", "ss", "n_src", "sum", "ss", "status"))
ok <- TRUE
for (i in items) {
    s <- src[i, ]; l <- live[i, ]
    same <- all(s == l)
    uniq <- sum(apply(src, 1, function(r) all(r == l))) == 1
    cat(sprintf("%-8s %6d %7d %8d | %6d %7d %8d  %s\n", i, l[1], l[2], l[3], s[1], s[2], s[3],
                if (same && uniq) "match,unique" else if (same) "match,NOT-unique" else "MISMATCH"))
    ok <- ok && same && uniq
}
cat(sprintf("%d/%d items reproduce their same-named source column exactly, with a unique fingerprint.\n\n",
            sum(sapply(items, function(i) all(src[i, ] == live[i, ]))), length(items)))

cat("(2) facet pairing sb07_k (pre goal) x sb12_k (post perceived change), same pid\n")
diag_hits <- 0; agg_ok <- TRUE
for (nm in c("s1", "s2")) {
    x <- get(nm)
    pre  <- x[x$time == 1, c("pid", sprintf("sb07_%02d", 1:15))]
    post <- x[!is.na(x$sb12_01), c("pid", sprintf("sb12_%02d", 1:15))]
    post <- post[!duplicated(post$pid), ]
    pre  <- pre[!duplicated(pre$pid), ]
    mm <- merge(pre, post, by = "pid")
    R <- cor(mm[, sprintf("sb07_%02d", 1:15)], mm[, sprintf("sb12_%02d", 1:15)], use = "pairwise.complete.obs")
    hits <- sapply(1:15, function(k) which.max(R[k, ]) == k)
    cat(sprintf("%s: n pairs = %d; diagonal r = %s\n", nm, nrow(mm), paste(sprintf("%.2f", diag(R)), collapse = " ")))
    cat(sprintf("%s: max off-diagonal r per row = %s\n", nm,
                paste(sprintf("%.2f", sapply(1:15, function(k) max(R[k, -k]))), collapse = " ")))
    md <- mean(diag(R)); mo <- mean(R[row(R) != col(R)])
    cat(sprintf("%s: diagonal is the row maximum in %d/15 rows; mean diagonal r = %.3f vs mean off-diagonal r = %.3f\n",
                nm, sum(hits), md, mo))
    diag_hits <- diag_hits + sum(hits)
    agg_ok <- agg_ok && md > mo
}
# Underpowered by design: perceived change (sb12) is dominated by a general
# "I changed" factor, so the per-row maximum test is NOT used as a gate (it is
# printed for the record). Only the aggregate diagonal > off-diagonal is gated.
ok <- ok && agg_ok
cat("\n(3) option direction\n")
for (nm in c("s1", "s2")) {
    x <- get(nm)
    m <- tapply(x$sb06_01, x$sb05, mean, na.rm = TRUE)
    r <- cor(rowMeans(x[, paste0("sb04_0", 1:3)]), rowMeans(x[, sprintf("sb12_%02d", 1:15)]), use = "complete.obs")
    cat(sprintf("%s: mean sb06_01 (5=completely) | sb05=1 (yes): %.2f, sb05=2 (no): %.2f; r(sb04 freq, sb12 changed) = %+.2f\n",
                nm, m["1"], m["2"], r))
    ok <- ok && m["1"] > m["2"] && r > 0
}
cat("Not established: absolute wording<->column rests on the codebook's explicit code labels;\n")
cat("check (2) would not detect a permutation applied identically to both facet blocks.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
