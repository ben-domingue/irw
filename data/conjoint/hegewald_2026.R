##Urban-rural stereotype single-profile conjoint (nine European countries) from
##Hegewald, S. (2026). The urban-rural divide in people's minds: Stereotypes of urbanites and
##ruralites in nine European countries. Political Behavior.
##https://doi.org/10.1007/s11109-026-10160-9
##Replication data: Harvard Dataverse doi:10.7910/DVN/8F5FQB, CC0 1.0, no restricted files.
##File read: conjoint_data.tab (as the original conjoint_data.csv). Hegewald_Polit_Behav_
##replication.R read as text (covariate codings). The published article could not be
##downloaded; design facts, question wording and level text are from the author's preprint of
##the same experiment (Hegewald 2024, "Cosmopolitan cities against nationalist hinterlands",
##OSF preprint doi:10.31219/osf.io/x25ne, Table 1 and footnotes 3-6), whose N (9,125) matches.
##Usage: Rscript hegewald_2026.R <dir holding conjoint_data.csv> <output dir>
##
##9,125 adults in CZ, DE, DK, GR (source code EL), ES, FR, HU, IT, PL (Bilendi online panels,
##Feb-Mar 2023, national quotas), about 1,000 per country. The author pools the countries
##(country fixed effects) and the attribute set is common, so ONE TABLE with cov_country.
##Each respondent saw 4 hypothetical person profiles one per screen (task = profile_no 1-4,
##profile = 1 always: a single-profile design), 5 attributes. Three questions per profile:
##  rating_rural: "Looking at the description of the person above, do you think that this
##    person typically lives in an urban area or typically lives in a rural area?" 0 = typically
##    lives in an urban area, 1 = typically lives in a rural area (source guess_rur).
##  rating_sureness: "You have indicated that the person shown above typically lives in an
##    urban area/typically lives in a rural area. How sure are you about this choice?"
##    1 = very sure, 2 = somewhat sure, 3 = somewhat unsure, 4 = very unsure (source uncer_num,
##    as stored; higher = LESS sure).
##  rating: feeling thermometer 0-100 ("...Scores between 50 and 100 mean that you have
##    positive and warm feelings toward this person... Looking at this person, how do you
##    feel?"), 100 = warmest.
##Attribute text: the preprint's Table 1 English master text, with the country placeholder
##written as "[country]"; respondents saw national-language versions naming their own country
##(not deposited). Source short labels -> text: Europhile/Eurosceptic -> "Believes that
##[country]'s membership of the European Union is a good/bad thing"; Pro-/Anti-immigrant ->
##"Believes that immigrants make [country] a better/worse place to live"; class "Identifies as
##upper middle class/working class"; education "Holds a university degree/Does not hold a
##university degree"; age "Is 25 years old/Is 65 years old". All levels drawn independently and
##uniformly (preprint); attribute order randomized per respondent, held across the 4 profiles,
##not recorded.
##Covariates: cov_country (ISO 3166 alpha-2; EL -> GR), cov_residence (v_16: Very rural /
##Rather rural / Rather urban / Very urban, the author's labels), cov_eu_membership (answer
##text: EU membership a good/bad/neither thing), cov_immigration (0-10; the author codes < 5 as
##anti-immigrant, so higher = more pro-immigrant), cov_education (High/Low, as stored),
##cov_age (years), cov_income_decile (1-10). Dropped: the author's derived
##guess_rur_with_sureness, the per-country respondent number lfdn (id = group_id, already an
##anonymous integer). No survey weight is deposited.
##N: 9,125 respondents = preprint summary table. Spot check: OLS of rating_rural on the five
##attributes with country fixed effects gives Eurosceptic 0.12, anti-immigrant 0.09, working
##class 0.12, no degree 0.19, 65 years 0.07 = the preprint's reported AMCEs (results section).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjoint_data.csv"))
stopifnot(nrow(s) == 36500, s[, .N, group_id][, all(N == 4)], s[, uniqueN(profile_no), group_id][, all(V1 == 4)])
txt <- list(cosnat1 = c(Europhile = "Believes that [country]'s membership of the European Union is a good thing",
                        Eurosceptic = "Believes that [country]'s membership of the European Union is a bad thing"),
            cosnat2 = c(`Pro-immigrant` = "Believes that immigrants make [country] a better place to live",
                        `Anti-immigrant` = "Believes that immigrants make [country] a worse place to live"),
            class = c(`Upper middle class identity` = "Identifies as upper middle class", `Working class identity` = "Identifies as working class"),
            educ = c(`University educated` = "Holds a university degree", `Not university educated` = "Does not hold a university degree"),
            age = c(`25 years old` = "Is 25 years old", `65 years old` = "Is 65 years old"))
for (v in names(txt)) stopifnot(all(s[[v]] %in% names(txt[[v]])))
res <- c("Very rural", "Rather rural", "Rather urban", "Very urban")
d <- s[, .(id = as.integer(group_id), task = as.integer(profile_no), profile = 1L,
           rating = as.integer(thermo), rating_rural = as.integer(guess_rur), rating_sureness = as.integer(uncer_num),
           attr_eu = unname(txt$cosnat1[cosnat1]), attr_immigration = unname(txt$cosnat2[cosnat2]),
           attr_class = unname(txt$class[class]), attr_education = unname(txt$educ[educ]), attr_age = unname(txt$age[age]),
           cov_country = fifelse(cntry == "EL", "GR", cntry), cov_residence = res[v_16], cov_eu_membership = EU_memb,
           cov_immigration = as.integer(immi), cov_education = educ_resp, cov_age = as.integer(age_resp), cov_income_decile = as.integer(inc_dec))]
stopifnot(!anyNA(d[, .(rating, rating_rural, rating_sureness)]), all(d$rating %in% 0:100), d[, uniqueN(cov_country), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hegewald_2026_urban_rural.csv"))
