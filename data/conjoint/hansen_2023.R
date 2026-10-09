##Teacher extra-role conjoint (Danish high-school teachers rating student profiles) from
##Hansen, P. (2023). How client characteristics cause extra-role behaviours in public service:
##Uncovering invisible frontline work. Public Management Review (online 2023-10-22), 1-21.
##https://doi.org/10.1080/14719037.2023.2270557
##Replication data: OSF project https://osf.io/a3knw/ (doi 10.17605/OSF.IO/A3KNW), CC BY 4.0
##(node licence). File read: data/data_raw.rds (the author's anonymized Qualtrics export,
##Danish answer text). Read as text only: README.txt, scripts/02-cleaning-data.R (Danish ->
##English translations, the author's coding of names by gender and origin),
##scripts/03-analysis.R.
##Usage: Rscript hansen_2023.R <raw dir> <output dir>
##
##1,794 Danish upper-secondary (gymnasium) teachers in the export; 1,507 rated at least one
##profile (the paper's n) and are kept. Each teacher saw 4 dilemmas, one student profile each
##(task = dilemma 1-4 in the export's f_1..f_4 block order, profile = 1), and rated on a 1-10
##scale whether they would go beyond their job for the student:
##  task 1 trial_dilemma "Stay after class"  1 = "Bliver ikke en halv time ekstra, helt sikkert",
##         10 = "Bliver en halv time ekstra, helt sikkert"
##  task 2 "Call during the weekend"   1 = "Lader ikke eleven ringe i weekenden, helt sikkert",
##         10 = "Lader eleven ringe i weekenden, helt sikkert"
##  task 3 "Accept hand-in"            1 = "Lader ikke eleven aflevere, helt sikkert",
##         10 = "Lader eleven aflevere, helt sikkert"
##  task 4 "Push deadline"             1 = "Rykker ikke fristen med en uge, helt sikkert",
##         10 = "Rykker fristen med en uge, helt sikkert"
##(trial_dilemma uses the author's English dilemma names; the dilemma prose is not in the
##deposit. Anchors are those stored in the export, which holds the anchor text for 1 and 10 and
##bare numbers 2-9; parsed to numbers as the author does.) Higher = more willing.
##Whether the dilemma order was randomized is not recorded (the export keeps one fixed block
##per dilemma).
##Attributes, Danish text as displayed (export), header labels in the export: attr_effort_history
##(INDSATS, HISTORISK, 4 levels), attr_effort_recent (INDSATS, NYLIG, 4), attr_academic
##(AKADEMISK, 5), attr_social (SOCIALT, 4), attr_name (NAVN, 40 first names). The attribute
##labels sit in the same position in every block (f_k_j), so attribute order is fixed. The
##author's translations are in 02-cleaning-data.R. The name carries gender and origin: the
##author codes 20 names as female and 20 as non-Danish (02-cleaning-data.R).
##Covariates: cov_gender (sex: Mand -> male, Kvinde -> female; "Andet/oensker ikke at svare"
##(other / prefer not to say, one option) -> NA because it merges other and refusal), cov_age
##(whole years 18-100), cov_work_experience and cov_tenure (years, as typed), cov_danish_parents
##(etnicity, the author's "Both parents born in Denmark": Ja / Nej as answered). Dropped:
##response_id (Qualtrics ID; re-keyed in file order), uo_1-3 and psm_1-5 (Likert batteries
##whose item wording is not in the deposit).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "data_raw.rds")))
stopifnot(!anyDuplicated(x$response_id))
x[, id := seq_len(.N)]
dil <- c(stay = "Stay after class", call = "Call during the weekend", handin = "Accept hand-in", deadline = "Push deadline")
lab <- c("INDSATS, HISTORISK", "INDSATS, NYLIG", "AKADEMISK", "SOCIALT", "NAVN")
an <- c("effort_history", "effort_recent", "academic", "social", "name")
d <- rbindlist(lapply(1:4, function(k) {
  for (j in 1:5) stopifnot(all(x[[sprintf("f_%d_%d", k, j)]] == lab[j]))
  r <- x[[paste0("dilemma_", names(dil)[k])]]
  v <- as.integer(sub(":.*", "", r))
  stopifnot(all(is.na(r) | v %in% 1:10), all(is.na(r) | grepl(":", r) == v %in% c(1, 10)))
  z <- data.table(id = x$id, task = k, profile = 1L, rating = v, trial_dilemma = dil[[k]])
  for (j in 1:5) z[, paste0("attr_", an[j]) := x[[sprintf("f_%d_1_%d", k, j)]]]
  z }))
d <- d[!is.na(rating)]
stopifnot(!anyNA(d))
ag <- x$age; ag[!(ag %in% 18:100)] <- NA
cv <- x[, .(id, cov_gender = c(Mand = "male", Kvinde = "female")[sex], cov_age = as.integer(ag),
            cov_work_experience = work_experience, cov_tenure = tenure, cov_danish_parents = etnicity)]
stopifnot(all(x$sex %in% c("Mand", "Kvinde", "Andet/ønsker ikke at svare", NA)))
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating", grep("^attr_", names(d), value = TRUE), "trial_dilemma"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hansen_2023_teacher_extra_role.csv"))
