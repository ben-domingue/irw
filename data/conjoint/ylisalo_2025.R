##Election-pledge vignette experiments (Finland, Germany) from
##Ylisalo, J., Matthieß, T., Praprotnik, K., & Ennser-Jedenastik, L. (2025). Election pledges in
##multiparty governments: When do voters accept non-fulfillment? British Journal of Political
##Science. https://doi.org/10.1017/S0007123425100860
##Replication data: Harvard Dataverse doi:10.7910/DVN/LQJNM1, CC0 1.0, no restricted files.
##Files read: data_fin_wide.xlsx, data_ger_wide.xlsx, data_ger_ptv_wide.xlsx (one row per
##respondent, wide over the 6 pledges) and their codebooks codebook_data_fin_wide.txt,
##codebook_data_ger_wide.txt, codebook_data_ger_ptv_wide.txt (saved as cb_fin.txt, cb_ger.txt,
##cb_ger_ptv.txt): every level text, question wording and covariate label below is parsed
##from these codebooks. Read as text: readme.txt, data_analysis_maintext.R.
##Usage: Rscript ylisalo_2025.R <raw dir> <output dir>
##
##Factorial vignette experiment (presentation = text): each respondent read 6 vignettes, one per
##pledge (a fixed set of 6 policy pledges per country, shown in random order; task = the
##recorded view order view_order_VignetteK), each saying the pledge was not fulfilled, with
##randomized attributes: number of government parties (size), status of the pledging party
##(position), coalition agreement (program), ministerial portfolio (ministry), attitude of the
##other government parties (others). attr_pledge is the pledge (codebook text "(Pledge: ...)");
##it varies within respondent by design, not by randomization. One profile per task.
##Level text is the English codebook labels (the surveys were in Finnish/Swedish and German;
##the instruments are not deposited). The German codebooks give shorter labels ("Included",
##"Junior partner") than the Finnish ("The promised policy was included in the government
##programme"), so level text differs between the countries.
##Three tables (separate samples; the paper analyses Finland and Germany side by side, not
##pooled, and the attribute levels differ: 3 vs 5 parties, three vs two party statuses):
##  ylisalo_2025_pledges_finland: rating = outcome_k, "How acceptable do you find the fact that
##    the promise was not fulfilled?" 0 = Not at all acceptable ... 10 = Fully acceptable.
##    2,466 respondents in the file (paper code: 2466); 44 never reached the vignettes (no
##    attributes) and are dropped with all tasks whose rating is missing. The paper's figures
##    keep Finnish citizens only (citizenship == 1); all are kept here (cov_citizenship).
##  ylisalo_2025_pledges_germany: same question and scale, 1,359 respondents (paper code: 1359).
##  ylisalo_2025_pledges_germany_ptv: separate German sample, outcome = "Propensity to vote
##    for the party that had made the pledge", 0 = Very unlikely ... 10 = Very likely (codebook
##    description, not the question wording). 4,721 rows in the file; rows with no vignette
##    attributes or no rating are dropped. Attention test (5 = passed) -> cov_attention_pass.
##Randomization restrictions are not documented; attribute order within a vignette not documented.
##Per-pledge respondent answers are task-level here: trial_opinion (opinion on the pledged policy,
##codebook label text, Fully agree ... Fully disagree), trial_importance (1 Not at all important
##... 7 Very important), trial_importance_rank (Germany main: 1 = most important ... 6).
##Covariates (codebook labels): cov_age_group, cov_education (edu3: Primary/Secondary/Tertiary),
##cov_gender (Germany: 1 Male, 2 Female, 3 Other); Finland cov_gender_code keeps the code
##(1 Male, 2 Female, 3 'Other/Prefer not to disclose', which mixes other and refusal);
##cov_vote_intention (label text), cov_leftright and cov_libcons (0-10; Finland 11 = Can't say),
##cov_trust_parties (0-10), Finland also cov_native_language and cov_citizenship (Yes/No) and
##cov_finished (No/Yes). ID re-keyed to integers in file order.
library(readxl); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cb <- function(f) {   # var -> list(text, labels named by code)
  L <- sub("\\s+$", "", gsub("\r", "", readLines(file.path(raw, f), encoding = "UTF-8")))
  res <- list(); cur <- NULL
  for (l in L) {
    if (grepl("^[A-Za-z_0-9]+ : ", l)) { cur <- sub(" : .*", "", l); res[[cur]] <- list(text = sub("^[A-Za-z_0-9]+ : ", "", l), lab = character()) }
    else if (!is.null(cur) && grepl("^[0-9]+ '", l)) {
      res[[cur]]$lab[sub(" .*", "", l)] <- sub("'$", "", sub("^[0-9]+ '", "", l))
    }
  }
  res
}
lab <- function(cbk, v, x) { m <- cbk[[v]]$lab; y <- unname(m[as.character(x)]); stopifnot(all(is.na(x) | !is.na(y))); y }
build <- function(xf, cf, name, covs) {
  w <- as.data.table(read_excel(file.path(raw, xf))); k <- cb(cf)
  stopifnot(!anyDuplicated(w$ID))
  d <- rbindlist(lapply(1:6, function(p) {
    pl <- sub("\\)$", "", sub(".*\\(Pledge: ", "", k[[paste0("outcome_", p)]]$text))
    e <- data.table(id = seq_len(nrow(w)), task = w[[paste0("view_order_Vignette", p)]], profile = 1L,
                    rating = as.integer(w[[paste0("outcome_", p)]]), attr_pledge = pl)
    for (v in c("size", "position", "program", "ministry", "others"))
      e[, paste0("attr_", v) := lab(k, paste0(v, "_1"), w[[paste0(v, "_", p)]])]
    if (paste0("opinion_", p) %in% names(w)) e[, trial_opinion := lab(k, "opinion_1", w[[paste0("opinion_", p)]])]
    if (paste0("importance_", p) %in% names(w)) e[, trial_importance := as.integer(w[[paste0("importance_", p)]])]
    if (paste0("importancerank_", p) %in% names(w)) e[, trial_importance_rank := as.integer(w[[paste0("importancerank_", p)]])]
    e
  }))
  ac <- setdiff(grep("^attr_", names(d), value = TRUE), "attr_pledge")
  na_attr <- d[, rowSums(is.na(.SD)) > 0, .SDcols = c(ac, "task")]
  stopifnot(d[na_attr, all(rowSums(is.na(.SD)) == length(ac) + 1L), .SDcols = c(ac, "task")])  # all-or-nothing: never reached
  d <- d[!na_attr & !is.na(rating)]
  stopifnot(all(d$rating %in% 0:10), !anyDuplicated(d[, .(id, task)]))
  for (v in names(covs)) {
    x <- w[[v]][d$id]
    d[, paste0("cov_", covs[[v]]) := if (length(k[[v]]$lab) && !covs[[v]] %in% c("leftright", "libcons", "gender_code")) lab(k, v, x) else as.integer(x)]
  }
  if ("cov_gender" %in% names(d)) d[, cov_gender := c(Male = "male", Female = "female", Other = "other")[cov_gender]]
  if ("attention" %in% names(w)) d[, cov_attention_pass := as.integer(w$attention[d$id] == 5)]
  d[, id := match(id, unique(sort(id)))]
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build("data_fin_wide.xlsx", "cb_fin.txt", "ylisalo_2025_pledges_finland",
      c(agegroup4 = "age_group", edu3 = "education", gender = "gender_code", language = "native_language",
        voteintention = "vote_intention", leftright = "leftright", libcons = "libcons", trustparties = "trust_parties",
        citizenship = "citizenship", Finished = "finished"))
build("data_ger_wide.xlsx", "cb_ger.txt", "ylisalo_2025_pledges_germany",
      c(agegroup4 = "age_group", edu3 = "education", gender = "gender", voteintention = "vote_intention",
        leftright = "leftright", libcons = "libcons", trustparties = "trust_parties"))
build("data_ger_ptv_wide.xlsx", "cb_ger_ptv.txt", "ylisalo_2025_pledges_germany_ptv", c())
