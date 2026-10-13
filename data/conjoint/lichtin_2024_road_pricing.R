##Road-pricing ("mobility pricing") policy-package conjoint (Swiss Mobility Panel, wave 2) from
##Lichtin, F. M., Smith, E. K., Axhausen, K. W., & Bernauer, T. (2024). How to design publicly
##acceptable road pricing? Experimental insights from Switzerland. Ecological Economics, 218, 108102.
##https://doi.org/10.1016/j.ecolecon.2023.108102
##Replication data: Zenodo doi:10.5281/zenodo.18255559 (concept DOI; also 10.5281/zenodo.18255560),
##CC BY 4.0. Files read: LichtinSmithAxhausenBernauerRoadPricing_DATA.dta (a data extract, 3,448
##respondents), the Stata analysis file ..._ANALYSIS.do (read as text: the English/German/French/
##Italian level texts of the five attributes) and Lichtin_Smith_Axhausen_Bernauer_Questionnaire.pdf
##(task wording, attribute grid, information treatments). The extract holds no demographics except
##household income, rural-urban type and car access; no name/ip/location fields.
##Usage: Rscript lichtin_2024_road_pricing.R <dir holding the .dta> <output dir>
##Output: lichtin_2024_road_pricing.csv. This is a DIFFERENT experiment from lichtin_2024_public_transport
##(wave 4, OSF g7k8m).
##Design: Swiss residents (online panel, 2021; German, French, Italian, with some English), 5 tasks, each
##a side-by-side pair of mobility-pricing "Proposal A / Proposal B" (profile 1 = A = package <t>a,
##profile 2 = B = package <t>b), 5 attributes (the packages are pipe-delimited strings split here):
##motorway toll per km, city-centre entrance fee per day, average motorway peak speed, average urban
##peak speed, use of the extra revenue (5 levels each). The deposit stores each profile in the
##respondent's survey language; the levels are mapped to the English text (the do-file's
##item*_en lists, which equal the English strings that 4% of respondents saw), so label_language is en and
##display_language de;fr;it;en. cov_language (de/fr/it/en) is read off the level text of the respondent's first task (one respondent, id 2756, switched from Italian to German in task 5).
##Outcomes (one table; same tasks):
##  choice: "Suppose you had to decide between the two proposals in a referendum today. Would you rather
##    support Proposal A or Proposal B?" (B_2_X). Stored per profile 0/1; forced choice, no opt-out.
##  rating: "How much would you favor or oppose Proposal A [B]?" (B_3_X / B_4_X), stored 1 = Strongly
##    favor, 2 = Somewhat favor, 3 = Neutral, 4 = Somewhat oppose, 5 = Strongly oppose (LOWER = more
##    favourable; kept raw, the authors' do-file reverses it for their figures). "Don't know" (9) -> NA.
##Tasks with no recorded choice (1,094 of 17,240 respondent-tasks, 6%) are dropped whole (a choice column
##must be on every profile of a task); no other tasks are dropped. 3,359 of the 3,448 respondents remain (89 had no recorded choice in any task).
##trial_info_treatment: between-respondent information vignette shown before the tasks (Control / CO2 emissions
##/ Air pollution / Noise pollution treatment; a short text about benefits of mobility pricing), a single
##randomised factor on respondents, not a profile attribute.
##Randomization restrictions, level probabilities and attribute order (the questionnaire lists the grid in
##a fixed row order) are not documented beyond that; all five attributes have 5 levels, shares near equal.
##Covariates: cov_household_income (w1_q74 value label, CHF/month categories; "no answer" -> NA),
##cov_urban_rural (are_rural_urban_2012 label, German: Staedtisch / Intermediaer / Laendlich),
##cov_car_own (w2_q1x1, 1 = won/owns a car "Yes, I won a car." per the value label, 0 = not selected).
##Dropped: environmental-attitude items (w1_q52*, w1_q53*), car-access company item.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "LichtinSmithAxhausenBernauerRoadPricing_DATA.dta")))
stopifnot(nrow(s) == 3448, uniqueN(s$ID) == 3448)
num <- function(x) as.integer(sub("^\\s*([0-9]+).*$", "\\1", x))
rev_map <- c("die Staatsschulden zu reduzieren." = "Reduce Federal Government Deficit",
  "die Einkommenssteuern zu reduzieren." = "Reduce Income Taxes", "die Benzinsteuern zu reduzieren." = "Reduce Petrol Taxes",
  "Investitionen im öffentlichen Verkehr zu tätigen" = "Fund Public Transportation",
  "‘grüne’ Infrastruktur zu finanzieren" = "Fund Green Infrastructure",
  "réduire le déficit du gouvernement fédéral." = "Reduce Federal Government Deficit",
  "réduire l’impôt sur le revenu." = "Reduce Income Taxes", "réduire les taxes sur l’essence." = "Reduce Petrol Taxes",
  "financer des infrastructures de transport public." = "Fund Public Transportation",
  "financer des infrastructures «vertes»." = "Fund Green Infrastructure",
  "ridurre il deficit del governo federale." = "Reduce Federal Government Deficit",
  "ridurre le imposte sul reddito." = "Reduce Income Taxes", "ridurre le imposte sul carburante." = "Reduce Petrol Taxes",
  "finanziare infrastrutture per il trasporto pubblico." = "Fund Public Transportation",
  "finanziare infrastrutture “verdi”." = "Fund Green Infrastructure",
  "Reduce Federal Government Deficit" = "Reduce Federal Government Deficit", "Reduce Income Taxes" = "Reduce Income Taxes",
  "Reduce Petrol Taxes" = "Reduce Petrol Taxes", "Fund Public Transportation" = "Fund Public Transportation",
  "Fund Green Infrastructure" = "Fund Green Infrastructure")
lang_of <- function(x2) fifelse(grepl("pro Tag", x2), "de", fifelse(grepl("par jour", x2), "fr", fifelse(grepl("al giorno", x2), "it", fifelse(grepl("per day", x2), "en", NA_character_))))
L <- list()
for (t in 1:5) for (p in 1:2) {
  sf <- c("a", "b")[p]
  parts <- tstrsplit(s[[paste0("w2_package_", t, sf)]], "|", fixed = TRUE)
  parts <- lapply(parts, trimws)
  rv <- unname(rev_map[parts[[5]]]); stopifnot(!anyNA(rv))
  ch <- as.integer(s[[paste0("w2_choice_", t, sf)]]); rt <- as.integer(s[[paste0("w2_rating_", t, sf)]]); rt[rt == 9L] <- NA
  L[[length(L) + 1]] <- data.table(id = s$ID, task = t, profile = p, choice = ch, rating = rt,
    attr_motorway_toll = paste0(num(parts[[1]]), " Rp/km"), attr_entrance_fee = paste0(num(parts[[2]]), " CHF per day"),
    attr_motorway_speed = paste0(num(parts[[3]]), " km/hr"), attr_urban_speed = paste0(num(parts[[4]]), " km/hr"),
    attr_revenue_use = rv, lang = lang_of(parts[[2]]))
}
d <- rbindlist(L)
stopifnot(!anyNA(d$lang), !anyNA(d[, .(attr_motorway_toll, attr_entrance_fee, attr_motorway_speed, attr_urban_speed)]),
          d[, uniqueN(attr_motorway_toll)] == 5, d[, uniqueN(attr_revenue_use)] == 5)
d[, lang_id := lang[1], id]; stopifnot(d[, uniqueN(lang), id][V1 > 1, .N] <= 1)  # one respondent (source id 2756) shows Italian text in tasks 1-4 and German in task 5; cov_language = first task
bad <- d[, .(n = sum(choice, na.rm = TRUE), na = anyNA(choice)), .(id, task)]
stopifnot(bad[na == FALSE, all(n == 1)], bad[, all(na == (n == 0) | !na)])
cat("tasks with missing choice:", bad[na == TRUE, .N], "of", nrow(bad), "\n")
d <- merge(d, bad[na == FALSE, .(id, task)], by = c("id", "task"))
tr <- c("Control", "CO2 emissions", "Noise pollution", "Air pollution")  # value labels 1..4 (Control, CO2, Noise, Air)
cv <- s[, .(id = ID, trial_info_treatment = names(attr(w2_cj_treat, "labels"))[match(as.integer(w2_cj_treat), attr(w2_cj_treat, "labels"))],
            cov_household_income = names(attr(w1_q74, "labels"))[match(as.integer(w1_q74), attr(w1_q74, "labels"))],
            cov_urban_rural = names(attr(are_rural_urban_2012, "labels"))[match(as.integer(are_rural_urban_2012), attr(are_rural_urban_2012, "labels"))],
            cov_car_own = as.integer(w2_q1x1))]
cv[cov_household_income == "no answer", cov_household_income := NA]
d <- merge(d, cv, by = "id"); setnames(d, "lang_id", "cov_language"); d[, lang := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "lichtin_2024_road_pricing.csv"))
cat("rows", nrow(d), "respondents", uniqueN(d$id), "\n")
