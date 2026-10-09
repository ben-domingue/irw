##Sino-Japanese policy-package conjoints (China and Japan) from
##Incerti, T., Mattingly, D., Rosenbluth, F., Tanaka, S., & Yue, J. (2021). Hawkish partisans:
##How political parties shape nationalist conflicts in China and Japan. British Journal of
##Political Science, 51(4), 1494-1515. https://doi.org/10.1017/S0007123420000095
##Replication data: Harvard Dataverse doi:10.7910/DVN/S4YXQB, CC0 1.0, no restricted files.
##Files read: China_Data_FINAL.dta and Japan_Data_FINAL.dta ("original format" downloads; the
##anonymized Qualtrics exports). The reshaping and the sample rules follow the authors'
##"1. Aggregate_CN.R" / "2. Aggregate_JP.R" (read as text, not run); wording and design from the
##Online Appendix (S0007123420000095sup001.pdf, sections A1-A3). The article body (paywalled)
##was not read.
##Usage: Rscript incerti_2021.R <raw dir> <output dir>
##
##Two tables, one per country: separate samples, separate fieldings and displayed text in
##different languages (Chinese / Japanese); the authors analyse them separately (Fig. 2-4).
##  incerti_2021_china_japan_cn: Chinese online respondents, 3,639 (the authors' dat_conjoint)
##  incerti_2021_china_japan_jp: Japanese online respondents, 3,331 with a conjoint (3,335 pass the
##    sample rules; the authors' data_conjoint has the same 19,986 rows)
##Each respondent saw 3 tasks (task 1-3) of two hypothetical Japan-China policy packages
##(profile 1 = 政策1 / Proposal 1, 2 = 政策2), 7 attributes (Yasukuni visits, economic
##cooperation / One Belt One Road, Japanese tariffs on Chinese goods, Chinese tariffs on Japanese
##goods, constitutional amendment on the SDF, Diaoyu/Senkaku sovereignty, Diaoyu/Senkaku
##resource development). attr_ text is the Chinese (cn) or Japanese (jp) text as displayed,
##taken from the export's level columns; English translations are in Appendix Table A.1.
##Attribute order was randomized once per respondent (the f / F_ name columns hold the same
##order in all three tasks for every respondent); attrpos_ gives the row (1-7).
##Outcome:
##  choice: Appendix A1 (English version of the instruction): "please compare the two sets of
##    policy proposals and choose which proposal you prefer between the two." Forced choice
##    between the two packages (Q4.2 / Q4.5 / Q4.8); no opt-out.
##Left out: the per-profile items Q4.3/4.6/4.9 (the authors' "score", stored 0-7 in the data,
##  wording and anchors not in any deposited file or the appendix) and Q4.4/4.7/4.10 (a 5-point
##  "which country does this favour" item: Chinese answer text in the CN export, unlabelled
##  codes 1-5 in the JP export, not analysed by the authors). The later vignette experiment
##  (Q5-Q9) is a separate one-factor-per-arm design and is not built.
##Restrictions: Appendix Table A.1: "Resource development by Japan only [attribute not available
##  if China has sovereignty]" and "Resource development by China only [... if Japan has
##  sovereignty]". (The authors' cjoint constraint_list names other pairs; the appendix and the
##  data are followed: those two pairs never occur.) Level weights not documented.
##Sample (authors' rules): CN drops early terminations (blank education, 116) and keeps
##  respondents with a conjoint (f11 non-blank): 3,639. JP keeps Finished, consent, Japanese
##  citizen, 20+, living in Japan, non-blank panel id, and drops 4 duplicated responses (the
##  authors' ResponseId exclusions); then rows with a conjoint (F_1_1 non-blank). JP tasks with no
##  answer to the choice question would be dropped (none occur; the authors keep them as NA).
##Dropped identifiers: JP ResponseId and NID (panel respondent id); ids are re-keyed as the
##  authors do (row number after the sample rules). Dates and free-text fields not kept.
##Covariates: CN cov_gender from q23 (男性 male, 女性 female; answer text), cov_age_group (q22
##  band text as exported, e.g. "25-29"), cov_education (q27 answer text). JP cov_gender from Q23
##  (authors' recode: 1 = male, otherwise not male; only codes 1/2 occur, 2 = female),
##  cov_age_group_code (Q22) and cov_education_code (Q26) keep codes: the JP export has no value
##  labels. No survey weight in either export.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
build <- function(x, fname, fprof, fq) {
  rows <- list()
  for (t in 1:3) for (p in 1:2) {
    d <- data.table(id = x$id, task = t, profile = p, ch = x[[fq[t]]])
    for (k in 1:7) {
      d[, paste0("nm", k) := x[[fname(t, k)]]]
      d[, paste0("lv", k) := x[[fprof(t, p, k)]]]
    }
    rows[[length(rows) + 1]] <- d
  }
  d <- rbindlist(rows)
  long <- melt(d, id.vars = c("id", "task", "profile", "ch"), measure.vars = patterns("^nm", "^lv"),
               variable.name = "pos", value.name = c("nm", "lv"))
  long[, pos := as.integer(pos)]
  long
}
key <- c(yasukuni = "yasukuni", obor = "economic_cooperation", jptariff = "japan_tariff", cntariff = "china_tariff",
         const = "constitution", sov = "diaoyu_sovereignty", dev = "diaoyu_development")
widen <- function(long, nmap) {
  long[, attr := key[nmap[nm]]]
  stopifnot(!anyNA(long$attr), all(long$lv != ""))
  w <- dcast(long, id + task + profile + ch ~ attr, value.var = "lv")
  setnames(w, key, paste0("attr_", key))
  pz <- dcast(long, id + task + profile ~ attr, value.var = "pos")
  setnames(pz, key, paste0("attrpos_", key))
  w <- merge(w, pz, by = c("id", "task", "profile"))
  stopifnot(w[, uniqueN(.SD), by = id, .SDcols = patterns("^attrpos_")][, all(V1 == 1)])
  w
}
## ---- China ----
cn <- as.data.table(read_dta(file.path(raw, "China_Data_FINAL.dta")))
cn <- cn[q27 != ""]
cn[, id := .I]
cn <- cn[f11 != ""]
lcn <- build(cn, function(t, k) paste0("f", t, k), function(t, p, k) paste0("f", t, p, k), c("q42", "q45", "q48"))
nm_cn <- c("靖国神社" = "yasukuni", "经济合作" = "obor", "日本对中国的关税水平" = "jptariff",
           "中国对日本的关税水平" = "cntariff", "日本修改宪法" = "const", "钓鱼岛主权" = "sov",
           "钓鱼岛及周边海域的开发" = "dev")
wcn <- widen(lcn, nm_cn)
stopifnot(all(wcn$ch %in% c("政策１", "政策２")))
wcn[, choice := as.integer((ch == "政策１") == (profile == 1))][, ch := NULL]
cv <- cn[, .(id, cov_gender = fifelse(q23 == "男性", "male", fifelse(q23 == "女性", "female", NA_character_)),
             cov_age_group = q22, cov_education = q27)]
stopifnot(!anyNA(cv$cov_gender), all(cv$cov_age_group != ""))
wcn <- merge(wcn, cv, by = "id")
## ---- Japan ----
jp <- as.data.table(read_dta(file.path(raw, "Japan_Data_FINAL.dta")))
jp <- jp[Finished != 0 & Q11 == 1 & Q21 == 1 & Q22 != 1 & Q24 != 48 & NID != "" &
           !(ResponseId %in% c(1894, 1840, 3549, 3183))]
jp[, id := .I]
jp <- jp[F_1_1 != ""]
ljp <- build(jp, function(t, k) paste0("F_", t, "_", k), function(t, p, k) paste0("F_", t, "_", p, "_", k), c("Q42", "Q45", "Q48"))
nm_jp <- c("靖国神社について" = "yasukuni", "経済協力について" = "obor", "日本の中国製品への関税について" = "jptariff",
           "中国の日本製品への関税について" = "cntariff", "日本国憲法改正について" = "const",
           "尖閣諸島の領有権について" = "sov", "尖閣諸島周辺の資源について" = "dev")
wjp <- widen(ljp, nm_jp)
wjp <- wjp[!is.na(ch)]
stopifnot(all(wjp$ch %in% 1:2))
wjp[, choice := as.integer(ch == profile)][, ch := NULL]
stopifnot(all(jp$Q23 %in% 1:2))
cv <- jp[, .(id, cov_gender = c("male", "female")[Q23], cov_age_group_code = as.integer(Q22), cov_education_code = as.integer(Q26))]
wjp <- merge(wjp, cv, by = "id")
## ---- checks + write ----
for (nm in c("cn", "jp")) {
  w <- get(paste0("w", nm))
  stopifnot(w[, .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)])
  setcolorder(w, c("id", "task", "profile", "choice", grep("^attr_", names(w), value = TRUE),
                   grep("^attrpos_", names(w), value = TRUE)))
  setorder(w, id, task, profile)
  fwrite(w, file.path(out, paste0("incerti_2021_china_japan_", nm, ".csv")))
  cat(nm, nrow(w), uniqueN(w$id), "\n")
}
