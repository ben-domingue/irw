## Covariance family (irw_cov, source = "cov"): six R-package matrices held for
## want of an N, whose N was found in an open copy of the source on 2026-11-18
## (#3582). All are read from pinned CRAN source tarballs (no install needed).
##
##  - ShinyItemAnalysis 1.6.0 (GPL-3): TestAnxietyCor, 20 Test Anxiety
##    Inventory items. N = 335 from the book's own download page for
##    Bartholomew, Steele, Moustaki & Galbraith (2008), chapter 7 readme
##    ("correlations between the responses to 20 items given by a sample of 335
##    male students in British Columbia (see Table 7.9)"; chapter 11 readme:
##    "335 male grade 12 students in British Columbia"; SPSS syntax /N=335,
##    LISREL Sample Size = 335). https://www.bristol.ac.uk/cmm/team/fs/aimdss-2nd-ed/downloads.html
##    The package matrix equals the book's anxiety.txt cell for cell.
##  (Rnest tabachnick_fidell2019 is not built: its N = 175 is inferred from a
##   third party, and the book ships the raw data; see held.csv.)
##  - MBESS 5.0.1 (GPL-2 | GPL-3): Cor.Mat.Lomax, 14 reading measures. N = 101
##    from the article's abstract (Lomax, 1983, J Exp Educ 52(1), 33-40): "The
##    sample consisted of 101 learning disabled children, ranging in age from
##    6 to 11 years". MBESS gives no variable names; they are written V1-V14 in
##    MBESS's documented order.
##  - smacof 2.1-7 (GPL-3): Lawler, 3 x 3 multitrait-multirater matrix.
##    N = 113 from Bagozzi & Yi (1992, APM 16, 373-380), Table 1 "Lawler's
##    (1967) Managerial Job Performance Data (N = 113)", and Widaman (1985,
##    APM 9, 1-26): "113 middle- and top-level managers". smacof stores it as
##    a dist object; the diagonal is written as 1. One cell differs from the
##    Bagozzi & Yi reprint: T3M3-T2M3 is 0.40 in smacof, .14 in the reprint.
##  - smacof 2.1-7 (GPL-3): Guttman1965, 21 tests selected by Guttman (1965,
##    Table 1) from Thurstone & Thurstone (1941), "N = 710 Eighth Grade
##    Children" (ERIC ED173439, p. 30). smacof's object is not symmetric: its
##    lower triangle equals Guttman's Table 1 (all 210 cells checked), its
##    upper triangle does not. Only the lower triangle is used (mirrored); no
##    value is changed. Variables are named with Guttman's test names.
##  - smacof 2.1-7 (GPL-3): OCP, 54 Organizational Culture Profile items.
##    N = 337 from Bilsky & Jehn (2002, open copy at noah.nrw, urn:nbn:de:hbz:
##    6-85659525375): "the correlation matrix of all 54 OCP-items (N= 337)",
##    data of Jehn, Chadwick & Thatcher (1997). smacof stores 0 on the
##    diagonal (similarity form); the diagonal is written as 1. Only columns
##    i1-i54 are used (not the facet and constraint columns).
##
## Per the IRW licensing summary table, data shipped in a GPL (or MIT) package
## may be reshared modified, with a notice of modification and its date, under
## the same licence.
##
## Modification (2026-11-18): reshaped to the long lower-triangle layout in
## data/covariance/README.md; similarity-form diagonals (0) written as 1;
## Guttman1965 mirrored from its lower triangle; variables named as above.
## No correlation or covariance value is changed.
##
## Usage:  Rscript data/covariance/batch_rpackages5.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_rpackages5.R <out dir>")
out <- args[1]
dir.create(out, showWarnings = FALSE, recursive = TRUE)
cache <- file.path(tempdir(), "cov_tarballs")
dir.create(cache, showWarnings = FALSE)

from_tarball <- function(pkg, version, file, object) {
  dest <- file.path(cache, paste0(pkg, "_", version, ".tar.gz"))
  if (!file.exists(dest)) {
    ok <- FALSE
    for (u in c(sprintf("https://cloud.r-project.org/src/contrib/%s_%s.tar.gz", pkg, version),
                sprintf("https://cloud.r-project.org/src/contrib/Archive/%s/%s_%s.tar.gz", pkg, pkg, version)))
      if (system2("curl", c("-4", "-sfL", "-m", "300", "-o", shQuote(dest), shQuote(u))) == 0) { ok <- TRUE; break }
    if (!ok) stop("could not download ", pkg, " ", version)
  }
  exdir <- file.path(cache, paste0(pkg, "_", version))
  member <- file.path(pkg, "data", file)
  utils::untar(dest, files = member, exdir = exdir)
  e <- new.env(); load(file.path(exdir, member), envir = e); get(object, envir = e)
}
exact <- function(x) {
  s <- formatC(x, digits = 15, format = "g")
  redo <- as.numeric(s) != x
  s[redo] <- formatC(x[redo], digits = 17, format = "g")
  trimws(s)
}
to_long <- function(m, stat, n) {
  m <- as.matrix(m); v <- colnames(m)
  if (is.null(v) || anyDuplicated(v)) stop("matrix needs unique column names")
  if (anyNA(m)) stop("blank cell")
  if (!isTRUE(all.equal(unname(m), unname(t(m)), tolerance = 0))) stop("matrix is not symmetric")
  idx <- which(lower.tri(m, diag = TRUE), arr.ind = TRUE)
  idx <- idx[order(idx[, "row"], idx[, "col"]), , drop = FALSE]
  data.frame(stat = stat, var1 = v[idx[, "row"]], var2 = v[idx[, "col"]],
             value = exact(m[idx]), n = as.integer(n), stringsAsFactors = FALSE)
}
write_table <- function(df, table)
  utils::write.csv(df, file.path(out, paste0(table, ".csv")), row.names = FALSE, na = "")

## --- Test Anxiety Inventory (Bartholomew et al., 2008) ----------------------
ta <- from_tarball("ShinyItemAnalysis", "1.6.0", "TestAnxietyCor.rda", "TestAnxietyCor")
stopifnot(all(diag(as.matrix(ta)) == 1), identical(colnames(ta), paste0("i", 1:20)))
write_table(to_long(ta, "cor", 335), "bartholomew_2008_testanxiety20")

## --- Lomax (1983) reading components ----------------------------------------
lo <- from_tarball("MBESS", "5.0.1", "Cor.Mat.Lomax.rda", "Cor.Mat.Lomax")
stopifnot(nrow(lo) == 14, ncol(lo) == 14, all(diag(lo) == 1), is.null(colnames(lo)))
dimnames(lo) <- list(paste0("V", 1:14), paste0("V", 1:14))
write_table(to_long(lo, "cor", 101), "lomax_1983_reading14")

## --- Lawler (1967) managerial performance MTMM ------------------------------
la <- as.matrix(from_tarball("smacof", "2.1-7", "Lawler.rda", "Lawler"))
stopifnot(all(diag(la) == 0))
diag(la) <- 1
write_table(to_long(la, "cor", 113), "lawler_1967_jobperf9")

## --- Guttman (1965) Table 1: 21 tests from Thurstone & Thurstone (1941) -----
g <- from_tarball("smacof", "2.1-7", "Guttman1965.rda", "Guttman1965")[[1]]
codes <- c("29", "33", "18", "34", "56", "1", "30", "38", "5", "10", "37", "14", "16",
           "15", "44", "31", "28", "43", "45", "47", "3")
tests <- c("High Numbers", "Letter Grouping", "Faces", "Letter Series", "Three Higher",
           "ABC", "Identical Numbers", "Number Patterns", "Arithmetic", "Completion",
           "Multiplication", "Dot Counting I", "Dot Counting III", "Dot Counting II",
           "Pursuit", "Identical Pictures", "Geometrical Forms", "Proverbs", "Vocabulary",
           "Paragraphs", "Addition")
stopifnot(identical(colnames(g), codes), identical(rownames(g), codes), all(diag(g) == 1))
m <- g; m[upper.tri(m)] <- t(g)[upper.tri(g)]   # mirror the lower triangle
stopifnot(all(m[lower.tri(m, diag = TRUE)] == g[lower.tri(g, diag = TRUE)]))
dimnames(m) <- list(tests, tests)
write_table(to_long(m, "cor", 710), "thurstone_1941_intelligence21")

## --- Organizational Culture Profile (Jehn et al., 1997) ---------------------
oc <- from_tarball("smacof", "2.1-7", "OCP.rda", "OCP")
oc <- as.matrix(oc[, paste0("i", 1:54)])
stopifnot(all(diag(oc) == 0))
diag(oc) <- 1
rownames(oc) <- colnames(oc)
write_table(to_long(oc, "cor", 337), "jehn_1997_ocp54")

cat("wrote 5 tables to", out, "\n")
