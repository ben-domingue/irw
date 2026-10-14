##Punitive-policy vignette experiments (UK): benefit sanctions and migrant sanctions from
##O'Grady, T. (2026). Deterrence and retribution as motives for supporting punitive public policies (article journal and DOI not stated in the
##deposit; the DataCite record gives only the title). Replication data: Harvard Dataverse doi:10.7910/DVN/9ILS3D, CC0 1.0.
##Files read: UCL_Results_250623_CLIENT.tab (June 2025 survey, saved as a.tab), UCL_Results_250730_CLIENT.tab (July 2025 survey, saved as b.tab)
##and the authors' R code (read as text; it gives the recodes, the direction of the scales and the figure labels of the factor levels).
##Usage: Rscript ogrady_2026.R <dir holding a.tab and b.tab> <output dir>
##
##YouGov UK panel adults. The authors analyse immigration from the June file (n = 2,228) and welfare from the July file (n = 2,013, welfare only):
##their code reads p = June for IMMI_* and q = July for WELFARE_*. The June file also holds a welfare block for the same 2,228 respondents
##(every respondent has both blocks); the authors never use it, so it is NOT built (reported, Ben may decide). Two tables:
##  ogrady_2026_welfare_sanctions     July file, one vignette per respondent about a benefit claimant (Universal Credit, JobCentre)
##  ogrady_2026_immigration_sanctions June file, one vignette per respondent about a migrant
##Factors (randomized; each respondent saw one level of each):
##  Welfare: claimant name (6: WELFARE_NAME 1 Emily, 2 Fatima, 3 Jelena, 4 Jack, 5 Hasan, 6 Marek; verified against the Welfare_description text in the
##  July file, which has the first 255 characters of the vignette, and its she/he pronouns); reason for unemployment (WELFARE_REASON 1 "made
##  redundant three months ago because the company where [he/she] worked suffered a fall in sales", 2 "made redundant three months ago due to [his/her] poor
##  performance and repeated unexplained absences from work"; the text is from Welfare_description); sanction (WELFARE_SANCTION: 4 = none, 1-3 ascending
##  severity per the authors' recode comment).
##  Immigration: migrant name (IMMI_NAME 1-6), reason for migrating (IMMI_REASON, labels from the authors' figure code in code order: 1 seeking asylum due to
##  fleeing war, 2 seeking better economic opportunities, 3 reuniting with family in the UK), sanction (IMMI_SANCTION 1 = no sanction, 2-4 ascending severity;
##  authors' tests and figure axis "Severity of Sanction").
##  A further 2-level piped base-text variant exists in both tables (WELFARE_BASETEXT_pipe / IMMI_BASETEXT_2_pipe, 50/50, and the *_pipe columns of reason and
##  sanction are level x variant); its content is not documented: kept as trial_basetext_variant (1/2, undocumented).
##LABELS: the sanction levels have no text in the deposit (the article could not be found), so they are stored as ordinal tags
##("none", "severity 1 of 3" ...); the immigration names are stored as "name 1".."name 6"; the claimant reason and names and the migrant reason are recovered
##text/figure labels (paraphrase for the migrant reasons). Flag: LABELS: tags only for the sanction levels and immigration names.
##Outcomes (wording not deposited; paraphrased from variable names and the authors' code; "don't know" codes (5; 6 for support) set to NA as the authors do;
##values otherwise raw; direction from the authors' recode comments):
##  Welfare: rating_support_sanctions (UCL1_1: raw 1 = strongly support .. 5 strongly oppose, 6 don't know; authors' Welf_DV = 6 - raw),
##   rating_claimant_accept_job (WelfareV_AcceptOffer 1-4: raw 1 = most likely; authors reverse so higher = more likely),
##   rating_self_accept_job (WelfareV_AttendInterview, which the authors rename AcceptOfferSelf: 1-4, raw 1 = most likely),
##   rating_fair_jobcentre (WelfareV_FairJobCentre 1-4: raw 1 = fairest; authors reverse).
##  Immigration: rating_support_detention (UCL1_2, same coding as UCL1_1), rating_migrant_likely_to_migrate (ImmiV_LikelyMigrate 1-4), rating_self_likely_to_migrate
##   (ImmiV_MigrateMyself 1-4), rating_fair_immigration_system (ImmiV_FairImmiSystem 1-4, raw 1 = fairest). The direction of the two likelihood items is
##   not reversed by the authors; raw 1 = most likely is inferred from the welfare items and the "superior behaviour" definition (self less likely than migrants).
##One vignette per respondent: id = ID (the survey's own sequential number, re-keyed to the same value), task = profile = 1. No opt-out.
##Covariates: cov_gender (profile_gender: code 2 = female per the authors' recode female <- profile_gender == 2; 1 = male), cov_age, cov_survey_weight (weight).
##Dropped: authoritarianism items, vote, education and social-grade codes, region, timestamps, derived recodes.
##PII FOUND: none.
##Count check: n = 2,228 and 2,013 as in the dataset description (2,228).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- function(f) fread(file.path(raw, f), showProgress = FALSE, encoding = "UTF-8")
June <- rd("a.tab"); July <- rd("b.tab")
setnames(June, 1, "ID"); setnames(July, 1, "ID")
stopifnot(nrow(June) == 2228, nrow(July) == 2013)
na5 <- function(v, bad = 5) { v <- as.integer(v); v[v %in% bad] <- NA; v }
sanc <- function(code, none) { ord <- setdiff(1:4, none); lab <- c("No sanction", "Sanction severity 1 of 3 (mildest)", "Sanction severity 2 of 3", "Sanction severity 3 of 3 (most severe)")
  r <- rep(1L, length(code)); for (i in 1:3) r[code == ord[i]] <- i + 1L; lab[r] }
cov <- function(x) data.table(cov_gender = c("male", "female")[x$profile_gender], cov_age = as.integer(x$age), cov_survey_weight = x[[grep("^weight$", names(x), ignore.case = TRUE)]])
wnames <- c("Emily", "Fatima", "Jelena", "Jack", "Hasan", "Marek")
wreason <- c("Made redundant three months ago because the company where the claimant worked suffered a fall in sales",
             "Made redundant three months ago due to the claimant's poor performance and repeated unexplained absences from work")
w <- data.table(id = July$ID, task = 1L, profile = 1L,
  rating_support_sanctions = na5(July$UCL1_1, c(6)), rating_claimant_accept_job = na5(July$WelfareV_AcceptOffer),
  rating_self_accept_job = na5(July$WelfareV_AttendInterview), rating_fair_jobcentre = na5(July$WelfareV_FairJobCentre),
  attr_claimant_name = wnames[July$WELFARE_NAME], attr_unemployment_reason = wreason[July$WELFARE_REASON],
  attr_sanction = sanc(July$WELFARE_SANCTION, 4L), trial_basetext_variant = as.integer(July$WELFARE_BASETEXT_pipe))
w <- cbind(w, cov(July))
stopifnot(!anyNA(w$attr_claimant_name), !anyNA(w$attr_unemployment_reason), !anyNA(w$attr_sanction))
ireason <- c("Seeking asylum due to fleeing war", "Seeking better economic opportunities", "Reuniting with family in the UK")
m <- data.table(id = June$ID, task = 1L, profile = 1L,
  rating_support_detention = na5(June$UCL1_2, c(6)), rating_migrant_likely_to_migrate = na5(June$ImmiV_LikelyMigrate),
  rating_self_likely_to_migrate = na5(June$ImmiV_MigrateMyself), rating_fair_immigration_system = na5(June$ImmiV_FairImmiSystem),
  attr_migrant_name = paste("name", June$IMMI_NAME), attr_migration_reason = ireason[June$IMMI_REASON],
  attr_sanction = sanc(June$IMMI_SANCTION, 1L), trial_basetext_variant = as.integer(June$IMMI_BASETEXT_2_pipe))
m <- cbind(m, cov(June))
stopifnot(!anyNA(m$attr_migration_reason), !anyNA(m$attr_sanction))
for (z in list(list(w, "ogrady_2026_welfare_sanctions"), list(m, "ogrady_2026_immigration_sanctions"))) {
  d <- z[[1]]; d <- d[rowSums(!is.na(d[, .SD, .SDcols = patterns("^rating")])) > 0]
  setorder(d, id, task, profile); fwrite(d, file.path(out, paste0(z[[2]], ".csv"))); cat(z[[2]], nrow(d), "rows\n")
}
