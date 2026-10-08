##Automation trade-off conjoint (single-profile ratings) from
##Magistro, B., Loewen, P., Bonikowski, B., Borwein, S., & Lee-Whiting, B. (2024). Attitudes toward
##automation and the demand for policies addressing job loss: The effects of information about
##trade-offs. Political Science Research and Methods, 12(4), 783-798.
##https://doi.org/10.1017/psrm.2024.1
##Replication data: Harvard Dataverse doi:10.7910/DVN/AJGHMH, CC0 1.0, no restricted files.
##File read: multi.csv. models_main_paper.R and appendix_final.R read as text (reshape and
##recodes). Design and wording: the article (section 4.3, Table 1) and its online appendix.
##Usage: Rscript magistro_2024.R <raw dir> <output dir>
##
##Cint quota samples in Australia, Canada, the UK and the US, 11-28 March 2022 (8,033 in all).
##2/3 were randomized to the "specific information" conjoint arm; only they are in this table
##(the news and generic-vignette arms saw no profiles): 5,302 respondents. After a prompt
##("A manufacturing firm in [country] decides to introduce a new computer-based
##productivity-improving technology. ... The following tables show different possible
##scenarios."), each saw FOUR tables (task 1-4), each ONE scenario (profile = 1) giving values
##"before innovation" (fixed) and "after innovation" (randomized). Task t = the source fields
##with suffix "" / 1 / 2 / 3 (product, product1, ...) and scen<t>_agree_*, as in the authors'
##reshape; task and profile are recorded.
##ONE TABLE pooling the four countries (cov_country, cov_language): the authors estimate all
##models pooled (article p.790) and the attributes are the same except for currency.
##Outcomes (each table, 5-point agreement + "don't know"; don't know is missing in the deposit):
##  rating: "The company's decision to introduce the new technology is fair" (1 = strongly
##    disagree .. 5 = strongly agree).
##  rating_ceo: would make the same decision if you were the CEO of the company (appendix
##    paraphrase; values 1-5, anchors not stated, presumably the same agreement scale).
##N with an answered task: 5,126 of the 5,302 (156 answered neither outcome in any table, plus
##the 20 with unsaved attributes).
##Attributes, the stored after-innovation values (Table 1 shows the layout):
##  product: the firm's product, as piped into the table in the respondent's language
##    (smartphone/Plane/Car/Vaccine; French Canada: Telephone intelligent/Avion/Automobile/Vaccin,
##    stored with accents as in the deposit). Price levels depend on it (restriction).
##  price_after: the after-innovation price AS STORED in the embedded field, a bare number
##    (e.g. 80000000, 12.5). Respondents saw it with a currency sign, and Table 1 writes the plane
##    price as "$100M"/"$80M"/"$50M"; the exact display format is not recoverable, so the bare
##    number is kept. Before prices: smartphone 600, plane 100000000, car 25000, vaccine 25 (same
##    numbers in every country, local currency). Levels: same / 20% / 50% cheaper.
##  high_skilled_workers_after: 200 / 250 / 350 (before: 200).
##  high_skilled_wage_after: "$125,000"/"$150,000" (US, Canada, Australia) or "£ 75,000"/
##    "£ 90,000" (UK), as stored. Before: $100,000 (US/CA), AUS$100,000, £60,000 (appendix).
##  low_skilled_workers_after: 150 / 50 (before: 200; no-change level excluded by design).
##  low_skilled_wage_after: "$20,000"/"$25,000" (US, CA), "$30,000"/"$40,000" (AU), "£ 13,000"/
##    "£ 17,000" (UK), as stored. Before: $30,000 / AUS$50,000 / £20,000.
##Row order of the table is fixed (Table 1); not randomized.
##20 respondents (19 Australia, 1 US) have no stored attribute values in any table although
##some answered: their tasks are dropped (levels not saved). Respondents with no answer to
##either outcome in a task have that task omitted.
##Covariates: cov_country, cov_language (Qualtrics UserLanguage: EN, FR-CA, ES-ES), cov_gender
##(source `female`: models_main_paper.R L171-173 female == 0 "Male", female == 1 "Female"; stored
##male / female), cov_college (0/1), cov_lr (left/centre/right), cov_age, cov_income (as entered),
##cov_employment (text of the screener answer), cov_attention_pass (source screen1: article p.791
##fn 6, "The attention check item asks respondents to select 'Somehow disagree'"; 1 = answered
##"Somewhat disagree", 0 = any other answer, NA = no answer), cov_policy_* (support for 8 policies, 1 = strongly
##disagree .. 5 = strongly agree, asked AFTER the four tables, so post-treatment).
##Dropped: ResponseId (Qualtrics, PII), the knowledge-check answers (they contain unpiped
##Qualtrics placeholders) and the authors' derived categories, the summary agree_1/agree_2
##(respondent means of the four tables), group.
##N: 5,302 in the conjoint arm (article: 2/3 of 8,033; total by country matches the deposit's
##8,033 rows incl. 109 with no group). Spot check: fairness marginal means by price level
##(3.190380 / 3.435280 / 3.520337) and by high-skilled count reproduce appendix Table A4 exactly.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "multi.csv"), na.strings = c("NA", ""), colClasses = "character")
stopifnot(nrow(s) == 8033)
s <- s[group == "Specific Information"]
stopifnot(nrow(s) == 5302, uniqueN(s$ResponseId) == 5302)
s[, id := seq_len(.N)]
sfx <- c("", "1", "2", "3")
rows <- list()
for (t in 1:4) {
  g <- function(v) s[[paste0(v, sfx[t])]]
  r <- data.table(id = s$id, task = t, profile = 1L,
                  rating = as.integer(s[[paste0("scen", t, "_agree_1")]]), rating_ceo = as.integer(s[[paste0("scen", t, "_agree_2")]]),
                  attr_product = g("product"), attr_price_after = g("priceafter"),
                  attr_high_skilled_workers_after = g("numhsafter"), attr_high_skilled_wage_after = g("wagehsafter"),
                  attr_low_skilled_workers_after = g("numlsafter"), attr_low_skilled_wage_after = g("wagelsafter"))
  rows[[t]] <- r
}
d <- rbindlist(rows)
ac <- grep("^attr_", names(d), value = TRUE)
miss <- d[, rowSums(is.na(.SD)), .SDcols = ac]
stopifnot(all(miss %in% c(0, length(ac))), uniqueN(d$id[miss > 0]) == 20)
d <- d[miss == 0 & !(is.na(rating) & is.na(rating_ceo))]
stopifnot(all(d$rating %in% c(NA, 1:5)), all(d$rating_ceo %in% c(NA, 1:5)))
# price levels are the product's same/20%/50% cheaper values
pl <- list(Plane = c(1e8, 8e7, 5e7), Avion = c(1e8, 8e7, 5e7), Car = c(25000, 20000, 12500), Automobile = c(25000, 20000, 12500),
           smartphone = c(600, 480, 300), "Téléphone intelligent" = c(600, 480, 300), Vaccine = c(25, 20, 12.5), Vaccin = c(25, 20, 12.5))
stopifnot(all(d$attr_product %in% names(pl)), d[, all(mapply(function(p, x) as.numeric(x) %in% pl[[p]], attr_product, attr_price_after))])
stopifnot(all(s$female %in% c("0", "1", NA)), all(s$screen1 %in% c("Strongly disagree", "Somewhat disagree", "Neither agree nor disagree",
                                                                    "Somewhat agree", "Strongly agree", NA)))
cv <- s[, .(id, cov_country = country, cov_language = UserLanguage, cov_gender = c("male", "female")[as.integer(female) + 1L], cov_college = as.integer(college),
            cov_lr = LR, cov_age = as.integer(age), cov_income = as.numeric(income), cov_employment = employment_screener,
            cov_attention_pass = as.integer(screen1 == "Somewhat disagree"))]
for (p in c("socialspend", "basicincome", "jobguarantee", "unskilled", "skilled", "trade", "reskill", "automationtax"))
  cv[, paste0("cov_policy_", p) := as.integer(s[[paste0("policy_", p)]])]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "magistro_2024_automation_fairness.csv"), scipen = 50)   # cov_income as 100000, not 1e+05
