##Work-visa single-profile conjoint (England and Japan) from
##Kawakami, R., Scotto, T. J., Dorussen, H., Pickering, S., Reifler, J., Sunahara, Y., Tago, A., &
##Yen, D. (2026). Who gets in? A conjoint analysis of labour market demand and immigration
##preferences in England and Japan. Journal of Ethnic and Migration Studies, 52(1), 65-84.
##https://doi.org/10.1080/1369183X.2025.2545432 (online 2025-09-10, open access CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/2GMCMX (deposited by Y. Sunahara), CC BY 4.0,
##no restricted files. Files read: immigration_UK.csv, immigration_JP.csv, trust_UK.csv,
##trust_JP.csv (Dataverse "original format" downloads). Level labels from the authors'
##immigration.R / online-appendix.R (read as text, not run), checked against the article's
##Table 1 and Figure 1 (screenshots of one England and one Japan task).
##Usage: Rscript kawakami_2026.R <raw dir> <output dir>
##
##June 2023, monthly political-trust survey: England (YouGov) and Japan (Rakuten Insight). Each
##task shows one hypothetical work-visa applicant (profile = 1) as a fixed-order attribute
##table (Figure 1): age, gender, job, country of origin, long or short term visa. England
##respondents saw 8 profiles, Japan respondents 4 (task = the t in visa_y_n_t<t>, recorded).
##TWO TABLES, one per country: the authors analyse the countries side by side, never pooled,
##the country-of-origin levels differ by country (England: India, Australia, Poland, Nigeria;
##Japan: Peru, China, Korea, Vietnam), the task counts differ, and Japan respondents saw Japanese.
##  kawakami_2026_visa_england  643 respondents x 8 = 5,144 rows (article: "646 English"
##      respondents but "5144 English responses" = 643 x 8; the deposit has 643).
##  kawakami_2026_visa_japan    1,501 respondents x 4 = 6,004 tasks; 27 with no answer
##      omitted (5,977 rows), as in the article (1,501; 6,004 responses).
##Outcome: choice = dep, "Should this person receive a work visa to come to the UK?" Yes = 1,
##No = 0 (Figure 1a; article: "[s]hould this person receive a work visa to come to [COUNTRY]?";
##Japan: この申請者は日本に来るための就労ビザを発給されるべきでしょうか? はい/いいえ, Figure 1b).
##Single-profile accept/reject, so opt_out = yes.
##Level text (authors' English labels, immigration.R): attr_age "24" / "44" / "64" (Figure 1 shows
##the number; the code's label adds "years old"); attr_gender Male / Female; attr_job Computer
##programmer / Doctor / Lawyer / Office manager / Fruit picker / Home care worker / Retail worker /
##Call center (Figure 1a shows "Retail worker"; the article's Table 1 lists the longer forms
##"Fruit and vegetable picker", "Retail salesperson", "Call Centre Telemarketer"); attr_country
##as above ("Viet Num" in the code is written Vietnam, as in Table 1; Table 1 says South Korea,
##the code Korea, kept as Korea); attr_visa_term Long term / Short term (Figure 1a; code: Long /
##Short). Japan's levels are English translations; respondents saw Japanese.
##Randomization restrictions and level probabilities are not stated in the article.
##Dropped: the authors' derived skill/demand codings (attr6-8), the ID1..ID5 Qualtrics field
##names, the political-trust battery (trust_*_core_*; question wording not in the deposit).
##Covariates (trust_<country>.csv, joined by respondent): cov_age (years), cov_gender
##(1 = male, 2 = female, from the authors' recode in online-appendix.R: factor(gender, levels =
##c(1,2), labels = c("Male","Female"))), cov_education_code, cov_income_code (codes; no labels
##in the deposit; the authors treat England education 15-18 and Japan 4-6 as a university
##degree), cov_ideology (0-10; the authors bin 0-4 Left, 5 Middle, 6-10 Right).
##Japan ResponseId (Qualtrics) and England ID re-keyed to integers in file order.
##No survey weight in the deposit.
##Check: the share of profiles granted a visa reproduces the article (p. 74): 61.6% England
##(3,171/5,144), 65.7% Japan (3,926/5,977). 3 Japan respondents answered no task (1,498 kept).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(cc, idcol, countries, file_out, ntask, nresp) {
  d <- fread(file.path(raw, sprintf("immigration_%s.csv", cc)), encoding = "UTF-8")
  setnames(d, 1, "src_id")
  t <- fread(file.path(raw, sprintf("trust_%s.csv", cc)), encoding = "UTF-8")
  setnames(t, 1, "src_id")
  stopifnot(!anyDuplicated(t$src_id), all(d$src_id %in% t$src_id),
            all(d$Question == paste0("visa_y_n_t", sub("q_attr1_concept1_task", "", d$ID1))))
  lab <- function(x, lv) { stopifnot(all(x %in% seq_along(lv))); lv[x] }
  o <- data.table(src_id = d$src_id, task = as.integer(sub("visa_y_n_t", "", d$Question)), profile = 1L,
                  choice = as.integer(d$dep),
                  attr_age = lab(d$attr1, c("24", "44", "64")),
                  attr_gender = lab(d$attr2, c("Male", "Female")),
                  attr_job = lab(d$attr3, c("Computer programmer", "Doctor", "Lawyer", "Office manager", "Fruit picker",
                                            "Home care worker", "Retail worker", "Call center")),
                  attr_country = lab(d$attr4, countries),
                  attr_visa_term = lab(d$attr5, c("Long term", "Short term")))
  stopifnot(o[, all(choice %in% c(0L, 1L, NA))], o[, .N, .(src_id, task)][, all(N == 1)],
            o[, uniqueN(task), src_id][, all(V1 == ntask)], uniqueN(o$src_id) == nresp)
  o <- o[!is.na(choice)]
  cv <- t[, .(src_id, cov_age = as.integer(age), cov_gender = c("male", "female")[gender],
              cov_education_code = as.integer(education), cov_income_code = as.integer(income), cov_ideology = as.integer(Ideology))]
  stopifnot(all(t$gender %in% 1:2))
  o <- merge(o, cv, by = "src_id")
  ids <- unique(d$src_id)
  o[, id := match(src_id, ids)][, src_id := NULL]
  setcolorder(o, "id")
  setorder(o, id, task, profile)
  fwrite(o, file.path(out, file_out))
  o
}
uk <- build("UK", "ID", c("India", "Australia", "Poland", "Nigeria"), "kawakami_2026_visa_england.csv", 8, 643)
jp <- build("JP", "ResponseId", c("Peru", "China", "Korea", "Vietnam"), "kawakami_2026_visa_japan.csv", 4, 1501)
stopifnot(nrow(uk) == 5144, nrow(jp) == 5977)
