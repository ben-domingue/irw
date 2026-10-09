##Foreign-direct-investment (FDI) screening conjoint (France, Germany, Italy) from
##Guidi, M., Moro, F. N., & Poletti, A. (2026). Geopolitics and opposition to foreign direct
##investment in the EU: Evidence from a conjoint experiment. Business and Politics.
##https://doi.org/10.1017/bap.2026.10027
##Replication data: Harvard Dataverse doi:10.7910/DVN/XJ5BUG, CC0 1.0, no restricted files.
##File read: gmp_fdi.csv (Dataverse "original format" download of gmp_fdi.tab). The authors'
##analysis.R was read as text. Design facts and level wording from the article (open access),
##"Research design and data", "Experimental design" and Table 1.
##Usage: Rscript guidi_2026.R <raw dir> <output dir>
##
##Bilendi opt-in panels, 15-23 April 2024, ~1,500 adults per country; the deposit holds only
##respondents who passed the attention screener (article fn. 73: 1,501-278 = 1,223 France,
##1,502-175 = 1,327 Germany, 1,502-319 = 1,183 Italy; the table counts match exactly).
##Each respondent saw 5 single hypothetical acquisitions of a domestic company by a foreign one
##(attributes as a table, attribute order randomized, not recorded) and was asked whether the
##government should block the acquisition.
##THREE TABLES, one per country (guidi_2026_fdi_france/_germany/_italy): the article calls
##them "three survey experiments", shown in French, German and Italian, and estimates every
##model separately by country (analysis.R: svyglm per country, contrasts compared across them).
##  choice = exp_response, 1 = the government should block the acquisition, 0 = not
##           (article: "Yi is a binary variable that equals 1 if the respondent wants to block
##           the acquisition and 0 otherwise"). A single-profile block / don't-block question,
##           so opt-out = yes in the design record.
##Task = ROW ORDER within respondent (the file holds exactly 5 consecutive rows per record);
##that the file keeps display order is assumed, not documented. profile = 1 throughout.
##Attribute text: the deposit stores short English labels; each is mapped to the article's
##English formulation in Table 1 (the stored text is that English version, with
##[RESPONDENT'S COUNTRY] replaced by the table's country; respondents saw a translation).
##The short label "More benefit to home country" = more benefit to the respondent's country
##(Table 1 marks "more benefit to the [acquiring] country" as the reference, as does
##analysis.R's first factor level "More benefit to foreign country").
##Covariates: the deposit has only the authors' dichotomized subgroup codings (the source
##items and the data-preparation script are not shared): cov_degree (educ_recoded),
##cov_anti_government, cov_anti_trade, cov_working, cov_right_wing as text, and
##cov_china_shock 0/1 (the authors' regional China-import-shock exposure flag, appendix E).
##Dropped: exp_relative_gain_acquisition_ordered (identical copy), mil_ally / china / eu
##(derived from the country attribute). No survey weight in the deposit (analysis.R uses
##weights = ~1). record kept as id (a survey record number, not a platform ID).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "gmp_fdi.csv"), encoding = "UTF-8")
stopifnot(all(diff(rleid(s$record)) >= 0), s[, .N, record][, all(N == 5)], s[, uniqueN(country), record][, all(V1 == 1)],
          all(s$exp_relative_gain_acquisition == s$exp_relative_gain_acquisition_ordered), all(s$exp_response %in% 0:1))
s[, task := seq_len(.N), record]
mp <- function(x, m) { stopifnot(all(x %in% names(m))); unname(m[x]) }
counts <- c(France = 1223L, Germany = 1327L, Italy = 1183L)
for (cc in names(counts)) {
  x <- s[country == cc]
  d <- data.table(id = as.integer(x$record), task = x$task, profile = 1L, choice = as.integer(x$exp_response))
  d[, attr_relative_gains := mp(x$exp_relative_gain_acquisition, c(
    "More benefit to foreign country" = paste0("the investment will bring more economic benefit to the country where the acquiring company is based than to ", cc),
    "Equal benefit" = paste0("the investment will bring equal economic benefit to the country where the acquiring company is based and ", cc),
    "More benefit to home country" = paste0("the investment will bring less economic benefit to the country where the acquiring company is based than to ", cc)))]
  d[, attr_acquiring_country := mp(x$exp_country_acquiring_company, c("EU member state" = "an EU Member State", China = "China",
    "United States" = "United States", "United Kingdom" = "United Kingdom", "Saudi Arabia" = "Saudi Arabia", India = "India"))]
  d[, attr_target_size := mp(x$exp_size_targeted_company, c("Small (less than 50 employees)" = "a small company (less than 50 employees)",
    "Medium (50-249 employees)" = "a medium company (between 50 and 249 employees)",
    "Big (more than 249 employees)" = "a large company (250 or more employees)"))]
  d[, attr_target_performance := mp(x$exp_situation_targeted_company, c("Economic distress" = "the company is in economic distress",
    "Doing well" = "the company is doing well"))]
  d[, attr_target_technology := mp(x$exp_hi_lo_tech_targeted_company, c("High-tech" = "high-tech firm", "Low-tech" = "low-tech firm"))]
  d[, attr_target_sector := mp(x$exp_sector_targeted_company, c(ICT = "information and communication",
    "Finance/insurance" = "financial and insurance activities", "Wholesale and retail trade" = "wholesale and retail trade",
    Manufacturing = "manufacturing", "Real estate" = "real estate", "Transportation and storage" = "transportation and storage",
    Agriculture = "agriculture"))]
  d[, attr_reciprocity := mp(x$exp_openness_foreign_investment_country_acquiring_company, c(
    "Less open" = paste0("the country where the acquiring company is based is less open to foreign investment than ", cc),
    "Equally open" = paste0("the country where the acquiring company is based is equally open to foreign investment as ", cc),
    "More open" = paste0("the country where the acquiring company is based is more open to foreign investment than ", cc)))]
  d[, `:=`(cov_degree = x$educ_recoded, cov_anti_government = x$anti_gov, cov_anti_trade = x$anti_trade,
           cov_working = x$working, cov_right_wing = x$rightwing, cov_china_shock = as.integer(x$china_shock))]
  for (v in c("cov_degree", "cov_anti_government", "cov_anti_trade", "cov_working", "cov_right_wing")) d[get(v) == "", (v) := NA]
  stopifnot(uniqueN(d$id) == counts[[cc]])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("guidi_2026_fdi_", tolower(cc), ".csv")))
}
