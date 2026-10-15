##Offshore wind farms vs marine protected areas choice experiment (Estonia) from
##Karlosheva (Karlõševa), A., Nõmmann, S., Nõmmann, T., Urbel-Piirsalu, E., Budziński, W., Czajkowski, M., & Hanley, N.
##(2016). Marine trade-offs: Comparing the benefits of off-shore wind farms and marine protected areas. Energy
##Economics, 55, 127-134. https://doi.org/10.1016/j.eneco.2015.12.022
##(Citation checked on Crossref; the article itself was not read.)
##Data: Mendeley Data doi:10.17632/j4zwwz8gh7.1, CC BY-NC 3.0 (Mendeley public API, data_licence). File read:
##data_EE1_01.mat (MATLAB 5 file with 100+ column vectors of length 28,800 = 800 respondents x 12 choice sets x 3
##alternatives; read here with a small binary reader, no MATLAB). The authors' script EE1_final_end.m was read as text
##(not run): it defines the attributes (DATA.SQ = alt == 1, AS = Apollo Shoal level 1-3 with names MPA / WP / EWP,
##WS = Western Shoals level, cost c, outcome ans1, 800 respondents, 12 tasks, 3 alternatives) and titles its WTP plots
##"Marine Protected Area / Wind Farm / 'Eco' Wind Farm on Apollo Shoal" and "... on Western Shoals".
##Usage: Rscript karlosheva_2016.R <dir holding data_EE1_01.mat> <output dir>
##
##800 Estonian respondents (online survey, 2013-2014). Each of 12 choice sets: the status quo (alt 1, all attributes 0,
##cost 0) and two alternatives (alt 2, 3), each describing what happens on two shoals (Apollo Shoal, Western Shoals):
##nothing (0), a marine protected area (1), a wind farm (2) or an 'eco' wind farm (3) on each, plus an annual cost
##(2, 5, 10, 20 for the alternatives). The status quo is a profile with levels ("No change" on both shoals, cost 0);
##there is no opt-out; exactly one alternative chosen per set (checked). The "No change" wording for code 0 is my
##inference (alternatives 2 and 3 also take 0 on a shoal), not the questionnaire's.
##LABELS: level text from the authors' script plot titles, not the questionnaire; the cost unit is EUR per year per
##household (script plot labels "WTP (EUR per year per household)"; cost enters the model as -c/10).
##Design: the design version differs across respondents (variable etap 1/2/3: 100/200/500 respondents), each with its
##own 12 x 2 alternatives: trial_design_version. Restrictions: none documented; level weights unknown.
##Attribute order fixed (assumed). task = cs3 1-12 (assumed order shown), profile = alt 1-3 (alt 1 = status quo).
##Covariates kept: cov_birth_year (q18), cov_gender_code (q19, 1/2, no codebook). Dropped: all other survey answers
##(q1-q27), keel, cdx.
##N vs paper: 800 respondents as in the script; the article's N not seen.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(path) {
  buf <- readBin(path, "raw", file.size(path)); pos <- 129L; res <- list()
  u32 <- function(b, p) sum(as.numeric(b[p:(p + 3)]) * c(1, 256, 65536, 16777216))
  while (pos < length(buf)) {
    t <- u32(buf, pos); n <- u32(buf, pos + 4L)
    if (t != 15L) break
    z <- memDecompress(buf[(pos + 8L):(pos + 7L + n)], "gzip", asChar = FALSE); pos <- pos + 8L + n
    rdel <- function(b, p) { tt <- u32(b, p)
      if (tt >= 65536) { nn <- tt %/% 65536; tt <- tt %% 65536; list(tt, b[(p + 4):(p + 3 + nn)], p + 8L) }
      else { nn <- u32(b, p + 4L); list(tt, b[(p + 8):(p + 7 + nn)], p + 8L + nn + (8L - nn %% 8L) %% 8L) } }
    e <- rdel(z, 1L); stopifnot(e[[1]] == 14L); b <- e[[2]]; p <- 1L
    fl <- rdel(b, p); p <- fl[[3]]; dm <- rdel(b, p); p <- dm[[3]]; nm <- rdel(b, p); p <- nm[[3]]; dt <- rdel(b, p)
    d <- readBin(dm[[2]], "integer", length(dm[[2]]) / 4, 4, endian = "little")
    sz <- c(1, 1, 2, 2, 4, 4, NA, NA, 8)[dt[[1]]]
    if (dt[[1]] %in% c(1L, 2L, 3L, 4L, 5L, 6L, 9L)) {
      k <- length(dt[[2]]) / sz; v <- dt[[2]]
      res[[rawToChar(nm[[2]])]] <- switch(as.character(dt[[1]]),
        "1" = readBin(v, "integer", k, 1, signed = TRUE), "2" = readBin(v, "integer", k, 1, signed = FALSE),
        "3" = readBin(v, "integer", k, 2, endian = "little"), "4" = readBin(v, "integer", k, 2, signed = FALSE, endian = "little"),
        "5" = readBin(v, "integer", k, 4, endian = "little"), "6" = { z4 <- readBin(v, "integer", k, 4, endian = "little"); ifelse(z4 < 0, z4 + 4294967296, z4) },
        "9" = readBin(v, "double", k, 8, endian = "little")) }
  }
  res
}
m <- rd(file.path(raw, "data_EE1_01.mat"))
stopifnot(all(c("id","cs3","alt","as","ws","c","ans1","etap","q18","q19") %in% names(m)))
x <- as.data.table(m[c("id","cs3","alt","as","ws","c","ans1","etap","q18","q19")])
stopifnot(nrow(x) == 28800, uniqueN(x$id) == 800, x[, .N, id][, all(N == 36)], x[, sum(ans1), .(id, cs3)][, all(V1 == 1)],
  x[alt == 1, all(as == 0 & ws == 0 & c == 0)], x[, uniqueN(etap), id][, all(V1 == 1)])
x[, rid := match(id, sort(unique(id)))]
lv <- c("No change", "Marine Protected Area", "Wind farm", "'Eco' wind farm")
d <- x[, .(id = rid, task = as.integer(cs3), profile = as.integer(alt), choice = as.integer(ans1),
  attr_apollo_shoal = lv[as + 1L], attr_western_shoals = lv[ws + 1L], attr_cost = paste0("EUR ", as.integer(c), " per year"),
  cov_birth_year = ifelse(q18 >= 1900 & q18 <= 2005, as.integer(q18), NA_integer_), cov_gender_code = as.integer(q19),
  trial_design_version = as.integer(etap))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^task$|^profile$")]), d[, .N, .(id, task)][, all(N == 3)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "karlosheva_2016_offshore_wind_mpa.csv"))
