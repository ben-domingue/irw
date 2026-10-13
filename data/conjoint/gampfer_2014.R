##North-South climate funding conjoint (United States and Germany) from
##Gampfer, R., Bernauer, T., & Kachi, A. (2014). Obtaining public support for North-South climate
##funding: Evidence from conjoint experiments in donor countries. Global Environmental Change, 29,
##118-126. https://doi.org/10.1016/j.gloenvcha.2014.08.006
##Replication data: Zenodo doi:10.5281/zenodo.17969439 (concept DOI; also 10.5281/zenodo.17969440),
##CC BY 4.0. Files read: compens_source_US.dta, compens_source_DE.dta (YouGov source files, one row per
##respondent, Stata value labels), plus Codebook compens_source_US.pdf / _DE.pdf (variable list,
##sampling and weighting notes). NOT read: Compensation_*_Clean/Final.dta.zip (analysis files, 18,000
##rows) and the MTurk files (Compensation_MTurk_Raw.xls, _Clean.dta.zip: a separate MTurk sample that
##the codebooks do not describe; left out).
##Usage: Rscript gampfer_2014.R <dir holding the two .dta files> <output dir>
##Writes TWO tables, one per sample, because the attribute text differs (English with US dollars
##versus German with euros) and the authors fielded two separate YouGov surveys:
##  gampfer_2014_climate_funding_us  1,500 US adults, YouGov, 16-21 Oct 2013 (matched sample, weighted)
##  gampfer_2014_climate_funding_de  1,500 German residents, YouGov, 29 Oct-2 Nov 2013 (matched, raked)
##Design: each respondent saw 6 tasks (the deposit's "Table 1".."Table 6"), each a pair of funding
##"Proposal 1" / "Proposal 2" (German "Vorschlag 1/2") described by 7 attributes: damage in the
##recipient countries, income of recipient countries relative to the home country, their carbon
##emissions relative to the home country, efficiency of fund use, who takes funding decisions,
##what the funds are used for, and the home country's contribution versus other countries. Task and
##profile are recorded (damage<t>a/b etc.: a = Proposal 1, b = Proposal 2; conjoint<t> = chosen
##proposal). Forced choice: every task has exactly one chosen proposal (1/2), no opt-out.
##Outcome: choice = 1 for the proposal picked in conjoint<t>. The deposit holds only the variable
##label "Conjoint Experiment - Table t" and the value labels Proposal 1 / Proposal 2; the question
##wording is NOT in the deposit (design_outcomes gives a paraphrase).
##Attribute text comes from the Stata value labels of the *_code variables (codes 1-4/5 -> label),
##which are the displayed level texts. Caveat: Stata truncates value labels at 80 characters; one
##level is cut: funduse level 3 ("... and protect recipient coun" / "... und sie vor Schaeden durch
##den Klim"). It is completed here as the conjunction of the two other levels' wording (US: "...and
##protect recipient countries against global warming damages"; DE: "...und sie vor Schaeden durch den
##Klimawandel schuetzen"): an INFERRED completion. In the German contribution labels the euro sign
##is read as "?" by haven; the codebook PDF shows it (euro), which is restored.
##Randomization restrictions, attribute order and level probabilities are not documented in the
##deposit; no attribute combination is missing (checked).
##Covariates: cov_survey_weight (YouGov case weight, US 0.21-7.04, DE 0.17-7.43; normalised to the
##sample size), cov_gender (value labels Male/Female, maenlich/weiblich -> male/female), cov_birth_year
##(birthyr / birthyear), cov_education (US educ, DE educ: answer text as labelled; DE "Keine Angabe" -> NA),
##cov_party_id (US only, pid3 text). Dropped: all other survey items, free-text verbatims, region,
##postcode (DE), urban, state (US), start/end times.
##Respondents 1,500 per sample = the paper's samples (matched down from 1,559 / 1,651 interviews).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) { l <- attr(x, "labels"); l <- l[l < 8 | l > 9999 | TRUE]; setNames(trimws(gsub("\r", "", names(l))), l) }
atts <- c(damage = "damage", income = "income", carbon = "carbon", efficiency = "efficiency",
          funddec = "funding_decisions", funduse = "funding_use", contribut = "contribution")
build <- function(f, name, fix) {
  s <- as.data.table(read_dta(file.path(raw, f)))
  stopifnot(nrow(s) == 1500, uniqueN(s$caseid) == 1500)
  L <- list()
  for (t in 1:6) for (p in 1:2) {
    sfx <- c("a", "b")[p]
    r <- data.table(id = as.integer(factor(s$caseid)), task = t, profile = p)
    for (v in names(atts)) {
      x <- s[[paste0(v, t, sfx, "_code")]]; m <- lab(x)
      txt <- m[as.character(as.integer(x))]; txt <- fix(v, txt)
      stopifnot(!anyNA(txt))
      r[[paste0("attr_", atts[[v]])]] <- unname(txt)
    }
    ch <- as.integer(s[[paste0("conjoint", t)]]); stopifnot(all(ch %in% 1:2))
    r$choice <- as.integer(ch == p)
    L[[length(L) + 1]] <- r
  }
  d <- rbindlist(L)
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d))
  cv <- data.table(id = as.integer(factor(s$caseid)), cov_survey_weight = as.numeric(s$weight))
  g <- lab(s$gender); cv[, cov_gender := unname(c(Male = "male", Female = "female", "männlich" = "male", weiblich = "female")[g[as.character(as.integer(s$gender))]])]
  cv[, cov_birth_year := as.integer(if (!is.null(s$birthyr)) s$birthyr else s$birthyear)]
  e <- lab(s$educ); cv[, cov_education := unname(e[as.character(as.integer(s$educ))])]
  cv[cov_education %in% "Keine Angabe", cov_education := NA]
  if (!is.null(s$pid3)) { pp <- lab(s$pid3); cv[, cov_party_id := unname(pp[as.character(as.integer(s$pid3))])] }
  d <- merge(d, cv, by = "id"); setcolorder(d, c("id", "task", "profile", "choice"))
  setorder(d, id, task, profile); fwrite(d, file.path(out, paste0(name, ".csv"))); d
}
fix_us <- function(v, txt) if (v == "funduse") sub("recipient coun$", "recipient countries against global warming damages", txt) else txt
fix_de <- function(v, txt) {
  if (v == "funduse") txt <- sub("durch den Klim$", "durch den Klimawandel schützen", txt)
  if (v == "contribut") txt <- gsub("?", "€", txt, fixed = TRUE)
  txt }
invisible(build("compens_source_US.dta", "gampfer_2014_climate_funding_us", fix_us))
invisible(build("compens_source_DE.dta", "gampfer_2014_climate_funding_de", fix_de))
