##UNFCCC reform-proposal conjoint (COP29 participants) from
##Koliev, F., Nasiritousi, N., Buylova, A., & Linnér, B.-O. (2026). Reform preferences of key
##actors in the UNFCCC process. Nature Climate Change, 16(8), 915-921.
##https://doi.org/10.1038/s41558-026-02723-9
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZYTBET, CC0 1.0. Files read:
##COP29_cjdata_final.csv (semicolon-delimited, one row per respondent x task x profile),
##README.txt, Supplementary_Material.pdf (Table A5, Figs S5-S6, survey instrument pages 1-6,
##AsPredicted #198,899 pre-registration), replication_code.r (read as text, not run).
##Usage: Rscript koliev_2026.R <dir holding COP29_cjdata_final.csv> <output dir>
##
##151 COP29 participants (state representatives recruited on site and digitally, non-state
##observers by email; Supplementary Fig. S5: n = 49 + 102 = 151), 6 tasks of 2 reform proposals,
##6 attributes, presented as a grid ("Proposal 1" / "Proposal 2"; instrument and Fig. S6).
##task, profile and attribute row positions (*_rowpos -> attrpos_*) are recorded. Attribute order is
##randomized once per respondent (rowpos constant within respondent in the data; the instrument
##pages show different orders across respondents' screenshots, same order across one respondent's
##tasks).
##  choice = selected: "Which proposal do you prefer (Proposal 1 or Proposal 2)? Please choose one."
##           Forced choice, no opt-out; exactly one chosen per task (stopifnot). The pre-registered
##           1-7 rating was dropped by the authors before fielding (Table A5).
##Attribute text: the data append " (SQ)" to each status-quo level; the pre-registration says the
##status-quo label "will not be shown to respondents" and the instrument screenshots show none, so
##the suffix is stripped. Otherwise the level text is as stored, which matches the instrument.
##Randomization: no restrictions documented (pre-registration: "Each proposal will randomly combine
##different levels of the attributes"); level probabilities not stated.
##Covariates (the only background questions asked, Table A5): cov_actor_group (q1 "Which group do
##you belong to?", stored as the authors' recoded constituency labels: Government, NGO, ENGO, RINGO,
##BINGO, ...), cov_region (q2 "Please select the region where you primarily reside or operate",
##answer text), cov_cop_experience (q3 "How many UNFCCC COPs have you attended?", answer text).
##Dropped: id (Qualtrics ResponseId), q1_15_text (free text "Other (please specify)", including
##organisation names), respondent_index (duplicate of respondent). id = source `respondent`.
##No survey weight.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "COP29_cjdata_final.csv"), sep = ";", encoding = "UTF-8")
stopifnot(nrow(s) == 1812, uniqueN(s$respondent) == 151, all(s$respondent == s$respondent_index))
at <- c(presidency_selection = "cop_presidency_selection", decision_making = "decision_making",
        implementation_focus = "implementation_focus", representation = "representation_at_co_ps",
        role_of_observers = "role_of_observers_at_co_ps", transparency = "transparency_and_accountability")
d <- data.table(id = as.integer(s$respondent), task = as.integer(s$task), profile = as.integer(s$profile),
                choice = as.integer(s$selected))
for (k in names(at)) d[, paste0("attr_", k) := sub(" \\(SQ\\)$", "", s[[at[[k]]]])]
for (k in names(at)) d[, paste0("attrpos_", k) := as.integer(s[[paste0(at[[k]], "_rowpos")]])]
stopifnot(d[, .N, .(id, task, profile)][, all(N == 1)], all(d$profile %in% 1:2),
          d[, sum(choice), .(id, task)][, all(V1 == 1)],
          !anyNA(d), !any(d[, .SD, .SDcols = patterns("^attr_")] == ""),
          d[, lapply(.SD, uniqueN), id, .SDcols = patterns("^attrpos_")][, all(unlist(.SD[, -1]) == 1)])
d[, cov_actor_group := s$q1]
d[, cov_region := s$q2]
d[, cov_cop_experience := s$q3]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "koliev_2026_unfccc_reform.csv"))
