# verify_dpt_noncog__grit.R
#
# This table is BLOCKED on rights, so NO item text was shipped and there is no
# item_text<->item mapping in existence to verify. The instrument is the 8-item
# Short Grit Scale (Grit-S; Duckworth & Quinn, 2009), of which this table holds
# items 1, 3 and 5. Its rights holder publishes the only authoritative copies at
# angeladuckworth.com/measures and states there:
#
#   "Researchers and educators are welcome to use the scales developed by
#    Angela's lab for non-commercial purposes"
#   "These scales are copyrighted. They cannot be published or used for
#    commercial purposes or wide public distribution."
#
# That is both a non-commercial clause and an explicit bar on publication /
# wide distribution, so it fires the SKILL's rights rules twice over and
# overrides the CC0 licence of the Harvard Dataverse deposit IRW's responses
# came from (2026-09-04 DSES/no-redistribution ruling).
#
# What this script re-runs is the evidence recorded in
# verification_dpt_noncog__grit.csv: the mapping that WOULD have been shipped is
# inference-free and was checked anyway, cell for cell, so the block is a rights
# decision and not a data problem.
#
#   1. The CC0 deposit (doi:10.7910/DVN/Y75CP2, Jeehp_15_19_raw data.xlsx) is a
#      self-documenting matrix: row 1 = survey code (Q19_1..Q19_3), row 2 =
#      original scale item number (SGS_1, SGS_3, SGS_5), row 4 = the question
#      text. data/dpt_noncognitive_traits.py maps Q19_1->grit_1, Q19_2->grit_3,
#      Q19_3->grit_5 and does no recoding, so IRW's item code IS the source's own
#      scale item number.
#   2. Falsifiable check: every item x resp cell count in the live IRW table must
#      equal the corresponding cell count of its assigned raw column. It does,
#      for all 15 cells. The three items' distributions differ enough that any
#      permutation of the three assignments breaks the match -- the script prints
#      the permuted comparison to show the route discriminates.
#   3. Direction of resp: the deposit stores RAW (un-reverse-scored) responses.
#      Demonstrated on the same file's IRI fantasy subscale, where the two
#      canonically reverse-worded items (IRI 7, 12) correlate NEGATIVELY with the
#      forward fantasy items. Combined with the paper's statement (JEEHP
#      2018;15:19, PMC6194478) that Grit-S items are "scored on a 5-point scale
#      ranging from 5 (very much like me) to 1 (not at all like me)", resp 5 is
#      the "very much like me" end.
#
# irw_fetch() is used deliberately: the table is 894 rows, and per item x resp
# counts are what the check needs.

suppressMessages({library(irw); library(readxl)})

TABLE <- "dpt_noncog__grit"
XLSX_URL <- "https://dataverse.harvard.edu/api/access/datafile/3234209"
CACHE <- file.path("..", "..", ".cache", TABLE, "raw.xlsx")

if (!file.exists(CACHE)) {
    dir.create(dirname(CACHE), recursive = TRUE, showWarnings = FALSE)
    utils::download.file(XLSX_URL, CACHE, mode = "wb", quiet = TRUE)
}

# Rows: 1 survey code (header), 2 scale item number, 3 domain, 4 question text,
# 5+ data. Read headerless so the label rows stay addressable.
raw <- as.data.frame(readxl::read_excel(CACHE, col_names = FALSE, .name_repair = "minimal"))
codes  <- as.character(unlist(raw[1, ]))
scalen <- as.character(unlist(raw[2, ]))
domain <- as.character(unlist(raw[3, ]))
qtext  <- as.character(unlist(raw[4, ]))

grit_cols <- which(trimws(ifelse(is.na(domain), "", domain)) == "Grit")
cat("source columns whose Domain row reads 'Grit':", length(grit_cols), "\n")
for (j in grit_cols)
    cat(sprintf("  col %d  %-7s %-7s %s\n", j, codes[j], scalen[j], substr(qtext[j], 1, 70)))

# Claimed mapping, from data/dpt_noncognitive_traits.py
MAP <- c(Q19_1 = "grit_1", Q19_2 = "grit_3", Q19_3 = "grit_5")

dat <- raw[5:nrow(raw), grit_cols, drop = FALSE]
colnames(dat) <- codes[grit_cols]
dat <- dat[!is.na(dat[[1]]), , drop = FALSE]
dat[] <- lapply(dat, as.numeric)
cat(sprintf("\nraw respondents: %d\n", nrow(dat)))

src_counts <- sapply(names(MAP), function(cc) tabulate(dat[[cc]], nbins = 5))
rownames(src_counts) <- 1:5

d <- irw::irw_fetch(TABLE)
live_counts <- sapply(MAP, function(it) tabulate(d$resp[d$item == it], nbins = 5))
rownames(live_counts) <- 1:5
cat(sprintf("live rows: %d ; distinct items: %d\n\n", nrow(d), length(unique(d$item))))

cat("item x resp cell counts, source column vs live item (claimed mapping)\n")
cat(sprintf("%-6s %-8s %-8s %6s %6s %6s %6s %6s\n",
            "src", "scale#", "live", "r=1", "r=2", "r=3", "r=4", "r=5"))
for (k in seq_along(MAP)) {
    cc <- names(MAP)[k]; it <- MAP[[k]]
    j <- grit_cols[match(cc, codes[grit_cols])]
    cat(sprintf("%-6s %-8s %-8s %6d %6d %6d %6d %6d   (raw)\n",
                cc, scalen[j], it, src_counts[1,k], src_counts[2,k], src_counts[3,k],
                src_counts[4,k], src_counts[5,k]))
    cat(sprintf("%-6s %-8s %-8s %6d %6d %6d %6d %6d   (live)\n",
                "", "", "", live_counts[1,k], live_counts[2,k], live_counts[3,k],
                live_counts[4,k], live_counts[5,k]))
}
exact <- identical(as.vector(src_counts), as.vector(live_counts))
cat(sprintf("\nall 15 cells identical under the claimed mapping: %s\n", exact))

# Does the route discriminate? Try the 5 wrong permutations of the 3 assignments.
perms <- list(c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
n_wrong_matching <- sum(sapply(perms, function(p)
    identical(as.vector(src_counts[, p]), as.vector(live_counts))))
cat(sprintf("wrong permutations of the 3 items that would also match: %d of 5\n",
            n_wrong_matching))

# Direction: is the deposit raw or already reverse-scored? IRI fantasy subscale.
iri_fwd <- c("IR_Index_1", "IR_Index_5", "IR_Index_16", "IR_Index_23", "IR_Index_26")
iri_rev <- c("IR_Index_7", "IR_Index_12")
getcol <- function(lbl) as.numeric(unlist(raw[5:nrow(raw), which(scalen == lbl)[1]]))
F <- sapply(iri_fwd, getcol); R <- sapply(iri_rev, getcol)
ok <- complete.cases(F, R); fmean <- rowMeans(F[ok, , drop = FALSE])
cat("\ndeposit is raw, not reverse-scored (IRI fantasy subscale):\n")
rc <- sapply(iri_rev, function(l) cor(fmean, R[ok, l]))
for (l in iri_rev)
    cat(sprintf("  %-12s (canonically reverse-worded) r with forward-item mean = %+.3f\n",
                l, rc[[l]]))
raw_dir <- all(rc < 0)

cat("\nNote: this establishes that the mapping the block withheld would have been\n",
    "correct, and the direction of resp. It establishes NOTHING about the rights\n",
    "question, which is the actual reason no CSV was written: that rests on the\n",
    "quoted clause at angeladuckworth.com/measures, which a reader must check by eye.\n", sep = "")

cat(if (exact && n_wrong_matching == 0 && raw_dir) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
