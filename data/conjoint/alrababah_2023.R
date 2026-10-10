##Refugee-return vignette conjoint (Syrian refugees in Lebanon, 2019) from
##Alrababa'h, A., Masterson, D., Casalis, M., Hangartner, D., & Weinstein, J. M. (2023). The
##dynamics of refugee return: Syrian refugees and their migration intentions. British Journal of
##Political Science, 53(4), 1108-1131. https://doi.org/10.1017/S0007123422000667 (open access)
##Replication data: Harvard Dataverse doi:10.7910/DVN/FK2NEV, CC0 1.0, no restricted files.
##File read: baseline_cjt.rds (the conjoint, long: one row per respondent x vignette). The
##authors' 05conjoint.R was read as text; the vignette template and level wording are from the
##article ("Conjoint Experiment" section). codebook.xlsx (Lebanon survey) gives `weights` =
##"Sampling weight". Other deposit files (raw survey svy.rds, respondent locations.rds, Jordan
##survey) were not downloaded.
##Usage: Rscript alrababah_2023.R <dir holding baseline_cjt.rds> <output dir>
##
##Face-to-face survey of a nationally representative sample of 3,003 Syrian refugee households in
##Lebanon (household head as respondent), August-October 2019, by a Lebanese survey firm.
##"Enumerators read to respondents a sequence of five separate hypothetical vignettes and, after
##each one, asked the respondents whether, under these conditions, they would return to Syria":
##"Imagine that one year from now, regarding the security situation in Syria, [1]. It appears
##that in [HOMETOWN], [2]. As for conscription, [3]. In Lebanon, [4]. Finally, regarding your
##friends and relatives, [5]." One profile per task (task = `variable`, vignette 1-5; profile 1).
##choice = outcome, "Under these conditions, would you be willing to return to Syria?" 1 = yes,
##0 = no (single-profile accept/reject, opt_out yes). 287 vignettes without an answer omitted.
##Attributes: the article's English text of each level (the survey was read in Arabic; the
##Arabic wording is not deposited), matched to the authors' short labels in the data by meaning
##(the article lists the same levels; the matching is unambiguous):
##  attr_safety (Your hometown is quite safe / Your hometown remains insecure / All of Syria is
##    quite safe), attr_syria_conditions (jobs OR services in one slot, 4 levels),
##  attr_conscription, attr_lebanon_conditions (job OR services, 4 levels), attr_network.
##"The order of the attributes was randomized across respondents" (article); the order is not in
##the deposit. Levels "randomly given" with no restrictions stated; level probabilities not stated.
##5 vignettes have no attribute text at all (blank in the source) and are dropped.
##cov_survey_weight = weights (codebook "Sampling weight"; constant within respondent, checked).
##Respondent id = response_num (the survey's own 1-3,003 numbering). No covariates other than the
##weight are in this file.
##N: 3,003 respondents in the file (= article); 2,998 have at least one answered vignette. Spot check: weighted OLS (as 05conjoint.R) gives
##hometown safe +0.35, all Syria safe +0.42, conscription ended +0.18 (article Figure 3).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "baseline_cjt.rds")))
stopifnot(nrow(s) == 15015L, uniqueN(s$response_num) == 3003L, s[, .N, response_num][, all(N == 5)],
          s[, uniqueN(weights), response_num][, all(V1 == 1)])
map <- function(v, m) { stopifnot(all(v %in% c(names(m), NA))); unname(m[v]) }
s[s == ""] <- NA
blank <- s[, is.na(cjt_safety) & is.na(cjt_econ_syria) & is.na(cjt_conscription) & is.na(cjt_econ_lebanon) & is.na(cjt_networks)]
stopifnot(sum(blank) == 5L)
s <- s[!blank & !is.na(outcome)]
d <- s[, .(id = as.integer(as.character(response_num)), task = as.integer(as.character(variable)), profile = 1L,
           choice = as.integer(outcome),
           attr_safety = map(cjt_safety, c("Your hometown is safe" = "Your hometown is quite safe",
                                           "Your hometown is not safe" = "Your hometown remains insecure",
                                           "All of Syria is safe" = "All of Syria is quite safe")),
           attr_syria_conditions = map(cjt_econ_syria, c(
             "There are many job opportunities" = "There are many job opportunities",
             "Public services easy to attain" = "Public services, such as health centers and schools, are relatively easy to attain",
             "There are few job opportunities" = "There are few job opportunities",
             "Public services hard to attain" = "Public services, such as health centers and schools, are difficult to attain")),
           attr_conscription = map(cjt_conscription, c("Military conscription ended" = "Military conscription has stopped",
                                                       "Military conscription remains" = "Military conscription is still in place")),
           attr_lebanon_conditions = map(cjt_econ_lebanon, c(
             "Good job in Lebanon" = "You have a good job in Lebanon",
             "No good job in Lebanon" = "You do not have a good job in Lebanon",
             "Public services available in Lebanon" = "Health centers and schools in Lebanon are available and affordable",
             "Public services not available in Lebanon" = "Health centers and schools in Lebanon are unavailable and unaffordable")),
           attr_network = map(cjt_networks, c("Friends in Lebanon" = "Most of your friends and relatives are in Lebanon",
                                              "Friends in Syria" = "Most of your friends and relatives are in Syria",
                                              "Friends elsewhere" = "Most of your friends and relatives are in Jordan, Turkey, and Iraq")),
           cov_survey_weight = weights)]
stopifnot(all(d$choice %in% 0:1), all(d$task %in% 1:5), !anyDuplicated(d[, .(id, task)]))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "alrababah_2023_refugee_return.csv"))
