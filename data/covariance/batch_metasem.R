## Covariance family (irw_cov, source = "cov"): metaSEM corpora (#3582, source 1).
##
## Source: metaSEM 2.0 (Mike W.-L. Cheung), GPL (>= 2), read from the pinned
## CRAN source tarball (no install needed to read its data files). Per the IRW
## licensing summary table, data shipped in a GPL package may be reshared
## modified, with a notice of modification and its date, under the same GPL.
##
## Modification (2026-11-17): each study matrix is reshaped to the long
## lower-triangle layout in data/covariance/README.md, one `group` per study.
## No value is changed. Where metaSEM repeats a study label (Nohe15A1/A2 list
## several samples under one citation), later repeats get " (2)", " (3)" so
## that groups are unique; the order is metaSEM's.
##
## A variable a study never measured (blank diagonal) is dropped from that
## study's matrix (Ben, 2026-11-17), as is a variable whose cells with every
## other measured variable are all blank. A pair of measured variables that the study
## did not report keeps its row with an empty `value` (Ben, 2026-11-18); a study
## with fewer than two measured variables, no reported off-diagonal cell, or an
## off-diagonal |r| >= 1 among its blank-cell matrices is not built (held.csv).
##
## Modification (2026-11-18): measured pairs the study did not report are now
## written as rows with an empty `value` instead of holding the study.
## Gnambs18 is the exception: 77 of its 113 matrices were reproduced from
## published factor loadings (CorMat = 0), which is model output and out of
## scope, so only the 36 observed matrices (CorMat = 1) are kept.
## Held (see held.csv): Digman97 (described as factor correlation matrices;
## pending a check of the paper) and Cheung09 (variables deleted at random by
## the package author to illustrate missing data: an altered subset of issp89).
##
## Modification (2026-11-18): per-study reliabilities that metaSEM ships
## (Nohe15A1/A2 RelXX, Boer16 RelLMX/RelTFL) are written as `rel` rows after
## each study's matrix rows, value as stored, only for variables in that study's
## matrix; a blank reliability gets no row. The help pages do not name the
## coefficient. Nohe15A2 names both strain reliabilities `RelS2`, so which is S1
## is not stated: only its F1 and F2 reliabilities are written. No existing
## row changes.
##
## Usage:  Rscript data/covariance/batch_metasem.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_metasem.R <out dir>")
out <- args[1]
dir.create(out, showWarnings = FALSE, recursive = TRUE)

PKG <- "metaSEM"; VER <- "2.0"; LICENCE <- "GPL (>= 2)"
cache <- file.path(tempdir(), "cov_tarballs")
dir.create(cache, showWarnings = FALSE)
tgz <- file.path(cache, paste0(PKG, "_", VER, ".tar.gz"))
if (!file.exists(tgz)) {
  ok <- FALSE
  for (u in c(sprintf("https://cloud.r-project.org/src/contrib/%s_%s.tar.gz", PKG, VER),
              sprintf("https://cloud.r-project.org/src/contrib/Archive/%s/%s_%s.tar.gz", PKG, PKG, VER)))
    if (system2("curl", c("-4", "-sfL", "-m", "300", "-o", shQuote(tgz), shQuote(u))) == 0) { ok <- TRUE; break }
  if (!ok) stop("could not download ", PKG, " ", VER)
}
msem <- function(name) {
  exdir <- file.path(cache, paste0(PKG, "_", VER))
  member <- file.path(PKG, "data", paste0(name, ".rda"))
  utils::untar(tgz, files = member, exdir = exdir)
  e <- new.env(); load(file.path(exdir, member), envir = e); get(name, envir = e)
}

to_long <- function(m, stat, n, group) {
  m <- as.matrix(m)
  v <- colnames(m)
  if (is.null(v) || anyDuplicated(v)) stop("matrix needs unique column names")
  ## Ben 2026-11-18: an off-diagonal cell may be blank (written empty); a
  ## diagonal may not.
  if (anyNA(diag(m))) stop("blank diagonal in ", group)
  if (!isTRUE(all.equal(unname(m), unname(t(m)), tolerance = 0))) stop("matrix is not symmetric: ", group)
  idx <- which(lower.tri(m, diag = TRUE), arr.ind = TRUE)
  idx <- idx[order(idx[, "row"], idx[, "col"]), , drop = FALSE]
  data.frame(stat = stat, var1 = v[idx[, "row"]], var2 = v[idx[, "col"]],
             value = m[idx], n = as.integer(n), group = group, stringsAsFactors = FALSE)
}

## write.csv keeps 15 significant digits, which changes full-precision doubles
## (the ISSP covariances) in the last digits. Write the shortest form that reads
## back as exactly the same double instead.
exact <- function(x) {
  s <- formatC(x, digits = 15, format = "g")
  redo <- rep(FALSE, length(x))
  redo[!is.na(x)] <- as.numeric(s[!is.na(x)]) != x[!is.na(x)]
  s[is.na(x)] <- ""
  s[redo] <- formatC(x[redo], digits = 17, format = "g")
  trimws(s)
}

uniq <- function(x) {
  k <- ave(seq_along(x), x, FUN = seq_along)
  ifelse(k == 1, x, paste0(x, " (", k, ")"))
}

rec <- list()
skipped <- list()
## One table per corpus. `pop` gives each study's population label (or "").
## `rel`: a data frame with one row per study and one column per variable.
build <- function(table, name, stat, citation, location, pop = NULL, keep = NULL, means = NULL, rel = NULL, notes = "") {
  x <- msem(name)
  mats <- x$data; n <- x$n
  if (is.null(keep)) keep <- rep(TRUE, length(mats))
  ## Roorda11 ships unnamed studies; they are numbered in metaSEM's order.
  labels <- names(mats)
  if (is.null(labels)) labels <- sprintf("study%02d", seq_along(mats))
  groups <- uniq(labels)
  if (is.null(pop)) pop <- rep("", length(mats))
  rows <- list()
  for (i in which(keep)) {
    m <- mats[[i]]
    ## Ben 2026-11-17: a variable the study never measured (blank diagonal) is
    ## dropped from that study's matrix; no value changes. Ben 2026-11-18: a
    ## measured pair the study did not report keeps its row with an empty value.
    ## A study with fewer than two variables, no reported off-diagonal cell, an
    ## off-diagonal |r| >= 1 (blank-cell matrices) or a blank mean is not built.
    measured <- !is.na(diag(m))
    m <- m[measured, measured, drop = FALSE]
    ## A variable whose cells with every other remaining variable are all blank
    ## was not measured either and is dropped (Ben's standing rule). Only matrices
    ## with blank cells are affected; one with no reported cell at all is held.
    repeat {
      if (ncol(m) < 3 || all(is.na(m[lower.tri(m)]))) break
      nob <- vapply(seq_len(ncol(m)), function(j) all(is.na(m[-j, j])), logical(1))
      if (!any(nob)) break
      m <- m[!nob, !nob, drop = FALSE]
    }
    dropped <- colnames(mats[[i]])[!colnames(mats[[i]]) %in% colnames(m)]
    off <- if (ncol(m) >= 2) m[lower.tri(m)] else numeric(0)
    nblank <- sum(is.na(off))
    why <- if (ncol(m) < 2) "fewer than two measured variables" else
      if (all(is.na(off))) "no reported off-diagonal cell among measured variables" else
      if (nblank > 0 && stat == "cor" && any(abs(off) >= 1, na.rm = TRUE)) "off-diagonal |r| >= 1" else
      if (!is.null(means) && anyNA(means[i, colnames(m)])) "blank mean for a measured variable" else ""
    if (nzchar(why)) {
      skipped[[length(skipped) + 1]] <<- data.frame(table = table, group = groups[i], reason = why)
      next
    }
    mats[[i]] <- m
    rows[[length(rows) + 1]] <- to_long(m, stat, n[i], groups[i])
    if (!is.null(means)) {
      mu <- means[i, colnames(mats[[i]])]
      rows[[length(rows) + 1]] <- data.frame(stat = "mean", var1 = names(mu), var2 = NA_character_, value = unname(mu),
                                             n = as.integer(n[i]), group = groups[i], stringsAsFactors = FALSE)
    }
    if (!is.null(rel)) {
      r <- unlist(rel[i, intersect(colnames(mats[[i]]), names(rel)), drop = FALSE])
      r <- r[!is.na(r)]
      if (length(r)) rows[[length(rows) + 1]] <- data.frame(stat = "rel", var1 = names(r), var2 = NA_character_, value = unname(r),
                                                            n = as.integer(n[i]), group = groups[i], stringsAsFactors = FALSE)
    }
    rec[[length(rec) + 1]] <<- data.frame(
      table = table, group = groups[i], n_obs = as.integer(n[i]), matrix_type = "unknown", missing = "unknown",
      population = pop[i], source_citation = citation, source_location = location,
      via = paste0("metaSEM::", name), capture = "package transcription", verified = "no",
      licence = LICENCE, licence_source = "metaSEM",
      notes = paste0(notes,
        if (length(dropped)) paste0("; not measured in this study, dropped: ", paste(dropped, collapse = ", ")) else "",
        if (nblank > 0) paste0("; ", nblank, " measured pair", if (nblank > 1) "s" else "", " not reported (blank cells, Ben 2026-11-18)") else ""))
  }
  tab <- do.call(rbind, rows)
  tab$value <- exact(tab$value)
  utils::write.csv(tab, file.path(out, paste0(table, ".csv")), row.names = FALSE, na = "", quote = c(1, 2, 3, 6))
}

b92 <- "Becker, B. J. (1992). Using results from replicated studies to estimate linear models. Journal of Educational Statistics, 17(4), 341-362. https://doi.org/10.3102/10769986017004341"
build("becker_1992_ability3", "Becker92", "cor", b92, "with corrections in Becker (1995), JEBS 20(1), 100-102",
      notes = "study-level matrices from a research synthesis; math, spatial and verbal ability")

x <- msem("Becker94")
build("becker_1994_ability3", "Becker94", "cor",
      "Becker, B. J., & Schram, C. M. (1994). Examining explanatory models through research synthesis. In H. Cooper & L. V. Hedges (Eds.), The handbook of research synthesis (pp. 357-381). Russell Sage Foundation.",
      "", pop = as.character(x$gender), notes = "five studies, female and male samples separately")

x <- msem("Gnambs18")
build("gnambs_2018_rses10", "Gnambs18", "cor",
      "Gnambs, T., Scharl, A., & Schroeders, U. (2018). The structure of the Rosenberg Self-Esteem Scale: A cross-cultural meta-analysis. Zeitschrift fur Psychologie, 226(1), 14-29. https://doi.org/10.1027/2151-2604/a000317",
      "", pop = paste(x$Country, x$Language, sep = "; "), keep = x$CorMat == 1,
      notes = "item correlations of the 10 Rosenberg Self-Esteem items; only the 36 studies whose matrix was reported (CorMat = 1); the 77 reproduced from factor loadings are left out")

x <- msem("issp89")
build("issp_1989_workorient9", "issp89", "cov",
      "International Social Survey Programme (1989). Work Orientations. Inter-University Consortium for Political and Social Research.",
      "nine variables selected by Cheung & Chan (2005, Psychological Methods 10, 40-64)", pop = names(x$data),
      notes = "per-country covariance matrices computed by Cheung & Chan from the ISSP microdata")

x <- msem("issp05")
build("issp_2005_workorient7", "issp05", "cov",
      "ISSP Research Group (2007). International Social Survey Programme 2005: Work Orientation III (ISSP 2005). GESIS Data Archive, ZA4350. https://doi.org/10.4232/1.4350",
      "seven variables selected by Cheung (metaSEM)", pop = names(x$data), means = x$means,
      notes = "per-country covariance matrices and means computed by Cheung from the ISSP microdata")

x <- msem("wvs94b")
build("wvs_1994_jobsat3", "wvs94b", "cov",
      "World Values Study Group (1994). World Values Survey, 1981-1984 and 1990-1993. Inter-university Consortium for Political and Social Research.",
      "as analysed by Au & Cheung (2004), Organization Studies 25, 1339-1362", pop = names(x$data),
      notes = "per-country covariance matrices of life satisfaction, job satisfaction and job autonomy, 1990-1993 wave, computed from the WVS microdata")

x <- msem("Mathieu15")
build("mathieu_2015_cohesion4", "Mathieu15", "cor",
      "Mathieu, J. E., Kukenberger, M. R., D'Innocenzo, L., & Reilly, G. (2015). Modeling reciprocal team cohesion-performance relationships, as impacted by shared leadership and members' competence. Journal of Applied Psychology, 100(3), 713-734. https://doi.org/10.1037/a0038898",
      "Table 1", pop = as.character(x$Sample), notes = "panel studies: cohesion (C) and performance (P) at two waves")

nohe <- "Nohe, C., Meier, L. L., Sonntag, K., & Michel, A. (2015). The chicken or the egg? A meta-analysis of panel studies of the relationship between work-family conflict and strain. Journal of Applied Psychology, 100(2), 522-536. https://doi.org/10.1037/a0038012"
x <- msem("Nohe15A1")
stopifnot(identical(names(x)[3:6], c("RelW1", "RelW2", "RelS1", "RelS2")))
build("nohe_2015_wfcstrain4", "Nohe15A1", "cor", nohe, "Table A1",
      rel = data.frame(W1 = x[[3]], W2 = x[[4]], S1 = x[[5]], S2 = x[[6]]),
      notes = "panel studies: work-to-family conflict (W) and strain (S) at two waves")
x <- msem("Nohe15A2")
stopifnot(identical(names(x)[3:4], c("RelF1", "RelF2")))
build("nohe_2015_fwcstrain4", "Nohe15A2", "cor", nohe, "Table A2",
      rel = data.frame(F1 = x[[3]], F2 = x[[4]]),  # both strain fields are named RelS2: not used
      notes = "panel studies: family-to-work conflict (F) and strain (S) at two waves")

x <- msem("Norton13")
build("norton_2013_hads14", "Norton13", "cor",
      "Norton, S., Cosco, T., Doyle, F., Done, J., & Sacker, A. (2013). The Hospital Anxiety and Depression Scale: A meta confirmatory factor analysis. Journal of Psychosomatic Research, 74(1), 74-81. https://doi.org/10.1016/j.jpsychores.2012.10.010",
      "", pop = as.character(x$population), notes = "item correlations of the 14 HADS items (x1-x14)")

## --- corpora with unmeasured variables (dropped per study, see build()) ----
build("craft_2003_csai4", "Becker09", "cor",
      "Craft, L. L., Magyar, T. M., Becker, B. J., & Feltz, D. L. (2003). The relationship between the Competitive State Anxiety Inventory-2 and sport performance: A meta-analysis. Journal of Sport and Exercise Psychology, 25(1), 44-65.",
      "metaSEM Becker09 (a subset was used in Becker, 2009)", pop = as.character(msem("Becker09")$Type_of_sport),
      notes = "CSAI-2 subscales and sport performance")
x <- msem("Boer16")
build("boer_2016_lmx", "Boer16", "cor",
      "Boer, D., Deinert, A., Homan, A. C., & Voelpel, S. C. (2016). Revisiting the mediating role of leader-member exchange in transformational leadership: The differential impact model. European Journal of Work and Organizational Psychology, 25(6), 883-899.",
      "", rel = data.frame(LMX = x$RelLMX, TFL = x$RelTFL), notes = "leader-member exchange and transformational leadership")
build("cheung_2000_tpb", "Cheung00", "cor",
      "Cheung, S.-F., & Chan, D. K.-S. (2000). The role of perceived behavioral control in predicting human behavior: A meta-analytic review of studies on the theory of planned behavior. Unpublished manuscript, Chinese University of Hong Kong.",
      "", notes = "theory of planned behaviour")
build("cooke_2016_tpbalcohol", "Cooke16", "cor",
      "Cooke, R., Dahdah, M., Norman, P., & French, D. P. (2016). How well does the theory of planned behaviour predict alcohol consumption? A systematic review and meta-analysis. Health Psychology Review, 10(2), 148-167.",
      "", notes = "theory of planned behaviour and alcohol consumption")
build("hunter_1983_jobperf4", "Hunter83", "cor",
      "Hunter, J. E. (1983). A causal analysis of cognitive ability, job knowledge, job performance, and supervisor ratings. In F. Landy, S. Zedeck, & J. Cleveland (Eds.), Performance measurement and theory (pp. 257-266). Erlbaum.",
      "", notes = "cognitive ability, job knowledge, work-sample performance and supervisor ratings")
build("roorda_2011_engagement", "Roorda11", "cor",
      "Roorda, D. L., Koomen, H. M. Y., Spilt, J. L., & Oort, F. J. (2011). The influence of affective teacher-student relationships on students' school engagement and achievement: A meta-analytic approach. Review of Educational Research, 81(4), 493-529.",
      "", notes = "teacher-student relationships, engagement and achievement")
build("scalco_2017_tpborganic", "Scalco17", "cor",
      "Scalco, A., Noventa, S., Sartori, R., & Ceschi, A. (2017). Predicting organic food consumption: A meta-analytic structural equation model based on the theory of planned behavior. Appetite, 112, 235-248.",
      "", notes = "theory of planned behaviour and organic food consumption")

if (length(skipped)) utils::write.csv(do.call(rbind, skipped), file.path(out, "skipped_studies.csv"), row.names = FALSE)
utils::write.csv(do.call(rbind, rec), file.path(out, "matrices.csv"), row.names = FALSE, na = "")
cat("wrote", length(unique(sapply(rec, `[[`, "table"))), "tables,", length(rec), "matrices to", out, "\n")
