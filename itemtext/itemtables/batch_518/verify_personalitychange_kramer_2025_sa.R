# verify_personalitychange_kramer_2025_sa.R -- Step 5b check for batch_518.
#
# Claim: each IRW item code (sa05, sa07_01, ...) IS the authors' own column of the
# same name in their deposited analysis files (OSF zevcs, reproduce.zip ->
# data/df_sbsa.rda [Study 1] + data/df_sbsa2.rda [Study 2]), and the study codebook
# (OSF zevcs /Codebook/Codebook Personality Change Intervention Study.pdf, pp. 17-24)
# prints item text against exactly those codes (SA05, SA07_01 "Sociable", ...).
#
# The falsifiable part is the code->column tie: if the IRW script had shifted a
# range or swapped two columns, per-item (n, sum, sum of squares) would not
# reproduce. The script also checks that every source column's fingerprint is
# UNIQUE, so a match on the same-named column cannot be a coincidence shared with
# another column.
#
# What this does NOT establish: the column->wording tie itself rests on the
# codebook printing each code beside its text (explicit-code-label exemption);
# no statistic independently ties e.g. "Sociable" to sa07_01.
suppressMessages(library(irw))
TABLE <- "personalitychange_kramer_2025_sa"

d <- as.data.frame(irw::irw_fetch(TABLE))
items <- sort(unique(d$item))

td <- tempfile(); dir.create(td)
zip <- file.path(td, "reproduce.zip")
download.file("https://osf.io/download/6xv7f/", zip, mode = "wb", quiet = TRUE)
unzip(zip, files = c("reproduce/data/df_sbsa.rda", "reproduce/data/df_sbsa2.rda"), exdir = td)
ld <- function(f) { e <- new.env(); load(f, envir = e); as.data.frame(get(ls(e)[1], e)) }
s1 <- ld(file.path(td, "reproduce/data/df_sbsa.rda"))
s2 <- ld(file.path(td, "reproduce/data/df_sbsa2.rda"))

fp <- function(x) { x <- x[!is.na(x) & x != -9]; c(n = length(x), sum = sum(x), ss = sum(x^2)) }
src_cols <- union(grep("^sa", names(s1), value = TRUE), grep("^sa", names(s2), value = TRUE))
src_cols <- src_cols[sapply(src_cols, function(c) is.numeric(c(s1[[c]], s2[[c]])))]
src <- t(sapply(src_cols, function(c) fp(c(if (c %in% names(s1)) s1[[c]], if (c %in% names(s2)) s2[[c]]))))
live <- t(sapply(items, function(i) fp(d$resp[d$item == i])))

cat(sprintf("%-8s %6s %7s %8s | %6s %7s %8s  %s\n", "item", "n_live", "sum", "ss", "n_src", "sum", "ss", "unique_fp"))
ok <- TRUE
for (i in items) {
    s <- src[i, ]; l <- live[i, ]
    same <- all(s == l)
    uniq <- sum(apply(src, 1, function(r) all(r == l))) == 1
    cat(sprintf("%-8s %6d %7d %8d | %6d %7d %8d  %s\n", i, l[1], l[2], l[3], s[1], s[2], s[3],
                if (same && uniq) "match,unique" else if (same) "match,NOT-unique" else "MISMATCH"))
    ok <- ok && same && uniq
}
cat(sprintf("\n%d/%d items reproduce their same-named source column exactly, with a unique fingerprint.\n",
            sum(sapply(items, function(i) all(src[i, ] == live[i, ]))), length(items)))

# Option-direction corroboration (resp<->option_text axis), from the same source files.
for (nm in c("s1", "s2")) {
    x <- get(nm)
    m <- tapply(x$sa06_01, x$sa05, mean, na.rm = TRUE)
    r <- cor(rowMeans(x[, paste0("sa04_0", 1:3)]), rowMeans(x[, sprintf("sa14_%02d", 1:15)]), use = "complete.obs")
    cat(sprintf("%s: mean sa06_01 ('how much want to be better at accepting', 5=completely) | sa05=1 (yes): %.2f, sa05=2 (no): %.2f; r(sa04 practice freq, sa14 accept-more) = %+.2f\n",
                nm, m["1"], m["2"], r))
    ok <- ok && m["1"] > m["2"] && r > 0
}
cat("Not established: wording<->column rests on the codebook's explicit code labels.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
