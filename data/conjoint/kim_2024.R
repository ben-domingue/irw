##Carbon-tax design paired conjoint (South Korea), control arm, from
##Kim, S. E., Kim, S. Y., & Suh, J. (2024). Public support for carbon tax in South Korea: The role of
##tax design and revenue recycling. Asia & the Pacific Policy Studies, 11(2), e385.
##https://doi.org/10.1002/app5.385
##Replication data: Harvard Dataverse doi:10.7910/DVN/M7QPIS, CC0 1.0. Files read: carbontax_korea.RData
##(one data.frame `dat_conjoint`, loaded into its own environment); carbon_tax_korea.R read as text (not
##run) for how it was built and for the authors' English level names.
##Usage: Rscript kim_2024.R <dir holding the .RData> <output dir>
##
##The survey randomized respondents to an information treatment before the conjoint; the deposit holds
##ONLY the control (no-information) arm: carbon_tax_korea.R builds `dat_conjoint` from the
##A<k>_CQ.Control answers and a separate `t_dat_conjoint` from A<k>_CQ.Treat, and only the former is in
##the .RData. So this table is the control arm: 845 respondents, up to 5 tasks of two carbon-tax
##proposals ("탄소세 정책안 A/B"), 4 attributes. Task (taskNum) and profile (choiceNum = A/B) are recorded.
##The authors dropped tasks with no answer (selected NA): 838 respondents have 5 tasks, 7 have fewer.
##Attribute levels are the Korean text shown (Qualtrics display text, with the authors' "<br />" -> " "):
##  attr_cost (월 평균 가계 부담, monthly household burden at 1 t CO2 per month): 40,000원 / 80,000원 /
##    120,000원
##  attr_energy (집중 과세 대상 에너지, main taxed energy): household / industrial / transport fuel
##  attr_redistribution (소득 재분배적 목적의 세수 사용, redistributive revenue use): 5 levels incl.
##    국가 보편 예산에 편입 (general budget), 국민 지급금 (universal dividend), 법인세 인하, 소득세 인하,
##    에너지 취약 계층 지원
##  attr_environment (환경적 목적의 세수 사용, environmental revenue use): 4 levels incl. 환경부 보편 예산에
##    편입, 기후 변화에 취약한 지역 지원, 녹색 일자리 창출, 신재생 에너지 개발 투자
##  The authors' English names (carbon_tax_korea.R cj() labels): 40,000/80,000/120,000 KRW; household,
##  industrial, transportation fuel; general government budget, tax rebate (universal dividends),
##  reducing corporate tax, reducing income tax, subsidy for the energy-poor; general Environment Ministry
##  budget, support regions vulnerable to climate change, green job creation, renewable energy investment.
##Attribute row order was not fixed (the authors' code looks attributes up by name in each task's
##c<k>_attrib<i>_name), but whether it varied per respondent or per task is not documented and the
##deposit does not keep it: no attrpos_.
##Outcome: choice = selected, which proposal the respondent chose ("탄소세 정책안 A/B"); exactly one per
##task (checked), no opt-out. Question wording not deposited. No rating in the deposit.
##No covariates are deposited. ResponseId (Qualtrics) is dropped; respondents re-keyed 1..845 in order of
##first appearance.
##Spot check: lm of choice on the four attributes, clustered by id: 80,000원 -0.14 (SE 0.013), 120,000원
##-0.28 (0.015) against 40,000원, the authors' cj() control-arm specification on the same rows; the article's
##figure values were not compared.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "carbontax_korea.RData"), envir = e)
s <- as.data.table(e$dat_conjoint)
stopifnot(nrow(s) == 8402, uniqueN(s$ResponseId) == 845)
s[, id := match(ResponseId, unique(ResponseId))]
d <- s[, .(id = as.integer(id), task = as.integer(taskNum), profile = as.integer(choiceNum), choice = as.integer(selected),
           attr_cost = as.character(cost), attr_energy = as.character(energy),
           attr_redistribution = as.character(redistribution_tax), attr_environment = as.character(environment_tax))]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$profile %in% 1:2))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), !any(grepl("<br", d[[v]])))
stopifnot(uniqueN(d$attr_cost) == 3, uniqueN(d$attr_energy) == 3, uniqueN(d$attr_redistribution) == 5, uniqueN(d$attr_environment) == 4)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kim_2024_carbon_tax_korea.csv"))
