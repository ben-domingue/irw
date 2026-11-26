## Covariance family (irw_cov, source = "cov"): correlation matrices shipped in
## non-SEM R packages (#3582, agent B sweep): GPArotation 2026.8-2, BGGM 2.2.0
## and SEset 1.0.1.
##
## Source: GPArotation 2026.8-2, GPL (>= 2), read from the pinned CRAN source
## tarball (data/CCAI.rda, data/WansbeekMeijer.rda); the .rda files are load()ed,
## nothing else in the tarball is run.
##   - CCAI_R: 14 x 14 item correlations of the Climate Change Action Inventory
##     Climate-Friendly Purchasing Choices domain, N = 461 (help page: 500 MTurk
##     workers, 15 deniers and 24 multivariate outliers removed). Bi, Y., &
##     Barchard, K. (2024). Purchasing choices that reduce climate change: An
##     exploratory factor analysis. Spectra Undergraduate Research Journal, 3(2).
##     https://doi.org/10.9741/2766-7227.1028. The help page says the matrix was
##     provided by the authors and "has not been published separately", i.e. it
##     was computed by the authors from their microdata. CCAI_pattern and
##     CCAI_Phi (model output) are not used. Values are full-precision
##     doubles (not a rounded printed table).
##   - NetherlandsTV$cov: 7 x 7 correlations among viewership of seven Dutch TV
##     channels, n.obs = 2154. Wansbeek, T., & Meijer, E. (2000). Measurement
##     error and latent variables in econometrics. North-Holland, p. 171. The
##     list element is called `cov` but the diagonal is 1: written as `cor`.
## Not used from GPArotation: Harman (= Harman23.cor, mullen_1939_physical8),
## Thurstone (box problem, artificial), GriffithMulaik (already built).
##
## Source: BGGM 2.2.0, GPL-2, read from the pinned CRAN source tarball
## (data/ptsd_cor1.rda ... ptsd_cor4.rda, data/asd_ocd.rda).
##   - ptsd_cor1-4 (Fried et al., 2018) are built by batch_semPackages.R as
##     fried_2018_ptsd16 (with symptom names), not here.
##   - asd_ocd: 17 x 17 correlations among 9 autism and 8 OCD repetitive-
##     behaviour symptoms, N = 213 (help page). Ruzzano, L., Borsboom, D., &
##     Geurts, H. M. (2015). Repetitive behaviors in autism and obsessive-
##     compulsive disorder: New perspectives from a network analysis. Journal of
##     Autism and Developmental Disorders, 45(1), 192-202.
##     https://doi.org/10.1007/s10803-014-2204-9 (also used by Jones, Ma &
##     McNally, 2019).
## All five are full-precision doubles, i.e. computed from microdata, not a
## rounded printed table.
##
## Source: SEset 1.0.1, GPL-3, read from the pinned CRAN source tarball
## (data/riskcor.rda). 6 x 6 correlations reported in the supplement (mmc1.pdf)
## of Hoorelbeke, K., Marchetti, I., De Schryver, M., & Koster, E. H. W. (2016).
## The interplay between cognitive risk and resilience factors in remitted
## depression: A network analysis. Journal of Affective Disorders, 195, 96-104.
## https://doi.org/10.1016/j.jad.2016.02.001. N = 69 (help page). Two-decimal
## values as published.
##
## Modification (2026-11-17): reshaped to the long lower-triangle layout in
## data/covariance/README.md, variables in the package's order. No value is
## changed; values are written in the shortest form that reads back as the same
## double.
##
## Usage:  Rscript data/covariance/batch_rpackages_b.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_rpackages_b.R <out dir>")
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

to_long <- function(m, stat, n, group = NA_character_, sym_tol = 0) {
  m <- as.matrix(m)
  v <- colnames(m)
  if (is.null(v) || anyDuplicated(v)) stop("matrix needs unique column names")
  if (!identical(unname(rownames(m)), unname(v))) stop("row and column names differ")
  if (anyNA(m)) stop("blank cell")
  if (max(abs(m - t(m))) > sym_tol) stop("matrix is not symmetric")
  idx <- which(lower.tri(m, diag = TRUE), arr.ind = TRUE)
  idx <- idx[order(idx[, "row"], idx[, "col"]), , drop = FALSE]
  data.frame(stat = stat, var1 = v[idx[, "row"]], var2 = v[idx[, "col"]],
             value = m[idx], n = as.integer(n), group = group, stringsAsFactors = FALSE)
}

## shortest form that reads back as exactly the same double (batch_metasem.R)
exact <- function(x) {
  s <- formatC(x, digits = 15, format = "g")
  redo <- as.numeric(s) != x
  s[redo] <- formatC(x[redo], digits = 17, format = "g")
  trimws(s)
}

write_table <- function(df, table) {
  if (all(is.na(df$group))) df$group <- NULL
  df$value <- exact(df$value)
  utils::write.csv(df, file.path(out, paste0(table, ".csv")), row.names = FALSE, na = "", quote = TRUE)
}

## --- CCAI purchasing choices ------------------------------------------------
ccai <- from_tarball("GPArotation", "2026.8-2", "CCAI.rda", "CCAI_R")
stopifnot(all(diag(ccai) == 1))
## CCAI_R holds full-precision doubles whose upper and lower triangles differ
## in the last bit (max 1.2e-16; 20 of 91 pairs): floating-point noise from its
## computation. The lower triangle is written exactly as stored.
write_table(to_long(ccai, "cor", 461, sym_tol = 1e-15), "bi_2024_ccai14")

## --- Netherlands TV viewership ----------------------------------------------
tv <- from_tarball("GPArotation", "2026.8-2", "WansbeekMeijer.rda", "NetherlandsTV")
stopifnot(tv$n.obs == 2154, all(diag(tv$cov) == 1))
write_table(to_long(tv$cov, "cor", tv$n.obs), "wansbeek_2000_tvviewing7")

## --- Ruzzano et al. (2015) autism / OCD -------------------------------------
asd <- as.matrix(from_tarball("BGGM", "2.2.0", "asd_ocd.rda", "asd_ocd"))
rownames(asd) <- colnames(asd)
stopifnot(all(diag(asd) == 1))
write_table(to_long(asd, "cor", 213), "ruzzano_2015_asdocd17")

## --- Hoorelbeke et al. (2016) cognitive risk ------------------------------
risk <- from_tarball("SEset", "1.0.1", "riskcor.rda", "riskcor")
stopifnot(all(diag(risk) == 1))
write_table(to_long(risk, "cor", 69), "hoorelbeke_2016_cogrisk6")

## --- exact round trip --------------------------------------------------------
chk <- list(list("bi_2024_ccai14", ccai, NA), list("wansbeek_2000_tvviewing7", tv$cov, NA),
            list("ruzzano_2015_asdocd17", asd, NA), list("hoorelbeke_2016_cogrisk6", risk, NA))
for (p in chk) {
  d <- utils::read.csv(file.path(out, paste0(p[[1]], ".csv")), stringsAsFactors = FALSE)
  if (!is.na(p[[3]])) d <- d[d$group == p[[3]], ]
  m <- p[[2]]
  got <- m[cbind(match(d$var1, rownames(m)), match(d$var2, colnames(m)))]
  stopifnot(nrow(d) == ncol(m) * (ncol(m) + 1) / 2, identical(d$value, unname(got)))
  cat(p[[1]], " ", p[[3]], ": ", nrow(d), " cells equal the package object exactly\n", sep = "")
}
