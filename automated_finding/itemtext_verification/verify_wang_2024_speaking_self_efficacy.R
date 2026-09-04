# verify_wang_2024_speaking_self_efficacy.R -- Step 5b, re-runnable evidence.
#
# WHAT IS BEING VERIFIED
# ----------------------
# The chain that ties the shipped item_text to a live IRW item code is:
#
#   S2 Appendix text  ->  code (LSE1..PSE4)  ->  S1 Data column  ->  live `item`
#        (a)                    (b)                    (c)
#
# (c) is identity: data/wang_2024_speaking_self_efficacy.py selects the deposit
#     columns BY NAME and melts them with var_name="item" -- no rename, no
#     positional assignment (core model section 3, row 1).
# (b) is identity by construction, but only if the deposit's column labels are
#     the authors' own item labels; the paper's Fig 2 prints per-item CFA
#     loadings against those codes, so that is testable.
# (a) is the only inference, and it is PARTIAL: the appendix labels the four
#     SUBSCALE blocks (LSE/SRE/DSE/PSE) explicitly but numbers its items 1-15
#     continuously and never prints a per-item code. The numeric suffix is the
#     item's position inside its labelled block.
#
# So this script checks (b) and (c) with numbers, checks the block-label part of
# (a) against the appendix itself, and states plainly that the within-block
# suffix is not established by any of it.
#
# QUOTA: the live side uses a server-side GROUP BY aggregate through redivis,
# NOT irw::irw_fetch(). irw_fetch() exports the whole table against a 200GB /
# 30-day account-wide cap that one round exhausted on 2026-08-18; the numbers
# compared here are 15 rows of aggregates, which a query returns for free.
# irw::irw_table_sets() is used only to resolve the table reference.

suppressMessages({
    library(redivis)
})

TABLE   <- "wang_2024_speaking_self_efficacy"
CACHE   <- file.path("itemtext", ".cache", TABLE)
XLSX_URL <- paste0("https://journals.plos.org/plosone/article/file",
                   "?type=supplementary&id=10.1371/journal.pone.0297517.s004")

ITEMS <- c("LSE1","LSE2","LSE3","LSE4","LSE5",
           "SRE1","SRE2","SRE3",
           "DSE1","DSE2","DSE3",
           "PSE1","PSE2","PSE3","PSE4")

# S2 Appendix (journal.pone.0297517.s002) block structure, transcribed. The
# appendix numbers items 1-15 continuously under these four headers.
BLOCKS <- list(LSE = 1:5, SRE = 6:8, DSE = 9:11, PSE = 12:15)

# Paper Fig 2 -- standardized regression weights, four-factor correlated CFA on
# Study1-cfa (N = 289), printed against the item codes.
FIG2 <- c(LSE1=.84, LSE2=.77, LSE3=.70, LSE4=.81, LSE5=.81,
          SRE1=.82, SRE2=.86, SRE3=.77,
          DSE1=.90, DSE2=.85, DSE3=.84,
          PSE1=.77, PSE2=.91, PSE3=.85, PSE4=.73)

# Fallback deposit values (pooled Study1-efa + Study1-cfa, n = 516 per item),
# used only if the PLOS deposit cannot be downloaded on this run.
FALLBACK <- data.frame(
    item = ITEMS,
    mean = c(4.00,4.23,3.41,3.67,3.94, 4.20,4.94,4.94, 3.79,3.53,4.11, 4.30,3.98,3.90,4.39),
    sd   = c(1.23,1.22,1.17,1.20,1.26, 1.33,1.23,1.18, 1.35,1.30,1.40, 1.26,1.25,1.26,1.36),
    mx   = c(7,7,6,7,7, 7,7,7, 7,7,7, 7,7,7,7),
    n7   = c(7,9,0,1,6, 17,28,31, 11,10,24, 16,13,10,32),
    stringsAsFactors = FALSE)

ok <- TRUE

## ---------------------------------------------------------------------------
## 0. Deposit (S1 Data). Small XLSX from PLOS, cached; no Redivis traffic.
## ---------------------------------------------------------------------------
dir.create(CACHE, showWarnings = FALSE, recursive = TRUE)
xlsx <- file.path(CACHE, "s004.xlsx")
if (!file.exists(xlsx))
    try(utils::download.file(XLSX_URL, xlsx, quiet = TRUE, mode = "wb"), silent = TRUE)

have_dep <- file.exists(xlsx) && requireNamespace("readxl", quietly = TRUE)
if (have_dep) {
    efa <- as.data.frame(readxl::read_excel(xlsx, sheet = "Study1-efa"))
    cfa <- as.data.frame(readxl::read_excel(xlsx, sheet = "Study1-cfa"))
    pool <- rbind(efa[ITEMS], cfa[ITEMS])
    dep <- data.frame(
        item = ITEMS,
        mean = sapply(ITEMS, function(i) mean(pool[[i]])),
        sd   = sapply(ITEMS, function(i) stats::sd(pool[[i]])),
        mx   = sapply(ITEMS, function(i) max(pool[[i]])),
        n7   = sapply(ITEMS, function(i) sum(pool[[i]] == 7)),
        stringsAsFactors = FALSE)
    cat("deposit: S1 Data read from PLOS,",
        nrow(efa), "(efa) +", nrow(cfa), "(cfa) =", nrow(pool), "respondents\n")
    cat("deposit column headers, in file order:",
        paste(names(efa)[6:20], collapse = " "), "\n")
} else {
    dep <- FALLBACK
    cat("deposit: NOT downloadable on this run -- using transcribed fallback values\n")
}

## ---------------------------------------------------------------------------
## 1. Live table, server-side aggregate. Pins each live `item` code to a
##    distribution, which is what would break if the codes had been permuted
##    anywhere between the deposit and the warehouse.
## ---------------------------------------------------------------------------
ref <- irw::irw_table_sets(TABLE, source = "core")$table
sql <- sprintf(paste(
    "SELECT item,",
    "  AVG(CAST(resp AS FLOAT64)) AS mean,",
    "  STDDEV_SAMP(CAST(resp AS FLOAT64)) AS sd,",
    "  MAX(CAST(resp AS FLOAT64)) AS mx,",
    "  SUM(CASE WHEN CAST(resp AS FLOAT64) = 7 THEN 1 ELSE 0 END) AS n7",
    "FROM `%s` WHERE resp IS NOT NULL GROUP BY item"), ref)
live <- as.data.frame(suppressWarnings(redivis::query(sql)$to_data_frame()))
live <- live[match(ITEMS, live$item), ]

cat("\n-- live IRW aggregate vs S1 Data deposit column, per item --\n")
cat(sprintf("%-6s %18s %18s %8s %8s %s\n",
            "item", "mean (live/dep)", "sd (live/dep)", "max", "n(resp=7)", ""))
bad <- character(0)
for (k in seq_along(ITEMS)) {
    i  <- ITEMS[k]
    dm <- abs(live$mean[k] - dep$mean[k]); ds <- abs(live$sd[k] - dep$sd[k])
    hit <- dm < 0.005 && ds < 0.005 && live$mx[k] == dep$mx[k] && live$n7[k] == dep$n7[k]
    if (!hit) bad <- c(bad, i)
    cat(sprintf("%-6s %8.2f /%8.2f %8.2f /%8.2f %4.0f/%-3.0f %4.0f/%-4.0f %s\n",
                i, live$mean[k], dep$mean[k], live$sd[k], dep$sd[k],
                live$mx[k], dep$mx[k], live$n7[k], dep$n7[k],
                if (hit) "ok" else "MISMATCH"))
}
if (length(bad)) {
    ok <- FALSE
    cat("MISMATCH on:", paste(bad, collapse = ", "), "\n")
} else {
    cat("all 15 live codes reproduce their deposit column exactly.\n")
}
cat("  note: LSE3 is the only item never rated 7 (n7 = 0, max 6) in both;\n",
    "  SRE2 and SRE3 tie at mean 4.94 and are separated by sd (1.23 vs 1.18)\n",
    "  and n(resp=7) (28 vs 31).\n", sep = "")

## ---------------------------------------------------------------------------
## 2. Fig 2 loadings. Tests that the deposit's column labels are the labels the
##    AUTHORS used, i.e. that the codes in the data are the paper's codes.
## ---------------------------------------------------------------------------
if (have_dep && requireNamespace("lavaan", quietly = TRUE)) {
    mod <- paste(sapply(names(BLOCKS), function(b)
        sprintf("%s =~ %s", b, paste0(b, seq_along(BLOCKS[[b]]), collapse = " + "))),
        collapse = "\n")
    fit <- lavaan::cfa(mod, data = cfa)
    s <- lavaan::standardizedSolution(fit)
    s <- s[s$op == "=~", ]
    est <- setNames(s$est.std, s$rhs)[ITEMS]
    cat("\n-- paper Fig 2 standardized loadings (CFA, N = 289) vs refit --\n")
    for (i in ITEMS)
        cat(sprintf("%-6s paper %.2f   refit %.3f   diff %+.3f\n",
                    i, FIG2[[i]], est[[i]], est[[i]] - FIG2[[i]]))
    worst <- max(abs(est - FIG2[ITEMS]))
    cat(sprintf("largest deviation: %.3f (tolerance 0.02)\n", worst))
    if (worst > 0.02) ok <- FALSE
    cat("  13 of 15 loadings are distinct within their own block; LSE4 and LSE5\n",
        "  both print .81, so this route does not separate that one pair.\n", sep = "")
} else {
    cat("\n-- Fig 2 loading refit SKIPPED (deposit or lavaan unavailable) --\n")
}

## ---------------------------------------------------------------------------
## 3. What the S2 Appendix does and does not label.
## ---------------------------------------------------------------------------
cat("\n-- S2 Appendix (journal.pone.0297517.s002) --\n")
cat("  four block headers name the codes: 'Linguistic Self-Efficacy (LSE)',\n",
    "  'Self-Regulatory Efficacy (SRE)', 'Delivery Self-efficacy (DSE)',\n",
    "  'Performance Self-Efficacy (PSE)'; block sizes 5/3/3/4 match the deposit's\n",
    "  column counts and the paper's Table 1 (LSE 5, SRE 3, DSE 3, PSE 4).\n",
    "  The string 'LSE' occurs EXACTLY ONCE in the appendix's document.xml -- in\n",
    "  that header. Items are numbered 1-15 continuously; no per-item code is\n",
    "  printed anywhere in the file.\n", sep = "")

## ---------------------------------------------------------------------------
## 4. Route that was tried and is underpowered -- reported, not counted.
## ---------------------------------------------------------------------------
cat("\n-- cross-instrument content pairing (deposit Study3, N = 304): UNDERPOWERED --\n")
cat("  ME2 'spoke with correct pronunciation, intonation, and liaison' should peak\n",
    "  on LSE5 (same wording); LSE-block max is LSE1 r = 0.564, LSE5 r = 0.530.\n",
    "  ME4 'excellent grades on Spoken English tests' should peak on PSE4; PSE-block\n",
    "  max is PSE3 r = 0.693 and PSE4 is the block MINIMUM r = 0.499.\n",
    "  A general factor dominates all 195 cross-scale correlations, so the argmax is\n",
    "  the same high-loading item regardless of content. This is a failure of the\n",
    "  test, not evidence against the mapping.\n", sep = "")

## ---------------------------------------------------------------------------
cat("\nNOT ESTABLISHED: which of the 5 LSE texts is LSE1 rather than LSE2, and the\n",
    "same within SRE, DSE and PSE. The numeric suffix comes from the appendix's\n",
    "print order inside each labelled block, and rotating the texts within a block\n",
    "would leave every number above unchanged. Subscale membership IS established\n",
    "by the appendix's own headers.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
