##Foreign-investment-project conjoint in ten middle-income countries from
##Bulman, D., Leng, N., & Ratigan, K. (2025). Firm's source country or project characteristics?
##Survey experiments on preferences for Chinese investment in the Global South. The Chinese
##Journal of International Politics, 18(3), 267-. https://doi.org/10.1093/cjip/poaf006
##Replication data: Harvard Dataverse doi:10.7910/DVN/YGXPVC, CC0 1.0, no restricted files.
##File read: SourceCountryProjectCharacteristics_CleanData.dta (Dataverse "original format" download;
##the wide Qualtrics-based file). The authors' Reshaping.do and Analysis.do were read as text (the
##attribute-name translations below come from Reshaping.do); SupplementaryMaterials.docx read;
##article read online (OUP, open access). ReshapedData.dta (373 MB) not used.
##Usage: Rscript bulman_2025.R <raw dir> <output dir>
##
##TGM Research online panels, July 2024, 20,001 respondents after the authors removed those who
##failed two attention checks (supplement A; attention_conjoint and attention_ctrl are 1 for all).
##Each saw 5 pairs of hypothetical foreign investment projects (task 1-5, project 1/2 = profile
##1/2), 7 attributes, all shown, and "indicated which project they preferred" (article; the
##instrument and verbatim wording are not deposited; supplement Table C1 shows an English example
##as an image). choice = conjoint_<task> (1/2), forced, no opt-out (one per task, checked).
##TEN TABLES, one per country (bulman_2025_fdi_<country>): the article pools the countries for its
##main AMCEs (and also runs each country separately, supplement D3a-j), but respondents saw the
##attributes in their survey language (English, Spanish, Portuguese, Indonesian, Malay, Chinese)
##and the deposit keeps that displayed text, so the levels cannot be shared across countries.
##Attribute text = c<task>_attrib<j>_project<p> as displayed (the migrant-workers level includes
##the country, e.g. "20 workers from China"); the row's attribute is identified from the displayed
##name c<task>_attrib<j>_name via the authors' translation table (Reshaping.do). Row order
##randomized per respondent and constant across that respondent's tasks (article; checked) ->
##attrpos_<attr>. trial_language = the language of the displayed attribute names (en, es, pt, id,
##ms, zh). Malaysia mixes Malay, English and Chinese across respondents (and a few respondents'
##names and levels are in different languages); Indonesia has 2 English respondents.
##Observed restriction: the country in the migrant-workers level is always the firm's country of
##origin (checked for English text).
##Covariates (the deposit has codes without value labels for most): cov_gender (d_female 1 ->
##female, 0 -> male; the supplement's 9,994 female / 10,007 male match), cov_college (d_college
##0/1, college graduate; supplement D4c counts match), cov_urban (d_urban 0/1, urban residence),
##cov_left_right (c_ideology_1, self-placement 0 left .. 10 right; supplement D4f),
##cov_voted_incumbent (c_vote_win 0/1, voted for the current president/prime minister in the last
##election; supplement D4g), cov_aware_chinese_project (c_project 0/1, aware of a local Chinese
##project; article Figure 5), cov_age_group_code (d_age 1-4; the supplement's 18-29 = 7,323 and
##30-44 = 7,562 match codes 1 and 2, codes 3 + 4 = 45+; the 3/4 cut is not documented),
##cov_income_code (d_income 1-7, country-specific income categories), cov_region_code (d_region,
##sub-national region, no labels), cov_user_language (Qualtrics UserLanguage).
##Dropped: ResponseId (Qualtrics; ids re-keyed 1..N in file order across all countries), the
##free-text conjoint_open, the separate "diamond" investment vignette (treatment and outcomes:
##diamond_*, coop_*, favorable_*; a different experiment), projectatt_*, the constant attention
##flags, and region/ctrycode duplicates. No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(zap_labels(read_dta(file.path(raw, "SourceCountryProjectCharacteristics_CleanData.dta"))))
stopifnot(nrow(s) == 20001, !anyDuplicated(s$responseid), all(s$attention_conjoint == 1), all(s$attention_ctrl == 1))
s[, rid := seq_len(.N)]
an <- list(
  source = c(en = "Firm's country of origin", es = "País de origen de la empresa", pt = "País de origem da empresa",
             id = "Negara asal perusahaan", ms = "Negara asal firma", zh = "公司的原属国"),
  project_type = c(en = "Project type", es = "Sector del proyecto", pt = "Tipo de projeto", id = "Jenis proyek", ms = "Jenis projek",
                   zh = "投资计划所在的行业"),
  local_jobs = c(en = "Local job creation", es = "Generación de empleo local", pt = "Criação de empregos locais",
                 id = "Penciptaan lapangan kerja lokal", ms = "Penciptaan pekerjaan tempatan", zh = "产生的本地工作机会"),
  migrant_workers = c(en = "Migrant workers", es = "Trabajadores migrantes", pt = "Trabalhadores imigrantes", id = "Pekerja migran",
                      ms = "Pekerja migran", zh = "来自公司原属国的外籍劳工"),
  labor_violations = c(en = "History of labor rights violations", es = "Antecedentes de infracciones laborales",
                       pt = "Histórico de violações de direitos trabalhistas", id = "Riwayat pelanggaran hak-hak buruh",
                       ms = "Sejarah pelanggaran hak buruh", zh = "剥削劳工的前科"),
  environment_plan = c(en = "Plan to reduce environmental impact", es = "Plan para disminuir el impacto ambiental",
                       pt = "Plano para reduzir o impacto ambiental", id = "Rencana untuk mengurangi dampak lingkungan",
                       ms = "Rancangan untuk mengurangkan kesan alam sekitar", zh = "有无减少对环境负面影响的计划"),
  bribery = c(en = "Accusations of bribing local politicians", es = "Denuncias por sobornar a políticos locales",
              pt = "Acusações de suborno a políticos locais", id = "Tuduhan menyuap politisi lokal",
              ms = "Tuduhan merasuah ahli politik tempatan", zh = "有无与当地政客进行腐败交易的前科"))
nmap <- rbindlist(lapply(names(an), function(k) data.table(attr = k, lang = names(an[[k]]), name = unname(an[[k]]))))
nmap <- nmap[!(lang == "id" & attr == "migrant_workers")]  # "Pekerja migran" is the same in Indonesian and Malay; language taken from other rows
stopifnot(!anyDuplicated(nmap$name))
# attribute names per row (constant across tasks)
for (t in 2:5) for (j in 1:7) stopifnot(all(s[[sprintf("c%d_attrib%d_name", t, j)]] == s[[sprintf("c1_attrib%d_name", j)]]))
nm <- sapply(1:7, function(j) s[[sprintf("c1_attrib%d_name", j)]])
ia <- matrix(nmap$attr[match(nm, nmap$name)], ncol = 7)
stopifnot(!anyNA(ia), all(apply(ia, 1, function(r) setequal(r, names(an)))))
lg <- matrix(nmap$lang[match(nm, nmap$name)], ncol = 7)
langs <- apply(lg, 1, function(r) { u <- unique(na.omit(r)); paste(sort(u), collapse = ";") })
L <- list()
for (t in 1:5) for (p in 1:2) {
  stopifnot(all(s[[paste0("conjoint_", t)]] %in% 1:2))
  x <- data.table(id = s$rid, task = t, profile = p, choice = as.integer(s[[paste0("conjoint_", t)]] == p))
  for (k in names(an)) {
    pos <- apply(ia, 1, function(r) match(k, r))
    lev <- sapply(seq_len(nrow(s)), function(i) s[[sprintf("c%d_attrib%d_project%d", t, pos[i], p)]][i])
    stopifnot(all(lev != ""))
    x[, paste0("attr_", k) := lev][, paste0("attrpos_", k) := pos]
  }
  L[[length(L) + 1]] <- x
}
d <- rbindlist(L)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
# migrant workers' country = firm's country (English text)
en <- d[attr_migrant_workers %like% "^[0-9]+ workers from "]
stopifnot(all(sub("^[0-9]+ workers from ", "", en$attr_migrant_workers) == en$attr_source))
cv <- s[, .(id = rid, country, trial_language = langs, cov_gender = fifelse(d_female == 1, "female", "male"), cov_college = as.integer(d_college),
            cov_urban = as.integer(d_urban), cov_left_right = as.integer(c_ideology_1), cov_voted_incumbent = as.integer(c_vote_win),
            cov_aware_chinese_project = as.integer(c_project), cov_age_group_code = as.integer(d_age), cov_income_code = as.integer(d_income),
            cov_region_code = as.integer(d_region), cov_user_language = userlanguage)]
stopifnot(all(s$d_female %in% 0:1), sum(s$d_female) == 9994, sum(s$d_college) == 5505)
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", names(an)), paste0("attrpos_", names(an)), "trial_language"))
for (cc in sort(unique(d$country))) {
  x <- d[country == cc][, country := NULL]
  setorder(x, id, task, profile)
  fwrite(x, file.path(out, paste0("bulman_2025_fdi_", tolower(cc), ".csv")))
}
