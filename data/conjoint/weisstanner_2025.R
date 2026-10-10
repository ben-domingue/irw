##Party-leader conjoint on symbolic class signalling from
##Weisstanner, D., & Engler, S. (2025). The electoral appeal of symbolic class signalling through
##cultural consumption. British Journal of Political Science, 55.
##https://doi.org/10.1017/S0007123425100513
##Replication data: Harvard Dataverse doi:10.7910/DVN/GEG7WJ, CC0 1.0, no restricted files.
##File read: SYMBREP_FINAL.tab (Dataverse original format, Stata 14, saved as symb.dta); the
##deposit's SymbClass_REPLICATION.do was read as text. Attribute text, the vignette template and
##the question wording are from the article's Supplementary Material ("Full question wordings and
##screenshots of the conjoint experiment", English translation and German original) and Table 1.
##Usage: Rscript weisstanner_2025.R <raw dir> <output dir>
##
##1,540 eligible voters in German-speaking Switzerland (Bilendi online panel, quotas on party,
##age, gender, education; fielded 27 January - 20 February 2023; paper: N = 1,550), each a voter of
##one of six parties. "The [PARTY] is preparing for the 2023 election campaign. Please imagine that
##there are new elections for the party leadership ..." [PARTY] = the respondent's party (the party
##voted for in 2019, or the party closest; kept as cov_conjoint_party / cov_conjoint_party_basis).
##5 tasks x 2 candidate profiles ("Candidate 1" / "Candidate 2"), each a bullet list under
##"Kandidat(in) für den PARTY-Vorsitz:". task = source `question`, profile = source `concept`.
##Attributes are stored in the GERMAN text respondents saw (Supplementary Material, German
##original), resolved from its placeholders:
##  attr_gender      Ist ein Mann / Ist eine Frau
##  attr_education   Besitzt einen Universitätsabschluss / Besitzt einen Lehrabschluss
##  attr_econ_position  Positioniert sich in der Wirtschafts- und Sozialpolitik eher am linken
##                   [SVP: gemässigten] / rechten Rand der Partei
##  attr_cult_position  Positioniert sich bei gesellschaftspolitischen Fragen (u.a. Zuwanderung,
##                   Gleichstellung) eher am linken [SVP: gemässigten] / rechten Rand der Partei
##  attr_class_origin   Ist aufgewachsen in wohlhabenden Verhältnissen als [Sohn / Tochter] eines
##                   Anwalts und einer Ärztin / ... in einer Lehrerfamilie als [Sohn / Tochter] eines
##                   Primarlehrers und einer Primarlehrerin / ... in einer Arbeiterfamilie als
##                   [Sohn / Tochter] eines Bauarbeiters und einer Supermarktangestellten
##  attr_cultural_consumption  Hört in der Freizeit gerne klassische Musik bei einem Glas Wein /
##                   Trifft in der Freizeit gerne Freunde / Geht in der Freizeit gerne ein Bier in
##                   der Lieblingsbeiz trinken
##Placeholders resolved here (INFERRED from the template, not from saved display text): "linken"
##is replaced by "gemässigten" when the respondent's party is the SVP, as the template says; Sohn
##is used for a man and Tochter for a woman. Mapping of the source codes (value labels Man/Woman,
##Tertiary/Non-tertiary, Econ./Cult. left/right, Upper/Middle/Working-class origin, Upper-class /
##Neutral / Lower-class cultural consumption) to these texts follows Table 1 and the .do file's
##coefficient labels. Attribute order: fixed as listed in the questionnaire (no source says it was
##randomized). Restrictions: the paper says attributes were "fully randomised except for economic
##and cultural attitudes, which were kept together"; the data show all four economic x cultural
##combinations in near-equal shares, and the rule is not explained further (design record:
##unknown).
##Outcomes (Supplementary Material wording, translated by the authors):
##  choice = "If you had to decide, which party president would you prefer?" Candidate 1 /
##           Candidate 2 / (Don't know). "Don't know" (1,344 of 7,700 tasks) is stored as NA on
##           both profiles, as in the authors' CHOICE_DV; otherwise exactly one profile is 1.
##  rating = "How likely is it that you will vote for the PARTY in the upcoming national elections if
##           candidate [1/2] becomes party president?" slider 0-100 per cent; (Don't know) = source
##           999 -> NA (source PRVOTE). Asked for each candidate; higher = more likely.
##Rows with neither outcome are dropped (count printed).
##Covariates (Stata value labels, English, as text): cov_gender (WOMAN 0 Man -> male, 1 Woman ->
##female; GENDER code 2, WOMAN missing -> other: the questionnaire's third option is "Other");
##cov_age (years), cov_age_group (REC_AGE bands), cov_education (EDUC labels, e.g. "Vocational
##education degree"; "Don't know" kept as text), cov_canton, cov_urban (URBAN, German labels),
##cov_vote2019 (PRTY_VTE: party voted for in 2019), cov_party_id (PRTY_AFF: "Is there a particular
##political party that is closer to you than all the other parties?"), cov_conjoint_party (PARTY,
##the party named in the vignettes), cov_conjoint_party_basis (REC_PARTY: Party vote / Party
##affiliation), cov_income (HINC), cov_employment (EMP), cov_mip (most important problem);
##codes as in the source: cov_household_size (NHHMEM), cov_sss (subjective social status 0 Bottom -
##10 Top), cov_lr (left-right 0-10), cov_redist and cov_ineq (1 Strongly disagree - 5 Strongly
##agree), cov_imm_econ, cov_imm_cult, cov_imm_life, cov_antielite, cov_trust_parliament (0-10, ends
##labelled in the source); 99 = Don't know in these codes. cov_duration_sec = total interview time.
##Dropped: uuid (panel identifier), start/end dates, conjoint version id, device, attention check
##(all pass), occupation-based class recodes and other derived variables (CLASS3*, oesch*, MOBILITY*,
##TERTIARY*, EDUC3, HINC_MID/HINCEQ/HINC10/HINC3, SSS3, IMM, PARTY2 and party dummies).
##Spot check (printed): marginal means of choice by cultural consumption (paper: classical music/
##wine about 0.46, meeting friends about 0.54, beer not different from 0.50).
suppressMessages({library(data.table); library(haven)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- as.data.table(read_dta(file.path(raw, "symb.dta")))
stopifnot(nrow(r) == 15400, uniqueN(r$record) == 1540)
lab <- function(x) { l <- attr(x, "labels"); v <- names(l)[match(as.numeric(x), l)]; stopifnot(all(is.na(x) | !is.na(v))); v }
num <- function(x) as.numeric(zap_labels(x))
svp <- num(r$PARTY) == 1
woman <- num(r$ATTR_GENDER) == 2
stopifnot(all(num(r$ATTR_GENDER) %in% 1:2))
kind <- fifelse(woman, "Tochter", "Sohn")
lr <- function(code) fifelse(code == 2, "rechten", fifelse(svp, "gemässigten", "linken"))
orig <- num(r$ATTR_ORIGIN); cc <- num(r$ATTR_CULTCON)
stopifnot(all(orig %in% 1:3), all(cc %in% 1:3), all(num(r$ATTR_ECONPOS) %in% 1:2), all(num(r$ATTR_CULTPOS) %in% 1:2), all(num(r$ATTR_EDUCATION) %in% 1:2))
gend <- num(r$GENDER); wom <- num(r$WOMAN)
ids <- sort(unique(r$record))
d <- data.table(id = match(r$record, ids), task = as.integer(r$question), profile = as.integer(r$concept),
  choice = as.integer(r$CHOICE_DV), rating = as.numeric(r$PRVOTE),
  attr_gender = fifelse(woman, "Ist eine Frau", "Ist ein Mann"),
  attr_education = c("Besitzt einen Universitätsabschluss", "Besitzt einen Lehrabschluss")[num(r$ATTR_EDUCATION)],
  attr_econ_position = paste0("Positioniert sich in der Wirtschafts- und Sozialpolitik eher am ", lr(num(r$ATTR_ECONPOS)), " Rand der Partei"),
  attr_cult_position = paste0("Positioniert sich bei gesellschaftspolitischen Fragen (u.a. Zuwanderung, Gleichstellung) eher am ", lr(num(r$ATTR_CULTPOS)), " Rand der Partei"),
  attr_class_origin = cbind(paste("Ist aufgewachsen in wohlhabenden Verhältnissen als", kind, "eines Anwalts und einer Ärztin"),
                            paste("Ist aufgewachsen in einer Lehrerfamilie als", kind, "eines Primarlehrers und einer Primarlehrerin"),
                            paste("Ist aufgewachsen in einer Arbeiterfamilie als", kind, "eines Bauarbeiters und einer Supermarktangestellten"))[cbind(seq_along(orig), orig)],
  attr_cultural_consumption = c("Hört in der Freizeit gerne klassische Musik bei einem Glas Wein", "Trifft in der Freizeit gerne Freunde",
                                "Geht in der Freizeit gerne ein Bier in der Lieblingsbeiz trinken")[cc],
  cov_gender = fifelse(!is.na(wom), c("male", "female")[wom + 1], fifelse(gend == 2, "other", NA_character_)),
  cov_age = as.integer(r$AGE), cov_age_group = lab(r$REC_AGE), cov_education = lab(r$EDUC), cov_canton = lab(r$CANTON),
  cov_urban = lab(r$URBAN), cov_vote2019 = lab(r$PRTY_VTE), cov_party_id = lab(r$PRTY_AFF), cov_conjoint_party = lab(r$PARTY),
  cov_conjoint_party_basis = lab(r$REC_PARTY), cov_income = lab(r$HINC), cov_employment = lab(r$EMP), cov_mip = lab(r$MIP),
  cov_household_size = num(r$NHHMEM), cov_sss = num(r$SSS), cov_lr = num(r$LR), cov_redist = num(r$REDIST), cov_ineq = num(r$INEQ),
  cov_imm_econ = num(r$IMMECON), cov_imm_cult = num(r$IMMCULT), cov_imm_life = num(r$IMMLIFE), cov_antielite = num(r$ANTIELIT),
  cov_trust_parliament = num(r$TRUST), cov_duration_sec = num(r$qtime))
stopifnot(all(gend[is.na(wom)] == 2), all(d$rating %in% c(0:100, NA)),
          d[, .(s = sum(choice), na = sum(is.na(choice))), .(id, task)][, all((s == 1 & na == 0) | na == 2, na.rm = TRUE)],
          d[, .N, .(id, task)][, all(N == 2)], d[, uniqueN(cov_conjoint_party), id][, all(V1 == 1)])
stopifnot(all(mapply(grepl, c("wohlhabenden", "Lehrerfamilie", "Arbeiterfamilie")[orig], d$attr_class_origin)))
n0 <- nrow(d); d <- d[!(is.na(choice) & is.na(rating))]; cat("rows with no outcome dropped:", n0 - nrow(d), "\n")
print(d[!is.na(choice), .(mm = round(mean(choice), 3), .N), attr_cultural_consumption])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "weisstanner_2025_symbolic_class.csv"))
