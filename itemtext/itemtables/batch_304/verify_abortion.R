# Verification for abortion (#2228, batch_304).
#
# SOURCE. The ltm R package (CRAN, GPL-2+): data(Abortion) and ?Abortion. The
# item codes item_1..item_4 are the data frame's own columns 'Item 1'..'Item 4',
# so the mapping is identity and this script proves it by reproduction.
#
# Route 1: data(Abortion) reproduces the live item x resp table exactly.
# Route 2: the direction of resp. Nothing in the package states which of 0/1
#   means 'the law should allow it'. The endorsement pattern does: 'the woman
#   decides on her own' is the least-supported of these four reasons in every
#   published reading of the 1986 British Social Attitudes data, and it is the
#   only item here below .5.
tb <- ".cache/batch_304/ltm.tar.gz"
if (!file.exists(tb)) stop("missing cached source: ", tb)
ex <- file.path(tempdir(), "ltm_src"); dir.create(ex, showWarnings = FALSE)
utils::untar(tb, exdir = ex, files = "ltm/data/Abortion.rda")
rda <- file.path(ex, "ltm", "data", "Abortion.rda")
if (!file.exists(rda)) stop("not in the tarball: ", rda)
e <- new.env(); load(rda, envir = e); src <- get("Abortion", envir = e)

d <- as.data.frame(irw::irw_fetch("abortion"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_304/abortion__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: reproduce the live table from data(Abortion) ===\n")
cat(sprintf("  packaged Abortion: %d x %d, columns %s\n", nrow(src), ncol(src),
            paste(colnames(src), collapse = ", ")))
lng <- do.call(rbind, lapply(seq_len(ncol(src)), function(j)
    data.frame(item = sprintf("item_%d", j), resp = src[[j]], stringsAsFactors = FALSE)))
ts <- as.data.frame(table(lng$item, lng$resp), stringsAsFactors = FALSE)
tl <- as.data.frame(table(d$item, as.numeric(d$resp)), stringsAsFactors = FALSE)
names(ts) <- names(tl) <- c("item", "resp", "n")
m <- merge(ts, tl, by = c("item", "resp"), all = TRUE)
r1 <- nrow(lng) == nrow(d) && all(!is.na(m$n.x)) && all(!is.na(m$n.y)) && all(m$n.x == m$n.y)
cat(sprintf("  cells compared: %d   rows src=%d live=%d\n", nrow(m), nrow(lng), nrow(d)))
cat(sprintf("  -> reproduced exactly: %s\n", r1))

cat("\n=== Route 2: which way round is resp? ===\n")
p <- tapply(as.numeric(d$resp), d$item, mean)
sh <- unique(items[, c("item", "item_text")])
for (i in sort(names(p)))
    cat(sprintf("  %-7s p(resp=1) = %.3f   %s\n", i, p[[i]],
                substr(sh$item_text[sh$item == i], 1, 60)))
r2 <- which.min(p) == which(sort(names(p)) == "item_1") && p[["item_1"]] < 0.5 &&
      all(p[setdiff(names(p), "item_1")] > 0.55)
cat(sprintf("  -> item_1 ('the woman decides on her own') is the only item below\n"))
cat(sprintf("     .5 and the lowest of the four: %s\n", r2))
cat("  That is the ordering the survey is known for, so resp 1 is 'the law\n")
cat("  should allow it'. Shipped as option_text 1 = Yes, 0 = No.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  item_1's wording. ?Abortion prints it as 'The woman decides on her own\n")
cat("  that she does not.' -- an incomplete sentence; the other three are\n")
cat("  complete. It ships as the package has it rather than being completed.\n")
cat("  The 0/1 labels 'No'/'Yes' are this project's, from the stem; the\n")
cat("  package labels neither value.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
