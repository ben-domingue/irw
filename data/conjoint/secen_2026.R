##Refugee destination-city conjoints (Arabic-speaking refugees in Germany and in Turkey, August 2024) from
##Secen, S., Ozturk, S., & Ozturk, A. (2026). Fearing not belonging: How local attitudes and policies
##shape refugees' destination preferences. Political Behavior. https://doi.org/10.1007/s11109-026-10180-5
##Replication data: Harvard Dataverse doi:10.7910/DVN/ANDKJP, CC0 1.0, no restricted files. Files read:
##Conjoint_Germany_rawdata (SPSS original, ?format=original) and Conjoint_Turkey_rawdata.sav (Qualtrics
##exports). Dofile_Conjoint_reshaping.do and "R script_main_AMCE_MM_analysis.R" read as text, not run.
##The article was not available (paywalled, repository copy embargoed): wording, levels, attribute
##order and the sample definition come from the Qualtrics exports (question text, level text piped
##into the task, value labels) and the authors' code.
##Usage: Rscript secen_2026.R <dir holding de_raw.sav and tr_raw.sav> <output dir>
##
##Two tables, one per country: separate samples and fieldings, and the authors estimate every AMCE
##and marginal mean per country (main R script: amce(..., data = dtu_tr) and (..., data = dtu_de),
##plotted side by side). Both surveys were shown in Arabic (UserLanguage = AR in every row), with the
##same six attributes and identical level text.
##Design: 5 tasks x 2 cities ("مدينة 1" / "مدينة 2"), 6 binary attributes, all shown. The six
##attribute rows were shown in an order drawn once per respondent (Qualtrics featureK.DISPLAY_NAME,
##one per respondent, used for all 5 tasks); attrpos_<attr> = row 1-6. Levels as displayed, in Arabic
##(the authors' codes in brackets): economy (state of the economy) "هناك العديد من الوظائف ذات الأجر
##الجيد في هذه المدينة" [good_jobs] / "هناك عدد قليل من الوظائف الجيدة في هذه المدينة" [no_good_jobs];
##syrians (number of Syrian refugees) [other_refugees / no_other_refugees]; benefits (benefits from
##local institutions) [institutional_benefit / no_]; locals (local population attitudes)
##[public_hostile / public_nonhostile]; family (family ties) [family / no_family]; mayor (local
##political leaders) [leader_hostile / leader_nonhostile]. No restriction is documented; level shares
##are 49.6-50.4% and all 64 combinations occur.
##choice = C<t>: "يرجى اختيار المدينة التي تفضل الانتقال إليها؟" ("Please choose the city you would
##prefer to move to", our translation); forced choice between city 1 and 2, no opt-out. task = t,
##profile = city number (recorded). Respondents who stopped part-way keep the tasks they answered
##(as in the authors' reshaped data); respondents with no answered task are omitted.
##Germany: 735 respondents, 3,512 tasks, identical to the authors' Conjoint_Germany_reshaped_data
##(7,024 non-missing chosen_ rows, 735 IDs; checked). Turkey: 4,322 respondents (3,717 with all 5 tasks).
##Covariates (English value-label text from the .sav): cov_gender (female: 1 Male, 2 Female; -1 "I do
##not know/Other" -> NA since it mixes refusal and other), cov_birth_year ("In which year were you
##born?": the value-label year; "1958 or before" -> NA), cov_education (-1 "I do not know\I do not wish
##to answer" -> NA), cov_party_id (partisan_germany / partisan_turkey, party felt closest to; asked of
##those with a party; "Other- specify" kept as text, its free text dropped), cov_partisanship,
##cov_country_of_origin, cov_legal_status, cov_year_arrival, cov_edu_host_country / cov_edu_host_years
##(edu_ger / edu_tur and years), cov_host_language (german_ / turkish_proficiency), cov_religion,
##cov_religiosity, cov_ethnic_identity, cov_attention_pass (Political_Behavior_11, "please select
##'Have done'": 1 if Have done, 0 otherwise, NA if not answered), cov_duration_sec (EndDate - StartDate,
##whole survey). trial_factor1 / trial_factor2: Qualtrics embedded data "treated"/"non_treated" set
##per respondent; their meaning is not documented in the deposit (kept as recorded, blank -> NA).
##Dropped: all free-text "_TEXT" fields (personal comments), Qualtrics dates, Status, channel,
##version/country flags, consent, vers_/revision_CBCONJOINT. No platform IDs, IP or location in the
##export; respondents are numbered in file order (as the authors' ID = _n). No survey weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
an <- c("حالة الاقتصاد" = "economy", "عدد اللاجئين السوريين" = "syrians", "فوائد المؤسسات المحلية" = "benefits",
        "مواقف السكان المحليين" = "locals", "الروابط العائلية" = "family", "القادة السياسيون المحليون" = "mayor")
lv <- list(economy = c("هناك العديد من الوظائف ذات الأجر الجيد في هذه المدينة", "هناك عدد قليل من الوظائف الجيدة في هذه المدينة"),
           syrians = c("هذه المدينة لديها بالفعل العديد من اللاجئين الذين يعيشون فيها", "لا يوجد الكثير من اللاجئين الذين يعيشون في هذه المدينة"),
           benefits = c("توفر المؤسسات المحلية فوائد اجتماعية للاجئين", "المؤسسات المحلية لا تقدم فوائد للاجئين"),
           locals = c("السكان المحليون أكثر عدائية تجاه اللاجئين", "السكان المحليون أقل عداءً تجاه اللاجئين"),
           family = c("لديك أقارب يعيشون في هذه المدينة", "ليس لديك أقارب يعيشون في هذه المدينة"),
           mayor = c("يتخذ رئيس البلدية إجراءات تقييدية ضد اللاجئين", "رئيس البلدية ليس معاديًا للاجئين"))
lab <- function(x, na = integer(0)) { y <- as.character(as_factor(x, levels = "labels")); y[zap_labels(x) %in% na | is.na(zap_labels(x))] <- NA; y }
build <- function(file, host, n_expect) {
  s <- as.data.table(read_sav(file))
  stopifnot(all(s$UserLanguage == "AR"))
  s[, rid := .I]
  s <- s[feature0.DISPLAY_NAME != ""]
  rows <- list()
  for (t in 1:5) for (p in 1:2) {
    x <- data.table(rid = s$rid, task = t, profile = p, C = as.integer(zap_labels(s[[paste0("C", t)]])))
    for (k in 0:5) {
      att <- an[s[[paste0("feature", k, ".DISPLAY_NAME")]]]
      txt <- s[[sprintf("feature%d.%d.%d_CBCONJOINT", k, t, p)]]
      stopifnot(!anyNA(att), mapply(function(a, v) v %in% lv[[a]], att, txt))
      for (a in unique(att)) { w <- att == a; x[w, paste0("attr_", a) := txt[w]]; x[w, paste0("attrpos_", a) := k + 1L] }
    }
    rows[[length(rows) + 1]] <- x
  }
  d <- rbindlist(rows, use.names = TRUE)[!is.na(C)]
  stopifnot(all(d$C %in% 1:2))
  d[, choice := as.integer(C == profile)][, C := NULL]
  stopifnot(d[, .N, .(rid, task)][, all(N == 2)], d[, sum(choice), .(rid, task)][, all(V1 == 1)],
            !anyNA(d[, .SD, .SDcols = patterns("^attr")]), uniqueN(d$rid) == n_expect | is.na(n_expect))
  keep <- s[rid %in% d$rid]
  yr <- lab(keep$age); yr[!grepl("^[0-9]{4}$", yr)] <- NA
  g <- zap_labels(keep$female)
  pb <- zap_labels(keep$Political_Behavior_11)
  hl <- if (host == "DE") c("edu_ger", "edu_germany_year", "german_proficiency", "partisan_germany") else
                          c("edu_tur", "edu_turkey_year", "turkish_proficiency", "partisan_turkey")
  cv <- data.table(rid = keep$rid,
    cov_gender = fifelse(g == 1, "male", fifelse(g == 2, "female", NA_character_)),
    cov_birth_year = as.integer(yr), cov_education = lab(keep$education, -1),
    cov_party_id = lab(keep[[hl[4]]], -1), cov_partisanship = lab(keep$partisanship),
    cov_country_of_origin = lab(keep$countryoforigin), cov_legal_status = lab(keep$legal_status),
    cov_year_arrival = lab(keep$year_arrival), cov_edu_host_country = lab(keep[[hl[1]]]),
    cov_edu_host_years = lab(keep[[hl[2]]]), cov_host_language = lab(keep[[hl[3]]]),
    cov_religion = lab(keep$religion), cov_religiosity = lab(keep$religiosity), cov_ethnic_identity = lab(keep$ethnic_identity),
    cov_attention_pass = fifelse(is.na(pb), NA_integer_, as.integer(pb == 3)),
    cov_duration_sec = as.numeric(difftime(keep$EndDate, keep$StartDate, units = "secs")),
    trial_factor1 = fifelse(keep$factor1 == "", NA_character_, keep$factor1),
    trial_factor2 = fifelse(keep$factor2 == "", NA_character_, keep$factor2))
  stopifnot(all(attr(keep$female, "labels")[c("Male", "Female")] == 1:2), attr(keep$Political_Behavior_11, "labels")[["Have done"]] == 3)
  d <- merge(d, cv, by = "rid")
  d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
  setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", names(lv)), paste0("attrpos_", names(lv))))
  setorder(d, id, task, profile)
  d
}
de <- build(file.path(raw, "de_raw.sav"), "DE", 735L)
stopifnot(nrow(de) == 7024L)
fwrite(de, file.path(out, "secen_2026_refugee_cities_de.csv"))
tr <- build(file.path(raw, "tr_raw.sav"), "TR", NA)
fwrite(tr, file.path(out, "secen_2026_refugee_cities_tr.csv"))
