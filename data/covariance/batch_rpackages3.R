## Covariance family (irw_cov, source = "cov"): test-manual matrices from GPL
## R packages (#3582, source 2).
##
## Source: EFAtools 1.1.0 (GPL-3; read from the pinned CRAN source tarball)
## and psychTools (GPL (>= 2)). Both matrices come from commercial test manuals:
## the WJ IV technical manual (EFAtools: "Tables are reproduced with permission
## from the publisher") and the NEO PI-R professional manual. Ruling (Ben,
## 2026-11-17): data in a GPL package is standard GPL, whatever its origin; the
## provenance is kept in matrices.csv.
##
## Modification (2026-11-17): reshaped to the long lower-triangle layout in
## data/covariance/README.md. No value is changed.
##
## Usage:  Rscript data/covariance/batch_rpackages3.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_rpackages3.R <out dir>")
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

to_long <- function(m, stat, n, group = NA_character_) {
  m <- as.matrix(m)
  v <- colnames(m)
  if (is.null(v) || anyDuplicated(v)) stop("matrix needs unique column names")
  if (anyNA(m)) stop("blank cell")
  if (!isTRUE(all.equal(unname(m), unname(t(m)), tolerance = 0))) stop("matrix is not symmetric")
  idx <- which(lower.tri(m, diag = TRUE), arr.ind = TRUE)
  idx <- idx[order(idx[, "row"], idx[, "col"]), , drop = FALSE]
  data.frame(stat = stat, var1 = v[idx[, "row"]], var2 = v[idx[, "col"]],
             value = m[idx], n = as.integer(n), group = group, stringsAsFactors = FALSE)
}
write_table <- function(df, table) {
  if (all(is.na(df$group))) df$group <- NULL
  utils::write.csv(df, file.path(out, paste0(table, ".csv")), row.names = FALSE, na = "")
}

rec <- list()
add <- function(table, group, n, population, citation, location, via, licence, notes) {
  rec[[length(rec) + 1]] <<- data.frame(
    table = table, group = group, n_obs = n, matrix_type = "unknown", missing = "unknown",
    population = population, source_citation = citation, source_location = location,
    via = via, capture = "package transcription", verified = "no",
    licence = licence, licence_source = sub("::.*", "", via), notes = notes)
}

## --- WJ IV norming sample, six age groups ----------------------------------
ages <- c("3_5", "6_8", "9_13", "14_19", "20_39", "40_90")
wj <- list()
for (a in ages) {
  x <- from_tarball("EFAtools", "1.1.0", paste0("WJIV_ages_", a, ".RData"), paste0("WJIV_ages_", a))
  g <- paste0("ages ", sub("_", "-", a))
  wj[[a]] <- to_long(x$cormat, "cor", x$N, g)
  add("mcgrew_2014_wjiv47", g, x$N, paste("WJ IV standardization sample,", g),
      "McGrew, K. S., LaForte, E. M., & Schrank, F. A. (2014). Technical manual: Woodcock-Johnson IV. Riverside.",
      "", paste0("EFAtools::WJIV_ages_", a), "GPL-3",
      paste0("cognitive and achievement subtests (", ncol(x$cormat), " at these ages); EFAtools reproduces the tables with the publisher's permission"))
}
write_table(do.call(rbind, wj), "mcgrew_2014_wjiv47")

## --- NEO PI-R facets --------------------------------------------------------
e <- new.env(); utils::data("neo", package = "psychTools", envir = e)
write_table(to_long(e$neo, "cor", 1000), "costa_1992_neopir30")
add("costa_1992_neopir30", "", 1000, "NEO PI-R normative sample",
    "Costa, P. T., & McCrae, R. R. (1992). Revised NEO Personality Inventory (NEO PI-R) and NEO Five-Factor Inventory (NEO-FFI) professional manual. Psychological Assessment Resources.",
    "", "psychTools::neo", "GPL (>= 2)",
    "correlations among the 30 facet scales as reported in the manual; variables are the facet codes N1-C6, whose full names (N1 = Anxiety, ...) are the row names of psychTools::neo")

utils::write.csv(do.call(rbind, rec), file.path(out, "matrices.csv"), row.names = FALSE, na = "")
cat("wrote", length(unique(sapply(rec, `[[`, "table"))), "tables,", length(rec), "matrices to", out, "\n")
