##Climate-pledge conjoint experiments in ten countries (two tables) from
##Aklin, M., Buntaine, M. T., & Mildenberger, M. (forthcoming). Public opinion and the political logic of
##international climate pledges. Global Environmental Politics.
##Replication data: OSF project u8z3n (https://doi.org/10.17605/OSF.IO/U8Z3N), CC0 1.0 (node licence and
##the archive's LICENSE.md). Files read from gep_replication.zip: data/ConjointAB_trimmed.csv,
##data/ConjointCD_trimmed.csv. Read as text only: README.md, CODEBOOK.md, script/01_replication.R and
##the pre-analysis plan Conditional_Climate_Conjoint_PAP_211019.pdf (same OSF node).
##Usage: Rscript aklin_2026.R <dir holding the two csv files> <output dir>
##
##Dynata online panels, October 2021 (week before COP26), age x gender quotas, in Brazil, China, Germany,
##India, Indonesia, Japan, Mexico, South Africa, the UK and the US; instrument translated into Portuguese,
##Mandarin, German, Bahasa Indonesia, Japanese, Spanish and isiZulu (South Africa: English or isiZulu;
##India: English only). The deposit stores the levels in English ("verbatim", CODEBOOK.md).
##Two conjoint experiments with different attribute sets -> two tables; each pools the ten countries
##(cov_country), as the authors' main estimates do. Same 12,646 respondents in both (only respondents
##who chose in all three tasks of both; SI Section 3), and `id` is the same person in both tables
##(source key = country x respondent index). The vignette experiment (Experiment 2; respondent-specific
##pledge relative to own baseline) is not a conjoint and has no key to these files: not built.
##3 tasks (task, in the order presented) x 2 profiles. The files have no profile column: within a task
##the two rows are taken as profile 1, 2 in file order (INFERRED; exactly one selected per task).
##Attribute order (PAP p.3): the first two attributes (unconditional, then conditional commitment) are
##fixed in that order; the order of the last two is randomized per respondent and kept across the three
##tasks; not recorded. No restrictions are documented and all 12 commitment combinations occur.
##Outcome (CODEBOOK.md, English instrument), forced choice:
##  aklin_2026_climate_pledges (Experiment 1): "Which of the following pledges would you prefer that
##    [HOMECOUNTRY] makes?" Attributes: unconditional commitment (0-50% "reduction regardless of what
##    other countries do"), conditional commitment, sector that must reduce pollution, who monitors.
##  aklin_2026_climate_transfers (Experiment 3): "Which country would you prefer to see financial and
##    technical assistance given to?" (two hypothetical developing countries). Attributes: unconditional
##    and conditional commitment of the recipient, its income level, who monitors.
##Covariate: cov_comprehension_check, the answer to the pre-experiment comprehension question ("20%" is
##correct, "30%" wrong, NA not answered; wording in CODEBOOK.md). Demographics are in the vignette files
##with no key to the conjoint rows, so none are attached. No survey weight.
##Spot check: Experiment 1 LPM of choice on the 12 combined commitment levels + sector + monitor reproduces
##output/estimates/fig02_domestic_levels.csv / figS05 (e.g. 50%+10% conditional 0.249, 50% only 0.204,
##Electricity -0.119, The UN 0.034).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ab <- fread(file.path(raw, "ConjointAB_trimmed.csv"))
cd <- fread(file.path(raw, "ConjointCD_trimmed.csv"))
key <- unique(rbind(ab[, .(country, respondent)], cd[, .(country, respondent)]))
setorder(key, country, respondent)
key[, id := .I]
stopifnot(nrow(key) == 12646)
build <- function(s, attrs) {
  s[, profile := seq_len(.N), .(country, respondent, task)]
  stopifnot(s[, .N, .(country, respondent, task)][, all(N == 2)], s[, sum(selected), .(country, respondent, task)][, all(V1 == 1)])
  d <- merge(s, key, by = c("country", "respondent"))
  o <- d[, .(id, task = as.integer(task), profile = as.integer(profile), choice = as.integer(selected))]
  for (v in names(attrs)) o[, (paste0("attr_", attrs[[v]])) := trimws(d[[v]])]
  o[, cov_country := d$country]
  o[, cov_comprehension_check := d$comprehension_check]
  stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_")]), uniqueN(o$id) == 12646, nrow(o) == 75876)
  setorder(o, id, task, profile)
  o
}
fwrite(build(ab, list(Unconditional.commitment.level = "unconditional_commitment", Conditional.commitment.level = "conditional_commitment",
                      What.sector.must.reduce.pollution. = "sector", Who.will.monitor.agreement. = "monitor")),
       file.path(out, "aklin_2026_climate_pledges.csv"))
fwrite(build(cd, list(Developing.country.unconditional.commitment.level = "unconditional_commitment",
                      Developing.country.conditional.commitment.level = "conditional_commitment",
                      Developing.country.income.level = "income_level", Who.will.monitor.agreement. = "monitor")),
       file.path(out, "aklin_2026_climate_transfers.csv"))
