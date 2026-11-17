## Covariance family (irw_cov, source = "cov"): classic SEM teaching matrices
## shipped with the R package sem (John Fox), #3582 source 2.
##
## Source: sem 3.1-16, GPL (>= 2). Four matrices are files in the package's
## etc/ directory, read with sem::readMoments() and the variable names its help
## examples give; the union-sentiment matrix is typed into the pathDiagram()
## help example (contributed by Michael Friendly) and is copied here verbatim.
## Per the IRW licensing summary table, data shipped in a GPL package may be
## reshared modified under the same GPL with a modification notice.
##
## Modification (2026-11-17): reshaped to the long lower-triangle layout in
## data/covariance/README.md. No value is changed.
##
## Left out: R-Thurstone.txt (the same matrix as thurstone_1941_ability9),
## M-McArdle.txt (a raw, uncentred moment matrix, neither cor nor cov) and the
## CNES matrix (computed in the example from raw data shipped with sem).
##
## Usage:  Rscript data/covariance/batch_sem.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_sem.R <out dir>")
out <- args[1]
dir.create(out, showWarnings = FALSE, recursive = TRUE)
suppressMessages(library(sem))
etc <- system.file("etc", package = "sem")
if (packageVersion("sem") != "3.1.16") warning("built against sem 3.1-16; installed ", packageVersion("sem"))

to_long <- function(m, stat, n) {
  m <- as.matrix(m)
  m[upper.tri(m)] <- t(m)[upper.tri(m)]          # readMoments fills the lower triangle only
  v <- colnames(m)
  if (is.null(v) || anyDuplicated(v) || anyNA(m)) stop("bad matrix")
  idx <- which(lower.tri(m, diag = TRUE), arr.ind = TRUE)
  idx <- idx[order(idx[, "row"], idx[, "col"]), , drop = FALSE]
  data.frame(stat = stat, var1 = v[idx[, "row"]], var2 = v[idx[, "col"]],
             value = m[idx], n = as.integer(n), stringsAsFactors = FALSE)
}
write_table <- function(df, table)
  utils::write.csv(df, file.path(out, paste0(table, ".csv")), row.names = FALSE, na = "")

rec <- list()
add <- function(table, n, type, population, citation, location, via, notes) {
  rec[[length(rec) + 1]] <<- data.frame(
    table = table, group = "", n_obs = n, matrix_type = type, missing = "unknown",
    population = population, source_citation = citation, source_location = location,
    via = via, capture = "package transcription", verified = "no",
    licence = "GPL (>= 2)", licence_source = "sem", notes = notes)
}
rm_ <- function(file, names, diag) suppressMessages(readMoments(file.path(etc, file), diag = diag, names = names))

write_table(to_long(rm_("R-DHP.txt", c("ROccAsp", "REdAsp", "FOccAsp", "FEdAsp", "RParAsp", "RIQ",
                                       "RSES", "FSES", "FIQ", "FParAsp"), FALSE), "cor", 329),
            "duncan_1968_peer10")
add("duncan_1968_peer10", 329, "pearson", "male high-school students (respondents R) and their best friends (F)",
    "Duncan, O. D., Haller, A. O., & Portes, A. (1968). Peer influences on aspirations: A reinterpretation. American Journal of Sociology, 74(2), 119-137.",
    "", "sem::etc/R-DHP.txt",
    "occupational and educational aspiration, parental aspiration, IQ and SES of respondent and friend")

write_table(to_long(rm_("S-Wheaton.txt", c("Anomia67", "Powerless67", "Anomia71", "Powerless71",
                                           "Education", "SEI"), TRUE), "cov", 932),
            "wheaton_1977_alienation6")
add("wheaton_1977_alienation6", 932, "pearson", "",
    "Wheaton, B., Muthen, B., Alwin, D. F., & Summers, G. F. (1977). Assessing reliability and stability in panel models. Sociological Methodology, 8, 84-136.",
    "", "sem::etc/S-Wheaton.txt",
    "covariance matrix; anomia and powerlessness in 1967 and 1971, education and socioeconomic index; the lavaan getCov() example matrix")

write_table(to_long(rm_("R-Kerchoff.txt", c("Intelligence", "Siblings", "FatherEd", "FatherOcc", "Grades",
                                            "EducExp", "OccupAsp"), FALSE), "cor", 737),
            "kerckhoff_1974_ambition7")
add("kerckhoff_1974_ambition7", 737, "pearson", "male students",
    "Kerckhoff, A. C. (1974). Ambition and attainment: A study of four samples of American boys. American Sociological Association.",
    "", "sem::etc/R-Kerchoff.txt", "intelligence, family background, grades, educational expectation and occupational aspiration")

write_table(to_long(rm_("R-Blau-Duncan.txt", c("x1", "x2", "y3", "y4", "y5"), TRUE), "cor", 20700),
            "blau_1967_occupation5")
add("blau_1967_occupation5", 20700, "pearson", "US men aged 20-64 (1962 Occupational Changes in a Generation survey)",
    "Blau, P. M., & Duncan, O. D. (1967). The American occupational structure. Wiley.",
    "", "sem::etc/R-Blau-Duncan.txt",
    "x1 = father's education, x2 = father's occupation, y3 = respondent's education, y4 = first job, y5 = occupation in 1962 (the classic path-analysis order)")

## Taken from the pathDiagram() help example's own text, so it is read exactly
## as sem ships it.
ex <- paste(utils::capture.output(tools::Rd2ex(tools::Rd_db("sem")[["pathDiagram.Rd"]])), collapse = "\n")
txt <- regmatches(ex, regexpr("union <- readMoments\\(diag=TRUE,.*?text=\"[^\"]*\"", ex))
if (length(txt) != 1) stop("union-sentiment block not found in the pathDiagram example")
union <- suppressMessages(readMoments(diag = TRUE, names = c("y1", "y2", "y3", "x1", "x2"),
                                      text = sub('.*text="', "", sub('"$', "", txt))))
write_table(to_long(union, "cov", 173), "mcdonald_1984_union5")
add("mcdonald_1984_union5", 173, "pearson", "textile workers",
    "McDonald, A., & Clelland, D. A. (1984). Textile workers and union sentiment. Social Forces, 63(2), 502-521.",
    "as analysed in Bollen (1989), Structural equations with latent variables, ch. 4", "sem::pathDiagram example",
    "covariance matrix; y1 = deference to managers, y2 = support for labour activism, y3 = sentiment towards unions, x1 = years in the mill, x2 = age")

utils::write.csv(do.call(rbind, rec), file.path(out, "matrices.csv"), row.names = FALSE, na = "")
cat("wrote", length(rec), "tables to", out, "\n")
