##Apartment-building vignette experiment (Denmark) from
##Larsen, M. V., & Nyholt, N. (2024). Understanding opposition to apartment buildings.
##Journal of Political Institutions and Political Economy. https://doi.org/10.1561/113.00000092
##(OSF preprint https://doi.org/10.31219/osf.io/nu98d)
##Replication data: Harvard Dataverse doi:10.7910/DVN/1ZPAKL, CC0 1.0. Files read: kom_data.dta
##(Dataverse "original format" download, Stata value labels), analysis.R and instructions.txt
##(read as text, not run). There is no questionnaire or codebook in the deposit.
##Usage: Rscript larsen_2024.R <dir holding kom_data.dta> <output dir>
##
##13,040 Danish adults, ONE text vignette each (task = profile = 1, inferred: one vignette
##per respondent; id = row number, the file has no respondent id). The vignette (Danish; stem
##truncated in the .dta label: "Kommunalbestyrelsen overvejer om de skal tillade, at der
##bygges ...") described a development the municipal council is considering, randomized in
##three attributes (levels = the Danish value-label text of V2_X_rand, V2_Y1_rand, V2_Y2_rand):
##  attr_type   : almene boliger / ejerboliger / lejeboliger / kontorer / butikslokaler
##                (the labels also list 4 other types that never occur in this file)
##  attr_size   : "500" / "1.000" / "10.000" (floor area; the authors' figure labels read "sqm";
##                the unit word is not in the data labels)
##  attr_height : 8 phrases. Retail premises get the wording "hvad der svarer til N etager
##                højt" (equivalent to N storeys high), every other type "på N etager"
##                ("i ét plan" for 1); N = 1, 3, 5, 7. The authors' analysis pools the two
##                wordings into a 4-level height.
##Restriction: the height wording depends on the type (see above). Level weights: type and
##height levels are near-equal within the allowed combinations (type 2,550-2,700 per level
##of each, retail 2,676 over 4 wordings); no source gives probabilities.
##Outcomes (stored raw):
##  rating = V2, support for the building project: 1 "Jeg er helt sikkert imod" (definitely
##    against) ... 4 neither for nor against ... 7 "helt sikkert for" (definitely for); 8 = "Ved ikke"
##    (don't know, 990 respondents, kept as 8). HIGHER 1-7 = more favourable. The authors' opposition
##    measure is V2 in 1-3 (don't know counted as not opposed).
##  rating_cheaper_home = V4_1 "Projektet vil gøre min bolig billigere" (The project will make
##    my home cheaper), rating_congestion = V4_10 "...skabe mere trængsel" (more congestion),
##    rating_undesirable_residents = V4_13 "...tiltrække folk til mit område, som jeg ikke
##    ønsker her", rating_poor_fit = V4_16 "...passe dårligt ind i området". All 1 helt uenig
##    (strongly disagree), 2 delvist uenig, 3 neither, 4 delvist enig, 5 helt enig; 6 = Ved ikke
##    (don't know, kept as 6). V4_1 is missing for 3,303 respondents (not asked of them, no
##    source says why) and is NA there.
##Covariates: cov_gender (gender; value labels Man = male, Woman = female, 16 NA), cov_birth_year,
##cov_education (uddannelse, .dta value-label text, Danish), cov_housing (Q6, value-label text),
##cov_municipality (c_Kommune), cov_survey_weight (dweight, the authors' design weight; used in
##all their models; mean 1.0). Dropped: the authors' derived variables (fivestories,
##sevenstories, bbr_etager_5/7: area building-height measures from a register, the authors'
##construction).
##N: 13,040 respondents (paper not compared beyond this). Spot-check: weighted share opposed
##(V2 in 1-3) is printed below.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "kom_data.dta"))
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L, choice = NA_integer_)
d[, choice := NULL]
d[, rating := as.integer(k$V2)]
d[, rating_cheaper_home := as.integer(k$V4_1_resp)]
d[, rating_congestion := as.integer(k$V4_10_resp)]
d[, rating_undesirable_residents := as.integer(k$V4_13_resp)]
d[, rating_poor_fit := as.integer(k$V4_16_resp)]
d[, attr_type := lab("V2_X_rand")]
d[, attr_size := lab("V2_Y1_rand")]
d[, attr_height := lab("V2_Y2_rand")]
d[, cov_gender := c("male", "female")[as.integer(k$gender)]]
d[, cov_birth_year := as.integer(k$birthyear)]
d[, cov_education := lab("uddannelse")]
d[, cov_housing := lab("Q6")]
d[, cov_municipality := as.character(k$c_Kommune)]
d[, cov_survey_weight := as.numeric(k$dweight)]
stopifnot(!anyNA(d$rating), !anyNA(d[, .(attr_type, attr_size, attr_height)]), nrow(d) == 13040)
cat("weighted share opposed (V2 in 1-3):", d[, weighted.mean(rating %in% 1:3, cov_survey_weight)], "\n")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "larsen_2024_apartment_opposition.csv"))
