##Job-application vignette conjoint from
##West, E. A., & Duell, D. (2024). How political representation empowers women.
##Political Behavior. https://doi.org/10.1007/s11109-024-09948-4
##Replication data: Harvard Dataverse doi:10.7910/DVN/2MXKOT, CC0 1.0. Files read:
##data_conjoint_women.csv, data_conjoint_men.csv (the authors' long data; the survey files, the news-article
##file and the congress-member file are not used). Codebook: none in the deposit; the analysis script
##(replicationFile_howRepresentationEmpowers.R) was read as text.
##Usage: Rscript west_2024.R <dir holding the two csv> <output dir>
##
##Two tables, one per sample (the authors analyse the women sample (main study) and the men sample
##(replication) separately and with different treatment sets, so they are not pooled):
##  west_2024_representation_women  4,545 US women (matches the 4,545 in the paper), 5 vignettes each, 22,725 rows
##  west_2024_representation_men    2,082 US men, 5 vignettes each, 10,410 rows
##Each respondent rated five hypothetical jobs (task = the deposit's `vignette` 1-5, one profile per task) whose
##four attributes were randomized: job title (Admin Assistant, Assistant Manager, Branch Manager, Executive
##Assistant, CEO), industry (Tech, Education), competitiveness ("Most competitive" / "Not [most competitive]")
##and pay ("Highest pay" / "Not [highest pay]"). Levels are the authors' plot labels from the deposit
##(category.label, industry.label, comp.label, high.pay.label); the deposit has no instrument, so the exact
##text shown on screen is not documented (the bracketed "Not [..]" labels are the authors' own). Respondent-level
##between-subject information/framing treatment (women: Negative / Positive / No frame / No information; men:
##Negative / Positive) about the number of women in Congress precedes the jobs; it is stored as trial_treatment
##(it is not an attribute of the job). Party assignment `pid` (Democrat / Republican / Other) is cov_partisan_group (the authors' variable).
##Outcomes (both 0-100 integer sliders per the data range; instrument wording not in the deposit):
##  rating         = likely.apply, willingness to apply for the described job (paraphrase)
##  rating_qualify = qualify.job, how qualified the respondent feels for the job (paraphrase)
##Higher = more likely / more qualified. No opt-out (single profile ratings). Restrictions: not documented
##(restrictions unknown; the data show every combination occurring). Level weights unknown (shares near equal).
##Covariates: cov_age (as recorded), cov_education (text of the recorded category, "Prefer not to say" -> NA),
##cov_gender (women file gender=2 -> female; men file gender=1 -> male; coding follows the file names),
##cov_partisan_group, men only cov_party_id_reported (PartyID: Democrat / Other / Republican, party identification).
##Dropped: all attitude scales, feeling thermometers, race, state, income, ideology, turnout, ResponseId, and
##the authors' dummy codes (tech, comp, high.pay, job.* integer codes). Respondent id = sid (re-keyed to integer).
##Men file: no vignette index, so task = row order within respondent (5 rows each; task_source inferred).
##Reproduction: not attempted beyond the N check (women N 4,545 matches the paper).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(g, tab) {
  k <- fread(file.path(raw, paste0("data_conjoint_", g, ".csv")))
  d <- data.table(id = as.integer(factor(k$sid)), profile = 1L)
  # women file has `vignette` 1-5; men file has no index, so task = row order within respondent (inferred)
  d[, task := if (g == "men") ave(seq_len(.N), k$sid, FUN = seq_along) else as.integer(k$vignette)]
  d[, `:=`(rating = as.integer(k$likely.apply), rating_qualify = as.integer(k$qualify.job),
           attr_job_title = k$category.label, attr_industry = k$industry.label,
           attr_competitiveness = k$comp.label, attr_pay = k$high.pay.label,
           cov_age = as.integer(k$age), cov_education = ifelse(k$education == "Prefer not to say", NA, k$education),
           cov_gender = if (g == "men") "male" else "female", cov_partisan_group = k$pid)]
  if (g == "men") d[, cov_party_id_reported := k$PartyID]
  d[, trial_treatment := if (g == "men") k$frame.treat else k$treatment]
  stopifnot(!anyNA(d[, .(rating, rating_qualify, attr_job_title, attr_industry, attr_competitiveness, attr_pay)]),
            d[, .N, .(id, task)][, all(N == 1)], d[, uniqueN(trial_treatment), id][, all(V1 == 1)])
  setcolorder(d, c("id", "task", "profile")); setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
}
build("women", "west_2024_representation_women")
build("men", "west_2024_representation_men")
