# Verification for MotAcademica_Ribeiro_2019 (#2228, batch_304).
#
# SOURCE. Harvard Dataverse doi:10.7910/DVN/KWTMWT (CC0), whose two .tab files
# carry columns Item1..Item29; the wording is the Anexo of the study's own
# open-access paper (Ribeiro, Saraiva, Pereira & Ribeiro, 2019, RAC 23(3)).
# The item codes are the data's own column names, but 'Item7' says nothing
# about which question it is, so the numbering needs an external check.
#
# Route 1: the paper's own Table 1 statistics. It reports that item 27 has the
#   highest mean in both samples (A: 5.66, B: 5.64) followed by item 26
#   (A: 5.45, B: 5.39). Recompute those from Amostra A.
# Route 2: the deposit reproduces the live table (both samples stacked).
# Route 3: the demotivation items the paper names should be the low-mean ones.
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

tab <- cached_source(".cache/batch_304/MotAcademica_A.tab",
       "https://dataverse.harvard.edu/api/access/datafile/3557415")
d <- as.data.frame(irw::irw_fetch("MotAcademica_Ribeiro_2019"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- shipped_items("MotAcademica_Ribeiro_2019", "itemtables/batch_304/MotAcademica_Ribeiro_2019__items.csv")
x <- read.table(tab, header = TRUE, sep = "\t")
it <- sprintf("Item%d", 1:29)

cat("=== Route 1: the paper's Table 1 means, from Amostra A ===\n")
mu <- round(colMeans(x[, it], na.rm = TRUE), 2)
cat(sprintf("  Amostra A: n = %d, items = %d\n", nrow(x), length(it)))
cat(sprintf("  Item27 mean = %.2f   (paper: 5.66)\n", mu[["Item27"]]))
cat(sprintf("  Item26 mean = %.2f   (paper: 5.45)\n", mu[["Item26"]]))
top2 <- names(sort(mu, decreasing = TRUE))[1:2]
cat(sprintf("  two highest-mean items here: %s\n", paste(top2, collapse = ", ")))
r1 <- abs(mu[["Item27"]] - 5.66) < 0.005 && abs(mu[["Item26"]] - 5.45) < 0.005 &&
      identical(top2, c("Item27", "Item26"))
cat(sprintf("  -> both values and their order match the paper: %s\n", r1))
cat("  That fixes the numbering: a permuted ItemN would not land two named\n")
cat("  means on the second decimal.\n")

cat("\n=== Route 2: the deposit reproduces the live table ===\n")
tab2 <- cached_source(".cache/batch_304/MotAcademica_B.tab",
        "https://dataverse.harvard.edu/api/access/datafile/3557414")
if (file.exists(tab2)) {
    y <- read.table(tab2, header = TRUE, sep = "\t")
    src <- rbind(x[, it], y[, it])
} else {
    cat("  (Amostra B not cached; comparing Amostra A's contribution only)\n")
    src <- x[, it]
}
lng <- do.call(rbind, lapply(it, function(c) {
    v <- as.numeric(src[[c]]); v <- v[!is.na(v)]
    data.frame(item = c, resp = v, stringsAsFactors = FALSE)
}))
cat(sprintf("  source long rows: %d   live rows: %d\n", nrow(lng), nrow(d)))
r2 <- if (file.exists(tab2)) {
    ts <- as.data.frame(table(lng$item, lng$resp), stringsAsFactors = FALSE)
    tl <- as.data.frame(table(d$item, as.numeric(d$resp)), stringsAsFactors = FALSE)
    names(ts) <- names(tl) <- c("item", "resp", "n")
    m <- merge(ts, tl, by = c("item", "resp"), all = TRUE)
    nrow(lng) == nrow(d) && all(!is.na(m$n.x)) && all(!is.na(m$n.y)) && all(m$n.x == m$n.y)
} else {
    nrow(lng) < nrow(d) && setequal(unique(lng$item), unique(d$item))
}
cat(sprintf("  -> %s\n", r2))

cat("\n=== Route 3: the demotivation items sit at the bottom ===\n")
demo <- sprintf("Item%d", c(1, 7, 9, 13, 16, 19))
cat("  paper's Desmotivacao items: ", paste(demo, collapse = ", "), "\n")
lo <- names(sort(mu))[1:6]
cat("  six lowest-mean items here:  ", paste(sort(lo), collapse = ", "), "\n")
r3 <- length(intersect(demo, lo)) >= 5
cat(sprintf("  -> at least five of six coincide: %s\n", r3))

cat("\n=== What this does NOT establish ===\n")
cat("  Where 'Moderada correspondencia' sits. The anexo prints five labels\n")
cat("  across seven points and its own table aligns that one across points\n")
cat("  3-5, so 3, 4 and 5 ship with empty option_text rather than a guess.\n")
cat("  The English in the *_translated columns is an IRW rendering.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
