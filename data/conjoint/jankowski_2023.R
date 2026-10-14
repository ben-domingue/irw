##2x2 factorial vignette on a strategic-voting campaign (Germany, 2021) from
##Jankowski, M. Support for strategic voting campaigns: Evidence from a survey experiment during the German General Election of 2021.
##Politische Vierteljahresschrift (accepted for publication Dec 2022 per the deposited preprint; year 2023 assumed, article DOI not
##stated in the deposit). Replication data: Harvard Dataverse doi:10.7910/DVN/QNOMXJ, CC0 1.0, no restricted files.
##Files read: final_maassen.rds, preprint.pdf (design and wording), Jankowski_Replication_PVS_StrategicVotingCampaign.Rmd (as text).
##Usage: Rscript jankowski_2023.R <dir holding final_maassen.rds> <output dir>
##
##988 Green voters (respondi panel, quotas for gender and age, one week before the 21 Sept 2021 election). Each read a description of
##electoral district 196 (CDU candidate Hans-Georg Maassen; Campact's campaign for the SPD candidate Frank Ullrich, asking Greens and
##Left to support him) and rated the campaign. Two clauses were randomly added to the description (2x2, one vignette per respondent;
##each row is a respondent, id = row number):
##  attr_justification: "The justification for the campaign is that the candidate of the SPD has the highest winning chances against
##    Hans-Georg Maassen. In the first tier of Germany's electoral system, only the candidate with the highest number of votes is elected
##    in the electoral district. With this campaign, Campact wants to avoid a situation in the electoral district where votes are split
##    between different left-wing candidates." or "(not shown)" (preprint, translated from German);
##  attr_party_cue: "The Greens support the campaign and they ask their voters to support the candidate of the SPD with their first
##    vote." or "(not shown)".
##Scope note: both clauses describe the evaluated object (the campaign), so the table is built; the authors call them information
##and party-cue treatments. Ben may prefer to hold it as "treatment arms".
##Outcome: rating = maassen_outcome, "How do you evaluate this campaign of Campact for the SPD candidate in electoral district 196?",
##1 'very bad' .. 10 'very good' (translated, preprint). Arms from info_treatment x party_treatment (maassen_treatment factor agrees,
##checked). Covariates: cov_gender (male/female/other from the SPSS value labels), cov_age (years), cov_left_right (leftright 1-10,
##'very left' 1 to 'very right' 10 per the preprint). Dropped: ResponseId, vote2017_green, pint, abi, partyeval_6 (other covariates/derived).
##Count check: 988 = preprint N. Preprint Table 1: mean evaluation 6.89 (reproduced below).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(readRDS(file.path(raw, "final_maassen.rds")))
stopifnot(nrow(d) == 988, !anyNA(d$maassen_outcome), !anyNA(d$info_treatment), !anyNA(d$party_treatment))
stopifnot(d[, all(rowSums(table(maassen_treatment, info_treatment + 2 * party_treatment) > 0) == 1)])
g <- attr(d$gender, "labels"); gl <- names(g)[match(as.numeric(d$gender), g)]
stopifnot(identical(unname(g), c(1, 2, 3)))
just <- "The justification for the campaign is that the candidate of the SPD has the highest winning chances against Hans-Georg Maaßen. In the first tier of Germany's electoral system, only the candidate with the highest number of votes is elected in the electoral district. With this campaign, Campact wants to avoid a situation in the electoral district where votes are split between different left-wing candidates."
cue <- "The Greens support the campaign and they ask their voters to support the candidate of the SPD with their first vote."
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L, rating = as.integer(d$maassen_outcome),
  attr_justification = ifelse(d$info_treatment == 1, just, "(not shown)"), attr_party_cue = ifelse(d$party_treatment == 1, cue, "(not shown)"),
  cov_gender = c(männlich = "male", weiblich = "female", divers = "other")[gl], cov_age = as.integer(d$age), cov_left_right = as.integer(d$leftright))
cat("mean evaluation", mean(r$rating), "(preprint 6.89)\n")
setorder(r, id, task, profile)
fwrite(r, file.path(out, "jankowski_2023_strategic_voting.csv")); cat("rows", nrow(r), "\n")
