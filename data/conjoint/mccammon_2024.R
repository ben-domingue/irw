##Prescribing phage therapy: paired treatment conjoint with choice and likelihood ratings, UK health professionals
##McCammon, S., Makarovs, K., Banducci, S., & Gold, V. (2024). Factors of prescribing phage therapy among UK
##healthcare professionals: Evidence from conjoint experiment and interviews (the deposit's accompanying study;
##the deposit gives no article DOI).
##Raw data: figshare doi:10.6084/m9.figshare.25435894, CC BY 4.0. Files read: merged_fordeposit.csv (saved as
##d.csv) and Phage_Therapies_Codebook.docx (the Qualtrics survey; text read from word/document.xml).
##Usage: Rscript mccammon_2024.R <dir holding d.csv> <output dir>
##
##192 rows = 190 respondents (HEALTH: Prolific health professionals, GP: a Panelbase sample of GPs) who saw the
##6-attribute design plus 2 respondents (HEALTH) who saw an earlier 5-attribute design (Duration of treatment,
##Success rate of therapy, Side effects, Approved for use, Type of treatment; F-1-1 = "Duration of Treatment");
##those 2 are dropped (different attribute set, far below 100). 5 tasks of 2 treatments.
##Attributes (positions are randomized per task: F-t-k names the attribute shown in row k, F-t-1-k and F-t-2-k the
##levels of Treatment 1 and 2): success rate (3 levels), side effect rate (4), type of treatment (4),
##administration route (3), patient attitude to treatment (3), severity of infection (2). attrpos_<attribute> =
##row position (1-6) of the attribute in that task.
##Outcomes: choice = Q19 "Which of the two treatments would you personally prefer to recommend to treat an
##infection[, presuming they are both a suitable option for the patient]?" (the clause is in the first task only);
##forced, no opt-out. rating = Q20 "On a scale from 1 to 10, where 1 indicates 'not at all likely' and 10 indicates
##'very likely', what is your likelihood of recommending Treatment 1 / Treatment 2?" asked for each treatment; the
##slider in the survey is labelled 0-10 and the data hold 0-10 (stored raw). Missing ratings ("NA", a few) are
##left empty; a task is dropped only if it has no choice and no ratings.
##Covariates: cov_sample (HEALTH / GP), cov_gender (Q33 codebook: 1 Man -> male, 2 Woman -> female, others NA),
##cov_birth_year (Q34, free text: only plain 4-digit years 1920-2010 kept), cov_ethnic_group (Q31 labels from the
##codebook), cov_region (Q32 labels from the codebook). Dropped: ResponseId, LONDON (duplicate of Q32).
##Respondent ids are row numbers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "d.csv"), encoding = "UTF-8", na.strings = c("NA", ""), colClasses = "character")
setnames(x, 1, "SAMPLE")
x <- x[-(1:2)]
stopifnot(nrow(x) == 192)
x <- x[`F-1-1` != "Duration of Treatment"]
stopifnot(nrow(x) == 190)
x[, id := .I]
an <- c("Success rate" = "success_rate", "Side effect rate" = "side_effect_rate", "Type of treatment" = "type_of_treatment",
        "Administration route" = "administration_route", "Patient attitude to treatment" = "patient_attitude", "Severity of infection" = "infection_severity")
rt <- c("a", "b", "c", "d", "e")
res <- list()
for (t in 1:5) {
  ch <- x[[paste0("Q19", rt[t])]]
  r1 <- x[[paste0("Q20", rt[t], "_1_1")]]
  r2 <- x[[if (t == 5) "Q20e_2_4" else paste0("Q20", rt[t], "_2_1")]]
  nmk <- sapply(1:6, function(k) x[[sprintf("F-%d-%d", t, k)]])        # respondents x 6 attribute names by row position
  for (p in 1:2) {
    d <- data.table(id = x$id, task = t, profile = p, choice = as.integer(as.integer(ch) == p), rating = as.integer(if (p == 1) r1 else r2))
    lev <- sapply(1:6, function(k) x[[sprintf("F-%d-%d-%d", t, p, k)]])
    for (nm in names(an)) {
      pos <- apply(nmk == nm, 1, which)
      stopifnot(is.integer(pos) || is.numeric(pos), length(pos) == nrow(x))
      d[, paste0("attr_", an[nm]) := lev[cbind(seq_len(nrow(x)), pos)]]
      d[, paste0("attrpos_", an[nm]) := as.integer(pos)]
    }
    res[[length(res) + 1]] <- d
  }
}
d <- rbindlist(res)
d[, cov_sample := x$SAMPLE[d$id]]
g <- x$Q33[d$id]
d[, cov_gender := ifelse(g == "1", "male", ifelse(g == "2", "female", NA_character_))]
byr <- x$Q34[d$id]
d[, cov_birth_year := ifelse(grepl("^(19[2-9][0-9]|200[0-9]|2010)$", byr), suppressWarnings(as.integer(byr)), NA_integer_)]
eth <- c("Multiple ethnic groups", "Asian / Asian British", "White / White British", "Black / African / Caribbean / Black British", "Other ethnic group", NA)
d[, cov_ethnic_group := eth[as.integer(x$Q31[d$id])]]
reg <- c("East of England", "East Midlands", "London", "North East", "North West", "Northern Ireland", "Scotland", "South East", "South West", "Wales", "West Midlands", "Yorkshire & Humberside")
d[, cov_region := reg[as.integer(x$Q32[d$id])]]
d <- d[!(is.na(choice) & is.na(rating))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, all(rating %in% c(0:10, NA))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mccammon_2024_phage_therapy.csv"))
