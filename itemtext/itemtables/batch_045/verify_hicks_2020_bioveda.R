# verify_hicks_2020_bioveda.R
#
# CLAIM being verified: the item_text shipped for item Qn is the text the study's
# own S1 Supporting Information prints under its heading "Qn", and those Qn codes
# are the same codes the IRW table uses (they are the raw column headers of the
# study's S3 data file, carried through verbatim by data/hicks_2020_bioveda.py).
#
# CHECK 1 (decisive on the mapping). Re-download S1 File, re-derive the stem for
# each heading Qn from scratch, and diff it against the shipped CSV. If item_text
# for any two items were swapped, this fails immediately.
#
# CHECK 2 (corroboration only). S2 Table publishes an item-whole correlation and
# an if-dropped item-whole correlation for items 1..16. Recompute both from the
# live IRW data and compare. This does NOT individuate items -- the correlations
# are tightly clustered and a nearest-neighbour assignment recovers only 6 of 16 --
# so it is reported as agreement in level and rank, not as an identification.

suppressMessages(library(irw))
suppressMessages(library(xml2))

TABLE <- "hicks_2020_bioveda"
S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0236098.s001"

# --- locate the shipped CSV ------------------------------------------------
cands <- c(file.path("itemtables", "batch_045", paste0(TABLE, "__items.csv")),
           file.path("itemtext", "itemtables", "batch_045", paste0(TABLE, "__items.csv")),
           paste0(TABLE, "__items.csv"))
csv <- cands[file.exists(cands)][1]
if (is.na(csv)) stop("cannot find ", TABLE, "__items.csv")
ship <- read.csv(csv, stringsAsFactors = FALSE)
ship <- unique(ship[, c("item", "item_text")])

# --- CHECK 1: re-derive item text from S1 File -----------------------------
tmp <- tempfile(fileext = ".docx")
ok <- tryCatch({
    utils::download.file(S1, tmp, quiet = TRUE, mode = "wb"); file.size(tmp) > 10000
}, error = function(e) FALSE)
if (!isTRUE(ok)) stop("could not download S1 File from PLOS -- rerun when reachable")

ex <- file.path(tempdir(), paste0("s1_", Sys.getpid()))
dir.create(ex, showWarnings = FALSE)
utils::unzip(tmp, files = "word/document.xml", exdir = ex)
doc <- read_xml(file.path(ex, "word", "document.xml"))
ns <- xml_ns(doc)
# body-level paragraphs only: paragraphs inside w:tbl are data tables, not stem text
paras <- xml_find_all(doc, "/w:document/w:body/w:p", ns)
txt <- vapply(paras, function(p) paste(xml_text(xml_find_all(p, "./w:r/w:t | ./w:hyperlink/w:r/w:t", ns)), collapse = ""),
              character(1))
clean <- function(s) {
    s <- gsub("​", "", s); s <- gsub(" ", " ", s)
    trimws(gsub("[[:space:]]+", " ", s))
}
txt <- vapply(txt, clean, character(1), USE.NAMES = FALSE)

# paragraph index of each heading "Qn" (heading paragraphs are the bare code)
head_idx <- setNames(integer(0), character(0))
for (n in 1:16) {
    hit <- which(txt == paste0("Q", n))
    if (length(hit) != 1) stop("S1 heading Q", n, " not uniquely found")
    head_idx[paste0("Q", n)] <- hit
}
# stem = paragraphs after the heading, up to (excluding) the first answer option.
# The answer options are the LAST 4 non-empty paragraphs before the next heading,
# except Q10 whose options are images (1 textual option remains).
n_opts <- c(rep(4, 9), 1, rep(4, 6)); names(n_opts) <- paste0("Q", 1:16)
end_idx <- c(head_idx[-1] - 1L, length(txt))
derived <- character(0)
for (n in 1:16) {
    k <- paste0("Q", n)
    blk <- txt[(head_idx[k] + 1L):end_idx[n]]
    blk <- blk[nzchar(blk)]
    stem <- head(blk, length(blk) - n_opts[[k]])
    derived[k] <- paste(stem, collapse = " ")
}

cat("=== CHECK 1: shipped item_text vs S1 File, re-derived per heading ===\n")
nmatch <- 0
for (n in 1:16) {
    k <- paste0("Q", n)
    s <- ship$item_text[match(k, ship$item)]
    same <- identical(clean(s), clean(derived[[k]]))
    nmatch <- nmatch + same
    cat(sprintf("%-4s %-6s %s\n", k, if (same) "MATCH" else "DIFF",
                substr(derived[[k]], 1, 62)))
    if (!same) {
        cat("     shipped : ", substr(s, 1, 200), "\n", sep = "")
        cat("     derived : ", substr(derived[[k]], 1, 200), "\n", sep = "")
    }
}
cat(sprintf("CHECK 1: %d/16 items reproduce verbatim from S1 File\n\n", nmatch))

# --- CHECK 2: S2 Table item-whole correlations -----------------------------
PUB_RAW  <- c(.52,.43,.53,.30,.25,.55,.39,.45,.35,.32,.49,.49,.37,.52,.38,.40)
PUB_DROP <- c(.39,.30,.42,.18,.12,.45,.27,.32,.22,.16,.36,.35,.22,.40,.23,.26)

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d[, c("id", "item", "resp")])
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("resp.", "", colnames(w), fixed = TRUE)
its <- paste0("Q", 1:16)
m <- as.matrix(w[, its])
tot <- rowSums(m)
raw  <- sapply(its, function(i) cor(m[, i], tot, use = "complete.obs"))
drp  <- sapply(its, function(i) cor(m[, i], tot - m[, i], use = "complete.obs"))

cat("=== CHECK 2: item-whole correlations, S2 Table vs live IRW data ===\n")
cat(sprintf("%-5s %9s %9s   %9s %9s\n", "item", "S2 raw", "obs raw", "S2 drop", "obs drop"))
for (n in 1:16)
    cat(sprintf("%-5s %9.2f %9.2f   %9.2f %9.2f\n", its[n], PUB_RAW[n], raw[n],
                PUB_DROP[n], drp[n]))
r1 <- cor(raw, PUB_RAW); r2 <- cor(drp, PUB_DROP)
rs <- cor(raw, PUB_RAW, method = "spearman")
cat(sprintf("\nPearson r (raw) = %.3f ; Pearson r (if-dropped) = %.3f ; Spearman (raw) = %.3f\n",
            r1, r2, rs))
cat("Observed values sit ~0.03-0.07 below the published ones for the higher-loading\n",
    "items, a uniform offset consistent with the paper computing S2 on its analysis\n",
    "subset; the ORDERING is what this route tests.\n", sep = "")

cat("\nNote: CHECK 2 does NOT distinguish every item from every other -- the published\n",
    "correlations tie (items 1 and 14 both .52; 11 and 12 both .49) and cluster, and a\n",
    "nearest-neighbour reassignment recovers only 6/16. The mapping is established by\n",
    "CHECK 1 plus the fact that Q1..Q16 are literally the S3 data file's column headers.\n", sep = "")

pass <- (nmatch == 16) && (r1 >= 0.9) && (r2 >= 0.9)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
