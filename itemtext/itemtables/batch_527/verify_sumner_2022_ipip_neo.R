# verify_sumner_2022_ipip_neo.R
#
# CLAIM UNDER TEST. The IRW item codes ("IPIP Item 1 (N)" .. "IPIP Item 48 (E)") are the
# source column names of Sumner et al. (2022) S1 Dataset (journal.pone.0278841.s002),
# which carry NO item wording. The shipped item_text assumes the study administered the
# 48 Neuroticism + Extraversion items of the IPIP-NEO-120 (Johnson 2014) in the
# instrument's own order: IPIP-NEO-120 item k (k = 1..120) cycles facets N1 E1 O1 A1 C1
# N2 E2 ... C6, so keeping only N and E gives study item 2m-1 = IPIP-NEO-120 item
# 5(m-1)+1 (N) and study item 2m = IPIP-NEO-120 item 5(m-1)+2 (E). Text, facet and key
# per item are hard-coded below from the shipped CSV and ipip.ori.org's IPIP-NEO-120 key.
#
# ROUTES (both break if two items from different facets, or of different key, swap text):
#  A. SUBSCALE TOTALS (route 3). The deposit carries the study's OWN scored facet and
#     domain columns ("IPIP-NEO N1 Anxiety Scale Score", ...). Summing the live items
#     assigned to each facet with the canonical reverse key must reproduce them exactly.
#  B. KEYING POLARITY (route 6). Each item's correlation with the rest of its domain
#     (canonical-keyed) must be positive for + keyed and negative for - keyed items.
#
# NOT ESTABLISHED: order among items of the SAME facet AND SAME key (e.g. the three +
# Anger items 3/15/27) -- any permutation inside such a group reproduces every number
# below. Status is therefore PARTIAL, not VERIFIED.
#
# Needs network: irw_fetch (44,544 rows) and the PLOS s002 supplement (~0.7 MB).

suppressMessages(library(irw))

TABLE <- "sumner_2022_ipip_neo"
S002  <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0278841.s002"

# study item number -> facet, canonical key (from ipip.ori.org/30FacetNEO-PI-RItems.htm)
FAC <- c("N1","E1","N2","E2","N3","E3","N4","E4","N5","E5","N6","E6")
MAP <- data.frame(j = 1:48, dom = rep(c("N","E"), 24),
                  facet = rep(FAC, 4), stringsAsFactors = FALSE)
MAP$item <- sprintf("IPIP Item %d (%s)", MAP$j, MAP$dom)
REV_J <- c(21, 33, 39, 41, 43, 45, 47,        # N: 51 81 96 101 106 111 116 in the 120
           26, 28, 38, 40, 42, 44)            # E: 62 67 92 97 102 107
MAP$key <- ifelse(MAP$j %in% REV_J, "-", "+")
FACET_COL <- c(N1="N1 Anxiety", N2="N2 Anger", N3="N3 Depression", N4="N4 Self-Consciousness",
               N5="N5 Immoderation", N6="N6 Vulnerability", E1="E1 Friendliness",
               E2="E2 Gregariousness", E3="E3 Assertiveness", E4="E4 Activity Level",
               E5="E5 Excitement-Seeking", E6="E6 Cheerfulness")

# ---- live data, wide ----
d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
W <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar = "id", timevar = "item",
             direction = "wide")
names(W) <- sub("^resp\\.", "", names(W))
W$id <- as.character(W$id)

# ---- study's own scored columns ----
tmp <- tempfile(fileext = ".tsv")
utils::download.file(S002, tmp, quiet = TRUE, headers = c(`User-Agent` = "IRW-itemtext/1.0"))
s <- read.delim(tmp, check.names = FALSE, stringsAsFactors = FALSE)
s$id <- as.character(s[["'ID'"]])
M <- merge(W, s[, c("id", grep("^IPIP-NEO .*Scale Score$", names(s), value = TRUE))], by = "id")
cat("live respondents:", nrow(W), "| joined to deposit on id:", nrow(M), "\n\n")

sc <- function(rows) rowSums(sapply(seq_len(nrow(rows)), function(i) {
    x <- M[[rows$item[i]]]; if (rows$key[i] == "-") 6 - x else x }))

ok <- TRUE
cat("A. Facet/domain scores: live items summed per shipped mapping vs study's column\n")
cat(sprintf("%-28s %-22s %s\n", "study column", "items (study #)", "exact/n"))
for (f in FAC) {
    rows <- MAP[MAP$facet == f, ]
    tgt  <- as.numeric(M[[paste("IPIP-NEO", FACET_COL[f], "Scale Score")]])
    hit  <- sum(sc(rows) == tgt, na.rm = TRUE); n <- sum(!is.na(tgt))
    cat(sprintf("%-28s %-22s %d/%d\n", FACET_COL[f],
                paste0(rows$j, rows$key, collapse = ","), hit, n))
    if (f != "N2" && hit != n) ok <- FALSE
}
# N2: the study's own Anger column is mis-scored -- it reproduces exactly as
# Item 2 (E) + Item 15 + Item 27 + (6 - Item 39), i.e. column 2 used in place of column 3.
tgt <- as.numeric(M[["IPIP-NEO N2 Anger Scale Score"]])
alt <- M[["IPIP Item 2 (E)"]] + M[["IPIP Item 15 (N)"]] + M[["IPIP Item 27 (N)"]] + 6 - M[["IPIP Item 39 (N)"]]
n2 <- sum(alt == tgt, na.rm = TRUE)
cat(sprintf("  N2 study column vs Item2(E)+15+27+(6-39) [study scoring slip]: %d/%d\n", n2, sum(!is.na(tgt))))
if (n2 != sum(!is.na(tgt))) ok <- FALSE
# Domain totals: N total is the study's own item sum, so it pins item 3 into N2 correctly.
tN <- as.numeric(M[["IPIP-NEO Neuroticism Scale Score"]])
hN <- sum(sc(MAP[MAP$dom == "N", ]) == tN, na.rm = TRUE)
cat(sprintf("  Neuroticism total (24 N items, canonical key): %d/%d\n", hN, sum(!is.na(tN))))
if (hN != sum(!is.na(tN))) ok <- FALSE
# E total: study reverse-scores item 30 ("Take control of things.", + keyed, and + in the
# study's own E3 column) in the domain total only. Reproduce that exactly.
tE <- as.numeric(M[["IPIP-NEO Extraversion Scale Score"]])
rowsE <- MAP[MAP$dom == "E", ]; rowsE30 <- rowsE; rowsE30$key[rowsE30$j == 30] <- "-"
cat(sprintf("  Extraversion total, canonical key: %d/%d; with item 30 reversed [study slip]: %d/%d\n",
            sum(sc(rowsE) == tE, na.rm = TRUE), sum(!is.na(tE)),
            sum(sc(rowsE30) == tE, na.rm = TRUE), sum(!is.na(tE))))
if (sum(sc(rowsE30) == tE, na.rm = TRUE) != sum(!is.na(tE))) ok <- FALSE

cat("\nB. Polarity: r(item, rest of domain, canonical-keyed) -- sign must match key\n")
agree <- 0
for (dm in c("N","E")) {
    rows <- MAP[MAP$dom == dm, ]
    for (i in seq_len(nrow(rows))) {
        rest <- sc(rows[-i, ]); x <- M[[rows$item[i]]]
        r <- cor(x, rest, use = "complete.obs")
        good <- (r > 0) == (rows$key[i] == "+"); agree <- agree + good
        cat(sprintf("  %-18s key %s  r = %+.2f %s\n", rows$item[i], rows$key[i], r,
                    if (good) "" else "<-- MISMATCH"))
    }
}
cat(sprintf("polarity agreement: %d/48\n", agree))
if (agree != 48) ok <- FALSE

grp <- table(paste(MAP$facet, MAP$key))
cat("\nNOT established: order within same-facet same-key groups; exchangeable pairs =",
    sum(choose(grp, 2)), "of", choose(48, 2), "\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
