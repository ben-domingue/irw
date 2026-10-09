##Expert factorial survey on future MENA-Europe migration (QuantMig) from
##Boissonneault, M., & Costa, R. (2022). QuantMig survey on the future of migration between Europe and
##the Middle East & North Africa [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7404130
##Study: Boissonneault, M., Costa, R., & de Valk, H. A. G. (2022). The future of migration between Europe
##and the Middle East & North Africa under scenarios of social change: A factorial survey among European
##migration professionals. QuantMig Project Deliverable D7.2. NIDI-KNAW/University of Groningen.
##Licence: CC BY 4.0 (Zenodo record). Files read: QMsurvey_respondentvignette.xlsx,
##QMsurvey_respondent.xlsx. Read as documentation: Deliverable D7.3 (guide to the databases, the
##codebook) and D7.2 (design), both PDFs on quantmig.eu.
##Usage: Rscript boissonneault_2022.R <dir holding the two xlsx files> <output dir>
##
##138 European migration professionals (academia, government, civil society), web survey in English,
##Nov 2021 - Jan 2022. Each evaluated 4 text vignettes (task = `rank`, the order of presentation;
##profile = 1). Seven binary factors, full 2^7 = 128-vignette universe split by AlgDesign::optBlock into
##questionnaire versions of 4 vignettes (fixed blocked design; trial_block = the optBlock block number,
##1-64, presumably 32 versions x 2 factor orders); versions assigned round-robin (D7.2 sec. 2.4, 2.6).
##Attribute text = the statement exactly as it appears in the `vignette` text (e.g. "People have become
##more favorable to immigration."), matched to the authors' 0/1 factor codes (D7.3 gives the statement
##for each code; the script checks every vignette). Exception: the `stable` code runs the other way
##from D7.3 (in the data 1 = "Countries have become less politically stable."; consistent with the
##paper's "More pol. instability" term); the text, not the code, is stored. Factor order: one of two fixed orders per
##questionnaire version (Europe first / MENA first, under the headers "In Europe," and "In the Middle
##East & North Africa,"); attrpos_* = position of the statement among the 7 in the displayed text.
##Outcomes (D7.3 wording; "[the situation described by the vignette]" as in the codebook):
##  rating_family / rating_work / rating_refugees / rating_return: "Based on [the situation described by
##  the vignette], compared to 2019, the number of family [work / refugee: refugees / return] migrants from
##  the Middle East & North Africa to Europe will be in 2030..." answered on a number line: Divided by 5,
##  3, 2, 1 1/2, 1 1/4, No change, Multiplied by 1 1/4, 1 1/2, 2, 3, 5. Stored as in the file, the
##  multiplication factor: 0.2, 0.333..., 0.5, 0.666..., 0.8, 1 (= No change; the D7.3 table prints 0,
##  the data hold 1), 1.25, 1.5, 2, 3, 5.
##  rating_compact: "Based on [the situation described by the vignette], compared to 2019, do you believe
##  that it will be more or less difficult to achieve by the year 2030 safe, orderly and regular
##  migration?" -3 Much more difficult ... 0 Neither more or less difficult ... 3 Much less difficult.
##Covariates (respondent file, codebook D7.3, answer text as stored): cov_think, cov_familiarity,
##cov_education (edu), cov_sector, cov_years_exp, and the no-change anchoring answers cov_mig_nochange
##(multiplication factor, same coding), cov_certain (% confident), cov_compact_nochange (-3 Very difficult
##... 3 Very easy). Dropped: comment and sector_other (free text), flag (derived).
##Check: the mean of cov_mig_nochange over respondents is 1.52 (D7.2 Table 2: 1.52, SD 0.48); a random-
##intercept model of ln(rating_family) on the 7 factors reproduces D7.2 Table 3 (Family) to 3 decimals
##(young .123, fundamentalism .054, instability .137, unemployment .120, aging .006, attitude .114, policy .146).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
v <- as.data.table(read_excel(file.path(raw, "QMsurvey_respondentvignette.xlsx")))
r <- as.data.table(read_excel(file.path(raw, "QMsurvey_respondent.xlsx")))
stopifnot(nrow(v) == 552, uniqueN(v$id) == 138, nrow(r) == 138, v[, .N, id][, all(N == 4)])
f <- c("young", "old", "fundament", "favourable", "stable", "policies", "employment")
pat <- list(young = c("decreased as women", "increased as women"), old = c("has slowed down", "has accelerated"),
            fundament = c("has lost ground", "has gained ground"), favourable = c("less favo", "more favo"),
            stable = c("less politically stable", "more politically stable"),
            policies = c("more restrictive", "less restrictive"), employment = c("similar levels", "much higher levels"))
key <- c(young = "proportion of young", old = "proportion of older", fundament = "fundamentalism",
         favourable = "favo[u]?rable to immigration", stable = "politically stable", policies = "Immigration policies",
         employment = "Unemployment rates")
lines <- lapply(strsplit(v$vignette, "\r?\n"), function(x) trimws(x[trimws(x) != ""]))
st <- lapply(lines, function(x) x[!x %in% c("During the period 2021-2030,", "In Europe,", "In the Middle East & North Africa,")])
stopifnot(all(lengths(st) == 7))
d <- data.table(id = as.integer(v$id), task = as.integer(v$rank), profile = 1L,
                rating_family = v$family, rating_work = v$work, rating_refugees = v$refugees, rating_return = v$return,
                rating_compact = as.integer(v$compact))
for (x in f) {
  pos <- vapply(st, function(s) { p <- grep(key[[x]], s); stopifnot(length(p) == 1); p }, 1L)
  txt <- mapply(function(s, p) s[p], st, pos)
  code <- v[[x]]
  stopifnot(all(code %in% 0:1), all(mapply(function(t) sum(vapply(pat[[x]], grepl, TRUE, t, fixed = TRUE)) == 1, txt)))
  ok <- mapply(function(t, c) grepl(pat[[x]][c + 1], t, fixed = TRUE), txt, code)
  ## `stable` is coded the other way round from D7.3 (1 = LESS stable in the data; the paper's Table 3
  ## term is "More pol. instability"); every other factor matches the codebook
  if (x == "stable") stopifnot(!any(ok)) else stopifnot(all(ok))
  d[, paste0("attr_", x) := txt]
  d[, paste0("attrpos_", x) := pos]
}
d[, trial_block := as.integer(v$block)]
stopifnot(all(d$rating_compact %in% -3:3), all(round(c(d$rating_family, d$rating_work, d$rating_refugees, d$rating_return), 3) %in%
          c(0.2, 0.333, 0.5, 0.667, 0.8, 1, 1.25, 1.5, 2, 3, 5)))
cv <- r[, .(id = as.integer(id), cov_think = think, cov_familiarity = fam, cov_education = edu, cov_sector = sector,
            cov_years_exp = as.integer(years_exp), cov_mig_nochange = mig_nochange, cov_certain = as.integer(certain),
            cov_compact_nochange = as.integer(compact_nochange))]
stopifnot(abs(mean(cv$cov_mig_nochange) - 1.52) < 0.005)
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "boissonneault_2022_migration_experts.csv"))
