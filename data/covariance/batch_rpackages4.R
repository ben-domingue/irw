## Covariance family (irw_cov, source = "cov"): held R-package matrices whose
## N or scope was resolved on 2026-11-17 (#3582).
##
## Sources (read from pinned CRAN source tarballs; no install needed):
##  - metaSEM 2.0, GPL (>= 2): Digman97. Digman (1997, JPSP 73, p. 1247-1248,
##    Method) says 13 of the 14 sets are product-moment correlations among
##    observed Big Five scores (factor-score composites or unweighted scale
##    composites); for Digman & Takemoto-Chock (1981b) "the factor correlations
##    came from an oblique solution by promax; the correlations were taken as
##    the intercosines of the factor axes", i.e. latent-factor correlations
##    (model output), so that study is left out (held.csv). Ns are Digman's
##    Appendix A, which match Digman97$n.
##  - ggm 2.5.4, GPL-2: stress. N = 72 from ggm's own help page for
##    fitCovGraph: "Correlations among four strategies to cope with stress for
##    72 students. Cox & Wermuth (1996), p. 73." The variables are unnamed in
##    ggm (Y, V, X, U) and are kept so.
## Per the IRW licensing summary table, data shipped in a GPL package may be
## reshared modified, with a notice of modification and its date, under the
## same GPL.
##
## Modification (2026-11-17): reshaped to the long lower-triangle layout in
## data/covariance/README.md, one `group` per study. No value is changed.
##
## Usage:  Rscript data/covariance/batch_rpackages4.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_rpackages4.R <out dir>")
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
  off <- m[lower.tri(m)]
  if (any(abs(off) >= 1)) stop("off-diagonal |r| >= 1 in ", group)
  idx <- which(lower.tri(m, diag = TRUE), arr.ind = TRUE)
  idx <- idx[order(idx[, "row"], idx[, "col"]), , drop = FALSE]
  data.frame(stat = stat, var1 = v[idx[, "row"]], var2 = v[idx[, "col"]],
             value = m[idx], n = as.integer(n), group = group, stringsAsFactors = FALSE)
}
## Shortest form that reads back as exactly the same double (batch_metasem.R).
exact <- function(x) {
  s <- formatC(x, digits = 15, format = "g")
  redo <- as.numeric(s) != x
  s[redo] <- formatC(x[redo], digits = 17, format = "g")
  trimws(s)
}
write_table <- function(df, table) {
  df$value <- exact(df$value)
  if (all(is.na(df$group))) df$group <- NULL
  utils::write.csv(df, file.path(out, paste0(table, ".csv")), row.names = FALSE, na = "",
                   quote = which(names(df) %in% c("stat", "var1", "var2", "group")))
}

rec <- list()
add <- function(table, group, n, population, citation, location, via, licence, notes) {
  rec[[length(rec) + 1]] <<- data.frame(
    table = table, group = group, n_obs = n, matrix_type = "unknown", missing = "unknown",
    population = population, source_citation = citation, source_location = location,
    via = via, capture = "package transcription", verified = "no",
    licence = licence, licence_source = sub("::.*", "", via), notes = notes)
}

## --- metaSEM::Digman97 (13 of 14 studies) ---------------------------------
d <- from_tarball("metaSEM", "2.0", "Digman97.rda", "Digman97")
latent <- "Digman & Takemoto-Chock (1981b)"   # promax factor intercosines: out
stopifnot(latent %in% names(d$data))
dig <- "Digman, J. M. (1997). Higher-order factors of the Big Five. Journal of Personality and Social Psychology, 73(6), 1246-1256. https://doi.org/10.1037/0022-3514.73.6.1246"
rows <- list()
for (i in seq_along(d$data)) {
  g <- names(d$data)[i]
  if (g == latent) next
  rows[[length(rows) + 1]] <- to_long(d$data[[i]], "cor", d$n[i], g)
  add("digman_1997_bigfive5", g, as.integer(d$n[i]), as.character(d$cluster[i]), dig,
      "Appendix B (correlations), Appendix A (N, participants)", "metaSEM::Digman97", "GPL (>= 2)",
      paste0("correlations among the five Big Five scores (A, C, ES, E, I) as observed composites ",
             "(factor-score or unweighted scale composites, Digman 1997 p. 1247-1248); study-level matrices from a research synthesis"))
}
write_table(do.call(rbind, rows), "digman_1997_bigfive5")

## --- ggm::stress ------------------------------------------------------------
s <- from_tarball("ggm", "2.5.4", "stress.rda", "stress")
write_table(to_long(s, "cor", 72), "cox_1996_coping4")
add("cox_1996_coping4", "", 72L, "students",
    "Cox, D. R., & Wermuth, N. (1996). Multivariate dependencies: Models, analysis and interpretation. Chapman & Hall.",
    "p. 73; data from Slangen, Kleemann & Krohne (1993), Coping with surgical stress, in Krohne (Ed.), Attention and avoidance (pp. 321-346), Springer",
    "ggm::stress", "GPL-2",
    "correlations among four coping strategies; ggm names the variables only Y, V, X, U; N = 72 from the ggm help page for fitCovGraph (\"72 students. Cox & Wermuth (1996), p. 73\")")

utils::write.csv(do.call(rbind, rec), file.path(out, "matrices.csv"), row.names = FALSE, na = "")
cat("wrote", length(unique(sapply(rec, `[[`, "table"))), "tables,", length(rec), "matrices to", out, "\n")
