# Verification for consideration_future_consequences (#2228, batch_303).
#
# BARE-INTEGER ITEM CODES (1..12), so the mapping needs a reproduction, not an
# argument. SOURCE: openpsychometrics.org/_rawdata/ CFCS archive, which ships
# codebook.txt (Q1..Q12 with wording and the 1-5 anchors) beside data.csv.
#
# Route 1: the archive's Q1..Q12 columns reproduce the live item x resp cell
#   counts exactly under the rename Qn -> n, with 0 (no answer) dropped.
# Route 2: shipped item_text is the codebook's wording, code for code.
# Route 3: the four CFCS 'immediate' items (3, 4, 5 and 12 in the published
#   scale, plus 9, 10, 11) key opposite to the 'future' items, so the
#   correlation sign pattern must split the way the published scale splits it.
zp <- ".cache/batch_303/cfcs.zip"
cb <- ".cache/batch_303/cfcs/CFCS/codebook.txt"
dz <- ".cache/batch_303/cfcs/CFCS/data.csv"
if (!file.exists(dz)) utils::unzip(zp, exdir = ".cache/batch_303/cfcs")
for (p in c(cb, dz)) if (!file.exists(p)) stop("missing cached source: ", p)

d <- as.data.frame(irw::irw_fetch("consideration_future_consequences"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_303/consideration_future_consequences__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
x <- read.csv(dz, sep = "\t", stringsAsFactors = FALSE, check.names = FALSE)
if (ncol(x) < 5) x <- read.csv(dz, stringsAsFactors = FALSE, check.names = FALSE)

cat("=== Route 1: reproduce the live table from the archive ===\n")
qc <- paste0("Q", 1:12)
cat(sprintf("  archive: %d rows, %d columns; Q1..Q12 present: %s\n",
            nrow(x), ncol(x), all(qc %in% names(x))))
src <- do.call(rbind, lapply(1:12, function(i) {
    v <- suppressWarnings(as.numeric(x[[paste0("Q", i)]]))
    v <- v[!is.na(v) & v >= 1 & v <= 5]
    data.frame(item = as.character(i), resp = v, stringsAsFactors = FALSE)
}))
ts <- as.data.frame(table(src$item, src$resp), stringsAsFactors = FALSE)
dn <- d[!is.na(d$resp), ]
tl <- as.data.frame(table(dn$item, as.numeric(dn$resp)), stringsAsFactors = FALSE)
names(ts) <- names(tl) <- c("item", "resp", "n")
m <- merge(ts, tl, by = c("item", "resp"), all = TRUE)
r1 <- nrow(src) == nrow(dn) && all(!is.na(m$n.x)) && all(!is.na(m$n.y)) && all(m$n.x == m$n.y)
cat(sprintf("  cells compared: %d   rows src=%d live(non-NA)=%d of %d\n",
            nrow(m), nrow(src), nrow(dn), nrow(d)))
cat(sprintf("  the live table keeps %d rows whose resp is NA -- the archive's 0\n", nrow(d) - nrow(dn)))
cat("  ('no answer chosen') and -1 codes, which data/consideration_future_\n")
cat("  consequences.R maps to NA but does not drop. Excluded from the compare.\n")
cat(sprintf("  -> every item x resp cell reproduced exactly under Qn -> n: %s\n", r1))

cat("\n=== Route 2: the codebook's wording ===\n")
cl <- readLines(cb, warn = FALSE)
hit <- grep("^Q[0-9]+\\. ", cl, value = TRUE)
code <- sub("^Q([0-9]+)\\..*", "\\1", hit)
text <- trimws(sub("^Q[0-9]+\\.\\s*", "", hit))
sh <- unique(items[, c("item", "item_text")])
key <- setNames(text, code)
r2 <- length(code) == 12 && setequal(code, sh$item) && all(sh$item_text == key[sh$item])
cat(sprintf("  codebook lists %d numbered items; all shipped texts match: %s\n", length(code), r2))
anch <- items$option_text[items$item == "1"][order(items$resp[items$item == "1"])]
r2b <- all(sapply(anch, function(a) any(grepl(a, cl, fixed = TRUE))))
cat(sprintf("  anchors '%s' all quoted in the codebook: %s\n",
            paste(anch, collapse = ", "), r2b))

cat("\n=== Route 3: the immediate/future keying splits as published ===\n")
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
mm <- as.matrix(w[, -1]); colnames(mm) <- sub("^resp\\.", "", colnames(mm))
fut <- c("1", "2", "6", "7", "8")
imm <- c("3", "4", "5", "9", "10", "11", "12")
fs <- rowMeans(mm[, fut, drop = FALSE], na.rm = TRUE)
rr <- sapply(colnames(mm), function(c) stats::cor(mm[, c], fs, use = "pairwise.complete.obs"))
rr <- rr[order(as.integer(names(rr)))]
for (i in names(rr)) cat(sprintf("    item %-3s r with future-subscale mean = %+.3f  (%s)\n",
                                 i, rr[i], if (i %in% fut) "future" else "immediate"))
r3 <- all(rr[fut] > 0) && all(rr[imm] < 0)
cat(sprintf("  -> all five future items positive, all seven immediate items negative: %s\n", r3))
cat("  A shifted numbering would put at least one item on the wrong side.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. Wording, codes and anchors all come from one codebook\n")
cat("  shipped with the data. The published CFC scale is Strathman et al.\n")
cat("  (1994); this is openpsychometrics' administration of it.\n")
cat("\nVERDICT:", if (r1 && r2 && r2b && r3) "PASS" else "FAIL", "\n")
