# verify_girma_2021_oslo3.R -- Step 5b re-runnable evidence.
#
# CLAIM under test: the three IRW item codes carry the OSSS-3 wording shipped in
# girma_2021_oslo3__items.csv --
#   CLOSENUM = Oslo 1 "How many people are so close to you ...?"  (4 options)
#   CONCERNP = Oslo 2 "How much interest and concern ...?"        (5 options, none..a lot)
#   HELPPRAT = Oslo 3 "How easy is it to get practical help ...?" (5 options, very difficult..very easy)
# and that the option_text ascends with resp (1 = least support).
#
# Two falsifiable numeric predictions, plus the self-describing-code exemption:
#   (A) STRUCTURE. Only Oslo 1 has four response categories; Oslo 2 and 3 have five.
#       So exactly one live item must show n_levels = 4 / max = 4, and it must be the
#       item whose shipped item_text is Oslo 1. (server-side aggregates, no export)
#   (B) DIRECTION + SCALE IDENTITY. In the source deposit (PLOS S1 Dataset) the authors'
#       own composite OSL3 must equal CLOSENUM+CONCERNP+HELPPRAT row for row, and their
#       categorical oslo3 / lowsupp / highsupp must follow the published OSSS-3 bands
#       (3-8 poor, 9-11 moderate, 12-14 strong; Kocalevent et al. 2018, PMC6050647).
#       That only holds if higher codes mean MORE support, i.e. the ascending anchors as
#       shipped. A reversed anchor set would put the authors' "lowsupp" group at the top.
# What (A) and (B) do not do is separate CONCERNP from HELPPRAT; that separation is the
# self-describing-code exemption (CONCERNP = concern from people, HELPPRAT = practical
# help), the codes being the source spreadsheet's own column names, melted unchanged by
# data/girma_2021_depression.py.

suppressMessages(library(irw))
TABLE <- "girma_2021_oslo3"
ok <- TRUE

items_csv <- file.path(dirname(sub("^--file=", "", commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
                       paste0(TABLE, "__items.csv"))
ic <- read.csv(items_csv, stringsAsFactors = FALSE)
nopt <- tapply(ic$resp, ic$item, function(x) length(unique(x)))
oslo1 <- unique(ic$item[grepl("close to you", ic$item_text, fixed = TRUE)])

cat("== (A) response-category structure, live vs shipped ==\n")
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
cat(sprintf("%-10s %6s %9s %9s %14s %14s\n", "item", "n", "resp_min", "resp_max",
            "live_levels", "shipped_opts"))
for (i in seq_len(nrow(pi))) {
    it <- pi$item[i]
    cat(sprintf("%-10s %6d %9d %9d %14d %14d\n", it, pi$n[i], pi$resp_min[i],
                pi$resp_max[i], pi$n_resp_levels[i], nopt[[it]]))
    if (nopt[[it]] != pi$n_resp_levels[i]) ok <- FALSE
}
four <- pi$item[pi$n_resp_levels == 4]
cat(sprintf("item with 4 categories: %s | shipped as Oslo 1: %s\n",
            paste(four, collapse = ","), paste(oslo1, collapse = ",")))
if (length(four) != 1 || length(oslo1) != 1 || four != oslo1) ok <- FALSE

cat("\n== (B) direction, against the source deposit's own composites ==\n")
url <- "https://doi.org/10.1371/journal.pone.0250927.s001"
tmp <- tempfile(fileext = ".xls")
utils::download.file(url, tmp, quiet = TRUE, mode = "wb")
d <- as.data.frame(readxl::read_excel(tmp))
s3 <- rowSums(d[, c("CLOSENUM", "CONCERNP", "HELPPRAT")])
cat(sprintf("rows: %d | sum(CLOSENUM,CONCERNP,HELPPRAT) == author's OSL3: %d rows | range %d-%d (paper states 3-14)\n",
            nrow(d), sum(s3 == d$OSL3), min(s3), max(s3)))
if (sum(s3 == d$OSL3) != nrow(d) || min(s3) != 3 || max(s3) != 14) ok <- FALSE

band <- cut(s3, breaks = c(2, 8, 11, 14), labels = c(1, 2, 3))
tab <- table(published_band = band, authors_oslo3 = d$oslo3)
print(tab)
agree <- sum(diag(as.matrix(tab)))
cat(sprintf("bands 3-8/9-11/12-14 vs authors' oslo3 1/2/3: %d of %d rows agree\n", agree, nrow(d)))
if (agree != nrow(d)) ok <- FALSE
cat(sprintf("mean sum where authors' lowsupp==1: %.2f ; where highsupp==1: %.2f (must be low<high for ascending anchors)\n",
            mean(s3[d$lowsupp == 1]), mean(s3[d$highsupp == 1])))
if (!(mean(s3[d$lowsupp == 1]) < mean(s3[d$highsupp == 1]))) ok <- FALSE

cat("\nNote: (A) pins CLOSENUM as Oslo 1 and (B) fixes the ascending option direction;\n",
    "CONCERNP vs HELPPRAT is settled by the self-describing source column names, not by a statistic.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
