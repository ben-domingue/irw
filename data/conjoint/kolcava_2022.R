##Supply-chain regulation conjoint (12 countries) from
##Kolcava, D., Smith, E. K., & Bernauer, T. (2022). Cross-national public acceptance of
##sustainable global supply chain policy instruments. Nature Sustainability, 6(1), 69-80.
##https://doi.org/10.1038/s41893-022-00984-8
##Replication data: Smith, K. (2022), Harvard Dataverse doi:10.7910/DVN/URL6A4, CC0 1.0.
##File read: Sust_supply_DATA.dta (Dataverse "original format" download of Sust_supply_DATA.tab;
##the .tab ingest replaced the en dashes and apostrophes of the level text with U+FFFD, the .dta
##keeps them). Read as text only: Questionnaire.docx (US English instrument), Sust_supply_CODING.do
##(level text of every language, outcome coding), Sust_supply_ANALYSIS.do, Readme.txt.
##Usage: Rscript kolcava_2022.R <dir holding Sust_supply_DATA.dta> <output dir>
##
##24,003 online respondents, about 2,000 in each of 12 countries (BE, CA, CH, DE, ES, FR, IT,
##JA = Japan, KO = South Korea, NL, UK, US), 2021. Five paired tasks (choice1..choice5; profile
##1 = Proposal A, 2 = Proposal B) of proposals for a new supply-chain disclosure law, 3 attributes:
##  attr_size: which companies the law applies to (4 levels);
##  attr_strictness: reporting requirements (3 levels);
##  attr_enforcement: what government can do if companies violate them (3 levels).
##Attribute text is the text stored in the data, i.e. as piped into the survey, in the
##respondent's language (9 language versions; CODING.do lists each), with the <b></b> bold
##tags removed and whitespace trimmed. The attribute order was fixed (questionnaire Block 10).
##TABLES: one per country (kolcava_2022_supply_chain_<country>): the level text differs by
##language and cannot be shared, and the authors report results by country (ANALYSIS.do
##Figure 2) as well as pooled. Countries with more than one language (BE: Dutch "BE"/French/
##English; CA; CH) keep each respondent's text; cov_language = the Qualtrics language code.
##The stored text's language follows cov_language (in Belgium a few EN respondents have Dutch
##or French text); kept as stored. TRANSLATION ERROR AS STORED: the Dutch (NL) middle
##strictness level reads "Strenger – vertrouwelijk jaarverslag, geen verplichte informatie"
##("no mandatory information", like the lowest level; English: "with mandatory summary
##information"); the same text is in CODING.do, so the Netherlands respondents probably saw it.
##Outcomes:
##  choice (Q10.4): "Suppose you had to decide between the two proposals in a vote today. Would
##    you rather support Proposal A or Proposal B?" Forced; exactly one per task.
##  rating (Q10.2 / Q10.3): "If you were presented Proposal A [B] today, would you be opposed or
##    in favour of it?" Source codes 1 In favor / 2 Opposed, stored as 1 = in favour,
##    0 = opposed (the authors' CODING.do sup_alt_ coding).
##trial_info_treatment: the information block shown before the conjoint, randomized
##(ExpA, CODING.do: 1 Control, 2 Con Market, 3 Pro Market).
##Covariates (raw codes; only these are in the deposit, no gender/age/education):
##cov_ideology (poli_ori, 1 left .. 11 right, asked after the conjoint), cov_support_regulation
##(Q5_6, 1 strongly disagree .. 7 strongly agree, pre-conjoint), cov_env_2..cov_env_8 (Q16_2_1..
##Q16_8_1, environmental-attitude items, 1-7), cov_attention_check_code (Q16_1, "please select
##the triangle": answer image codes 5/6/7/9, which image is the triangle is not documented;
##99.6% chose 9), cov_svo_2..cov_svo_7 (Q18_2..Q18_7 social-value-orientation slider items,
##1-9; 44 missing).
##Dropped: ResponseId (Qualtrics id; re-keyed), ExpB and Q11_10_1/Q12_10_1/Q13_10_1 (a separate
##post-conjoint policy-probe experiment), the authors' derived scales.
##N: 24,003 respondents, 10 rows each, = the LONG file's 240,030 rows; per country 2,000-2,002
##(CODING.do factor() uses n = 24003).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "Sust_supply_DATA.dta"))
s <- as.data.table(zap_labels(k))
stopifnot(nrow(s) == 24003, !anyDuplicated(s$ResponseId))
s[, id := seq_len(.N)]
clean <- function(x) trimws(gsub("\\s+", " ", gsub("</?b>", "", x)))
rows <- list()
for (t in 1:5) for (p in 1:2) {
  q <- c("A", "B")[p]
  rows[[length(rows) + 1]] <- s[, .(id, task = t, profile = p,
    choice = as.integer(get(sprintf("A%d_Q10_4", t)) == p),
    rating = as.integer(c(1L, 0L)[get(sprintf("A%d_Q10_%d", t, p + 1L))]),
    attr_size = clean(get(sprintf("choice%d_size%d", t, p))),
    attr_strictness = clean(get(sprintf("choice%d_strict%d", t, p))),
    attr_enforcement = clean(get(sprintf("choice%d_action%d", t, p))))]
}
d <- rbindlist(rows)
stopifnot(!anyNA(d), d[, all(attr_size != "" & attr_strictness != "" & attr_enforcement != "")],
          d[, sum(choice), .(id, task)][, all(V1 == 1)],
          uniqueN(d$attr_size) == 36, uniqueN(d$attr_strictness) == 27, uniqueN(d$attr_enforcement) == 27)
stopifnot(all(s$ExpA %in% c("1", "2", "3")))
cv <- s[, .(id, country, cov_language = language,
            trial_info_treatment = c("Control", "Con Market", "Pro Market")[as.integer(ExpA)],
            cov_ideology = as.integer(poli_ori), cov_support_regulation = as.integer(Q5_6),
            cov_env_2 = as.integer(Q16_2_1), cov_env_3 = as.integer(Q16_3_1), cov_env_4 = as.integer(Q16_4_1),
            cov_env_5 = as.integer(Q16_5_1), cov_env_6 = as.integer(Q16_6_1), cov_env_7 = as.integer(Q16_7_1),
            cov_env_8 = as.integer(Q16_8_1), cov_attention_check_code = as.integer(Q16_1),
            cov_svo_2 = as.integer(Q18_2), cov_svo_3 = as.integer(Q18_3), cov_svo_4 = as.integer(Q18_4),
            cov_svo_5 = as.integer(Q18_5), cov_svo_6 = as.integer(Q18_6), cov_svo_7 = as.integer(Q18_7))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating", "attr_size", "attr_strictness", "attr_enforcement", "trial_info_treatment"))
cn <- c(BE = "belgium", CA = "canada", CH = "switzerland", DE = "germany", ES = "spain", FR = "france", IT = "italy",
        JA = "japan", KO = "korea", NL = "netherlands", UK = "uk", US = "us")
stopifnot(all(d$country %in% names(cn)))
for (c1 in names(cn)) {
  x <- d[country == c1][, country := NULL]
  setorder(x, id, task, profile)
  x[, id := match(id, unique(id))]
  fwrite(x, file.path(out, paste0("kolcava_2022_supply_chain_", cn[[c1]], ".csv")))
}
