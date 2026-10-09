##Electric-vehicle policy-package conjoint (Switzerland, May-October 2018) from
##Brückmann, G., & Bernauer, T. (2020). What drives public support for policies to enhance electric
##vehicle adoption? Environmental Research Letters, 15(9), 094002. https://doi.org/10.1088/1748-9326/ab90a5
##Replication data: Harvard Dataverse doi:10.7910/DVN/XF0GD9, CC0 1.0. File read:
##replicationdata_ERL2020GBTB.RData (object tt). RCode_ERL2020GBTB.R read as text, not run (code-to-label
##mapping of attributes and covariates). Attribute text, wording and design from the article (Sec. 3,
##Table 1, Fig. 1); the German instrument (SI 8) was not seen.
##Usage: Rscript bruckmann_2020.R <dir holding the .RData> <output dir>
##
##Postal survey invitation to car holders in the German-speaking cantons Aargau, Schwyz, Zug and Zurich:
##a random sample of non-EV holders plus all EV holders; 5,325 completed (= the article; 4,147 non-EV,
##1,178 EV holders). One fielding, one instrument; the authors analyse both groups pooled and split, so
##one table with cov_ev_holder (evdt). The source id restarts within each group; ids are re-keyed over
##(id, evdt) in file order, as the authors' uid.
##5 tasks x 2 policy proposals. profile = seite (2 = left/first, 3 = second; alternates in every pair);
##task = pair index within respondent from row order (inferred: rows come in seite 2/3 pairs and, where
##answered, exactly one proposal per pair is chosen).
##Outcomes:
##  choice = choice, binary choice "whether policy option A or B is preferred" (paraphrase; forced
##           choice, no opt-out). 4 tasks with both proposals chosen and 1 task with one missing are set
##           to NA on both profiles; 2,731 tasks have no choice.
##  rating = rating, 7-point Likert rating of each proposal (article: "ratings of each proposed policy,
##           irrespectively if chosen or not"); anchors not seen; chosen proposals average 4.7, others 3.0,
##           so higher = more support (inferred from the data, not stated).
##Rows with neither outcome are dropped.
##Attributes (level text = the article's English Table 1; respondents saw German):
##  attr_charging (charging 0-3), attr_subsidy (subsidy 0-3), attr_information (info 0 keep / 1 stricter /
##  2 abolish), attr_registration (registration 0 allowed / 1 forbid from 2020), attr_funding (financing
##  0-4). Code order from RCode labels (l_charging, l_subsidy, l_info, l_registration, l_financing),
##  matched to Table 1 text. Funding was shown only to the half of respondents randomly assigned to the
##  funding arm (visiblefin = 1; trial_funding_shown); elsewhere attr_funding = "(not shown)".
##Restriction (Table 1 note b): in the funding arm, "No additional funding" appears if and only if the
##proposal has no new charging infrastructure and no subsidy (confirmed in the data: 1,641 profiles).
##Attribute order randomized per respondent and held for all 5 tasks (article); not in the deposit.
##Covariates: cov_ev_holder (evdt 1/0), cov_age_group (age: RCode labels "born < 1945" ... "born >= 1985"),
##cov_household_income (hhinc 1-5: RCode labels, CHF per month as labelled there; ".n" = NA),
##cov_higher_education (higheduc 0/1, undocumented beyond the name), cov_gender_code (gender: RCode labels
##1 "male", 2 "not male", but 2 is two-thirds of these car holders, so the codes are kept),
##cov_print (print 0/1, undocumented; probably the paper questionnaire), cov_tesla and cov_icev_backup
##(EV holders: holds a Tesla / a back-up non-BEV car, RCode labels), cov_ever_drove_bev (non-EV holders,
##0 No / 1 Yes; ".w" and blank = NA), cov_nextcarbev_code and cov_carusedays (undocumented, as stored).
##envsc (the authors' environmental-concern scale score) is dropped as derived. No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "replicationdata_ERL2020GBTB.RData"), envir = e)
x <- as.data.table(e$tt)
x[, k := seq_len(.N), .(id, evdt)]
stopifnot(x[, .N, .(id, evdt)][, all(N == 10)], x[, all(seite == ifelse(k %% 2 == 1, 2, 3))])
x[, `:=`(task = as.integer((k + 1) %/% 2), profile = as.integer(seite - 1))]
x[, bad := !(sum(choice) %in% 1), .(id, evdt, task)]
x[bad == TRUE, choice := NA]
txt <- function(v, codes, labs) { stopifnot(all(v[!is.na(v)] %in% codes)); labs[match(v, codes)] }
x[, uid := .GRP, .(id, evdt)]
d <- x[, .(id = uid, task, profile, choice = as.integer(choice), rating = as.integer(rating),
  attr_charging = txt(charging, 0:3, c("No new additional charging infrastructure", "1 out of 1000 parking spaces",
                                       "10 out of 1000 parking spaces", "100 out of 1000 parking spaces")),
  attr_subsidy = txt(subsidy, 0:3, c("No subsidy", "Subsidy of 1000 CHF", "Subsidy of 3000 CHF", "Subsidy of 5000 CHF")),
  attr_information = txt(info, 0:2, c("Maintain current information requirements: energy label attached to newly sold cars",
    "Stricter information requirements: energy labels must show additional fuel consumption data from real driving and visibility must be increased",
    "Abolish current information requirements on fuel consumption, CO2 emissions, and energy efficiency of cars")),
  attr_registration = txt(registration, 0:1, c("Allowed", "Forbid registration from 2020 onward")),
  attr_funding = ifelse(visiblefin == 0, "(not shown)", txt(financing, 0:4, c("No additional funding",
    "General federal budget without an increase in income taxes (savings in other areas of the budget)",
    "General federal budget with an increase in income taxes",
    "Fee (malus) of CHF 4000 when purchasing a car with gasoline/diesel engine",
    "Price increase for motorway vignette from 40 to 100 CHF"))),
  trial_funding_shown = as.integer(visiblefin),
  cov_ev_holder = as.integer(evdt),
  cov_age_group = txt(age, 1:6, c("born < 1945", "born 1945-1954", "born 1955-1964", "born 1965-1974", "born 1975-1984", "born >= 1985")),
  cov_household_income = txt(suppressWarnings(as.integer(hhinc)), 1:5, c("Below CHF 4000", "CHF 4000-8000", "CHF 8000-12000", "CHF 12000-16000", "More than CHF 16000")),
  cov_higher_education = as.integer(higheduc), cov_gender_code = as.integer(gender), cov_print = as.integer(print),
  cov_tesla = txt(Tesla, 0:1, c("No", "Yes")), cov_icev_backup = txt(icevbackup, 0:1, c("No", "Yes")),
  cov_ever_drove_bev = txt(suppressWarnings(as.integer(ifelse(everdrovebev %in% c("0", "1"), everdrovebev, NA))), 0:1, c("No", "Yes")),
  cov_nextcarbev_code = as.integer(nextcarbev), cov_carusedays = carusedays)]
stopifnot(!anyNA(d[, .(attr_charging, attr_subsidy, attr_information, attr_registration, attr_funding)]),
          d[, all((trial_funding_shown == 1) == (attr_funding != "(not shown)"))],
          d[attr_funding == "No additional funding", all(attr_charging %like% "^No new" & attr_subsidy == "No subsidy")],
          d[trial_funding_shown == 1 & attr_charging %like% "^No new" & attr_subsidy == "No subsidy", all(attr_funding == "No additional funding")],
          d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %in% c(1:7, NA))])
d <- d[!(is.na(choice) & is.na(rating))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bruckmann_2020_ev_policy.csv"))
cat(nrow(d), "rows,", uniqueN(d$id), "respondents\n")
