##Gender-affinity candidate conjoint (UK) from
##Tirado Castro, A., & Banducci, S. (2026). Not just women for women: How gendered affinities affect
##candidate support. Research & Politics. https://doi.org/10.1177/20531680261439753
##Replication data: Harvard Dataverse doi:10.7910/DVN/MJQKMQ, CC0 1.0, no restricted files. Files
##read: "Not Just Women for Women - Dataset-1.tab" in its original Stata format (value labels) and
##Gender_Affinity_Dataset_Codebook.pdf (pdftotext). The article was not accessible (publisher bot
##wall), so outcome wording is a paraphrase from the codebook.
##Usage: Rscript tiradocastro_2026.R <dir holding the .dta saved as data.dta> <output dir>
##
##2,518 UK respondents (survey provider and dates not in the deposit), 10 rows each = 5 tasks x 2
##hypothetical parliamentary candidates, 8 attributes (codebook section 2; level text from the
##codebook): gender, political experience, previous occupation, number of children, ethnic group,
##party (Reform UK, Liberal Democrats, Labour Party, Green Party, Conservative Party), Brexit position,
##localness. The file has NO task or profile column: rows are in respondent blocks of 10 and
##consecutive row pairs form a task (every pair has exactly one chosen profile), so task and
##profile are INFERRED from row order. Attribute order and restrictions are not documented.
##  choice: which candidate the respondent preferred (`chosen`; codebook "whether the candidate
##    profile was selected in the conjoint task"). Forced choice.
##  rating: 0-10 evaluation (0 "Very negative evaluation", 10 "Very positive evaluation"). The
##    codebook says the chosen candidate was rated, but every profile, chosen or not, has a rating
##    (non-chosen profiles mostly low), so both are kept as stored.
##Covariates (codebook / .dta labels): cov_gender (gender: 0 Man -> male, 1 Woman -> female),
##cov_age (years), cov_education (1 Primary education, 2 Secondary education, 3 University degree,
##4 Postgraduate degree), cov_children (number; 9 = "Prefer not to say / Missing response" per the
##codebook -> NA), cov_sexuality (0 Heterosexual, 1 LGBA), cov_political_interest (Q1 label text;
##"Don't know" kept), cov_vote (Q5 "Which party did you vote for?", label text; vote choice, not
##party identification), cov_gender_equality (Q15, 0-10, 98 = Don't know, as stored),
##cov_masculinity, cov_femininity (0-6), cov_gender_identity (label text: Hyper, Strong, Weak,
##Counter-typical), cov_gender_importance (gender_imp, 0-6). Dropped: the panel respondent id
##(re-keyed 1..N in file order) and the derived chosen_woman, women_with_children, women_military.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(x) == 25180, x[, .N, ID][, all(N == 10)], all(x[, rleid(ID)] == x[, match(ID, unique(ID))]))
x[, id := rleid(ID)][, r := seq_len(.N), id][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
stopifnot(x[, sum(chosen), .(id, task)][, all(V1 == 1)])
lv <- list(pol_experience = c("No previous political experience", "Has stood as a candidate previously", "Has been a local councilor", "Has been a Member of Parliament"),
           previous_occupation = c("Worked as a teacher", "Worked as a social worker", "Worked as military personnel", "Worked as a legal professional", "Worked as a business owner"),
           children_cand = c("Has no children", "Has one child", "Has two children", "Has three children"),
           ethnic_group = c("White", "Black", "Asian"),
           party_id = c("Reform UK", "Liberal Democrats", "Labour Party", "Green Party", "Conservative Party"),
           brexit = c("Remain", "Leave"),
           localness = c("New to the area", "Lived in the area for 2 years", "Lived in the area for 15 years", "Born in the area"))
for (v in names(lv)) stopifnot(all(x[[v]] %in% seq_along(lv[[v]])))
stopifnot(all(x$gender_cand %in% 0:1), !anyNA(x$rating), all(x$rating %in% 0:10))
lab <- function(v) { s <- as.character(as_factor(v, levels = "labels")); fifelse(is.na(s) | s == "", NA_character_, s) }
d <- x[, .(id, task, profile, choice = as.integer(chosen), rating = as.integer(rating),
           attr_gender = c("Male candidate", "Female candidate")[gender_cand + 1],
           attr_experience = lv$pol_experience[pol_experience], attr_occupation = lv$previous_occupation[previous_occupation],
           attr_children = lv$children_cand[children_cand], attr_ethnic_group = lv$ethnic_group[ethnic_group],
           attr_party = lv$party_id[party_id], attr_brexit = lv$brexit[brexit], attr_localness = lv$localness[localness],
           cov_gender = c("male", "female")[as.integer(zap_labels(gender)) + 1L], cov_age = age,
           cov_education = c("Primary education", "Secondary education", "University degree", "Postgraduate degree")[education],
           cov_children = fifelse(children == 9, NA_real_, children),
           cov_sexuality = c("Heterosexual", "LGBA")[sexuality + 1],
           cov_political_interest = lab(Q1), cov_vote = lab(Q5), cov_gender_equality = as.integer(zap_labels(gender_equality)),
           cov_masculinity = masculinity, cov_femininity = femininity, cov_gender_identity = lab(gender_identity),
           cov_gender_importance = gender_imp)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "tiradocastro_2026_gender_affinity.csv"))
