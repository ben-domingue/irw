##Next-door-neighbour conjoints in five countries (TRI-POL panel, wave 3) from
##Torcal, M., Comellas, J. M., & Vrânceanu, A. (2026). Social distance as a product of
##political identities: Evidence from a conjoint experiment in five countries. Political
##Science Research and Methods (forthcoming; no DOI found on 2026-10-07).
##Replication data: Harvard Dataverse doi:10.7910/DVN/WAYIQJ, CC0 1.0, no restricted files.
##Files read: TRI_POL_AR_V1.dta, TRI_POL_CH_V1.dta, TRI_POL_ES_V1.dta, TRI_POL_IT_V1.dta,
##TRI_POL_PT_V1.dta (Dataverse "original format"; the TRI-POL panel files, Stata value
##labels). Design and wording from the wave-3 English master questionnaires on OSF
##(osf.io/3t7jz, "Survey panel-Questionnaires/<country>/Questionnaire_<country>_Wave3.pdf");
##the authors' "0. Reshape.do" read as text. Panel data documented in Torcal et al. (2023),
##Data in Brief 48, 109219.
##Usage: Rscript torcal_2026.R <raw dir> <output dir>
##
##FIVE TABLES, one per country: the attribute sets differ by country (country-specific
##regional identity, parties and religions; a language attribute only in Spain, a vaccination
##attribute only in Italy) and the paper analyses each country separately.
##  torcal_2026_neighbours_argentina, _chile, _spain, _italy, _portugal
##Online panel respondents (TRI-POL wave 3). Each saw 12 pairs of hypothetical families
##"moving next door" (Neighbour A = profile 1, Neighbour B = profile 2) described by 10 (AR,
##CH, PT) or 11 (ES, IT) attributes, and answered:
##  choice = "Many people are able to select the neighbourhood where they prefer to live, but
##           we do not have the option to choose our next door neighbours. If you could choose
##           the basic characteristics of the family unit moving next door to you... Which
##           profile would you prefer to have as your next-door neighbour?" Neighbour A / B,
##           forced, no opt-out. Respondents saw it in Spanish, Italian or Portuguese; the
##           English master questionnaire is the source of this wording.
##Level text = the panel files' Stata value labels (English), e.g. "Left", "Born outside
##Spain", "Man-and-man", "PSOE"/"pp". Respondents saw fuller, translated phrasings (the
##questionnaire's example: "Left-wing", "Born outside Spain", "A man-and-man family unit",
##"PSOE supporter", "Non-pet owner (dog, cat...)").
##RESTRICTIONS (questionnaire design tables): non-uniform weights (born in country 4:3 vs
##outside 4:1; man-and-woman 1:2 vs same-sex couples 1:4 each; Italy anti-vax 6:1), and
##party levels tied to ideology (Spain/Chile/Portugal/Italy: each ideology only with listed
##parties; Argentina: listed "no combine with left/right" rules; Spain: ERC, JxC, PNV, Bildu
##only with "Nationalist"). Attribute ORDER was randomized once per respondent and kept
##fixed, but is not in the data.
##Kept: every respondent with at least one answered task (tasks with no answer dropped).
##cov_in_authors_sample = 0 for respondents the authors drop ("I do not have the right to
##vote" on the wave-1 party question p37_<cc>_1 == 22, per "0. Reshape.do"); with it the
##respondent counts match the authors' Conjoint_<country>.dta exactly (AR 975, CH 916,
##ES 1,071, IT 986, PT 821). The TRI-POL files carry no respondent id column; id = row
##order in the panel file. No other covariates are kept (the authors' in-group and
##attrition-weight variables are derived).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ctry <- c(argentina = "AR", chile = "CH", spain = "ES", italy = "IT", portugal = "PT")
sfx <- c(AR = "AR_3", CH = "CH_3", ES = "ES_3", IT = "IT_3", PT = "PO_3")
anames <- c(a = "territory", b = "ideology", c = "birthplace", e = "sexual_orientation", f = "party",
            g = "education", h = "environmentalism", i = "pet", j = "religion", k = "politicisation")
for (nm in names(ctry)) {
  cc <- ctry[[nm]]; s <- sfx[[cc]]
  x <- read_dta(file.path(raw, sprintf("TRI_POL_%s_V1.dta", cc)))
  an <- anames
  if (cc == "ES") an <- c(an, d = "language")
  if (cc == "IT") an <- c(an, d = "vaccination")
  ia <- as.numeric(zap_missing(x[[sprintf("p37_%s_1", sub("_3", "", s))]]))
  lab <- function(v) {
    l <- attr(v, "labels"); l <- l[!is.na(l) & l < 800]
    z <- as.numeric(zap_missing(v)); z[!is.na(z) & z >= 800] <- NA
    r <- names(l)[match(z, l)]; stopifnot(all(is.na(z) | !is.na(r))); r
  }
  d <- rbindlist(lapply(1:12, function(t) rbindlist(lapply(1:2, function(p) {
    ch <- as.numeric(zap_missing(x[[sprintf("esmP12_%d_%s", t, s)]])); ch[!is.na(ch) & ch > 2] <- NA
    y <- data.table(id = seq_len(nrow(x)), task = t, profile = p, choice = as.integer(ch == p))
    y[, cov_in_authors_sample := as.integer(is.na(ia) | ia != 22)]
    for (k in names(an)) y[, paste0("attr_", an[[k]]) := lab(x[[sprintf("esmP12%s_%d_%s_%s", k, t, c("A", "B")[p], s)]])]
    y
  }))))
  d <- d[!is.na(choice)]
  ac <- grep("^attr_", names(d), value = TRUE)
  stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 2)],
            !anyNA(d[, ..ac]))
  setorder(d, id, task, profile)
  d[, id := match(id, unique(id))]
  setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", sort(unname(an))), "cov_in_authors_sample"))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("torcal_2026_neighbours_", nm, ".csv")))
}
