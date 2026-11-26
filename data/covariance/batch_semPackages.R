## Covariance family (irw_cov, source = "cov"): published matrices shipped with
## SEM-oriented CRAN packages (#3582).
##
## Sources (read from pinned CRAN source tarballs; nothing is installed and no
## downloaded code is run):
##   - umx 4.80.1 (GPL-3): data/Fischbein_wt.rda, Fischbein (1977), weight of
##     66 females at six occasions. The help page prints the typed lower
##     triangle; the stored object equals it exactly (checked below), so the
##     ensurePD = TRUE in its recipe did not alter any value.
##   - OpenMx 2.22.11 (Apache License 2.0): inst/models/passing/maes1998.R, a
##     test model transcribing Tables 2 and 3 of Maes et al. (1998) for two
##     samples (ABD, N = 854; AFT, N = 568). The .R file is parsed as TEXT with
##     regular expressions; it is never sourced.
##   - BGGM 2.2.0 (GPL-2): data/ptsd_cor1.rda ... ptsd_cor4.rda, the 16-symptom
##     PTSD correlation matrices that Fried et al. (2018) released for their four
##     patient samples (N = 526, 365, 926, 965, from the help pages). Variables
##     are X1-X16 in the package; they are renamed to the symptom labels in the
##     order the help pages list them. Values are unchanged.
##
## Modification (2026-11-17): reshaped to the long lower-triangle layout in
## data/covariance/README.md. No value is changed.
##
## Usage:  Rscript data/covariance/batch_semPackages.R <out dir>

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript batch_semPackages.R <out dir>")
out <- args[1]
dir.create(out, showWarnings = FALSE, recursive = TRUE)

cache <- file.path(tempdir(), "cov_tarballs")
dir.create(cache, showWarnings = FALSE)
tarball <- function(pkg, version) {
  dest <- file.path(cache, paste0(pkg, "_", version, ".tar.gz"))
  if (!file.exists(dest)) {
    ok <- FALSE
    for (u in c(sprintf("https://cloud.r-project.org/src/contrib/%s_%s.tar.gz", pkg, version),
                sprintf("https://cloud.r-project.org/src/contrib/Archive/%s/%s_%s.tar.gz", pkg, pkg, version)))
      if (system2("curl", c("-4", "-sfL", "-m", "600", "-o", shQuote(dest), shQuote(u))) == 0) { ok <- TRUE; break }
    if (!ok) stop("could not download ", pkg, " ", version)
  }
  dest
}
member <- function(pkg, version, path) {
  exdir <- file.path(cache, paste0(pkg, "_", version))
  utils::untar(tarball(pkg, version), files = file.path(pkg, path), exdir = exdir)
  file.path(exdir, pkg, path)
}
from_tarball <- function(pkg, version, file, object) {
  e <- new.env(); load(member(pkg, version, file.path("data", file)), envir = e); get(object, envir = e)
}

## shortest string that reads back as exactly the same double
exact <- function(x) {
  s <- formatC(x, digits = 15, format = "g")
  redo <- as.numeric(s) != x
  s[redo] <- formatC(x[redo], digits = 17, format = "g")
  trimws(s)
}

to_long <- function(m, stat, n, group = NA_character_) {
  m <- as.matrix(m)
  v <- colnames(m)
  if (is.null(v) || anyDuplicated(v)) stop("matrix needs unique column names")
  if (anyNA(m)) stop("blank cell")
  if (!isTRUE(all.equal(unname(m), unname(t(m)), tolerance = 0))) stop("matrix is not symmetric")
  off <- m[lower.tri(m)]
  if (any(abs(off) >= 1)) stop("off-diagonal correlation of |r| >= 1")
  idx <- which(lower.tri(m, diag = TRUE), arr.ind = TRUE)
  idx <- idx[order(idx[, "row"], idx[, "col"]), , drop = FALSE]
  data.frame(stat = stat, var1 = v[idx[, "row"]], var2 = v[idx[, "col"]],
             value = m[idx], n = as.integer(n), group = group, stringsAsFactors = FALSE)
}
write_table <- function(df, table) {
  if (all(is.na(df$group))) df$group <- NULL
  df$value <- exact(df$value)
  utils::write.csv(df, file.path(out, paste0(table, ".csv")), row.names = FALSE, na = "")
}

rec <- list()
add <- function(table, group, n, population, citation, location, via, licence, licence_source, notes) {
  rec[[length(rec) + 1]] <<- data.frame(
    table = table, group = group, n_obs = n, matrix_type = "unknown", missing = "unknown",
    population = population, source_citation = citation, source_location = location,
    via = via, capture = "package transcription", verified = "no",
    licence = licence, licence_source = licence_source, notes = notes)
}

## --- umx::Fischbein_wt ------------------------------------------------------
fw <- as.matrix(from_tarball("umx", "4.80.1", "Fischbein_wt.rda", "Fischbein_wt"))
## the lower triangle as printed in man/Fischbein_wt.Rd
typed <- c(1.000,
           0.985, 1.000,
           0.968, 0.981, 1.000,
           0.957, 0.970, 0.985, 1.000,
           0.932, 0.940, 0.964, 0.975, 1.000,
           0.890, 0.897, 0.927, 0.949, 0.973, 1.000)
tm <- matrix(0, 6, 6); tm[upper.tri(tm, diag = TRUE)] <- typed; tm <- t(tm)
tm[upper.tri(tm)] <- t(tm)[upper.tri(tm)]
if (!identical(unname(fw), tm)) stop("umx::Fischbein_wt differs from its help page")
write_table(to_long(fw, "cor", 66), "fischbein_1977_weight6")
add("fischbein_1977_weight6", "", 66, "66 females measured six times at 6-month intervals during puberty (twin growth study)",
    "Fischbein, S. (1977). Intra-pair similarity in physical growth of monozygotic and of dizygotic twins during puberty. Annals of Human Biology, 4(5), 417-430.",
    "", "umx::Fischbein_wt", "GPL-3", "umx",
    "correlations of body weight across six occasions (the help page gives time 6 as t0 + 32 months); N = 66 from the umx help page")

## --- OpenMx test model maes1998.R (Maes et al., 1998, Tables 2 and 3) -------
src <- readLines(member("OpenMx", "2.22.11", "inst/models/passing/maes1998.R"), warn = FALSE)
diagno <- c("ALC", "GAD", "MDD", "PAN", "PHO")
vars <- c(paste0("wife", diagno), paste0("husband", diagno))
parse_sample <- function(obj, tag) {
  m <- matrix(NA_real_, 10, 10, dimnames = list(vars, vars))
  ## within-spouse cells:  obj['a', 'b'] <- .399
  re1 <- sprintf("^%s\\['(\\w+)', '(\\w+)'\\] <- (-?[0-9.]+)\\s*$", obj)
  for (l in grep(re1, src, value = TRUE)) {
    p <- regmatches(l, regexec(re1, l))[[1]]
    if (!is.na(m[p[2], p[3]])) stop("cell set twice")
    m[p[2], p[3]] <- m[p[3], p[2]] <- as.numeric(p[4])
  }
  ## cross-spouse rows:  obj['wifeALC', husband] <- c(.119, ...)
  re2 <- sprintf("^%s\\['(wife\\w+)', husband\\] <- c\\(([-0-9., ]+)\\)\\s*$", obj)
  for (l in grep(re2, src, value = TRUE)) {
    p <- regmatches(l, regexec(re2, l))[[1]]
    v <- as.numeric(strsplit(p[3], ",")[[1]])
    if (length(v) != 5) stop("cross row length")
    h <- paste0("husband", diagno)
    if (any(!is.na(m[p[2], h]))) stop("cell set twice")
    m[p[2], h] <- v; m[h, p[2]] <- v
  }
  diag(m) <- 1
  if (anyNA(m)) stop("unparsed cell in ", tag)
  m
}
## numObs per sample, from the mxData() lines
nobs <- function(obj) {
  l <- grep(sprintf("mxData\\(%s, type = \"cov\", numObs = [0-9]+\\)", obj), src, value = TRUE)
  if (length(l) != 1) stop("numObs not found for ", obj)
  as.integer(sub(".*numObs = ([0-9]+).*", "\\1", l))
}
maes <- list(ABD = parse_sample("c2", "ABD"), AFT = parse_sample("c3", "AFT"))
ns <- c(ABD = nobs("c2"), AFT = nobs("c3"))
stopifnot(ns[["ABD"]] == 854L, ns[["AFT"]] == 568L)
write_table(do.call(rbind, lapply(names(maes), function(g) to_long(maes[[g]], "cor", ns[[g]], g))),
            "maes_1998_assortmating10")
for (g in names(maes))
  add("maes_1998_assortmating10", g, ns[[g]], paste0("husbands and wives, sample ", g),
      "Maes, H. H., Neale, M. C., Kendler, K. S., Hewitt, J. K., Silberg, J. L., Foley, D. L., Meyer, J. M., Rutter, M., Simonoff, E., Pickles, A., & Eaves, L. J. (1998). Assortative mating for major psychiatric diagnoses in two population-based samples. Psychological Medicine, 28(6), 1389-1401.",
      "Table 2 (within-spouse: wives above the diagonal, husbands below) and Table 3 (wife x husband)",
      "OpenMx inst/models/passing/maes1998.R", "Apache License (== 2.0)", "OpenMx",
      paste0("lifetime diagnoses of alcoholism, generalized anxiety, major depression, panic and phobia for both spouses; ",
             "cross-spouse block is not symmetric (wife ALC x husband GAD differs from wife GAD x husband ALC), as published; ",
             "N = ", ns[[g]], " from the numObs of the OpenMx test model (couples); diagnoses are binary, so the correlations are presumably tetrachoric (not checked against the paper)"))

## --- BGGM::ptsd_cor1-4 (Fried et al., 2018) ---------------------------------
sym <- c("intrusive_thoughts", "nightmares", "flashbacks", "reactivity", "avoid_thoughts",
         "avoid_situations", "amnesia", "disinterest", "detached", "numbing",
         "foreshortened_future", "sleep", "irritability", "concentration",
         "hypervigilance", "startle")
fried_n <- c(526L, 365L, 926L, 965L)
fried <- list()
for (i in 1:4) {
  x <- as.matrix(from_tarball("BGGM", "2.2.0", paste0("ptsd_cor", i, ".rda"), paste0("ptsd_cor", i)))
  if (!identical(colnames(x), paste0("X", 1:16))) stop("unexpected BGGM column names")
  dimnames(x) <- list(sym, sym)
  g <- paste0("sample", i)
  fried[[i]] <- to_long(x, "cor", fried_n[i], g)
  add("fried_2018_ptsd16", g, fried_n[i], paste0("trauma patients receiving treatment for PTSD, sample ", i, " of 4"),
      "Fried, E. I., Eidhof, M. B., Palic, S., Costantini, G., Huisman-van Dijk, H. M., Bockting, C. L. H., Engelhard, I., Armour, C., Nielsen, A. B. S., & Karstoft, K.-I. (2018). Replicability and generalizability of posttraumatic stress disorder (PTSD) networks: A cross-cultural multisite study of PTSD symptoms in four trauma patient samples. Clinical Psychological Science, 6(3), 335-351.",
      "correlation matrices the authors released with the paper (values at full precision, so computed by the authors from their raw data, not transcribed from a printed table)",
      paste0("BGGM::ptsd_cor", i), "GPL-2", "BGGM",
      paste0("16 DSM-IV PTSD symptoms; N = ", fried_n[i], " from the BGGM help page; BGGM names the variables X1-X16, renamed here to the symptom labels in the help-page order; ",
             "correlation type (Pearson or polychoric) not stated in BGGM, not checked against the paper"))
}
write_table(do.call(rbind, fried), "fried_2018_ptsd16")

utils::write.csv(do.call(rbind, rec), file.path(out, "matrices.csv"), row.names = FALSE, na = "")
cat("wrote", length(unique(sapply(rec, `[[`, "table"))), "tables,", length(rec), "matrices to", out, "\n")
