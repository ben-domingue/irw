##Allocation of a new cancer drug between two patients, physician conjoint, from
##Tranvag, E. J., Strand, R., Ottersen, T., & Norheim, O. F. (2021). Precision medicine and the
##principle of equal treatment: a conjoint analysis. BMC Medical Ethics, 22, 55.
##https://doi.org/10.1186/s12910-021-00625-3
##Data: figshare collection 10.6084/m9.figshare.c.5419493 (Springer Nature supplements; figshare
##licence field "CC BY + CC0"). File read: 12910_2021_625_MOESM4_ESM.csv (Additional file 4,
##file id 27956732). Read as text for labels: MOESM3 (.r, the authors' revalue() recodes),
##MOESM1 (English translation of the survey), MOESM2 (marginal-means appendix).
##Usage: Rscript tranvag_2021.R <dir holding the .csv> <output dir>
##
##Norwegian physicians (cancer-treating doctors; survey in Norwegian, English translation
##deposited), 6 tasks x 2 patients (profiles A/B), 7 attributes. Question: "Given the
##information available, to whom would you allocate the new drug? [Choose A or B]" (translated);
##the scenario: only one of the two patients can get the new drug (400 000 NOK, +6 months), the
##other gets standard treatment. choice = `selected` (1 = patient allocated the drug). Forced
##choice, no opt-out (exactly one chosen per kept task).
##Levels (text from the authors' revalue() code and the survey translation): Biomarker status
##Positive/Negative (code 1/2); ECOG performance score 0/1/2 (stored as the digits; the survey
##defines the scale); Patient age 63/75/87 years (alder 1/2/3); Sex Female/Male (1/2);
##Comorbidity Healthy/Moderate/Severe (komorbiditet 1/2/3; the authors' code says none/moderate/
##severe, the survey Healthy/Moderate/Severe); Smoking status Smoker/Non-smoker (1/2);
##Education level Low/Medium/High (utd 1/2/3; the article's Table 1 uses Low/Medium/High, the
##survey translation's example table prints Low/High, the randomization comment lists primary
##school, secondary school, college or university, the authors' code basic/secondary/higher).
##Processing: the file has 166 respondents x 12 rows (6 tasks x 2 profiles) = 1,992 rows. 96 tasks
##(192 rows, 32 respondents' remaining pages) have all attributes blank (not saved) and are dropped,
##as the authors' own na.omit does; 40 further tasks have attributes but no response (selected = 0
##on both rows, conjoint_respons blank) and are dropped (no outcome). Kept: 724 tasks, 131
##respondents (110 with all six tasks). Profile order = row order within (responseid,
##conjoint_id); for all 724 kept tasks the chosen row's position equals the stored response
##conjoint_respons (1 = A, 2 = B), so profile order is confirmed. Task = conjoint_id (1-6).
##N vs paper: the article reports 115 completed responses and 690 observations (115 x 6) out of
##1,029 invited; the deposit has 131 respondents with at least one answered task (110 with all six,
##724 tasks). The deposit has 21 partial respondents the article seems to exclude; all kept here.
##AMCE check: positive vs negative biomarker = +0.25 (lm, SE 0.023 clustered by id); article +25 points.
##Randomization: the translation's comment says each variable is randomly assigned from its values;
##no restriction documented. Attribute order fixed (one table, same row order). No survey weight,
##no respondent covariates in the file (importance ratings q21_*, q20 are respondent-level
##items and are dropped; the demographic items are not deposited). id = responseid re-keyed to
##consecutive integers. Count vs paper: not checked beyond the file (see return).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "12910_2021_625_MOESM4_ESM.csv"))
x[, pos := seq_len(.N), .(responseid, conjoint_id)]
x[, `:=`(nna = sum(is.na(biomark)), sel = sum(selected)), .(responseid, conjoint_id)]
stopifnot(x[, .N, .(responseid, conjoint_id)][, all(N == 2)])
k <- x[nna == 0 & sel == 1]
stopifnot(k[selected == 1, all(pos == conjoint_respons)])
lv <- function(v, labs) labs[v]
d <- k[, .(id = as.integer(factor(responseid)), task = as.integer(conjoint_id), profile = pos, choice = as.integer(selected),
           attr_biomarker_status = lv(biomark, c("Positive", "Negative")),
           attr_ecog = as.character(ecog),
           attr_age = lv(alder, c("63 years", "75 years", "87 years")),
           attr_sex = lv(kjonn, c("Female", "Male")),
           attr_comorbidity = lv(komorbiditet, c("Healthy", "Moderate", "Severe")),
           attr_smoking = lv(royk, c("Smoker", "Non-smoker")),
           attr_education = lv(utd, c("Low", "Medium", "High")))]
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "tranvag_2021_precision_medicine.csv"))
