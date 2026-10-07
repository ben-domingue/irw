##Immigrant flow/stock conjoint (US) from
##Margalit, Y., & Solodoch, O. (2022). Against the flow: Differentiating between public
##opposition to the immigration stock and flow. British Journal of Political Science, 52(3),
##1055-1075. https://doi.org/10.1017/S0007123420000940
##Replication data: Harvard Dataverse doi:10.7910/DVN/EGARNT, CC0 1.0, no restricted files.
##File read: flowstock_cjoint_replication.dta (Dataverse "original format" download; long
##format, one row per profile, Stata value labels). The deposit's flowstock_codebook.txt
##covers only the main survey file, not this one; design and wording are from the article
##(open access, CC BY-NC-SA). The authors' .do/.R files were read as text, not run.
##Usage: Rscript margalit_2022.R <dir holding the .dta> <output dir>
##
##Lucid national quota sample, February 2019: 2,247 respondents, 4 pairs of immigrant
##profiles each (source `profile` encodes task*10 + profile: 11, 12, ..., 42), 9 attributes
##replicating Hainmueller & Hopkins (2015), with fewer education, job-plan and prior-trip
##levels. Every respondent has all 8 rated profiles.
##"Designs 1-3" (as listed in the Avina et al. 2026 meta-reanalysis) are the three framing
##arms, randomized between respondents: trial_frame = cjoint_treat label
##  "Flows" (1,116 respondents): visa applicants abroad who wish to enter the US;
##  "Stocks" (668): resident aliens in the US who wish to renew their visa;
##  "Stocks-deport" (463): as Stocks, where refusal is described as deportation.
##The attribute set and level codes are the same in all three arms, and the authors fit one
##pooled model with arm interactions (Figure 7, Figure A3), so this is ONE table with
##trial_frame, not three.
##Outcome (rating, 1-7, 7 = most favourable): "On a scale from 1 to 7, where 1 indicates
##that the U.S. should absolutely not admit [definitely deport] the immigrant [resident
##alien] and 7 indicates that the United States should definitely admit [allow] the
##immigrant [resident alien to stay], what would you decide regarding applicant [resident
##alien] #1?" (bracketed = stock wording; endpoints 'Absolutely not admit'/'Definitely
##deport' .. 'Definitely admit'/'Definitely allow'). Each profile was rated; no forced choice
##is in the deposit, so there is no choice column.
##Attribute text: the Stata value labels are the authors' SHORT labels (e.g. "fluent
##English", "once w/o authorization", "contract with employer"), used as is. The full
##displayed wording (and any wording change between arms) is in the article's online
##Appendix Section 4, not read. Attribute order and randomization restrictions are not
##documented in the deposit.
##Covariates: none. The respondent file (flowstock_replication.dta, keyed by Qualtrics
##ResponseId) cannot be linked to this file (keyed by a separate Lucid UUID `rid`; row
##order does not match: cross-tab of arms is not one-to-one), so no covariates are joined.
##Dropped: rid (platform UUID; id is the source's integer ID label 1..2,247), the authors'
##stock_* interaction dummies. N = 2,247 matches the main survey file; the article gives
##"approximately 1,120 respondents in both the flow and stock treatment group".
##Spot check: respondent fixed-effects OLS of rating on all 9 attributes x Stocks-deport
##(Flows and Stocks-deport arms, as the .do file's Figure 7 model) reproduces the deposited
##flows_Fig7_data.xlsx main effects (male -0.05, high school 0.13, college 0.20, broken
##English -0.16).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "flowstock_cjoint_replication.dta"))
lab <- function(x) { y <- as.character(as_factor(x, levels = "labels")); stopifnot(!anyNA(y)); y }
d <- data.table(id = as.integer(k$ID), task = as.integer(k$profile) %/% 10L, profile = as.integer(k$profile) %% 10L,
                rating = as.integer(k$Qjoint_), trial_frame = lab(k$cjoint_treat))
for (v in c("gender", "education", "language", "country", "profession", "experience", "emplans", "reason", "trips"))
  d[, paste0("attr_", v) := lab(k[[paste0("A_", v)]])]
setnames(d, c("attr_country", "attr_emplans", "attr_reason", "attr_trips"),
         c("attr_origin", "attr_job_plans", "attr_application_reason", "attr_prior_trips"))
stopifnot(uniqueN(d$id) == 2247, d[, .N, id][, all(N == 8)], d[, uniqueN(trial_frame), id][, all(V1 == 1)],
          all(d$rating %in% 1:7), uniqueN(k$rid) == 2247)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "margalit_2022_stock_flow.csv"))
