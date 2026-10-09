##Wealth-tax revenue spending conjoint (Germany, March 2024) from
##Ahrens, L., Bremer, B., & Hakelberg, L. (2026). Taxing uber-polluters: Carbon inequality and support
##for wealth taxation to finance the green transition. Climate Policy.
##https://doi.org/10.1080/14693062.2026.2661351
##Replication data: Harvard Dataverse doi:10.7910/DVN/I4FXDZ, CC0 1.0 (dataverse licence; the
##package README says CC BY 4.0 for data), no restricted files. One file, dataverse_upload.zip; read
##from it: data/raw/240328_Final_deidentified.sav (survey, de-identified by the authors),
##data/raw/dcm_design.xlsx (sheets "Conjoint design" = the design rows per version x task x option,
##"Labels" = German level text), weighting/data_weightsonly.Rdata (entropy-balancing weights).
##Read as text only: README.md, codebook.md, docs/deidentification_note.md,
##code/TaxingUberPolluters.Rmd (merge logic: chunk "Prepare Conjoint data"). Article (open access,
##Leuphana repository) for design facts and Table 1.
##Usage: Rscript ahrens_2026.R <dir holding the unzipped dataverse_upload/> <output dir>
##
##bilendi online access panel, Germany, 21-29 March 2024; quota sample, attention-check failures
##screened out. Respondents were told to assume the government had reintroduced the wealth tax and
##would spend the revenue on responding to climate change; they then saw 5 pairs (task 1-5) of
##randomly created spending proposals (Option 1 = profile 1, Option 2 = profile 2), 4 attributes x 4
##levels each, with the restriction (article p. 5) that at least one attribute is "No additional
##spending" in every proposal (holds in every design row: checked below).
##Outcomes:
##  choice  = q17_<t> "DCM Task: <t>", Option 1/2: "select the proposal they prefer" (article p. 4;
##            the German wording is in the article's Supplementary Table 2, not deposited; no opt-out).
##  rating  = q18_<t> / q19_<t> "Wie sehr sind Sie für Option 1?" / "... Option 2?": 1 Sehr stark dafür,
##            2 Etwas dafür, 3 Weder dafür noch dagegen, 4 Etwas dagegen, 5 Sehr stark dagegen.
##            Stored as in the source, so LOWER = MORE in favour (the authors reverse it for analysis).
##Tasks with no choice and no rating are omitted; a task with only some answers keeps NA in the
##others. Attribute text is the German text respondents saw (xlsx "Labels"); English in Table 1:
##  attr_compensation (Ausgleichszahlungen), attr_public_investment (Staatliche Investitionen),
##  attr_firm_subsidies (Subventionen für Unternehmen), attr_household_subsidies (Subventionen für
##  Haushalte); level 1 of each = "Keine zusätzlichen Ausgaben" ("No additional expenditure").
##Design rows are matched by (conjoint_Version, task, option) exactly as in the authors' Rmd; the
##design's question number is the task number (rec_conjointorder1 is "[0, 1, 2, 3, 4]" for everyone,
##i.e. task order not randomized).
##Attribute order was randomized per respondent: trial_attribute_order keeps the source string
##rec_attribute_order (e.g. "[4, 1, 3, 2]"; 24 permutations). Whether it lists the attributes in
##display order or gives each attribute's position is not documented, so no attrpos_ columns.
##Framing experiment run before the conjoint (between-respondent): trial_frame from TESTGROUP via
##the codebook (1 Control, 2 Climate (pro), 3 Inequality (pro), 4 Contra, 5 Climate & Contra,
##6 Inequality & Contra).
##Sample: the authors' analysis sample of 4,653 (the 143 respondents without Bundesland are dropped,
##as in the Rmd; they also have no wgt.2/wgt.3). Every one of them has all 10 ratings, but 4,393 of
##23,265 tasks have no choice (639 respondents answered no choice question at all, 577 skipped some);
##choice is NA on both options of those tasks. Why the choice is missing is not documented.
##Weights (weighting/weighting_de.R, entropy balancing): cov_survey_weight = wgt.3 (age x sex x
##education + East/West + 2024 vote-intention margins); cov_weight_1 = wgt.1 (age x sex x
##education), cov_weight_2 = wgt.2 (+ East/West). The conjoint analysis in the article is unweighted.
##Covariates (value labels in the .sav): cov_age (q2, years, top-coded at 85 by the authors);
##cov_gender (q3 Männlich = male, Weiblich = female, Divers = other, "Ich mache lieber keine Angabe"
##= NA); cov_education (q4 answer text, German); cov_bundesland (q5_3 text); cov_leftright_code (q6:
##1 = "0 – Links" .. 11 = "10 – Rechts", 12 Weiß ich nicht, 13 refusal); cov_vote_2021_code (q7) and
##cov_vote_intention (q8, answer text; refusal -> NA; a vote, not party identification);
##cov_wealthtax_support_code (q11: 1 Sehr stark dafür .. 5 Sehr stark dagegen); cov_income_code (q28,
##11 net household income bands), cov_wealth_code (q30), cov_debt_code (q31) (12 bands each).
##Dropped: record (internal ID; re-keyed in source order), the other attitude/budget-slider items,
##q20 attribute-importance items, timers, attention-check items, derived variables.
##N: 4,653 matches the article. Spot check: the article's AMCEs on choice (lump-sum payment to all
##citizens +18.0 points, public transport investment +17.7, vs no additional spending) reproduce.
suppressMessages({library(haven); library(data.table); library(readxl)})
a <- commandArgs(TRUE); raw <- file.path(a[1], "dataverse_upload"); out <- a[2]
s <- as.data.table(read_sav(file.path(raw, "data/raw/240328_Final_deidentified.sav")))
s <- s[q5_4 != ""]
stopifnot(nrow(s) == 4653, all(s$rec_conjointorder1 == "[0, 1, 2, 3, 4]"))
e <- new.env(); load(file.path(raw, "weighting/data_weightsonly.Rdata"), envir = e); w <- as.data.table(e$df_weights)
des <- as.data.table(read_excel(file.path(raw, "data/raw/dcm_design.xlsx"), sheet = "Conjoint design"))
lab <- as.data.table(read_excel(file.path(raw, "data/raw/dcm_design.xlsx"), sheet = "Labels", col_names = FALSE))
setnames(lab, c("code", "text"))
lab[, attr := cumsum(grepl("^ATTR", code))]
lab <- lab[!grepl("^ATTR", code) & !is.na(code)]
stopifnot(lab[, .N, attr]$N == 4, lab[code == "1", all(text == "Keine zusätzlichen Ausgaben")])
## restriction: at least one "no additional spending" level per proposal
stopifnot(des[, all(attr1 == 1 | attr2 == 1 | attr3 == 1 | attr4 == 1)], des[, .N, .(version, question, concept)][, all(N == 1)])
vl <- function(x) { l <- attr(x, "labels"); v <- as.numeric(zap_labels(x)); unname(setNames(names(l), l)[as.character(v)]) }
d <- s[, .(rid = seq_len(.N), version = as.numeric(conjoint_Version), record)]
d <- d[CJ(rid = rid, task = 1:5, profile = 1:2), on = "rid"]
d <- des[d, on = .(version, question = task, concept = profile)]
setnames(d, c("question", "concept"), c("task", "profile"))
stopifnot(!anyNA(d$attr1))
for (k in 1:4) d[, paste0("A", k) := lab[attr == k]$text[match(get(paste0("attr", k)), as.numeric(lab[attr == k]$code))]]
setnames(d, paste0("A", 1:4), c("attr_compensation", "attr_public_investment", "attr_firm_subsidies", "attr_household_subsidies"))
d[, paste0("attr", 1:4) := NULL]
## outcomes
ch <- as.matrix(s[, paste0("q17_", 1:5), with = FALSE]); r1 <- as.matrix(s[, paste0("q18_", 1:5), with = FALSE]); r2 <- as.matrix(s[, paste0("q19_", 1:5), with = FALSE])
ch <- unclass(zap_labels(ch)); r1 <- unclass(zap_labels(r1)); r2 <- unclass(zap_labels(r2))
idx <- cbind(d$rid, d$task)
d[, chosen := as.integer(ch[idx])]
stopifnot(all(d$chosen %in% c(1, 2, NA)))
d[, choice := as.integer(chosen == profile)][, chosen := NULL]
d[, rating := as.integer(ifelse(profile == 1, r1[idx], r2[idx]))]
stopifnot(all(d$rating %in% c(1:5, NA)))
d <- d[d[, .(keep = any(!is.na(choice) | !is.na(rating))), .(rid, task)], on = .(rid, task)][keep == TRUE][, keep := NULL]
d[, trial_attribute_order := s$rec_attribute_order[rid]]
stopifnot(all(as.numeric(s$TESTGROUP) %in% 1:6))
d[, trial_frame := c("Control", "Climate (pro)", "Inequality (pro)", "Contra", "Climate & Contra", "Inequality & Contra")[as.numeric(s$TESTGROUP)[rid]]]
cv <- s[, .(cov_age = as.integer(q2),
            cov_gender = c("male", "female", "other", NA)[as.numeric(q3)],
            cov_education = vl(q4), cov_bundesland = vl(q5_3),
            cov_leftright_code = as.integer(q6), cov_vote_2021_code = as.integer(q7),
            cov_vote_intention = vl(q8), cov_wealthtax_support_code = as.integer(q11),
            cov_income_code = as.integer(q28), cov_wealth_code = as.integer(q30), cov_debt_code = as.integer(q31))]
cv[cov_vote_intention == "Ich mache lieber keine Angabe", cov_vote_intention := NA]
stopifnot(all(as.numeric(s$q3) %in% 1:4))
cv[, rid := .I]
cv <- w[, .(record, cov_survey_weight = wgt.3, cov_weight_1 = wgt.1, cov_weight_2 = wgt.2)][s[, .(record)], on = "record"][, rid := .I][cv, on = "rid"][, record := NULL]
stopifnot(!anyNA(cv$cov_survey_weight))
d <- cv[d, on = "rid"]
d[, id := match(rid, unique(rid))]
d[, c("rid", "version", "record") := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 %in% c(1, NA))])
setcolorder(d, c("id", "task", "profile", "choice", "rating", grep("^attr_", names(d), value = TRUE), grep("^trial_", names(d), value = TRUE)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ahrens_2026_wealth_tax_spending.csv"))
