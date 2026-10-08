##Business-partner conjoint with Senegalese firms from
##Bhandari, A. (2023). Social, formal, and political determinants of trade under weak rule
##of law: Experimental evidence from Senegalese firms. Comparative Political Studies, 56(2),
##163-192. https://doi.org/10.1177/00104140221089648
##Replication data: Harvard Dataverse doi:10.7910/DVN/FOV6WJ, CC0 1.0. Files read:
##conjoint_data.RData (one data frame `conjoint_data`, loaded into its own environment);
##Codebook.pdf and analysis.R read as text. The article (paywalled) was not read.
##Usage: Rscript bhandari_2023.R <dir holding conjoint_data.RData> <output dir>
##
##2,389 firm respondents (neighbourhoods of Dakar, per the codebook), 4 rounds of 2
##hypothetical business deals each. task = `round`, profile = `profile` (1 = left, 2 =
##right; both recorded). Six attributes, level text as stored ("Character string ...
##presented in the conjoint experiment", codebook; English, while respondents probably saw
##French or Wolof; not documented): contract (Informal/Formal contract), personal connection
##(Not politically connected / Friend of local mayor / of MP / of president; the codebook
##calls this "personal connection"), political affiliation, business size, ethnicity and
##religion of the firm manager. Attribute order was randomized: `Randomization scheme`
##(1-4, "which randomization order of conjoint attributes respondent received") varies by
##round and is kept as trial_attribute_order, but the four orders are not documented, so no
##attrpos_ columns. In 4 of 9,556 rounds the two deals are identical.
##Outcomes. Each question offered Deal 1 / Deal 2 / Neither / Both (98 refused, 99 don't
##know), so each deal is judged on its own and both are per-profile 0/1 ratings (as in
##donnaloja_2022), equal to the authors' preferred_firm and breach_risk indicators:
##  rating = 1 if the respondent said they would be more likely to choose this deal
##    (codebook: "which deal more likely to choose"); "Both" -> 1 on both, "Neither" -> 0.
##  rating_breach = 1 if the respondent said this deal was more likely to end in breach
##    (higher = WORSE; not reversed).
##  Refusals and don't-knows are left blank (prefer: 159 rounds; breach: 758 rounds); rows
##  blank on both are omitted, which drops 7 respondents: 2,382 respondents, 18,962 rows.
##  The article's N was not checked (paywalled). Spot check (OLS, SEs clustered by id):
##  informal vs formal contract -0.27 on rating; no published number was available to compare.
##Covariates: cov_female (codebook gender 1 = Female), cov_age (years; 8 values above 100,
##data-entry errors up to 707,000,000, set blank), cov_formal_firm (1 = formal firm).
##DROPPED: KEY (ODK instance uuid; re-keyed to integers), neighbourhood and its free-text
##"other", the free-text ethnicity/religion/party "other" fields, the authors' coethnic and
##coreligion flags (derived from the profile), and the other firm survey items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "conjoint_data.RData"), envir = e)
s <- as.data.table(e$conjoint_data)
stopifnot(nrow(s) == 19112, uniqueN(s$KEY) == 2389, s[, .N, KEY][, all(N == 8)], s[, .N, .(KEY, round, profile)][, all(N == 1)],
          s[, uniqueN(prefer), .(KEY, round)][, all(V1 == 1)], s[, uniqueN(breach), .(KEY, round)][, all(V1 == 1)])
judge <- function(ans, prof) fifelse(ans %in% c(98, 99), NA_integer_, as.integer(ans == prof | ans == 4))
key <- sort(unique(as.character(s$KEY)))
d <- s[, .(id = match(as.character(KEY), key), task = as.integer(round), profile = as.integer(profile),
           rating = judge(prefer, profile), rating_breach = judge(breach, profile),
           attr_contract = as.character(c_contract), attr_personal_connection = as.character(c_personal_cxn),
           attr_political_affiliation = as.character(c_political_affil), attr_business_size = as.character(c_business_size),
           attr_manager_ethnicity = as.character(c_ethnicity), attr_manager_religion = as.character(c_religion),
           trial_attribute_order = as.integer(`Randomization scheme`),
           cov_female = as.integer(gender), cov_age = fifelse(age > 100, NA_integer_, as.integer(pmin(age, 1e6))),
           cov_formal_firm = as.integer(formal_firm))]
stopifnot(all(d$rating == s$preferred_firm, na.rm = TRUE), all(d$rating_breach == s$breach_risk, na.rm = TRUE))
d <- d[!(is.na(rating) & is.na(rating_breach))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bhandari_2023_trade_partners.csv"))
