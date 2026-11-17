## Covariance family (irw_cov, source = "cov"): two correlation matrices from
## smacof 2.1-7 (GPL-3; read from the pinned CRAN source tarball) whose N the
## book's own dataset descriptions give (Borg & Groenen, Modern Multidimensional
## Scaling, 2nd ed., dataset page https://personal.eur.nl/groenen/mmds/datasets/).
##
##  - smacof::Guttman1991$R: 12 WISC-R subtests, U.S. children. The smacof object
##    is not symmetric: its LOWER triangle equals the book's "Wechsler Test Tasks
##    U.S." file ("The correlations are based on 2200 U.S. children."); its upper
##    triangle matches neither the U.S. nor the Israel file. Only the lower
##    triangle is used (mirrored); no value is changed.
##  - smacof::crimes (50 U.S. states) is not built: correlations over aggregate
##    units await Ben's scope ruling (held.csv).
##
## Modification (2026-11-17): reshaped to the long lower-triangle layout in
## data/covariance/README.md. No value is changed.
##
## Usage:  Rscript data/covariance/batch_smacof.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_smacof.R <out dir>")
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

## --- Guttman & Levy (1991), WISC-R U.S. ------------------------------------
g <- from_tarball("smacof", "2.1-7", "Guttman1991.rda", "Guttman1991")$R
m <- g; m[upper.tri(m)] <- t(g)[upper.tri(g)]   # mirror the lower triangle
stopifnot(all(m[lower.tri(m, diag = TRUE)] == g[lower.tri(g, diag = TRUE)]))
write_table(to_long(m, "cor", 2200), "guttman_1991_wiscr12")

cat("wrote 1 table to", out, "\n")
