##Cross-Strait agreement conjoint from
##Pan, H.-H., Kastner, S. L., & Pearson, M. M. (2025). Is China-Taiwan rapprochement possible?
##Experimental evidence from Taiwan. Journal of Conflict Resolution, 69(7-8), 1143-1171.
##https://doi.org/10.1177/00220027241300045
##Replication data: Harvard Dataverse doi:10.7910/DVN/6CWQYJ, CC0 1.0. File read:
##PPK_CSRAgreement_JCR_.tab (Dataverse original .dta = csr_analysis.dta). Clause text from the
##authors' analysis do-file (PPK_CSRAgreement_JCR_analysis.do, read as text, Figure 2 eqlabels)
##and the .dta variable labels. The article was not accessible (publisher 403).
##Usage: Rscript pan_2025.R <dir holding ppk.dta (the original .dta renamed)> <output dir>
##
##Online survey in Taiwan, April 2022 (wave 2); 3,446 respondents x 5 hypothetical cross-Strait
##agreements = 17,230 rows (published summaries report 2,905 respondents: not reconciled).
##Single-profile design: each agreement shows a subset of 8 possible concessions, 4 by China
##(pledge to unify without force; stop fighter jets / reduce missiles; support Taiwan's
##participation in IOs such as WHO; increase Taiwan's exports to China) and 4 by Taiwan (reduce
##arms procurement from the US; renounce independence; recognize both sides belong to one China;
##reduce restrictions on mainland investment). Each clause is coded Shown/Hidden in the source:
##Shown -> the clause text, Hidden -> "(not shown)". Each clause appears in ~50% of agreements;
##no agreement has zero clauses (observed restriction: 1-8 clauses shown).
##choice = support_w2, "Support for CSR agreement" (Support = 1 / Oppose = 0; accept/reject of a
##single agreement, so opt_out = yes). Wording paraphrased (questionnaire not deposited).
##trial_us_china_frame = random_usch_w2, a respondent-level randomized framing (none / US support /
##China threat / US support and China threat; "[Blank]" label -> "none").
##Task = row order within respondent (no task column; display order of the 5 agreements is not
##recorded); profile = 1.
##Covariates: cov_gender (gender_w2: Female = 0, Male = 1, value labels); the deposit's other
##respondent variables are the authors' binary recodes and are kept with their codes (labels in
##the .dta): cov_born_before_1978, cov_north, cov_college, cov_income_above_median, cov_pan_blue
##(ptyid: Pan-Green 0 / Pan-Blue 1), cov_natlid_chinese_or_both, cov_pro_unification,
##cov_pro_independence, cov_economy_over_security, cov_us_credible, cov_china_credible,
##cov_us_defend_no_indep / cov_us_defend_indep (1-4), cov_social_contact_china_live/born,
##cov_prob_china_attack (0-100, before the agreements), cov_prob_attack_if_accept /
##cov_prob_attack_if_reject (0-100, asked once per respondent). Qualtrics ResponseIds re-keyed;
##start/end timestamps dropped. No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- list.files(raw, pattern = "\\.dta$", full.names = TRUE); stopifnot(length(f) == 1)
x <- as.data.table(zap_labels(read_dta(f)))
x[, rid := as.character(responseid_w2)]
stopifnot(length(rle(x$rid)$lengths) == uniqueN(x$rid))           # rows of a respondent are contiguous
ids <- unique(x$rid); x[, id := match(rid, ids)]; x[, task := seq_len(.N), by = id]
cl <- c(ch_force_w2 = "attr_china_no_force", ch_missile_w2 = "attr_china_reduce_military", ch_who_w2 = "attr_china_ios_who",
        ch_exp_w2 = "attr_china_imports", tw_usarm_w2 = "attr_taiwan_us_arms", tw_indep_w2 = "attr_taiwan_renounce_independence",
        tw_onech_w2 = "attr_taiwan_one_china", tw_invest_w2 = "attr_taiwan_china_investment")
txt <- c(ch_force_w2 = "China: Pledge to unify Taiwan without the use of force",
         ch_missile_w2 = "China: Stop fighter jets from circling Taiwan and reduce missiles targeting Taiwan",
         ch_who_w2 = "China: Support our country's participation in IOs such as WHO",
         ch_exp_w2 = "China: Increase our country's export to China",
         tw_usarm_w2 = "Taiwan: Reduce arms procurement from the US",
         tw_indep_w2 = "Taiwan: Pledge to renounce Taiwan's independence",
         tw_onech_w2 = "Taiwan: Recognize that both sides belong to one China",
         tw_invest_w2 = "Taiwan: Reduce restrictions on mainland China's investments in our country")
d <- x[, .(id, task, profile = 1L, choice = as.integer(support_w2))]
for (v in names(cl)) { stopifnot(all(x[[v]] %in% 0:1)); d[, (cl[[v]]) := ifelse(x[[v]] == 1, txt[[v]], "(not shown)")] }
stopifnot(all(rowSums(x[, names(cl), with = FALSE]) >= 1), !anyNA(d$choice), x[, uniqueN(random_usch_w2), id][, all(V1 == 1)])
d[, trial_us_china_frame := c("none", "US support", "China threat", "US support and China threat")[x$random_usch_w2]]
d[, `:=`(cov_gender = c("female", "male")[x$gender_w2 + 1L], cov_born_before_1978 = x$age_w2, cov_north = x$reg_w2,
         cov_college = x$college_w2, cov_income_above_median = x$inc_w2, cov_pan_blue = x$ptyid_w2,
         cov_natlid_chinese_or_both = x$natlid_w2, cov_pro_unification = x$unify_w2, cov_pro_independence = x$indep_w2,
         cov_economy_over_security = x$economy_w2, cov_us_credible = x$us_credit_w2, cov_china_credible = x$ch_credit_w2,
         cov_us_defend_no_indep = x$usdef_noindep_w2, cov_us_defend_indep = x$usdef_indep_w2,
         cov_social_contact_china_live = x$soc_ch2_w2, cov_social_contact_china_born = x$soc_ch1_w2,
         cov_prob_china_attack = x$prob_chwar_w2, cov_prob_attack_if_accept = round(x$accept_prob_chwar_w2, 4),
         cov_prob_attack_if_reject = round(x$reject_prob_chwar_w2, 4))]
stopifnot(!anyNA(d$cov_gender), d[, .N, id][, all(N == 5)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pan_2025_crossstrait_agreement.csv"))
cat(nrow(d), uniqueN(d$id), mean(d$choice), "\n")
