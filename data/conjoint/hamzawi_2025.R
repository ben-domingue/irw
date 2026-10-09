##Japanese party-choice conjoint (valence and policy) from
##Hamzawi, Kato & Endo (2025). What brings you to the party? Voter preferences on parties
##through policy and valence dynamics. Party Politics. https://doi.org/10.1177/13540688251339631
##Replication data: Harvard Dataverse doi:10.7910/DVN/FTIKPX, CC BY 4.0, no restricted files.
##File read: valencejapan_data_replication.RData (objects `d` respondent file, `dcj` long
##conjoint file; loaded into their own environment). Design facts and wording from the APSA
##preprint (doi:10.33774/apsa-2024-2bq4l, CC BY 4.0): p. 9-10, Table 1, Online Appendix A.1
##and the pre-registration pages (A-10); the deposit README lists files only.
##Usage: Rscript hamzawi_2025.R <raw dir> <output dir>
##
##1,866 Japanese adults (Rakuten Insight panel, Qualtrics, 1-3 July 2022, quotas on gender
##and age cohort; 579 of 2,445 respondents never saw attributes because of a connection
##error and are not in the deposit). 10 forced choices between two hypothetical parties,
##14 attributes (11 valence, 3 policy). Two electoral contexts, 5 tasks each, as
##trial_context: "(S/M)MD" = choose the party whose CANDIDATE you prefer in the district
##(single/multi-member) race; "PR" = proportional-representation vote. The authors pool both
##(cregg by = ~cj_cxt), so ONE table.
##TASK ORDER CAVEAT: in the deposit tasks 1-5 are always the MD block and 6-10 the PR block,
##but the preprint (p. 9, A-10) says the block order was flipped for a random half of
##respondents and the deposit does not record which half. So `task` is the authors' index
##(MD block first), recorded in the source, NOT necessarily the display order across blocks.
##Outcome: choice = `selected`. Question (MD, Japanese in Appendix A.1): "次の２つの架空の
##政党のうち、どちらの政党に所属する候補者が選挙区の投票先としてより好ましいと思いますか。
##もし、どちらが好ましいかはっきりとは言えない場合でも、どちらか一方、あえていえばより好まし
##いと思われる方を選んでください。" (PR: 比例区 for 選挙区). Forced choice; skipping was
##allowed by the ethics committee (preprint fn 7): the 524 skipped tasks (both profiles NA,
##1,048 rows; 2.8% of tasks, as the preprint reports) are omitted, leaving 18,136 tasks
##(9,061 MD, 9,075 PR; the preprint says "18,136 cases for each" context, which matches the
##TOTAL task count, not a per-context count). 32 respondents skipped all 10 tasks, so the
##table has 1,834 respondents.
##Attribute text: the deposit stores the authors' English labels (respondents saw Japanese,
##Appendix Table A1); used as stored, internal double spaces collapsed ("1  chair" ->
##"1 chair"). Attribute order was randomized once per respondent (valence and policy blocks
##each shuffled, block order shuffled, fixed across that respondent's tasks); the deposit's
##*.rowpos columns are kept as attrpos_*.
##Restrictions (Table 1 note): ministers yes -> MPs not 0; ministers no -> MPs not 374;
##committee chairs / bills / MPs elected 2+ times / leader tenure constrain MPs and years since
##formation (full list in the note). Level shares are therefore unequal (e.g. MPs: 0 members
##97 rows vs 59 members 12,718).
##Covariates (respondent file `d`, matched by ResponseId, then dropped): cov_party_id (psup,
##"選挙でどの政党に投票するかは別にして、ふだんあなたは何党を支持していますか。", Japanese value-label
##text; 99 答えたくない and -99 -> NA); cov_dual_surname (ide_13, -3 against .. 3 in favour of
##"選択的夫婦別姓制度を導入する"); cov_tax_status_quo / cov_tax_8pct / cov_tax_5pct /
##cov_tax_abolish (constax_1-4) and cov_constref_incl_art9 / cov_constref_excl_art9 /
##cov_constref_defend (constreform_1-3): closeness 0 遠い (distant), 1 neither, 2 やや近い,
##3 とても近い (value labels); cov_therm_ldp / _cdp / _komeito / _ishin / _jcp / _dpfp
##(pfeeling_4-9, 0-100 thermometers, party from the variable label). -99 (no answer) -> NA in
##all of these.
##Dropped: Qualtrics ResponseId (Response.ID; PII-like platform ID), respondentIndex
##(= respondent), cj_md/cj_pr dummies. No survey weight in the deposit.
##N: 1,866 in the deposit and preprint; 1,834 with at least one answered task. Marginal
##means fall with scandal count (None 0.55 .. 10 times 0.42), the direction the preprint reports.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "valencejapan_data_replication.RData"), envir = e)
s <- as.data.table(e$dcj); r <- as.data.table(lapply(e$d, function(x) { attributes(x) <- NULL; x }))
stopifnot(uniqueN(s$respondent) == 1866, s[, .N, respondent][, all(N == 20)])
s <- s[!is.na(selected)]
stopifnot(s[, .(sum(selected), .N), .(respondent, task)][, all(V1 == 1 & N == 2)])
at <- c(ministers = "cj_cabministers", committee_chairs = "cj_comchairs", mps = "cj_memdiet",
        bills_introduced = "cj_nbillsintro", mps_reelected = "cj_mp2times", years_since_formation = "cj_yrssinceform",
        districts_with_candidates = "cj_districtswcand", promises_achieved = "cj_promises", scandals = "cj_scandals",
        leader_tenure = "cj_leaderyears", leader_personality = "cj_leaderpersonality",
        policy_dual_surname = "cj_policysurnames", policy_consumption_tax = "cj_policyconstax",
        policy_constitution = "cj_policyconstref")
d <- s[, .(id = as.integer(respondent), task = as.integer(task), profile = as.integer(profile),
           choice = as.integer(selected), trial_context = as.character(cj_cxt))]
for (n in names(at)) {
  v <- s[[at[n]]]; stopifnot(!anyNA(v))
  d[, paste0("attr_", n) := gsub("\\s+", " ", trimws(as.character(v)))]
}
for (n in names(at)) d[, paste0("attrpos_", n) := as.integer(s[[paste0(at[n], ".rowpos")]])]
stopifnot(d[, uniqueN(attrpos_scandals), id][, all(V1 == 1)])
## respondent covariates
m <- match(s$Response.ID, r$ResponseId); stopifnot(!anyNA(m))
na99 <- function(x) { x <- as.integer(round(x)); x[x == -99L] <- NA_integer_; x }
pl <- attr(e$d$psup, "labels")
ps <- as.integer(r$psup[m]); pid <- names(pl)[match(ps, pl)]; pid[ps %in% c(99L, -99L)] <- NA
stopifnot(all(ps %in% c(-99L, 1:11, 99L)))
d[, cov_party_id := pid]
d[, cov_dual_surname := na99(r$ide_13[m])]
cv <- c(tax_status_quo = "constax_1", tax_8pct = "constax_2", tax_5pct = "constax_3", tax_abolish = "constax_4",
        constref_incl_art9 = "constreform_1", constref_excl_art9 = "constreform_2", constref_defend = "constreform_3",
        therm_ldp = "pfeeling_4", therm_cdp = "pfeeling_5", therm_komeito = "pfeeling_6", therm_ishin = "pfeeling_7",
        therm_jcp = "pfeeling_8", therm_dpfp = "pfeeling_9")
for (n in names(cv)) d[, paste0("cov_", n) := na99(r[[cv[n]]][m])]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hamzawi_2025_party_valence.csv"))
