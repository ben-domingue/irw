# verify_kraft_todd_2017_panas.R
#
# CLAIM UNDER TEST: PANASPOS1..10 / PANASNEG1..10 in the IRW table map onto the
# 20 PANAS adjectives in the order the study's own S2 File prints them --
# PANASPOS1=Interested, PANASNEG1=Distressed, PANASPOS2=Excited, ... ,
# PANASNEG10=Afraid.
#
# The mapping was NOT read off a label: the S3 workbook's headers are bare codes.
# It rests on two independent routes, both re-run here from the primary sources.
#
#   ROUTE A (structural, separates every item). The S3 workbook's PANAS columns
#   are ordered PANASPOS1, PANASNEG1, PANASPOS2, PANASNEG2, PANASPOS3, PANASNEG3,
#   PANASNEG4, PANASNEG5, PANASPOS4, PANASPOS5, PANASNEG6, PANASPOS6, PANASNEG7,
#   PANASPOS7, PANASNEG8, PANASPOS8, PANASPOS9, PANASNEG9, PANASPOS10, PANASNEG10.
#   The valence sequence that implies (P N P N P N N N P P N P N P N P P N P N) is
#   compared position-by-position against the PA/NA valence of the 20 adjectives in
#   the order the S2 File prints them, using the published PANAS keying. A match at
#   all 20 positions means the workbook's column order IS the administration order,
#   which then pins each numbered code to one adjective. Under a random
#   10-of-20 valence assignment this match has probability 1/choose(20,10)=1/184756.
#
#   ROUTE B (content, independent, corroborates but does not separate synonym
#   pairs). The mapping predicts five near-synonym pairs inside the negative block
#   -- Scared/Afraid, Distressed/Upset, Nervous/Jittery, Hostile/Irritable,
#   Guilty/Ashamed. Criterion, stated in advance: for each pair, at least one
#   member's single highest correlate among the other nine negative items must be
#   its predicted partner. The one-sided form is deliberate -- Scared, Afraid and
#   Nervous form a fear cluster whose members can outrank a partner (Nervous's own
#   top correlate is Scared at 0.835, above Jittery at 0.747), and Irritable sits
#   with the general distress factor (top correlate Upset 0.659, above Hostile
#   0.618), so a mutual-top rule would reject a correct mapping. Checked on the S3
#   response data.
#
#   BRIDGE. data/kraft_todd_2017_empathic_nonverbal.py melts the S3 workbook's own
#   columns BY NAME, so the live item codes are those headers verbatim (core model
#   s3, pattern 1). Confirmed here server-side with irw::irw_table_sets(), which
#   does not export the table.
#
# WHAT THIS DOES NOT ESTABLISH: route B alone cannot tell Scared from Afraid (or
# Alert from Attentive, Excited from Enthusiastic, etc.) -- those are separated
# only by route A's column-order match. The two routes together distinguish every
# item from every other; either one alone would not.
#
# Sources (both public, CC BY 4.0, PLOS ONE 10.1371/journal.pone.0177758):
#   S2 File .s002 (docx) -- "Measures", the PANAS block
#   S3 File .s003 (xlsx) -- the response data IRW processed

suppressMessages(library(irw))

TABLE  <- "kraft_todd_2017_panas"
BASE   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0177758."
UA     <- "IRW-Finder/1.0 (ben.domingue@gmail.com)"
CACHE  <- file.path("..", "..", ".cache", TABLE)   # run from the batch dir; falls back below
if (!dir.exists(CACHE)) CACHE <- tempdir()

get <- function(sfx, ext) {
    p <- file.path(CACHE, paste0(sfx, ".", ext))
    if (!file.exists(p))
        utils::download.file(paste0(BASE, sfx), p, quiet = TRUE,
                             headers = c("User-Agent" = UA), mode = "wb")
    p
}

ok <- TRUE

## ---- S2 File: the administered adjective order -----------------------------
docx <- get("s002", "docx")
tmp  <- file.path(tempdir(), "s002x"); unlink(tmp, recursive = TRUE); dir.create(tmp)
utils::unzip(docx, files = "word/document.xml", exdir = tmp)
xml  <- paste(readLines(file.path(tmp, "word/document.xml"), warn = FALSE), collapse = " ")
txt  <- gsub("<[^>]*>", " ", xml)
# The PANAS block runs from its attribution line to the CARE scale's attribution
# line. Anchor on those, not on the bare words "PANAS"/"CARE" -- both appear in
# the file's caption sentence before either block starts.
block <- sub("^.*?Adapted from Watson", "", txt, perl = TRUE)
block <- sub("Adapted from Mercer.*$", "", block, perl = TRUE)

ADJ <- c("Interested","Distressed","Excited","Upset","Strong","Guilty","Scared",
         "Hostile","Enthusiastic","Proud","Irritable","Alert","Ashamed","Inspired",
         "Nervous","Determined","Attentive","Jittery","Active","Afraid")
pos <- sapply(ADJ, function(a) {
    m <- regexpr(paste0("\\b", a, "\\b"), block, ignore.case = FALSE)
    if (m[1] < 0) NA_integer_ else m[1]
})
if (anyNA(pos)) { cat("FAIL: adjectives not found in S2 PANAS block:",
                      paste(ADJ[is.na(pos)], collapse = ", "), "\n"); ok <- FALSE }
s2_order <- names(sort(pos))
cat("S2 File PANAS block, adjectives in printed order:\n  ",
    paste(s2_order, collapse = ", "), "\n\n", sep = "")
if (!identical(s2_order, ADJ)) { cat("FAIL: S2 print order is not the expected order\n"); ok <- FALSE }

# Published PANAS keying (Watson, Clark & Tellegen 1988): PA = items 1,3,5,9,10,12,14,16,17,19.
PA_IDX  <- c(1,3,5,9,10,12,14,16,17,19)
valence <- ifelse(seq_along(ADJ) %in% PA_IDX, "P", "N")

## ---- S3 File: the workbook column order ------------------------------------
xlsx <- get("s003", "xlsx")
hdr  <- names(suppressMessages(readxl::read_excel(xlsx, n_max = 0, .name_repair = "minimal")))
pcol <- hdr[grepl("^PANAS", hdr)]
cat("S3 workbook PANAS column order:\n  ", paste(pcol, collapse = ", "), "\n\n", sep = "")

col_val <- ifelse(grepl("POS", pcol), "P", "N")
cat("ROUTE A -- valence sequence, position by position\n")
cat("  S2 adjectives : ", paste(valence, collapse = " "), "\n", sep = "")
cat("  S3 columns    : ", paste(col_val, collapse = " "), "\n", sep = "")
nmatch <- sum(valence == col_val)
cat(sprintf("  matched %d/20 positions (random-assignment probability of 20/20 = 1/%d)\n\n",
            nmatch, choose(20, 10)))
if (nmatch != 20) { cat("FAIL: valence sequences differ\n"); ok <- FALSE }

# Numbering must ascend within each valence block, else "k-th POS column" is meaningless.
num <- as.integer(sub("^PANAS(POS|NEG)", "", pcol))
if (!identical(num[col_val == "P"], 1:10) || !identical(num[col_val == "N"], 1:10)) {
    cat("FAIL: code numbering does not ascend with column position\n"); ok <- FALSE
}

derived <- setNames(character(0), character(0))
ip <- 0; inn <- 0
for (i in seq_along(ADJ)) {
    if (valence[i] == "P") { ip <- ip + 1; nm <- paste0("PANASPOS", ip) }
    else                   { inn <- inn + 1; nm <- paste0("PANASNEG", inn) }
    derived[nm] <- ADJ[i]
}

## ---- Compare against the shipped file --------------------------------------
f <- file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(), value = TRUE)[1])),
               paste0(TABLE, "__items.csv"))
if (!file.exists(f)) f <- paste0(TABLE, "__items.csv")
shipped <- unique(read.csv(f, stringsAsFactors = FALSE)[, c("item", "item_text")])
cat("shipped item_text vs mapping derived from the two sources\n")
bad <- 0
for (nm in names(derived)) {
    got <- shipped$item_text[shipped$item == nm]
    flag <- if (length(got) == 1 && identical(got, unname(derived[nm]))) "ok" else { bad <- bad + 1; "MISMATCH" }
    cat(sprintf("  %-11s derived=%-13s shipped=%-13s %s\n", nm, derived[nm],
                if (length(got)) got[1] else "<none>", flag))
}
cat(sprintf("  %d/%d agree\n\n", length(derived) - bad, length(derived)))
if (bad > 0) ok <- FALSE

## ---- ROUTE B: synonym-pair correlations ------------------------------------
d <- suppressMessages(readxl::read_excel(xlsx, .name_repair = "minimal"))
neg <- pcol[col_val == "N"]
D   <- as.data.frame(lapply(d[neg], function(x) suppressWarnings(as.numeric(x))))
C   <- cor(D, use = "pairwise.complete.obs")
lab <- derived[neg]
PAIRS <- list(c("Scared","Afraid"), c("Distressed","Upset"), c("Nervous","Jittery"),
              c("Hostile","Irritable"), c("Guilty","Ashamed"))
cat("ROUTE B -- for each predicted synonym pair, at least one member's top correlate\n")
cat("          among the other nine negative items must be its predicted partner\n")
for (p in PAIRS) {
    a <- names(lab)[lab == p[1]]; b <- names(lab)[lab == p[2]]
    ra <- sort(C[a, setdiff(neg, a)], decreasing = TRUE)
    rb <- sort(C[b, setdiff(neg, b)], decreasing = TRUE)
    hit <- names(ra)[1] == b || names(rb)[1] == a
    cat(sprintf("  %-11s(%s) x %-11s(%s) r=%.3f | top for %s = %s (%.3f), top for %s = %s (%.3f) %s\n",
                p[1], a, p[2], b, C[a, b],
                p[1], lab[names(ra)[1]], ra[1], p[2], lab[names(rb)[1]], rb[1],
                if (hit) "ok" else "MISMATCH"))
    if (!hit) ok <- FALSE
}
cat("\n")

## ---- BRIDGE: live item codes are the workbook headers ----------------------
s <- irw::irw_table_sets(TABLE, source = "core")
cat("BRIDGE -- live IRW item set vs S3 PANAS headers: ",
    if (setequal(s$items, pcol)) sprintf("identical (%d codes)\n", length(pcol)) else "MISMATCH\n", sep = "")
if (!setequal(s$items, pcol)) ok <- FALSE
cat("live resp set:", paste(sort(s$resp), collapse = ", "),
    "| S2 anchors: Very slightly or not at all / A little / Moderately / Quite a bit / Extremely\n\n")

cat("Note: route B cannot separate the members of a synonym pair from each other\n",
    "(Scared vs Afraid, Alert vs Attentive, ...); route A's 20/20 column-order match is\n",
    "what does. Neither route alone distinguishes every item.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
