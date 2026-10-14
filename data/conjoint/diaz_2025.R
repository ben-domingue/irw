##Mayor gender x performance information food-programme vignette, Argentina, from
##Diaz, G., Oliveros, V., Weitz-Shapiro, R., & Winters, M. S. (2025). Ignoring women's performance: A survey
##experiment on policy implementation in Argentina. British Journal of Political Science.
##https://doi.org/10.1017/S0007123424000668
##Replication data: Harvard Dataverse doi:10.7910/DVN/SWIPBZ, CC0 1.0. File read: credit.rda (README.pdf, main.R
##read as text). Usage: Rscript diaz_2025.R <dir holding credit.rda saved as f10381691> <output dir>
##
##2,040 Netquest online-panel respondents in Argentina (March 2021; paper N = 2,040), one vignette each (36
##conditions, 3 x 2 x 3 x 2): "Imagine a Peronist/PRO/[no party] mayor who is running for re-election. During
##his/her time in office the mayor carried out a programme to help poor people, which consisted of distributing
##boxes of food, as shown in the photo. Beneficiaries are strictly selected based on need / theoretically selected
##based on need, but in practice those with contacts inside the municipality receive priority / [omitted]."
##(English wording from the article's description of the vignette; respondents saw Spanish. Level text below is a
##paraphrase of that description; the deposit stores only dummies and the English recodes in main.R.)
##Factors: attr_mayor_gender (man/woman, via Spanish pronoun/article; photo names Pedro/Alicia), attr_distribution_info
##(particularism No = "strictly selected based on need" [authors' Unbiased]; Yes = "in theory selected on need, in
##practice contacts get priority" [Biased]; Omit = control, "(not shown)"), attr_mayor_party (PJ = Peronist, PRO, Omit =
##"(not shown)"), attr_name_on_box (name = 1: the mayor's name, matching gender, shown on the photographed food box;
##name = 0: "(not shown)").
##One vignette per respondent: task = 1, profile = 1, id = row of the file (the ticket/responseid are dropped).
##Outcomes, all 1-4 ("not at all likely" ... "very likely"; axis labels in main.R, wording from main.R plot labels and
##the article's description, so paraphrase): rating_vote_mayor (vote_respond, would vote for the mayor),
##rating_help_reelect (help_reelect, programme would help the mayor win re-election), rating_satisfied (satisfy_respond,
##R would be satisfied with the programme), rating_need_based (distrib_unbiased, box goes to those most in need),
##rating_corrupt / rating_patronage / rating_buyvotes (mayor_corrupt, mayor_patron, mayor_buyvotes: likelihood the
##mayor was corrupt / offered patronage / buys votes). Other v*/benefic/vecinos/_01 columns are not described in the
##deposit and are not kept. Rows with all seven outcomes missing are dropped; individual NAs are stored as NA.
##(21 respondents with all seven outcomes missing are dropped: 2,019 remain.)
##Covariates: cov_gender (sex Female/Male), cov_age, cov_province, cov_ses (nse, Netquest SES band), cov_duration_sec
##(durationinseconds). Dropped: IP address, latitude/longitude, response id, ticket, dates, household-head
##occupation/education, derived dummies, recall checks, partisanship codes (undocumented).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "f10381691"), e); k <- as.data.table(e$credit)
stopifnot(nrow(k) == 2040, all(k$name %in% 0:1), all(k$male_mayor %in% 0:1))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L)
oc <- c(vote_mayor = "vote_respond", help_reelect = "help_reelect", satisfied = "satisfy_respond",
            need_based = "distrib_unbiased", corrupt = "mayor_corrupt", patronage = "mayor_patron", buyvotes = "mayor_buyvotes")
for (n in names(oc)) d[[paste0("rating_", n)]] <- as.integer(k[[oc[[n]]]])
d[, `:=`(attr_mayor_gender = c("woman", "man")[k$male_mayor + 1L],
         attr_distribution_info = c(No = "strictly selected based on need", Yes = "theoretically selected based on need, but in practice those with contacts inside the municipality receive priority", Omit = "(not shown)")[k$particularism],
         attr_mayor_party = c(PJ = "Peronist", PRO = "PRO", Omit = "(not shown)")[k$party],
         attr_name_on_box = ifelse(k$name == 1, ifelse(k$male_mayor == 1, "Pedro", "Alicia"), "(not shown)"),
         cov_gender = tolower(k$sex), cov_age = as.integer(k$age), cov_province = k$provincia, cov_ses = k$nse,
         cov_duration_sec = as.integer(round(k$durationinseconds)))]
stopifnot(!anyNA(d$attr_distribution_info), !anyNA(d$attr_mayor_party))
d <- d[rowSums(!is.na(d[, grep("^rating_", names(d)), with = FALSE])) > 0]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "diaz_2025_mayor_credit.csv"))
