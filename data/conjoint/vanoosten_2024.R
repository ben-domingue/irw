##Politician-vignette experiment, EMMAVID the Netherlands, from
##van Oosten, S., Mügge, L., Hakhverdian, A., & van der Pas, D. (2024). Dutch Ethnic Minority and
##Muslim Attitudes, Voting, Identity and Discrimination (EMMAVID) - EMMAVID Data the Netherlands
##[Data set]. Harvard Dataverse. Analysed in van Oosten, S. (2023). Who favor in-group politicians?
##In-group voting in France, Germany and the Netherlands and the challenges to the descriptive and
##substantive representation of Muslims. OSF Preprints. https://doi.org/10.31219/osf.io/rkejd
##Replication data: Harvard Dataverse doi:10.7910/DVN/BGVJZQ, CC0 1.0, no restricted files.
##Files read: DataNL_EMMAVID_vanOosten_etal_2024-2.sav (SPSS original), "Codebook Netherlands -
##EMMAVID - Van Oosten et al 2024.pdf" (English questionnaire, Part 3b and Table A1 names; OSF
##pre-registration text), and the authors' "Code Van Oosten 2023 - OSF - Who Favor In-Group
##Politicians-2.R" read as text (not run) for the variable-to-profile mapping and the statement codes.
##Usage: Rscript vanoosten_2024.R <raw dir> <output dir>
##
##905 respondents of a Dutch online panel (NIPObase, minority groups oversampled; Dutch-language
##questionnaire). Part 3b: three pairs of text vignettes ("<first name> <surname> has a Turkish
##background and practices Islam. She says the tax rate for the rich must be higher"); task = pair
##1-3 (profiles 3-4, 5-6, 7-8 of the questionnaire, in the order shown), profile = 1st / 2nd
##politician of the pair. Randomized per profile: background x religion (V40_k, 12 combinations),
##gender and first name (V10_k / V20_k, drawn from the background's name list in codebook Table A1),
##surname (V30_k, same list), policy statement (V2001-V2006, 8 issues x 2 directions).
##attr_ text: background and religion from the .sav V40 value labels ("Politician has a <X>
##background and <practices Islam / practices Christianity / doesn't practice any religion>"), split
##into attr_background and attr_religion; attr_gender = the pronoun used in the vignette (.sav V10
##labels "She"/"His"; "His" is stored as "He", the subject pronoun of "He says"); attr_first_name /
##attr_surname = V20 / V30 value labels; attr_statement = the authors' English statement for codes
##1-16 (their R code L1615-1631, matching the codebook's statement list V7101-V7116). Respondents saw
##Dutch; the stored text is the deposit's English.
##Outcomes (codebook Part 3b; .sav value labels):
##  rating_represents "Do you think this politician represents you?"
##  rating_trust      "How much do you trust this politician?"
##  rating_capable    "How capable do you think this politician is to perform well on the job?"
##     each stored RAW as the .sav code 1-11, whose value labels are "0 - Not at all", 1, ..., 9,
##     "10 Very much" (so code = displayed number + 1; higher = more favourable).
##  choice            "Which politician are you most likely to vote for?" (V380/V410/V440: 1 = first,
##                    2 = second politician of the pair; forced choice, no opt-out; every pair answered).
##trial_group = V50 ("Group 1" / "Group 2 (Control group)", assignment not explained in the codebook);
##trial_block_order = V51 (statements first vs profiles first, Dutch label text).
##Dropped: Part 3a (profiles 1-2: background/religion/gender only, outcome = which policy position
##the respondent expects, a different design); the free-text "why" answers; INTNR (panel interview
##number, re-keyed to integers in file order); all other survey blocks. No survey weight is deposited.
##Covariates: cov_gender (V640 "Gender": Male = male, Female = female), cov_age (LFT, panel age in
##years), cov_education (OPL, panel highest education, Dutch value-label text; "Weet niet \ wil niet
##zeggen" mixes don't know and refusal and is kept as text), cov_parent_born_nl (V50041 label text,
##place of birth of mother or father), cov_duration_sec (INTTIME, interview duration in seconds).
##N: 905 in the deposit; the OSF preprint pools FR/DE/NL and was not checked for the NL count.
##Spot check: none reproduced (preprint estimates pool three countries).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_sav(file.path(raw, "DataNL_EMMAVID_vanOosten_etal_2024-2.sav"))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
stmt <- c("The tax rate for the rich must be higher", "The tax rate for the rich must be lower",
          "The government should raise the support for the unemployed", "Our government should lower the support for the unemployed",
          "Our government should do more to combat climate change than now", "Our government should do less to combat climate change than now",
          "The government needs to raise fuel prices", "Our government needs to lower fuel prices",
          "Immigrants are an asset to our country", "Immigrants are a burden to our country",
          "Islam should not be restricted by law", "Islam should be restricted by law",
          "That men and women receive equal pay for equal work should be regulated by law",
          "That men and women receive equal pay for equal work should not be regulated by law",
          "Homosexual couples should not be allowed to adopt children", "Homosexual couples should be allowed to adopt children")
# the statement labels in the .sav (V7101-V7116) are the same 16 texts in the same order
stopifnot(identical(sapply(sprintf("V71%02d", 1:16), function(v) attr(s[[v]], "label")), setNames(stmt, sprintf("V71%02d", 1:16))))
rq <- c("V359", "V369", "V389", "V399", "V419", "V429"); cq <- c("V380", "V410", "V440")
n <- nrow(s); rows <- list()
for (j in 1:6) {
  k <- j + 2L; t <- (j + 1L) %/% 2L; p <- 2L - j %% 2L
  bg <- lab(s[[paste0("V40_", k)]]); g <- lab(s[[paste0("V10_", k)]])
  stopifnot(!anyNA(bg), all(g %in% c("She", "His")), all(as.numeric(s[[paste0("V10_", k)]]) == as.numeric(s[[paste0("V20_", k)]])))
  m <- regmatches(bg, regexec("^Politician has an? (.*) background and (.*)\\.$", bg))
  stopifnot(all(lengths(m) == 3))
  ch <- as.integer(s[[cq[t]]]); stopifnot(all(ch %in% 1:2))
  r <- lapply(1:3, function(q) as.integer(s[[paste0(rq[j], "_", q)]]))
  stopifnot(all(unlist(r) %in% 1:11), all(as.integer(s[[paste0("V200", j)]]) %in% 1:16))
  rows[[j]] <- data.table(id = seq_len(n), task = t, profile = p, choice = as.integer(ch == p),
    rating_represents = r[[1]], rating_trust = r[[2]], rating_capable = r[[3]],
    attr_first_name = lab(s[[paste0("V20_", k)]]), attr_surname = lab(s[[paste0("V30_", k)]]),
    attr_gender = ifelse(g == "She", "She", "He"),
    attr_background = sapply(m, `[`, 2), attr_religion = gsub("&apos;", "'", sapply(m, `[`, 3), fixed = TRUE),
    attr_statement = stmt[as.integer(s[[paste0("V200", j)]])])
}
d <- rbindlist(rows)
stopifnot(!anyNA(d$attr_surname), !anyNA(d$attr_first_name), d[, sum(choice), .(id, task)][, all(V1 == 1)])
cv <- data.table(id = seq_len(n), trial_group = lab(s$V50), trial_block_order = lab(s$V51),
                 cov_gender = c("male", "female")[as.integer(s$V640)], cov_age = as.integer(s$LFT),
                 cov_education = lab(s$OPL), cov_parent_born_nl = lab(s$V50041), cov_duration_sec = as.integer(s$INTTIME))
stopifnot(all(s$V640 %in% 1:2))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating_represents", "rating_trust", "rating_capable"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vanoosten_2024_politicians_nl.csv"))
