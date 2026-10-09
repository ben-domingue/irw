##Agri-environmental scheme DCE, English farmers, from
##Tyllianakis, E., Will, M., Václavík, T., & Ziv, G. (2025). Drivers and preferences of European farmers
##for agri-environmental public goods schemes: A two-stage analysis. Journal for Nature Conservation, 86,
##126912. https://doi.org/10.1016/j.jnc.2025.126912
##Data: Will, M., Biffi, S., Tyllianakis, E., Vaclavik, T., & Müller, B. Farm-level survey data on
##participation in agri-environmental schemes from regions in Germany, Czechia and England. Zenodo,
##doi:10.5281/zenodo.17551096, CC BY 4.0 (record licence), open access.
##Files read: Data_EN_cleaned.csv, Codebook_BESTMAP_Survey.xlsx, Survey_EN.pdf. The choice cards are
##IMAGES in Survey_EN.pdf (pages 8-13 = group 1 scenarios 1-6, Q2.1-Q2.16; pages 16-21 = group 2,
##Q3.1-Q3.16); the design below was transcribed from them by eye. Every transcribed payment is one of the
##article's UK payment levels (Appendix Table A), checked in the script.
##Usage: Rscript tyllianakis_2025.R <raw dir> <output dir>
##
##107 English farmers (online, Cint panel, Sep 2021 - Apr 2022). Labelled DCE, Ngene S-efficient fixed
##blocked design: 2 blocks (Condition 1 = group 1, Condition 2 = group 2; trial_block) x 6 choice cards.
##Each card shows four schemes, always in the order Flower areas/strips, Cover crops, Maintaining
##permanent grassland, Converting arable land to permanent grassland (profile 1-4 = that order), plus a
##"No scheme" column ("You will not receive funding for any agri-environmental practices you may carry
##out on your farm."): the opt-out, not a profile. Group 1 shows No scheme last, group 2 first (so in
##group 2 the four schemes sit one column to the right; profile numbers still count schemes only).
##attr_scheme is the alternative label (fixed per position, not randomized); attr_duration ("1 year",
##"5 years", "10 years"), attr_advisory_support ("Yes, free of charge" / "No"), attr_admin_effort
##(Low / Medium / High), attr_payment ("£620 per hectare", yearly payment) as displayed. Payment levels are
##scheme-specific (five per scheme, article Appendix A), so payment is restricted by scheme.
##choice: "Scenario x/6: Please choose your preferred scheme. ... If you do not have permanent grassland,
##  please do not consider the option "Maintaining permanent grassland"." Options 1-4 schemes, 5 = No
##  scheme (same codes in both groups; Survey_EN.pdf). opt-out yes: a No-scheme task has choice 0 on all
##  four profiles.
##rating_land_share: on the chosen scheme's row only (NA elsewhere): "I would apply the chosen scheme on
##  ___ % of my arable land." (Q2.2/Q3.2..., after flower strips, cover crops, conversion) or "... % of my
##  permanent grassland." (Q2.3/Q3.3..., after maintaining grassland); 0-100 as entered.
##Covariates (codebook text): cov_gender (Q9.7: Male = male, Female = female, Other = other, Prefer not to
##say -> NA), cov_age_group (Q9.8 band text; Prefer not to say -> NA), cov_education (Q9.2 "What is the
##highest level of farming education you have completed?"; Prefer not to say -> NA), cov_farm_type
##(Q1.2), cov_organic (Q1.3), cov_years_farming (Q9.1), cov_duration_sec (Qualtrics Duration, whole
##survey).
##Dropped: IP addresses (98 rows), latitude/longitude (98), farm postcode district (Q1.1), Qualtrics and
##Cint panel identifiers (ResponseId, rid, RISN, transaction_id, Research_ID, cintid, ProjectToken, ...),
##free text, all other survey blocks and the authors' derived fractions. Respondent id = row order.
##No survey weight. N = 107 matches the article's UK observations (Table 2).
##NOT in this table: the German (74) and Czech (69) case studies of the same deposit. The article pools
##all three (same statistical design), but their cards are German/Czech text with EUR payments and
##different card contents, and each sample is under 100.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Data_EN_cleaned.csv"))
sch <- c("Flower areas/strips", "Cover crops", "Maintaining permanent grassland",
         "Converting arable land to permanent grassland")
# design[block][[card]]: per scheme c(duration, advisory, admin, payment), transcribed from Survey_EN.pdf images
Y <- "Yes, free of charge"; N <- "No"
card <- function(...) matrix(c(...), ncol = 4, byrow = TRUE)
des <- list(
  list(card("10 years", Y, "Low", "620",   "1 year", N, "Low", "180",
            "10 years", Y, "High", "190",  "5 years", N, "High", "1,100"),
       card("10 years", N, "Medium", "690", "1 year", N, "Medium", "135",
            "5 years", Y, "High", "190",   "10 years", N, "Low", "800"),
       card("10 years", N, "Low", "410",   "1 year", N, "Low", "135",
            "5 years", N, "Low", "285",    "10 years", Y, "Medium", "1,250"),
       card("1 year", N, "Medium", "410",  "5 years", Y, "Medium", "120",
            "10 years", N, "Medium", "285", "10 years", Y, "Low", "1,100"),
       card("1 year", Y, "Medium", "825",  "5 years", N, "Medium", "150",
            "10 years", Y, "Low", "240",   "5 years", N, "Low", "800"),
       card("5 years", Y, "High", "550",   "10 years", Y, "High", "90",
            "10 years", Y, "High", "190",  "5 years", N, "Medium", "1,665")),
  list(card("5 years", Y, "Low", "620",    "1 year", Y, "High", "120",
            "1 year", Y, "Medium", "215",  "10 years", N, "High", "1,400"),
       card("5 years", N, "High", "550",   "10 years", N, "Low", "180",
            "1 year", N, "Low", "140",     "5 years", Y, "High", "1,250"),
       card("1 year", Y, "Low", "825",     "10 years", Y, "High", "90",
            "5 years", N, "Medium", "140", "10 years", Y, "Medium", "1,100"),
       card("10 years", N, "High", "550",  "5 years", N, "Low", "150",
            "1 year", N, "Low", "140",     "5 years", Y, "Low", "800"),
       card("5 years", Y, "Medium", "410", "10 years", Y, "Medium", "120",
            "1 year", Y, "High", "215",    "5 years", Y, "High", "1,665"),
       card("1 year", N, "High", "690",    "5 years", Y, "High", "90",
            "5 years", N, "Medium", "240", "10 years", N, "Medium", "1,400")))
paylev <- list(c(410, 550, 620, 690, 825), c(90, 120, 135, 150, 180), c(140, 190, 215, 240, 285),
               c(800, 1100, 1250, 1400, 1665))                  # article Appendix Table A, UK
for (b in 1:2) for (t in 1:6) for (j in 1:4)
  stopifnot(as.numeric(gsub(",", "", des[[b]][[t]][j, 4])) %in% paylev[[j]])
pick <- list(paste0("Q2.", c(1, 4, 7, 10, 13, 16)), paste0("Q3.", c(1, 4, 7, 10, 13, 16)))
arab <- list(paste0("Q2.", c(2, 5, 8, 11, 14, 17), "_1"), paste0("Q3.", c(2, 5, 8, 11, 14, 17), "_1"))
gras <- list(paste0("Q2.", c(3, 6, 9, 12, 15, 18), "_1"), paste0("Q3.", c(3, 6, 9, 12, 15, 18), "_1"))
blk <- as.integer(s$Condition); stopifnot(all(blk %in% 1:2))
rows <- list()
for (i in seq_len(nrow(s))) {
  b <- blk[i]
  stopifnot(all(!is.na(unlist(s[i, pick[[b]], with = FALSE]))), all(is.na(unlist(s[i, pick[[3 - b]], with = FALSE]))))
  for (t in 1:6) {
    ch <- as.integer(s[[pick[[b]][t]]][i]); stopifnot(ch %in% 1:5)
    sh <- if (ch == 3) s[[gras[[b]][t]]][i] else if (ch %in% c(1, 2, 4)) s[[arab[[b]][t]]][i] else NA
    m <- des[[b]][[t]]
    rows[[length(rows) + 1]] <- data.table(id = i, task = t, profile = 1:4, choice = as.integer(1:4 == ch),
      rating_land_share = ifelse(1:4 == ch, as.numeric(sh), NA_real_),
      attr_scheme = sch, attr_duration = m[, 1], attr_advisory_support = m[, 2], attr_admin_effort = m[, 3],
      attr_payment = paste0("£", m[, 4], " per hectare"), trial_block = b)
  }
}
d <- rbindlist(rows)
cv <- data.table(id = seq_len(nrow(s)),
  cov_gender = c("male", "female", "other", NA)[s$Q9.7],
  cov_age_group = c("Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85 or older", NA)[s$Q9.8],
  cov_education = c("No training", "Vocational/professional training", "Bachelor's degree", "Master's degree",
                    "Professional degree", "Doctorate degree", NA)[s$Q9.2],
  cov_farm_type = c("Full-time individual/family-run farm", "Part-time individual/family-run farm",
                    "Cooperative of farms", "Company owned", "Other")[s$Q1.2],
  cov_organic = c("No", "Yes, certified organic", "In transition to fully organic", "Mixed, organic/non-organic")[s$Q1.3],
  cov_years_farming = as.integer(s$Q9.1),
  cov_duration_sec = as.integer(s$Duration..in.seconds.))
stopifnot(all(s$Q9.7 %in% 1:4), all(s$Q9.8 %in% 1:10), all(s$Q9.2 %in% 1:7), all(s$Q1.2 %in% 1:5), all(s$Q1.3 %in% 1:4))
d <- merge(d, cv, by = "id")
stopifnot(d[, sum(choice), by = .(id, task)][, all(V1 <= 1)], d[choice == 0, all(is.na(rating_land_share))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "tyllianakis_2025_agri_schemes_uk.csv"))
