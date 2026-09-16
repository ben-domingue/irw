# verify_wang_2026_attitude.R -- Step 5b, batch_217.
#
# The claim under test: the three ATT wordings shipped in
# itemtables/batch_217/wang_2026_attitude__items.csv are attached to the item
# codes ATT1, ATT2, ATT3 by NUMBER, via the code labels the source itself
# prints.  Nothing in the deposit ties wording to a column, so the chain is:
#
#   (A) Wang & Zou's S1 Appendix questionnaire prints each attitude item with
#       its own code, "AT1-...", "AT2-...", "AT3-..." -- so the wording carries
#       its number in the source, not merely its position in a list.  This is
#       re-derived below by re-downloading the .docx and diffing it against the
#       shipped item_text.  It is the check that would break if item_text for
#       ATT1 and ATT3 were swapped.
#   (B) The paper's Table 2 (an image) reports loadings, CA, CR, AVE under the
#       codes ATT1/ATT2/ATT3, i.e. the data's own codes.  Recomputing them from
#       the S2 Appendix columns of the same name shows those published numbers
#       belong to those columns in that orientation, not to a permutation.
#
# What this does NOT establish: (A) turns on AT<n> in the appendix meaning the
# same n as ATT<n> in the data file -- the construct prefix differs by a letter
# and nothing in the deposit states the correspondence.  And the three items are
# near-synonymous enjoyment items (pleasant / enjoyable / fun) whose means
# (3.79 / 3.72 / 3.73) and loadings (.824 / .818 / .834) are within .02, so no
# statistical route can separate them: a permutation of the three wordings among
# the three codes would be undetectable.  Hence PARTIAL, not VERIFIED.

TABLE <- "wang_2026_attitude"
ITEMS <- c("ATT1", "ATT2", "ATT3")

# Wang Y, Zou B (2026) PLOS ONE 10.1371/journal.pone.0346229, Table 2 (.t002).
PUB_LOADING <- c(ATT1 = 0.825, ATT2 = 0.815, ATT3 = 0.836)
PUB_CA <- 0.766; PUB_CR <- 0.865; PUB_AVE <- 0.681
TOL_LOADING <- 0.02; TOL_REL <- 0.005

S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346229.s001"
S2 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346229.s002"

csv_path <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                      paste0(TABLE, "__items.csv"))
if (!file.exists(csv_path)) csv_path <- file.path("itemtables", "batch_217", paste0(TABLE, "__items.csv"))
ship <- read.csv(csv_path, stringsAsFactors = FALSE)
shipped <- unname(vapply(ITEMS, function(i) unique(ship$item_text[ship$item == i]), character(1)))

ok_a <- FALSE
docx <- tempfile(fileext = ".docx")
res <- try(utils::download.file(S1, docx, quiet = TRUE, mode = "wb"), silent = TRUE)
if (!inherits(res, "try-error") && file.exists(docx) && file.size(docx) > 1000) {
    xmld <- tempfile(); dir.create(xmld)
    utils::unzip(docx, files = "word/document.xml", exdir = xmld)
    xml <- paste(readLines(file.path(xmld, "word", "document.xml"), warn = FALSE), collapse = "")
    xml <- gsub("</w:p>", "\n", xml)          # one line per paragraph / cell
    xml <- gsub("<[^>]+>", "", xml)
    xml <- gsub("&#8211;|&#8212;", "-", xml); xml <- gsub("&amp;", "&", xml)
    lines <- unique(trimws(strsplit(xml, "\n")[[1]]))
    appendix <- character(0)
    for (n in 1:3) {
        hit <- grep(sprintf("^AT%d[-–]", n), lines, value = TRUE)
        appendix[n] <- if (length(hit)) trimws(sub(sprintf("^AT%d[-–]", n), "", hit[1])) else NA_character_
    }
    cat("(A) S1 Appendix code labels vs shipped item_text\n")
    cat(sprintf("%-6s %-46s %-46s %s\n", "item", "appendix AT<n>", "shipped item_text", "match"))
    for (n in 1:3)
        cat(sprintf("%-6s %-46s %-46s %s\n", ITEMS[n], appendix[n], shipped[n],
                    identical(appendix[n], shipped[n])))
    ok_a <- !anyNA(appendix) && all(appendix == shipped)
} else {
    cat("(A) could not download S1 Appendix -- cannot re-derive the code-label diff\n")
}

ok_b <- FALSE
xlsx <- tempfile(fileext = ".xlsx")
res <- try(utils::download.file(S2, xlsx, quiet = TRUE, mode = "wb"), silent = TRUE)
have_reader <- requireNamespace("readxl", quietly = TRUE)
if (!inherits(res, "try-error") && file.exists(xlsx) && file.size(xlsx) > 1000 && have_reader) {
    raw <- as.data.frame(readxl::read_excel(xlsx))
    a <- as.matrix(raw[, ITEMS]); storage.mode(a) <- "double"
    z <- scale(a)
    w <- rep(1 / sqrt(3), 3)                   # PLS mode A, single construct
    for (k in 1:200) {
        s <- as.vector(z %*% w); s <- s / sd(s)
        w <- apply(z, 2, function(x) cor(x, s)); w <- w / sqrt(sum(w^2))
    }
    s <- as.vector(z %*% w); s <- s / sd(s)
    load <- apply(z, 2, function(x) cor(x, s))
    tot <- var(rowSums(a)); ca <- 3 / 2 * (1 - sum(apply(a, 2, var)) / tot)
    ave <- mean(load^2); cr <- sum(load)^2 / (sum(load)^2 + sum(1 - load^2))
    cat("\n(B) Table 2 (image .t002) recomputed from the S2 Appendix columns\n")
    cat(sprintf("%-6s %10s %10s %8s %8s %8s\n", "item", "published", "observed", "diff", "mean", "sd"))
    for (n in 1:3)
        cat(sprintf("%-6s %10.3f %10.3f %8.3f %8.2f %8.2f\n", ITEMS[n], PUB_LOADING[n], load[n],
                    load[n] - PUB_LOADING[n], mean(a[, n]), sd(a[, n])))
    cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", "CA", PUB_CA, ca, ca - PUB_CA))
    cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", "CR", PUB_CR, cr, cr - PUB_CR))
    cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", "AVE", PUB_AVE, ave, ave - PUB_AVE))
    rank_ok <- identical(order(load), order(PUB_LOADING))
    cat(sprintf("loading rank order matches published (%s vs %s): %s\n",
                paste(ITEMS[order(-load)], collapse = ">"),
                paste(ITEMS[order(-PUB_LOADING)], collapse = ">"), rank_ok))
    ok_b <- rank_ok && max(abs(load - PUB_LOADING)) <= TOL_LOADING &&
            max(abs(c(ca - PUB_CA, cr - PUB_CR, ave - PUB_AVE))) <= TOL_REL
} else {
    cat("\n(B) could not download/read the S2 Appendix -- skipped\n")
}

cat("\nNote: the loading spread across the three items is .018, far inside estimation\n",
    "noise, so (B) fixes the code-to-column orientation only; it cannot separate the\n",
    "three wordings from each other. Only the printed AT<n> labels in (A) do that, and\n",
    "they do it on the assumption AT<n> == ATT<n>. PARTIAL by design.\n", sep = "")

cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
