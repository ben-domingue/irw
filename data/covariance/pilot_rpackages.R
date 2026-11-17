## Pilot tables for the covariance family (irw_cov, source = "cov").
##
## Source: matrices already transcribed into R packages -- psychTools and psych
## (William Revelle) and base R `datasets`. All three are GPL (>= 2). Per the
## IRW licensing summary table, data shipped in a GPL package may be reshared
## modified, with a notice of modification and its date, under the same GPL;
## matrices.csv carries licence = "GPL (>= 2)" and the package as licence_source.
##
## What "modified" means here: the matrix is reshaped from a square R matrix to
## the long lower-triangle layout in data/covariance/README.md. No value is
## changed, rounded or smoothed. Burt (1915) is kept non-positive-definite as
## published; the validator flags it (V8).
##
## Every table is a published matrix with no raw data in IRW. Several overlap
## (holzinger_1939_grantwhite9 and thurstone_1941_ability9 are subsets of
## holzinger_1939_grantwhite24 and bechtoldt_1961_ability17 sample 2); the
## record says so rather than dropping one, because each is a canonical
## teaching matrix in its own right.
##
## Usage:  Rscript data/covariance/pilot_rpackages.R <out dir>
## Then:   python3 -m irw_validate.cov <out dir>/*.csv

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript pilot_rpackages.R <out dir>")
out <- args[1]
dir.create(out, showWarnings = FALSE, recursive = TRUE)

get_data <- function(name) {
  e <- new.env()
  for (p in c("psychTools", "psych")) {
    suppressWarnings(utils::data(list = name, package = p, envir = e))
    if (exists(name, envir = e, inherits = FALSE)) return(get(name, envir = e))
  }
  ## psych keeps Chen and West inside the Schmid file
  suppressWarnings(utils::data("Schmid", package = "psych", envir = e))
  if (exists(name, envir = e, inherits = FALSE)) return(get(name, envir = e))
  stop("no dataset ", name, " in psychTools or psych")
}

## Square matrix -> long lower triangle, row by row in published order.
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
add <- function(table, group, n, type, population, citation, location, via, notes = "") {
  rec[[length(rec) + 1]] <<- data.frame(
    table = table, group = group, n_obs = n, matrix_type = type, missing = "unknown",
    population = population, source_citation = citation, source_location = location,
    via = via, capture = "package transcription", verified = "no",
    licence = "GPL (>= 2)", licence_source = sub("::.*", "", via), notes = notes)
}

## --- Holzinger & Swineford -------------------------------------------------
write_table(to_long(get_data("Holzinger"), "cor", 355), "holzinger_1937_bifactor14")
add("holzinger_1937_bifactor14", "", 355, "pearson", "school children",
    "Holzinger, K. J., & Swineford, F. (1937). The bi-factor method. Psychometrika, 2, 41-54.",
    "", "psychTools::Holzinger")

hs24 <- datasets::Harman74.cor
write_table(to_long(hs24$cov, "cor", hs24$n.obs), "holzinger_1939_grantwhite24")
add("holzinger_1939_grantwhite24", "", hs24$n.obs, "pearson", "Grant-White school, grades 7-8",
    "Holzinger, K. J., & Swineford, F. (1939). A study in factor analysis: The stability of a bi-factor solution. Supplementary Educational Monographs, 48.",
    "as reproduced in Harman (1976), Modern Factor Analysis, 24 psychological variables",
    "datasets::Harman74.cor")

write_table(to_long(get_data("Holzinger.9"), "cor", 145), "holzinger_1939_grantwhite9")
add("holzinger_1939_grantwhite9", "", 145, "pearson", "Grant-White school, grades 7-8",
    "Holzinger, K. J., & Swineford, F. (1939). A study in factor analysis: The stability of a bi-factor solution. Supplementary Educational Monographs, 48.",
    "LISREL example NPV.KM; the x1-x9 of lavaan::HolzingerSwineford1939 for Grant-White",
    "psychTools::Holzinger.9", "subset of holzinger_1939_grantwhite24's sample")

## --- Thurstone, Bechtoldt, Brigham, Tucker --------------------------------
write_table(to_long(get_data("Thurstone"), "cor", 213), "thurstone_1941_ability9")
add("thurstone_1941_ability9", "", 213, "pearson", "high-school students",
    "Thurstone, L. L., & Thurstone, T. G. (1941). Factorial studies of intelligence. University of Chicago Press.",
    "nine variables selected by McDonald (1999) from Bechtoldt (1961) sample 2",
    "psychTools::Thurstone", "subset of bechtoldt_1961_ability17 group sample2")

b <- rbind(to_long(get_data("Bechtoldt.1"), "cor", 212, "sample1"),
           to_long(get_data("Bechtoldt.2"), "cor", 213, "sample2"))
write_table(b, "bechtoldt_1961_ability17")
for (g in list(c("sample1", 212), c("sample2", 213)))
  add("bechtoldt_1961_ability17", g[1], as.integer(g[2]), "pearson", "high-school students",
      "Bechtoldt, H. P. (1961). An empirical study of the factor analysis stability hypothesis. Psychometrika, 26, 405-432.",
      "", "psychTools::Bechtoldt.1 / Bechtoldt.2")

boys <- get_data("Thurstone.33")
brig <- to_long(boys, "cor", 4175, "boys")
g33 <- tryCatch(get_data("Thurstone.33G"), error = function(e) NULL)
## The girls' matrix ships without names; the help page says it is "the same 9
## variables", in the same order, so it takes the boys' names.
if (!is.null(g33) && is.null(colnames(g33))) dimnames(g33) <- dimnames(boys)
if (!is.null(g33)) brig <- rbind(brig, to_long(g33, "cor", 2899, "girls"))
write_table(brig, "brigham_1932_ability9")
add("brigham_1932_ability9", "boys", 4175, "pearson", "College Entrance Examination Board candidates",
    "Brigham, C. C. (1932). A study of errors. College Entrance Examination Board.",
    "Table VIII, p. 352", "psychTools::Thurstone.33")
if (!is.null(g33))
  add("brigham_1932_ability9", "girls", 2899, "pearson", "College Entrance Examination Board candidates",
      "Brigham, C. C. (1932). A study of errors. College Entrance Examination Board.",
      "", "psychTools::Thurstone.33G")

write_table(to_long(get_data("Tucker"), "cor", 710), "tucker_1958_ability9")
add("tucker_1958_ability9", "", 710, "pearson", "",
    "Tucker, L. R. (1958). An inter-battery method of factor analysis. Psychometrika, 23, 111-136.",
    "", "psychTools::Tucker", "nine variables from Thurstone & Thurstone (1941)")

## --- Physical, emotional, health, ability ----------------------------------
h23 <- datasets::Harman23.cor
write_table(to_long(h23$cov, "cor", h23$n.obs), "mullen_1939_physical8")
add("mullen_1939_physical8", "", h23$n.obs, "pearson", "girls aged 7-17",
    "Mullen, F. (1939). Factors in the growth of girls seven to seventeen years of age. Unpublished doctoral dissertation, University of Chicago.",
    "as reproduced in Harman (1976), Table 2.3", "datasets::Harman23.cor")

write_table(to_long(get_data("burt"), "cor", 172), "burt_1915_emotions11")
add("burt_1915_emotions11", "", 172, "pearson", "school children aged 9-12",
    "Burt, C. (1916). General and specific factors underlying the primary emotions. Report of the British Association for the Advancement of Science, 85th meeting, 694-696.",
    "pp. 694-696", "psychTools::burt",
    "not positive definite as published; Sorrow-Tenderness .87 is probably a typo for .81 (psychTools::burt), kept as published")

write_table(to_long(get_data("Reise"), "cor", 35000), "reise_2007_health16")
add("reise_2007_health16", "", 35000, "unknown", "health outcomes respondents",
    "Reise, S. P., Morizot, J., & Hays, R. D. (2007). The role of the bifactor model in resolving dimensionality issues in health outcomes measures. Quality of Life Research, 16, 19-31.",
    "", "psychTools::Reise", "source given in psychTools as personal communication from S. Reise")

ab <- datasets::ability.cov
write_table(to_long(ab$cov, "cov", ab$n.obs), "smith_1983_ability6")
add("smith_1983_ability6", "", ab$n.obs, "pearson", "",
    "Smith, G. A., & Stanley, G. (1983). Clocking g: Relating intelligence and measures of timed performance. Intelligence, 7, 353-368.",
    "", "datasets::ability.cov", "covariance matrix; the package's centre vector is all zeros, so no means are given")

write_table(to_long(get_data("Chen"), "cov", 403), "chen_2006_hrqol18")
add("chen_2006_hrqol18", "", 403, "unknown", "",
    "Chen, F. F., West, S. G., & Sousa, K. H. (2006). A comparison of bifactor and second-order models of quality of life. Multivariate Behavioral Research, 41, 189-225.",
    "", "psych::Chen", "covariance matrix")

utils::write.csv(do.call(rbind, rec), file.path(out, "matrices.csv"), row.names = FALSE, na = "")
cat("wrote", length(list.files(out, pattern = "csv$")) - 1, "tables and matrices.csv to", out, "\n")
