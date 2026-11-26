## Covariance family (irw_cov, source = "cov"), second R-package batch (#3582, source 2).
##
## Source: matrices already transcribed into GPL R packages. Each package's
## licence was read from its DESCRIPTION file:
##   fungible 2.4.8   GPL (>= 2)        EFAtools 1.1.0   GPL-3
##   ggm 2.5.4        GPL-2             GPArotation      GPL (>= 2)
##   psychTools       GPL (>= 2)
## Per the IRW licensing summary table, data shipped in a GPL package may be
## reshared modified, with a notice of modification and its date, under the same
## GPL; matrices.csv carries the licence and the package as licence_source.
##
## Modification (2026-11-17): each matrix is reshaped from a square R matrix to
## the long lower-triangle layout in data/covariance/README.md. No value is
## changed, rounded or smoothed.
##
## fungible, EFAtools and ggm are not installed: fungible imports MBESS, which
## imports OpenMx (a heavy compile). Their data files are read straight from the
## pinned CRAN source tarballs, so nothing is installed and the version is fixed.
##
## Considered and left out, with reasons, in the PR description for #3582:
## duplicates of pilot tables (fungible::Thurstone41 = psych::Tucker), matrices
## with no N in the package (pending the original papers), and matrices held
## for licence or provenance doubts (WJ-IV and NEO-PI-R manual matrices,
## Project Talent, fungible::Jackson67, EFAtools::RiskDimensions).
##
## Usage:  Rscript data/covariance/batch_rpackages2.R <out dir>
## Then:   python3 -m irw_validate.cov <out dir>/*.csv

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_rpackages2.R <out dir>")
out <- args[1]
dir.create(out, showWarnings = FALSE, recursive = TRUE)

## --- reading pinned CRAN tarballs -----------------------------------------
tarball_cache <- file.path(tempdir(), "cov_tarballs")
dir.create(tarball_cache, showWarnings = FALSE)

from_tarball <- function(pkg, version, file, object) {
  dest <- file.path(tarball_cache, paste0(pkg, "_", version, ".tar.gz"))
  if (!file.exists(dest)) {
    urls <- c(sprintf("https://cloud.r-project.org/src/contrib/%s_%s.tar.gz", pkg, version),
              sprintf("https://cloud.r-project.org/src/contrib/Archive/%s/%s_%s.tar.gz", pkg, pkg, version))
    ## curl -4: R's own downloader stalls on IPv6 on some machines
    ok <- FALSE
    for (u in urls) if (system2("curl", c("-4", "-sfL", "-m", "300", "-o", shQuote(dest), shQuote(u))) == 0) { ok <- TRUE; break }
    if (!ok) stop("could not download ", pkg, " ", version)
  }
  exdir <- file.path(tarball_cache, paste0(pkg, "_", version))
  member <- file.path(pkg, "data", file)
  utils::untar(dest, files = member, exdir = exdir)
  e <- new.env()
  load(file.path(exdir, member), envir = e)
  get(object, envir = e)
}

from_installed <- function(pkg, object) {
  e <- new.env()
  utils::data(list = object, package = pkg, envir = e)
  get(object, envir = e)
}

## --- shared helpers (as pilot_rpackages.R) ---------------------------------
to_long <- function(m, stat, n, group = NA_character_) {
  m <- as.matrix(m)
  v <- colnames(m)
  if (is.null(v) || anyDuplicated(v)) stop("matrix needs unique column names")
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
add <- function(table, group, n, type, population, citation, location, via, licence, notes = "") {
  rec[[length(rec) + 1]] <<- data.frame(
    table = table, group = group, n_obs = n, matrix_type = type, missing = "unknown",
    population = population, source_citation = citation, source_location = location,
    via = via, capture = "package transcription", verified = "no",
    licence = licence, licence_source = sub("::.*", "", via), notes = notes)
}

## --- fungible 2.4.8 --------------------------------------------------------
write_table(to_long(from_tarball("fungible", "2.4.8", "Boruch70.rda", "Boruch70"), "cor", 111),
            "boruch_1970_mtmm14")
add("boruch_1970_mtmm14", "", 111, "unknown", "supervisors, each rated via their least and most effective subordinate",
    "Boruch, R. F., Larkin, J. D., Wolins, L., & MacKinney, A. C. (1970). Alternative methods of analysis: Multitrait-multimethod data. Educational and Psychological Measurement, 30, 833-853.",
    "", "fungible::Boruch70", "GPL (>= 2)",
    "multitrait-multimethod: 7 dimensions x 2 sources (X = least, Y = most effective subordinate)")

write_table(to_long(from_tarball("fungible", "2.4.8", "Malmi79.rda", "Malmi79"), "cor", 97),
            "malmi_1979_learning12")
add("malmi_1979_learning12", "", 97, "unknown", "",
    "Malmi, R. A., Underwood, B. J., & Carroll, J. B. (1979). The interrelationships among some associative learning tasks. Bulletin of the Psychonomic Society, 13(3), 121-123. https://doi.org/10.3758/BF03335032",
    "", "fungible::Malmi79", "GPL (>= 2)",
    "free recall (FR), serial learning (SL) and paired-associate (PA) tasks")

## --- ggm 2.5.4 -------------------------------------------------------------
write_table(to_long(from_tarball("ggm", "2.5.4", "anger.rda", "anger"), "cov", 684),
            "cox_1996_anger4")
add("cox_1996_anger4", "", 684, "pearson", "female students",
    "Cox, D. R., & Wermuth, N. (1996). Multivariate dependencies: Models, analysis and interpretation. Chapman and Hall.",
    "", "ggm::anger", "GPL-2",
    "covariance matrix; X = anxiety state, Y = anger state, Z = anxiety trait, U = anger trait (ggm help page); the study that collected the data is not named in ggm")

## --- EFAtools 1.1.0 --------------------------------------------------------
write_table(to_long(from_tarball("EFAtools", "1.1.0", "IDS2_R.RData", "IDS2_R"), "cor", 1991),
            "grob_2018_ids2_14")
add("grob_2018_ids2_14", "", 1991, "unknown", "IDS-2 standardization and validation sample, ages 5-20",
    "Grieder, S., & Grob, A. (2019). Exploratory factor analyses of the Intelligence and Development Scales-2: Implications for theory and practice. Assessment. https://doi.org/10.1177/1073191119845051",
    "", "EFAtools::IDS2_R", "GPL-3",
    "14 intelligence subtests of the IDS-2 (Grob & Hagmann-von Arx, 2018, Hogrefe); abbreviations in the EFAtools help page")

## --- GPArotation -----------------------------------------------------------
write_table(to_long(from_installed("GPArotation", "GriffithMulaik"), "cor", 523),
            "griffith_1998_interpersonal24")
add("griffith_1998_interpersonal24", "", 523, "unknown", "Georgia Tech introductory psychology students rating stereotypical persons",
    "Griffith, D., & Mulaik, S. A. (1998). Personality trait factors from the interpersonal domain. Poster, Society for Multivariate Experimental Psychology.",
    "reproduced in Mulaik (2018), Fundamentals of common factor analysis, Wiley Handbook of Psychometric Testing", "GPArotation::GriffithMulaik", "GPL (>= 2)",
    "24 of 52 bipolar trait-adjective scales, four per hypothesised factor")

## --- psychTools ------------------------------------------------------------
write_table(to_long(from_installed("psychTools", "Pollack"), "cor", 262), "pollack_2012_estress9")
add("pollack_2012_estress9", "", 262, "pearson", "entrepreneurs",
    "Pollack, J. M., Vanepps, E. M., & Hayes, A. F. (2012). The moderating role of social ties on entrepreneurs' depressed affect and withdrawal intentions in response to economic stress. Journal of Organizational Behavior, 33(6), 789-810.",
    "", "psychTools::Pollack", "GPL (>= 2)",
    "the ESTRESS example of Hayes (2013)")

cl <- rbind(to_long(from_installed("psychTools", "colom"), "cor", 1369, "all"),
            to_long(from_installed("psychTools", "colom.ed0"), "cor", 301, "ed0"),
            to_long(from_installed("psychTools", "colom.ed1"), "cor", 432, "ed1"),
            to_long(from_installed("psychTools", "colom.ed2"), "cor", 525, "ed2"),
            to_long(from_installed("psychTools", "colom.ed3"), "cor", 111, "ed3"))
write_table(cl, "colom_2002_wais14")
for (g in list(c("all", 1369), c("ed0", 301), c("ed1", 432), c("ed2", 525), c("ed3", 111)))
  add("colom_2002_wais14", g[1], as.integer(g[2]), "unknown", "Spanish WAIS-III standardization sample (703 women, 666 men)",
      "Colom, R., Abad, F. J., Garcia, L. F., & Juan-Espinosa, M. (2002). Education, Wechsler's Full Scale IQ, and g. Intelligence, 30, 449-462.",
      "", "psychTools::colom", "GPL (>= 2)",
      if (g[1] == "all") "whole sample; groups ed0-ed3 are its four education levels" else "education-level subset of group all")

utils::write.csv(do.call(rbind, rec), file.path(out, "matrices.csv"), row.names = FALSE, na = "")
cat("wrote", length(list.files(out, pattern = "csv$")) - 1, "tables and matrices.csv to", out, "\n")
