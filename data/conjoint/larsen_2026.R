##Local-preservationism (NIMBY) vignette experiment, Denmark, from
##Larsen, M. V., & Nyholt, N. (2026). Understanding nimbyism as local preservationism.
##The Journal of Politics. https://doi.org/10.1086/741691
##Replication data: Harvard Dataverse doi:10.7910/DVN/IJEUE1, CC0 1.0. File read: sample.parquet (arrow).
##Codebook.pdf, readme.txt and analysis.R read as text (not run). The vignette wording (Table 1) is from the
##authors' OSF preprint (martinvlarsen.com/nimbyism.pdf, 8-page extract). municipalities.gpkg is not used.
##Usage: Rscript larsen_2026.R <dir holding sample.parquet> <output dir>
##
##28,850 Danish adults (stratified random sample from the population register, Epinion, June 2023), ONE vignette
##each (task = profile = 1; the file's `id` is a string 00001..28850 that is kept as the integer id).
##Vignette (paper Table 1): "The city council is considering whether to allow construction of [project type] on a
##plot of land in the municipality. It will be a construction project covering [size] square meters and have
##[height]. The project will be located at the red dot in the map below. [The construction site will be about d km
##from your home.]" Each level of each attribute was drawn with equal probability (paper, p. 12).
##  attr_project_type (proj_type): social housing / owner-occupied housing / rental housing / retail / offices / a public
##      institution / factory premises / a biogas plant / a sewage plant. The deposit stores short tags
##      ("private housing" = owner-occupied housing, "office premises" = offices); level text taken from the article's
##      Table 1; the deposit stores short tags.
##  attr_size_sqm (proj_size): 500 / 1,000 / 10,000 (square meters; tags "500", "1.000", "10.000").
##  attr_height (proj_height): one story / three stories / five stories / seven stories (tags 1, 3, 5, 7).
##  attr_distance_to_home: the project was placed at random in a donut around the respondent's home with outer radius
##      d km and inner radius d-1 km, d = 1..10 equally likely (assigned category dist_c; the realized distance dist_e
##      lies within the band, checked). Shown on a personalized map to 80.6% of respondents and, for half, also stated in
##      text. Text: "0-1 km" ... "9-10 km"; "(not shown)" for the 2,848 respondents (distinfo == "no info") who got
##      neither a map nor the distance text (the control group). The 2,741 text-only respondents (no map) are given the
##      band: the paper says the text states "about d km" (the d of the band), the band text is therefore an
##      approximation of what they read.
##  trial_map_shown ("map"/"no map") and trial_distance_stated_in_text (0/1): the display arms.
##Restrictions: none among type, size, height (all 108 combinations occur, shares near equal); the project was
##re-drawn when the sampled location was impossible (outside the municipality, sea), so realized distance is selected
##for some respondents (paper p. 14: controlled with "never-taker" dummies); the assigned band is as drawn.
##Outcomes (ratings, raw; the Danish wording is not in the deposit, the codebook gives English wording):
##  rating = opposition, "Are you for or against the proposed development project?" 1 I am definitely against ...
##      4 neither for nor against ... 7 I am definitely for; 8 = Don't know (kept as 8, 2,411 respondents). Higher 1-7 =
##      more favourable.
##  rating_poor_fit (fitin) "The project will not fit well into the area.", rating_undesirable_residents (exclusion)
##      "The project will bring people to my area that I don't want here.", rating_congestion "The project will create
##      more congestion.", rating_home_value_drop (homevalue) "The project will reduce the value of my property."
##      (homeowners only, NA otherwise), rating_rent_drop (rentvalue) "The project will reduce my rent" (a subset of
##      renters, NA otherwise), rating_unrealistic (realistic) "It is unrealistic that the municipality will go ahead
##      with such a project." All 1 Completely disagree, 2 Somewhat disagree, 3 Neither agree nor disagree,
##      4 Somewhat agree, 5 Completely agree, 6 Don't know (kept as 6).
##Covariates: cov_gender (Man = male, Woman = female, 35 NA), cov_age_group (20-39 / 40-59 / 60+), cov_homeowner
##(Homeowner / Renter), cov_ideology (left-right self-placement value labels: Left-wing ... Right-wing, NA for none),
##cov_survey_weight (design_weight, mean 1.0, age/gender/education post-stratification weight of the authors).
##Dropped: zip code (anonymised fixed-effect id), municipality, education (the deposit relabels it "Education type N"),
##income, housing situation, the eight local-preservationism items and the other attitude items, minutes to site,
##never-taker dummies, the dichotomised and derived variables (proj_large, *_d, dist_3, dist_12, *_weight except
##design_weight), inverse-probability weights (their probabilities are scrambled by the authors).
##N matches the paper (n = 28,850).
suppressMessages({library(arrow); library(data.table); library(haven)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_parquet(file.path(raw, "sample.parquet")))
stopifnot(nrow(k) == 28850, uniqueN(k$id) == 28850)
d <- data.table(id = as.integer(k$id), task = 1L, profile = 1L)
iv <- function(x) as.integer(zap_labels(x))
d[, rating := iv(k$opposition)]
d[, rating_poor_fit := iv(k$fitin)][, rating_undesirable_residents := iv(k$exclusion)][, rating_congestion := iv(k$congestion)]
d[, rating_home_value_drop := iv(k$homevalue)][, rating_rent_drop := iv(k$rentvalue)][, rating_unrealistic := iv(k$realistic)]
tp <- c("social housing" = "social housing", "private housing" = "owner-occupied housing", "rental housing" = "rental housing",
        "a public institution" = "a public institution", "office premises" = "offices", "factory premises" = "factory premises",
        "a biogas plant" = "a biogas plant", "a sewage plant" = "a sewage plant", "retail premises" = "retail")
stopifnot(all(as.character(k$proj_type) %in% names(tp)))
d[, attr_project_type := tp[as.character(k$proj_type)]]
d[, attr_size_sqm := c("500" = "500", "1.000" = "1,000", "10.000" = "10,000")[as.character(k$proj_size)]]
d[, attr_height := c("1" = "one story", "3" = "three stories", "5" = "five stories", "7" = "seven stories")[as.character(k$proj_height)]]
dc <- as.integer(k$dist_c)
d[, attr_distance_to_home := ifelse(k$distinfo == "info", paste0(dc - 1L, "-", dc, " km"), "(not shown)")]
d[, trial_map_shown := as.character(k$map)]
d[, trial_distance_stated_in_text := as.integer(as.character(k$text))]
d[, cov_gender := c(Man = "male", Woman = "female")[as.character(k$gender)]]
d[, cov_age_group := gsub("–", "-", as.character(k$age))]
d[, cov_homeowner := as.character(k$homeowner)]
lb <- attr(k$ideol, "labels"); d[, cov_ideology := names(lb)[match(iv(k$ideol), lb)]]
d[, cov_survey_weight := k$design_weight]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "larsen_2026_local_preservation.csv"))
