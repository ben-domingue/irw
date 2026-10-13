##Private-public co-regulation conjoint (Switzerland) from
##Kolcava, D., Rudolph, L., & Bernauer, T. (2021). Citizen preferences on private-public
##co-regulation in environmental governance: Evidence from Switzerland. Global Environmental
##Change, 68, 102226. https://doi.org/10.1016/j.gloenvcha.2021.102226
##Replication data: Zenodo doi:10.5281/zenodo.18231150 (concept DOI; resolves to the latest version
##10.5281/zenodo.18231151), CC BY 4.0, open access. File read: coregulation_rep_cj.csv. Read as text only:
##English_Survey_Coregulation.pdf (English instrument), readme.txt, replication_cj.R (authors' code, not run).
##Usage: Rscript kolcava_2021.R <dir holding coregulation_rep_cj.csv> <output dir>
##
##1,916 Swiss citizens (Intervista Online Access Panel, 10 Nov - 10 Dec 2019). Each respondent was randomly
##assigned to ONE green-economy context (Exp: 945 pesticides/agriculture, 971 finance/climate investments), read a
##newspaper excerpt and a policy target (finance: cut climate-damaging investments 70% by 2050; pesticides: cut
##pesticide use 50% by 2050), then saw 5 tasks of two reform "Proposals" (profile 1 = Proposal A, 2 = B) that differ on
##four attributes (the four open questions of the instrument):
##  attr_decision   who decides on concrete measures (6 levels);
##  attr_report     how the sector reports on implementation (confidential / public annual report);
##  attr_monitoring who monitors the report for accuracy (4 levels);
##  attr_law        whether binding state regulation follows if the sector misses its target (Not at all / by 2025 / 2035 / 2045).
##TABLE: ONE table, the two contexts pooled (the authors pool them in the main AMCEs, Fig. A.5 "pooled and by green
##economy context"; the attribute and level wording is the same except that "the financial sector" becomes "the
##agricultural sector"). The context is trial_context. The deposit stores short labels (e.g. "firms&ngos"); they are
##expanded here to the instrument's answer-option wording with the context's sector name replaced by the neutral
##"the sector" (the displayed text said "the financial sector" in the finance context and "the agricultural sector" in the
##pesticides context; trial_context says which), so the level text is shared across the two contexts, and the report/monitoring/law
##options to the instrument's short option headings ("Public report", "Mandatory monitoring by the Federal
##Administration", "Binding regulation by 2035", "Not at all"). The sector-specific sentence tails of the options are not
##stored per level. Mapping: firms=the sector alone; parliament=parliament alone; firms&parliament, ngos&parliament, firms&ngos,
##firms&ngos&parliament = the listed actors together; no monitoring/administration/ngos/administration&ngos; no law.
##Outcomes (all forced choices between Proposal A and B, no opt-out; each question asked on every task):
##  choice = "Suppose you had to decide in a referendum today. Would you rather accept Proposal A or Proposal B?"
##  choice_responsiveness = (data column resp) "Regardless of whether you are personally for or against the proposals: Is the
##     design of Proposal A or Proposal B more likely to ensure that a policy is made and implemented that most citizens of
##     Switzerland want?"
##  choice_effectiveness = (data column eff) "... more likely to ensure that the financial industry achieves the goal of
##     investing 70% less in climate-damaging firms?" (pesticides context: the agricultural sector's goal; the English
##     wording for that context is not printed in the instrument, the finance wording is the one shown).
##  The order of the effectiveness / responsiveness questions was random across respondents, fixed across tasks (not recorded).
##Randomization: no restriction or level probabilities are documented (instrument: "Each of them has different options");
##observed level shares are near-equal. Attribute order: the instrument lists the four questions in the order above; no
##randomization of order is documented.
##Dropped: ecscore (authors' environmental-concern scale), tt_invest / tt_pesticides (derived context dummies), pair
##(row counter), eff/resp are kept as the choice_ columns. No respondent covariates or weight in the file.
##Count check: 19,160 rows = 1,916 respondents x 5 tasks x 2 profiles; every task has exactly one chosen profile on each of
##the three questions.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "coregulation_rep_cj.csv"), encoding = "UTF-8")
stopifnot(nrow(d) == 19160, uniqueN(d$ID) == 1916)
dec <- c("firms" = "The sector alone", "parliament" = "Parliament alone", "firms&parliament" = "Parliament and the sector together",
         "ngos&parliament" = "Parliament and environmental NGOs together", "firms&ngos" = "Environmental NGOs and the sector together",
         "firms&ngos&parliament" = "Environmental NGOs, the sector and parliament together")
d[, attr_decision := dec[decision]]
d[, attr_report := c(confidential = "Confidential report", public = "Public report")[report]]
d[, attr_monitoring := c("no monitoring" = "No mandatory monitoring of the report",
                         administration = "Mandatory monitoring by the Federal Administration",
                         ngos = "Mandatory monitoring by environmental NGOs",
                         "administration&ngos" = "Mandatory monitoring by the Federal Administration and environmental NGOs jointly")[monitoring]]
d[, attr_law := c("no law" = "Not at all", "2025" = "Binding regulation by 2025", "2035" = "Binding regulation by 2035",
                  "2045" = "Binding regulation by 2045")[law]]
stopifnot(!anyNA(d[, .(attr_decision, attr_report, attr_monitoring, attr_law)]))
o <- d[, .(id = match(ID, sort(unique(ID))), task = as.integer(task), profile = match(profile, c("A", "B")),
           choice = as.integer(choice), choice_responsiveness = as.integer(resp), choice_effectiveness = as.integer(eff),
           attr_decision, attr_report, attr_monitoring, attr_law, trial_context = Exp)]
stopifnot(o[, sum(choice), .(id, task)][, all(V1 == 1)], o[, sum(choice_responsiveness), .(id, task)][, all(V1 == 1)],
          o[, sum(choice_effectiveness), .(id, task)][, all(V1 == 1)], !anyNA(o$profile))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "kolcava_2021_coregulation.csv"))
