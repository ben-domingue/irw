##Bioplastic tomato-packaging discrete choice experiment from
##Findrik, E., & Meixner, O. (2026). Consumer acceptance of bioplastic food packaging: Anonymized
##data and research materials from a discrete choice experiment in Germany [Data set]. Zenodo.
##Deposit: Zenodo record 21740286, doi:10.5281/zenodo.21740286, CC BY 4.0 (record licence; README
##agrees). No article DOI given in the record.
##Files read: data_valid.sav (869 respondents, one row each; Choice01-Choice12 = card picked) and
##XLSTAT_V4_final.xlsm, sheet "Choices_Frequ3" (the 12 card profiles, columns I-L, English level
##names). Attribute text as displayed comes from survey_original.pdf (German questionnaire, pp.
##5-14); survey_overview.pdf lists the variables.
##Usage: Rscript findrik_2026.R <dir holding the .sav and .xlsm> <output dir>
##
##German online sample, November 2024 (README), n = 869. Fixed design (XLSTAT choice-based
##design): 12 cards, 12 choice sets of 3 cards each ("Auswahl k: Kirschtomaten (250 g)"),
##shown in the questionnaire's fixed order 1-12 (in blocks of 4 with attitude questions
##between); set k uses cards listed in the SPSS variable label of Choice<k> (e.g. Choice01:
###12 - #01 - #11), in that left-to-right order (profile 1-3), checked against the questionnaire.
##Every respondent saw the same 12 sets: one table, no blocks.
##Outcome: choice, "Welches dieser Produkte würden Sie kaufen?" (Which of these products would
##you buy?). Opt-out: "Keines dieser 3 Produkte" (None of these 3 products, coded 0 in the
##source) is a fixed alternative without attributes, so not a profile: those sets have choice = 0
##on all 3 cards (opt_out = yes).
##Attributes (German display text; questionnaire card lines "Verpackung: ...", "...abbaubar",
##"Produkt hält n Tage länger", "Preis Verpackung: ..."): packaging material Biokunststoff /
##Konventioneller Kunststoff (xlsm Bio-based / Fossil-based), biodegradability Biologisch abbaubar /
##Nicht biologisch abbaubar, extra shelf life "Produkt hält 3/5/7 Tage länger", packaging price
##0,30 / 0,45 / 0,60 EUR (the attribute prefixes "Verpackung:" and "Preis Verpackung:" are left
##off the levels).
##trial_info: random assignment before the DCE (Group; questionnaire p. 4 "Zufällige Zuteilung
##zu Gruppe 1 (Info) und Gruppe 2 (keine Info)"): with / without an information text about
##bioplastics.
##Covariates (SPSS value labels, English): cov_gender (1 Female = female, 2 Male = male, 3 Divers
##= other, 0 Prefer not to answer = NA), cov_age_group (band text), cov_education (label text),
##cov_hhsize, cov_income (label text; prefer-not = NA); raw attitude items keep codes 1-5
##(1 strongly disagree ... 5 strongly agree): cov_envcon1-5, cov_foodwaste1-4 (items 2-4 from the
##source's unreversed "original" variables Foodwaste2r-4r), cov_fns1-4; cov_bpf1-2 (1 yes, 2 no),
##cov_ka1-5 (1 True, 2 False, 3 I don't know), cov_info_read (1 read and understood, 2 read but
##lacks technical knowledge; NA in the no-information arm). Dropped: derived *_correct scores,
##indexes, individual part-worths (U_*, W_*, Zero). IDs are the deposit's anonymous study IDs.
##No survey weight in the deposit.
library(haven); library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "data_valid.sav"))
x <- as.data.table(suppressMessages(read_excel(file.path(raw, "XLSTAT_V4_final.xlsm"), "Choices_Frequ3", col_names = FALSE)))
pr <- x[2:13, 8:12]; setnames(pr, c("card", "mat", "bio", "shelf", "price"))
pr[, card := as.integer(sub("Profil ", "", card))]
stopifnot(identical(sort(pr$card), 1:12))
pr[, mat := c("Bio-based" = "Biokunststoff", "Fossil-based" = "Konventioneller Kunststoff")[mat]]
pr[, bio := c("Biodegradable" = "Biologisch abbaubar", "Non-biodegradable" = "Nicht biologisch abbaubar")[bio]]
pr[, shelf := sprintf("Produkt hält %s Tage länger", sub(" days", "", shelf))]
stopifnot(!anyNA(pr), all(pr$price %in% c("0,30 EUR", "0,45 EUR", "0,60 EUR")))
# card 12 is set 1 / position 1 in the questionnaire: Biokunststoff, Biologisch abbaubar, 3 Tage, 0,30 EUR
stopifnot(pr[card == 12, mat == "Biokunststoff" & bio == "Biologisch abbaubar" & price == "0,30 EUR"])
sets <- rbindlist(lapply(1:12, function(k) {
  lab <- attr(s[[sprintf("Choice%02d", k)]], "label")
  cards <- as.integer(regmatches(lab, gregexpr("(?<=#)[0-9]+", lab, perl = TRUE))[[1]])
  stopifnot(length(cards) == 3)
  data.table(task = k, profile = 1:3, card = cards)
}))
stopifnot(identical(sets[task == 1, card], c(12L, 1L, 11L)))
resp <- data.table(id = as.integer(s$ID))
for (k in 1:12) resp[, paste0("c", k) := as.integer(zap_labels(s[[sprintf("Choice%02d", k)]]))]
long <- melt(resp, id.vars = "id", variable.name = "task", value.name = "pick")
long[, task := as.integer(sub("c", "", task))]
stopifnot(all(long$pick %in% 0:3))
d <- merge(long, sets, by = "task", allow.cartesian = TRUE)
d[, choice := as.integer(profile == pick)]
d <- merge(d, pr, by = "card")
d <- d[, .(id, task, profile, choice, attr_packaging_material = mat, attr_biodegradability = bio,
           attr_extra_shelf_life = shelf, attr_price = price, trial_card = card)]
cv <- data.table(id = as.integer(s$ID),
                 trial_info = c("with information about bioplastic", "without information about bioplastic")[as.integer(s$Group)])
lab <- function(v) { z <- as.character(as_factor(s[[v]], levels = "labels")); z[z == "Prefer not to answer"] <- NA; z }
g <- as.integer(zap_labels(s$Gender)); stopifnot(all(g %in% c(0:3, NA)))
cv[, cov_gender := c("female", "male", "other")[match(g, 1:3)]]
cv[, `:=`(cov_age_group = lab("Age"), cov_education = lab("Education"), cov_hhsize = lab("HHSize"), cov_income = lab("Income"))]
codes <- c(paste0("EnvCon", 1:5), "Foodwaste1", "Foodwaste2r", "Foodwaste3r", "Foodwaste4r", paste0("FNS", 1:4),
           "BPF1", "BPF2", paste0("KA", 1:5), "Info")
nm <- c(paste0("cov_envcon", 1:5), paste0("cov_foodwaste", 1:4), paste0("cov_fns", 1:4), "cov_bpf1", "cov_bpf2",
        paste0("cov_ka", 1:5), "cov_info_read")
for (i in seq_along(codes)) cv[, (nm[i]) := as.integer(zap_labels(s[[codes[i]]]))]
d <- merge(d, cv, by = "id")
stopifnot(!anyNA(d$trial_info), d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "findrik_2026_bioplastic_packaging.csv"))
