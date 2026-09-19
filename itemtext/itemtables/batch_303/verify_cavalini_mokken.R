# Verification for cavalini_mokken (#2228, batch_303).
#
# SOURCE. The mokken R package (CRAN, GPL-2+) ships the data set AND its man
# page; ?cavalini prints all seventeen coping statements against Item1..Item17
# and states the 0-3 anchors. So the item codes are the data object's own
# column names -- there is no mapping step -- and this script proves it by
# reproducing the live table from the packaged data.
#
# Route 1: the packaged cavalini matrix reproduces the live item x resp cell
#   counts exactly.
# Route 2: every shipped item_text is a line of the man page, in order.
# Route 3: the shipped anchors are the man page's own 0-3 labels.
tb <- ".cache/batch_303/mokken.tar.gz"
if (!file.exists(tb)) stop("missing cached source: ", tb)
ex <- file.path(tempdir(), "mokken_src"); dir.create(ex, showWarnings = FALSE)
utils::untar(tb, exdir = ex)
rda <- file.path(ex, "mokken", "data", "cavalini.rda")
rd  <- file.path(ex, "mokken", "man", "cavalini.Rd")
for (p in c(rda, rd)) if (!file.exists(p)) stop("not in the tarball: ", p)

e <- new.env(); load(rda, envir = e)
src <- get("cavalini", envir = e)
d <- as.data.frame(irw::irw_fetch("cavalini_mokken"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_303/cavalini_mokken__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: reproduce the live table from the packaged data ===\n")
cat(sprintf("  packaged cavalini: %d x %d, columns %s ... %s\n",
            nrow(src), ncol(src), colnames(src)[1], colnames(src)[ncol(src)]))
lng <- do.call(rbind, lapply(colnames(src), function(c) {
    v <- as.numeric(src[, c]); v <- v[!is.na(v)]
    data.frame(item = c, resp = v, stringsAsFactors = FALSE)
}))
ts <- as.data.frame(table(lng$item, lng$resp), stringsAsFactors = FALSE)
tl <- as.data.frame(table(d$item, as.numeric(d$resp)), stringsAsFactors = FALSE)
names(ts) <- names(tl) <- c("item", "resp", "n")
m <- merge(ts, tl, by = c("item", "resp"), all = TRUE)
r1 <- nrow(lng) == nrow(d) && all(!is.na(m$n.x)) && all(!is.na(m$n.y)) && all(m$n.x == m$n.y)
cat(sprintf("  cells compared: %d   rows src=%d live=%d\n", nrow(m), nrow(lng), nrow(d)))
cat(sprintf("  -> every item x resp cell reproduced exactly: %s\n", r1))

cat("\n=== Route 2: the seventeen statements, from two places in the package ===\n")
rl <- readLines(rd, warn = FALSE)
hit <- grep("^Item[0-9]+\\s*\\\\tab", rl, value = TRUE)
code <- sub("^(Item[0-9]+)\\s*\\\\tab.*", "\\1", hit)
text <- trimws(sub("^Item[0-9]+\\s*\\\\tab\\s*", "", hit))
text <- trimws(sub("\\\\cr\\s*$", "", text))
text <- gsub("``", "\u201c", text); text <- gsub("''", "\u201d", text)
text <- sub("^(.)", "\\U\\1", text, perl = TRUE)
cat(sprintf("  man page \\tabular lists %d Item rows\n", length(code)))
sh <- unique(items[, c("item", "item_text")])
key <- setNames(text, code)
r2a <- length(code) == 17 && setequal(code, sh$item) && all(sh$item_text == key[sh$item])
for (i in seq_along(code)) cat(sprintf("  %-7s %s\n", code[i], substr(text[i], 1, 74)))
cat(sprintf("  -> codes and wording match the shipped file: %s\n", r2a))
lb <- attributes(src)$labels
cat("  the data object also carries its own labels attribute; it is a lightly\n")
cat("  different rendering of the same seventeen statements, in the same order:\n")
same <- sapply(seq_len(17), function(i) {
    a <- tolower(gsub("[^a-z ]", "", tolower(text[i])))
    b <- tolower(gsub("[^a-z ]", "", tolower(lb[i])))
    length(intersect(strsplit(a, " +")[[1]], strsplit(b, " +")[[1]])) >= 2
})
for (i in which(text != sub("^(.)", "\\U\\1", lb, perl = TRUE)))
    cat(sprintf("    %-7s man: %-42s attr: %s\n", code[i], text[i], lb[i]))
r2b <- length(lb) == 17 && all(same)
cat(sprintf("  -> the two agree item for item: %s\n", r2b))
cat("  item_text ships the man-page rendering; both are the package's English\n")
cat("  for a Dutch original, and the man page is the published one.\n")
r2 <- r2a && r2b

cat("\n=== Route 3: the anchors ===\n")
anch <- items$option_text[items$item == "Item1"][order(items$resp[items$item == "Item1"])]
cat(sprintf("  shipped: %s\n", paste(sprintf("%d=%s", 0:3, anch), collapse = ", ")))
doc <- paste(rl, collapse = " ")
r3 <- all(sapply(anch, function(a) grepl(a, doc, fixed = TRUE))) &&
      setequal(sort(unique(as.numeric(d$resp))), 0:3)
cat(sprintf("  -> all four labels appear in the man page, resp set is 0-3: %s\n", r3))

cat("\n=== What this does NOT establish ===\n")
cat("  The administered Dutch wording. Cavalini's 1992 dissertation is the\n")
cat("  original and is not online; the English in item_text is the mokken\n")
cat("  package's rendering, which is what the study is distributed as.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
