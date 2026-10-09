##Product choice conjoints (United States: T-shirts; India: televisions) from
##DiGiuseppe, M., & Barry, C. M. (2022). Do consumers follow the flag? Perceptions of hostility and
##consumer preferences. International Interactions, 48(6), 1200-1215.
##https://doi.org/10.1080/03050629.2022.2089133
##Replication data: Harvard Dataverse doi:10.7910/DVN/PEZ7EE, CC0 1.0. Files read (Dataverse "original
##format", Stata 16): CFTF_usa.tab, CFTF_india.tab. Not used: CTFTF_usa_w1_demos.tab (wave-1
##covariates keyed by MTurk workerId, already merged into CFTF_usa) and anes_demos.tab (ANES 2020
##benchmark). No codebook, questionnaire or analysis code is deposited, and the article was not
##reachable: question wording, screen layout, survey language in India and any randomization
##restrictions are not documented.
##Usage: Rscript digiuseppe_2022.R <dir holding the two .tab files> <output dir>
##
##Two experiments with different products and attribute sets -> two tables. Both: 5 tasks (taskid),
##3 product profiles per task (prof), one chosen per task (forced choice in the data: exactly one
##chosen in every task; no "none" option recorded).
##  digiuseppe_2022_tshirt_usa: 1,228 US respondents (MTurk wave 2, Dec 2019; recordeddate). Attributes
##    (.dta value labels): made in (9 countries), material, quality (Poor..Excellent), price (labels
##    "5", "10", "15", "20"; presumably US dollars, the displayed format is unknown). choice = tschoice.
##  digiuseppe_2022_tv_india: 998 Indian respondents (Dec 2019). Attributes (text columns, identical
##    to the .dta value labels of the _-prefixed copies): made in (10 countries), resolution and
##    refresh rate, customer reviews (stars), brand, price (the value-label text, Indian digit grouping,
##    e.g. "1,00,000"; presumably rupees). choice = TVchosenDV.
##task/profile are recorded. Rows are ordered by respid, taskid, prof. Attribute order: not recorded.
##Level shares are near-equal; all made-in x brand combinations occur (India).
##Covariates, USA: cov_gender (female: 1 -> female, 0 -> male, authors' recode), cov_age (age, as
##recorded), cov_education (educ2 answer text; "" -> NA), cov_urbanrural, cov_employed (answer text),
##cov_attention_pass (attentionpass) and cov_attention_pass_w2 (attentionpassW2), authors' 0/1 flags;
##cov_income (income_, .dta labels as text), cov_partyid_code (PARTYID, codes 0-6, no labels in the
##deposit), cov_news, cov_coouse, cov_coouse_2, cov_globiz, and the respondent's per-country ratings
##cov_ta_<country> (threat), cov_ha_<country> (hostility), cov_la_<country> (labor conditions), all as
##.dta value-label text; cov_block8_do (Qualtrics display order of block 8: terror2 / terror2b; not
##documented). 44 respondents lack the wave-1 covariates (NA).
##Covariates, India: cov_gender (answer text Female/Male -> female/male; "" -> NA), cov_birth_year
##(yearofb, as recorded; includes implausible entries such as 19934; the authors' age variable,
##computed from it, is not kept), cov_married, cov_school1, cov_education (school2 answer text;
##blank when school1 = No), cov_employment, cov_income, cov_householdsize (text as typed), cov_state,
##cov_party1, cov_newspolitics, cov_religion, cov_onlineshopper, cov_afford, cov_coouse, cov_coo2,
##cov_news, cov_globalization, cov_q119/q121/q123 (wording not deposited), cov_attention_pass (payattn),
##cov_ha_<country> and cov_la_<country>: the respondent's hostility and labor-condition ratings of
##each country, rebuilt as text (Hostile/Neutral/Friendly; Good/Fair/Poor) from the authors'
##per-country indicator columns (exactly one indicator is 1 per country, checked).
##Dropped: MTurk workerid, assignmentid, hitid and ZIP code (USA); respondentID (labelled workerId),
##city and employmentfollow (free text), attn (free-text attention answer) (India); dates, timings,
##display-order strings, and derived dummies (made_*, madein_*, ur_*, UR_*, nocollege, *hostile,
##*labor, pakthreat, agegroup, _merge).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(v) as.character(as_factor(v, levels = "labels"))
txt <- function(v) { v <- trimws(as.character(v)); v[v == ""] <- NA_character_; v }
chk <- function(d) {
  stopifnot(d[, .N, .(id, task)][, all(N == 3)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
            d[, .N, id][, all(N == 15)], !anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
  setorder(d, id, task, profile); d
}
## USA
u <- as.data.table(read_dta(file.path(raw, "CFTF_usa.tab")))
stopifnot(nrow(u) == 18420, uniqueN(u$respid) == 1228)
du <- u[, .(id = as.integer(respid), task = as.integer(taskid), profile = as.integer(prof), choice = as.integer(tschoice),
            attr_made_in = lab(madeinTShirt), attr_material = lab(material), attr_quality = lab(quality), attr_price = lab(priceTshirt),
            cov_gender = c("male", "female")[female + 1], cov_age = as.integer(age), cov_education = txt(educ2),
            cov_urbanrural = txt(urbanrural), cov_employed = txt(employed), cov_attention_pass = as.integer(attentionpass),
            cov_attention_pass_w2 = as.integer(attentionpassW2), cov_income = lab(income_), cov_partyid_code = as.integer(PARTYID),
            cov_news = lab(news_), cov_coouse = lab(COOuse_), cov_coouse_2 = lab(COOuse_2), cov_globiz = lab(globiz),
            cov_block8_do = txt(block8_do))]
for (k in c("TA", "HA", "LA")) for (cn in c("china", "thai", "sk", "viet", "malay", "india", "taiwan", "paki", "phil"))
  du[, paste0("cov_", tolower(k), "_", cn) := lab(u[[paste0(k, "_", cn, "_")]])]
fwrite(chk(du), file.path(out, "digiuseppe_2022_tshirt_usa.csv"))
## India
x <- as.data.table(read_dta(file.path(raw, "CFTF_india.tab")))
stopifnot(nrow(x) == 14970, uniqueN(x$respid) == 998)
stopifnot(all(x$madeinTV == lab(x[["_madeinTV"]])), all(x$brandTV == lab(x[["_brandTV"]])), all(x$resrateTV == lab(x[["_resrateTV"]])),
          all(x$custrevTV == lab(x[["_custrevTV"]])))
stopifnot(all(x$priceTV == gsub(",", "", lab(x[["_priceTV"]]))))
di <- x[, .(id = as.integer(respid), task = as.integer(taskid), profile = as.integer(prof), choice = as.integer(TVchosenDV),
            attr_made_in = madeinTV, attr_resolution = resrateTV, attr_reviews = custrevTV, attr_brand = brandTV,
            attr_price = lab(`_priceTV`),
            cov_gender = c(Female = "female", Male = "male")[txt(gender)], cov_birth_year = as.integer(yearofb),
            cov_married = txt(married), cov_school1 = txt(school1), cov_education = txt(school2), cov_employment = txt(employment),
            cov_income = txt(income), cov_householdsize = txt(householdsize), cov_state = txt(state), cov_party1 = txt(party1),
            cov_newspolitics = txt(newspolitics), cov_religion = txt(religion), cov_onlineshopper = txt(onlineshopper),
            cov_afford = txt(afford), cov_coouse = txt(coouse), cov_coo2 = txt(coo2), cov_news = txt(news),
            cov_globalization = txt(globalization), cov_q119 = txt(q119), cov_q121 = txt(q121), cov_q123 = txt(q123),
            cov_attention_pass = as.integer(payattn))]
for (cn in c("china", "thai", "sk", "viet", "mal", "bang", "taiw", "pak", "phil", "rus")) {
  h <- cbind(x[[paste0("hostile_", cn)]], x[[paste0("neutral_", cn)]], x[[paste0("friendly_", cn)]])
  l <- cbind(x[[paste0("Lgood_", cn)]], x[[paste0("Lfair_", cn)]], x[[paste0("Lpoor_", cn)]])
  stopifnot(all(rowSums(h) == 1), all(rowSums(l) == 1))
  di[, paste0("cov_ha_", cn) := c("Hostile", "Neutral", "Friendly")[max.col(h)]]
  di[, paste0("cov_la_", cn) := c("Good", "Fair", "Poor")[max.col(l)]]
}
fwrite(chk(di), file.path(out, "digiuseppe_2022_tv_india.csv"))
