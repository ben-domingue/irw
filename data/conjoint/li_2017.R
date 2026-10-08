##FDI-project conjoint (China) from
##Li, X., & Zeng, K. (2017). Individual preferences for FDI in developing countries:
##Experimental evidence from China. Journal of Experimental Political Science, 4(3), 195-205.
##https://doi.org/10.1017/XPS.2017.15
##Replication data: Harvard Dataverse doi:10.7910/DVN/DJTMJC, CC0 1.0. File read: data.dta
##(Dataverse "original format" download; Qualtrics export, Chinese text GB18030-encoded).
##readme.txt and code.do read as text; questionnaire = the article's supplementary appendix A
##(S205226301700015Xsup001.docx, English translation).
##Usage: Rscript li_2017.R <dir holding data.dta> <output dir>
##
##Chinese online respondents, wave 1 Nov 2014 (2,224) and wave 2 Oct 2015 (622); the authors
##pool the waves (code.do), so one table with trial_wave. 4 pairs of hypothetical FDI projects,
##7 attributes. Level text is the Chinese text shown, from the Qualtrics embedded fields
##q68_1_text .. q68_7_text (decoded from GB18030), checked 1:1 against the authors' English
##codes: country (投资方: 美国/日本/澳大利亚/菲律宾), industry (所属行业, 4), entry mode
##(投资方式, 4), job impact (对当地就业的影响, 3), amount (投资额: 1000/3000/5000万美元),
##local concessions (地方配套优惠措施, 3), wage (项目员工待遇, 4). q68_15_text gives the order in
##which the 7 attribute names were shown: attrpos_* (1 = top). The appendix says ordering and
##levels were fully randomized for each pair (restrictions none).
##Layout: the file stacks 8 blocks per wave (rows i, i+N, ..., i+7N for one respondent, N =
##2,224 / 622). Task and profile are INFERRED: blocks k and k+4 form task k (in every one of
##the 2,846 respondents x 4 tasks exactly one of the two is preferred; no other pairing of
##the 8 blocks does this), block k = profile 1 and block k+4 = profile 2. Which block was
##"Project 1" (left) is not recorded; the attribute order is identical within each inferred pair.
##Outcomes (same screen):
##  choice = "Of these two projects, which one do you prefer?" Project 1 / Project 2, forced.
##  rating = "Suppose that your city is evaluating the two FDI projects above and is seeking
##    your opinion. Please rate the two projects on a 7-point scale, with 7 equal to 'complete
##    support' and 1 equal to 'no support at all.'" (English translation in the appendix).
##4 tasks (8 profile rows, 3 respondents) have no embedded attribute text or order (not
##saved); they are dropped, leaving 2,846 respondents and 11,380 tasks.
##Covariates (authors' codes): cov_age_group_code (age group 1-6; the file carries no labels and
##the appendix lists the bands inconsistently, so the code is kept, under the _code name),
##cov_gender (male: readme.txt "male: gender (male=1)", and code.do Figure E4 labels male==0
##Female; written male/female), cov_han, cov_rural_hukou, cov_coastal, cov_college, cov_ccp, cov_cyl, cov_income (1-7,
##N10), cov_social_status (0-9 as stored), cov_soe, cov_foreign_firm, cov_private_firm,
##cov_manufacturing, cov_service, cov_news_interest (1-4).
##Dropped: Qualtrics ResponseId (v1, re-keyed to integers), occupation free text (q39_text),
##raw q* columns, the authors' attribute dummies and edu1-3.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "data.dta"))))
for (v in grep("_text$", names(s), value = TRUE)) s[, (v) := trimws(iconv(get(v), "GB18030", "UTF-8"))]
s[, v1 := as.character(v1)][, blk := seq_len(.N), v1]
stopifnot(s[, .N, v1][, all(N == 8)], all(s$male %in% 0:1))
s[, task := (blk - 1L) %% 4L + 1L][, profile := (blk - 1L) %/% 4L + 1L]
stopifnot(s[, sum(prefer), .(v1, task)][, all(V1 == 1)])
s[, miss := Reduce(`|`, lapply(paste0("q68_", 1:7, "_text"), function(v) is.na(get(v)) | get(v) == ""))]
nbad <- s[, any(miss), .(v1, task)][, sum(V1)]
s <- s[, if (!any(miss)) .SD, .(v1, task)][, miss := NULL]
an <- c(country = "投资方", industry = "所属行业", entry_mode = "投资方式", job_impact = "对当地就业的影响",
        amount = "投资额", concessions = "地方配套优惠措施", wage = "项目员工待遇")
codes <- c(country = "country", industry = "industry", entry_mode = "method", job_impact = "job",
           amount = "value", concessions = "policy", wage = "wage")
for (k in seq_along(an)) {
  txt <- s[[paste0("q68_", k, "_text")]]
  stopifnot(nrow(unique(data.table(txt, s[[codes[k]]]))) == uniqueN(txt), uniqueN(txt) == uniqueN(s[[codes[k]]]))
  s[, paste0("attr_", names(an)[k]) := txt]
}
ord <- strsplit(s$q68_15_text, ",")
stopifnot(all(lengths(ord) == 7), all(vapply(ord, function(o) setequal(o, an), TRUE)))
for (k in names(an)) s[, paste0("attrpos_", k) := vapply(ord, function(o) match(an[[k]], o), 1L)]
stopifnot(s[, uniqueN(q68_15_text), .(v1, task)][, all(V1 == 1)])
s[, id := match(v1, unique(v1))]
d <- s[, c(list(id = id, task = task, profile = profile, choice = as.integer(prefer), rating = as.integer(rating)),
           .SD[, c(paste0("attr_", names(an)), paste0("attrpos_", names(an))), with = FALSE],
           list(trial_wave = as.integer(wave), cov_age_group_code = as.integer(age), cov_han = as.integer(han), cov_gender = c("female", "male")[male + 1L],
                cov_rural_hukou = as.integer(rural), cov_coastal = as.integer(eastern), cov_college = as.integer(college),
                cov_ccp = as.integer(ccp), cov_cyl = as.integer(cyl), cov_income = as.integer(income),
                cov_social_status = as.integer(socialstatus), cov_soe = as.integer(SOE), cov_foreign_firm = as.integer(foreign),
                cov_private_firm = as.integer(private), cov_manufacturing = as.integer(manu), cov_service = as.integer(service),
                cov_news_interest = as.integer(news)))]
stopifnot(nbad == 4, uniqueN(d$id) == 2846, d[, .N, .(id, task)][, all(N == 2)], !anyNA(d$rating))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "li_2017_fdi_china.csv"))
