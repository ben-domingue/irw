# verify_piterova-slovak-science-related-populism.R
#
# CLAIM UNDER TEST -------------------------------------------------------------
# The item text shipped for this table comes from the study's own OSF supplement
# ("Wording of questions", osf.io/yfx6h file 658022b6513a741e1aaed239), which
# prefixes every reproduced item with the very code the live table uses
# ("Ppl1: ...", "Anti1: ...", "TrustSc3: ..."). Those codes are also, verbatim,
# the column headers of the deposit's response file
# ("datacleaned_2023 ANONYM.xlsx", osf.io/yfx6h file 65141a1f333aef0229d7065b).
# So the mapping claim has two links, and this script tests both:
#
#   (A) the xlsx column named <code> IS the live item named <code>
#   (B) the wording the supplement attaches to <code> is really that variable
#
# (A) is tested structurally: for all 96 items, live per-item n / resp_min /
#     resp_max / n_resp_levels (server-side aggregates -- NO table export) must
#     equal the same four numbers computed from the xlsx column of that name.
#     The response-scale signature is highly discriminating across blocks
#     (7-point, 5-point, 0-10, 0/1 binary, the {1,2,3,4,98} literacy quiz, and
#     Control2's single constant value).
#
# (B) is tested numerically: 20 statistics the paper and its companion deposit
#     publish under NAMED constructs are recomputed from the xlsx columns that
#     the supplement assigns to those names. If the supplement's code labels
#     were permuted, the per-item means for PercSc1-4, TrustSc1-3 and PolOr1/2
#     and the subscale means for SciPop / anti-elitism / sovereignty /
#     homogeneity / distrust would not land on the published values.
#
# WHAT THIS DOES NOT ESTABLISH -------------------------------------------------
# The published statistics separate PercSc1-4, TrustSc1-3 and PolOr1 vs PolOr2
# individually, and pin Control2 outright, but within Anti1-4, Sov1-4, Homo1-4
# and the SciPop pairs they only pin SUBSCALE membership -- order inside those
# blocks rests on the supplement's explicit per-code labels, not on these
# numbers. 63 of the 96 items ship no item_text at all and therefore carry no
# mapping claim to test.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "piterova-slovak-science-related-populism"
CACHE <- file.path(".cache", TABLE)
XLSX  <- file.path(CACHE, "data.xlsx")
dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
if (!file.exists(XLSX))
    download.file("https://osf.io/download/65141a1f333aef0229d7065b/", XLSX,
                  mode = "wb", quiet = TRUE)

x <- as.data.frame(read_excel(XLSX))
for (nm in names(x)) x[[nm]] <- suppressWarnings(as.numeric(x[[nm]]))

ok <- TRUE

## ---- (A) xlsx column <-> live item, structural signature ---------------------
s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
pi$item <- as.character(pi$item)

cat("=== (A) live per-item aggregates vs the xlsx column of the same name ===\n")
mismatch <- character(0)
for (i in seq_len(nrow(pi))) {
    it <- pi$item[i]
    if (!it %in% names(x)) { mismatch <- c(mismatch, paste0(it, ": absent from xlsx")); next }
    v <- x[[it]][!is.na(x[[it]])]
    got <- c(length(v), min(v), max(v), length(unique(v)))
    want <- as.numeric(c(pi$n[i], pi$resp_min[i], pi$resp_max[i], pi$n_resp_levels[i]))
    if (!isTRUE(all.equal(got, want)))
        mismatch <- c(mismatch, sprintf("%s: live %s vs xlsx %s", it,
                                        paste(want, collapse = "/"), paste(got, collapse = "/")))
}
cat(sprintf("items reconciled on n/min/max/levels: %d of %d\n",
            nrow(pi) - length(mismatch), nrow(pi)))
if (length(mismatch)) { cat(paste0("  ", mismatch, collapse = "\n"), "\n"); ok <- FALSE }
cat("distinctive signatures present: Control2 = {2} only; ScLit* = {1,2,3,4,98};\n",
    "  PolPro*/Proxi* = {0,1}; ConsM*/PolOr*/TrustSc* = {0..10}\n", sep = "")
cat(sprintf("  Control2 observed values: {%s}\n",
            paste(sort(unique(x$Control2[!is.na(x$Control2)])), collapse = ",")))
cat(sprintf("  ScLit1 observed values:   {%s}\n",
            paste(sort(unique(x$ScLit1[!is.na(x$ScLit1)])), collapse = ",")))

## ---- (B) published statistics vs the codes the supplement labels -------------
m  <- function(v) round(mean(v), 2)
sd2 <- function(v) round(sd(v), 2)
scale_mean <- function(codes, rev = character(0)) {
    mat <- x[, codes, drop = FALSE]
    for (r in rev) mat[[r]] <- 6 - mat[[r]]
    rowMeans(mat)
}

# Published: Piterova (2024) Ceskoslovenska psychologie 68(2):156-173, Table S2
# and Table S3 of the OSF supplement; the last four rows come from the same
# author's companion deposit for the same 2023 dataset (osf.io/3w98r,
# "Supplementary materials - Table S2, wording.pdf").
CHECKS <- list(
    list("PercSc1 (perception of science 1)", x$PercSc1,                       3.73, 0.98),
    list("PercSc2 (perception of science 2)", x$PercSc2,                       3.36, 0.98),
    list("PercSc3 (perception of science 3)", x$PercSc3,                       3.13, 1.05),
    list("PercSc4 (perception of science 4)", x$PercSc4,                       2.89, 1.05),
    list("TrustSc1 (trust in science)",       x$TrustSc1,                      6.36, 2.33),
    list("TrustSc2 (trust in scientists)",    x$TrustSc2,                      6.40, 2.32),
    list("TrustSc3 (trust in institutions)",  x$TrustSc3,                      6.23, 2.41),
    list("PolOr1 (left-right)",               x$PolOr1,                        4.93, 2.25),
    list("PolOr2 (conservative-liberal)",     x$PolOr2,                        4.69, 2.39),
    list("SciPop total (Ppl1,Homo2,Eli1-2,Tru1-2,Dec1-2)",
         scale_mean(c("Ppl1","Homo2","Eli1","Eli2","Tru1","Tru2","Dec1","Dec2")), 4.08, 1.18),
    list("conception of ordinary people (Ppl1,Homo2)", scale_mean(c("Ppl1","Homo2")), 4.55, 1.28),
    list("conception of academic elite (Eli1,Eli2)",   scale_mean(c("Eli1","Eli2")),  3.94, 1.56),
    list("truth-speaking sovereignty (Tru1,Tru2)",     scale_mean(c("Tru1","Tru2")),  4.06, 1.56),
    list("decision-making sovereignty (Dec1,Dec2)",    scale_mean(c("Dec1","Dec2")),  3.76, 1.48),
    list("political populism (Anti1-4,Sov1-4,Homo1-4)",
         scale_mean(c(paste0("Anti",1:4), paste0("Sov",1:4), paste0("Homo",1:4))),   5.14, 1.01),
    list("anti-elitism (Anti1-4)",  scale_mean(paste0("Anti",1:4)), 5.77, 1.17),
    list("popular sovereignty (Sov1-4)", scale_mean(paste0("Sov",1:4)), 5.43, 1.27),
    list("homogeneity of people (Homo1-4)", scale_mean(paste0("Homo",1:4)), 4.21, 1.31),
    list("distrust of experts (Distrust1-3, 3 reversed)",
         scale_mean(paste0("Distrust",1:3), rev = "Distrust3"), 2.89, 0.81),
    list("relative deprivation (RelDep1-7) [companion deposit]",
         scale_mean(paste0("RelDep",1:7)), 4.82, 1.17)
)
TOL <- 0.011
cat("\n=== (B) published vs recomputed from the supplement's own item codes ===\n")
cat(sprintf("%-52s %12s %12s %8s\n", "statistic", "published", "observed", "dM"))
bad <- 0
for (ch in CHECKS) {
    v <- ch[[2]][!is.na(ch[[2]])]
    om <- m(v); os <- sd2(v)
    d <- abs(om - ch[[3]]); ds <- abs(os - ch[[4]])
    if (d > TOL || ds > TOL) bad <- bad + 1
    cat(sprintf("%-52s %6.2f/%-5.2f %6.2f/%-5.2f %8.3f\n",
                ch[[1]], ch[[3]], ch[[4]], om, os, om - ch[[3]]))
}
cat(sprintf("\nstatistics reproduced within %.3f (mean and SD): %d of %d\n",
            TOL, length(CHECKS) - bad, length(CHECKS)))
if (bad > 0) ok <- FALSE

## ---- (C) marker item ---------------------------------------------------------
cat("\n=== (C) marker: Control2 tells respondents to tick 2 ===\n")
c2 <- x$Control2[!is.na(x$Control2)]
cat(sprintf("Control2: n=%d, all equal to 2? %s\n", length(c2), all(c2 == 2)))
if (!all(c2 == 2)) ok <- FALSE
c1 <- x$Control1[!is.na(x$Control1)]
cat(sprintf("Control1 (\"I do not understand a word of Slovak\"): mean %.2f, values {%s}\n",
            mean(c1), paste(sort(unique(c1)), collapse = ",")))

cat("\nNote: within Anti1-4, Sov1-4, Homo1-4 and each SciPop pair these numbers pin\n",
    "subscale membership only; the order inside those blocks rests on the supplement's\n",
    "explicit per-code labels. 63 of 96 items ship blank item_text.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
