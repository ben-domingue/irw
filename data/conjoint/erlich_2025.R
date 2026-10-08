##Bribery-scenario conjoints (Ukraine) from
##Erlich, A., Gans-Morse, J., & Nichter, S. (2025). Selective bribery: When do citizens engage in
##corruption? Comparative Political Studies, 58(5), 996-1036. https://doi.org/10.1177/00104140241259444
##Replication data: Harvard Dataverse doi:10.7910/DVN/EVEOQN, CC0 1.0 (one archive,
##selective_bribery.tgz). Files read from SelectiveBribery_RepMaterials_ToSubmit/:
##  data_raw/SelectiveBribery_DataRaw_ToSubmit.xlsx (Qualtrics export, one row per respondent)
##  data_clean/raked_weights.rds (the authors' raked weight wt_fin, by Participant_ID)
##Design text from the IPR working paper version (WP-22-28, 2022), Experimental Design section and
##Table 2; the authors' scripts clean_corruption_conjoint.R and create_long.R were read as text.
##Usage: Rscript erlich_2025.R <dir holding SelectiveBribery_RepMaterials_ToSubmit> <output dir>
##
##Facebook-recruited Ukrainian adults, Aug-Oct 2020, survey in Ukrainian or Russian (respondent's
##choice). Sample = the authors' analysis sample (clean_corruption_conjoint.R): Progress >= 90 and
##not living outside Ukraine: 3,060 respondents, as in the article. Each respondent saw two
##scenarios, 4 screens each, in random block order (FL_39_DO/FL_40_DO); each screen a table of two
##side-by-side scenarios (A, B) with 11 attributes. The two scenarios have different attribute
##levels (wait time, need, substitute providers) and are analysed separately by the authors, so
##they are TWO tables:
##  erlich_2025_bribery_license: driver's licence vignette ("Nina is tired of taking public
##    transportation to work and wants a driver's license. When she goes to the driving school, the
##    instructor, Ivan, informs her that there will be a considerable wait time ...")
##  erlich_2025_bribery_clinic: healthcare vignette ("Petro has hurt his leg and needs a doctor ...
##    The doctor, Ruslana, informs him that there will be a considerable wait ...")
##task = screen number in the order shown (1-4 if the scenario block came first, 5-8 if second);
##trial_block_first = 1 if this scenario's block came first. profile 1 = scenario A, 2 = B.
##Outcomes (wording from the working paper, English; survey was in uk/ru):
##  choice: "indicate in which scenario - A or B - Nina [Petro] would be more likely to pay a bribe"
##    (DL<k>_FC_1 / MD<k>_FC_1: "Сценарий А" / "Сценарий Б"). Forced, no opt-out.
##  rating: "On a [7-point] scale from 'definitely no' to 'definitely yes,' how likely would Nina be
##    to pay a bribe to the instructor [doctor] to receive the license [treatment] more quickly?"
##    (_q1_A/_q1_B), asked of each scenario.
##  rating_self: "Using the same scale, if you were in Nina's position, how likely would you be to
##    pay a bribe ...?" (_q2_A/_q2_B).
##  The ratings are exported as Russian answer text; mapped 1 = "Абсолютно нет" (definitely no),
##  2 "Скорее всего нет", 3 "Наверно нет", 4 "И да, и нет", 5 "Наверно да", 6 "Скорее всего да",
##  7 = "Абсолютно да" (definitely yes), i.e. the order of the scale as the paper describes it
##  (no -> yes); the authors' recode_scale() numbers the same labels in the opposite direction
##  (1 = Абсолютно да) and their normalize() reverses it again before analysis, so here higher =
##  more likely to bribe, as in the paper's figures. A rating left blank is NA.
##Tasks with no forced-choice answer are dropped (as create_long.R does).
##Attributes: the 11 grid attributes come in one pipe-separated field per scenario (dl_traits<k>a/b,
##md_traits<k>a/b) in the order red tape, competing services, future interaction, other bribers,
##past interaction, detection risk, enforced, need, bribe size, first mover (instructor/doctor hinted
##at bribe), other official (more than one official required) (create_long.R / clean script
##separate()). Stored as displayed, in the respondent's survey language (Ukrainian or Russian; the
##Ukrainian "Taк"/"Нi" spellings with Latin letters are kept as displayed; outer spaces trimmed).
##The paper's Table 2 gives the row labels: wait time without bribe; commute to work by public
##transport / seriousness of injury; other nearby driving schools / clinics; typical bribe size;
##if bribed, is instructor/doctor certain to speed up; used same instructor/doctor in the past;
##will use again; percent of other drivers/patients giving bribes; probability police will catch
##the payment; instructor/doctor hinted at bribe; requires more than one instructor/doctor.
##Two task-level attributes in the vignette text (same for A and B): attr_citizen_name (the
##citizen, dl_citnames/md_citnames) and attr_official_name (instructor dl_drivernames / doctor
##md_docnames), the nominative form of the randomized name (first pipe field; the other fields are
##grammatical forms). Names were randomized by gender and Ukrainian/Russian ethnicity (paper fn 16);
##the authors' gender and ethnicity coding of each name is in clean_corruption_conjoint.R.
##Attribute order was randomized per respondent (fixed across the 8 screens) but is not recorded:
##no attrpos_ columns.
##Covariates: cov_gender (gender...149: "Женский" -> female, "Мужской" -> male; the authors' recode
##to Women/Men), cov_age (age, years as entered; one value is 120), cov_education (ed, Russian answer
##text), cov_survey_language (choice_lang, answer text), cov_native_language (lang), cov_oblast,
##cov_city_size, cov_income (inc) as answer text; cov_attention_pass_1 / _2 from screener1 /
##screener2 with the authors' correct answers ("Никакое из вышеперечисленных"; "Зеленый,Красный"),
##NA when not answered (the authors count non-response as a fail); cov_duration_sec = Qualtrics
##"Duration (in seconds)" for the whole survey (elapsed time for the 53 partial completes);
##cov_survey_weight = the authors' raked weight wt_fin (NA for 10 respondents without one).
##Dropped: Qualtrics ResponseId, Participant_ID (panel/lottery id, re-keyed to integers),
##LocationLatitude/LocationLongitude (GPS for some respondents: PII), browser, timers, list
##experiment and other survey items.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- file.path(a[1], "SelectiveBribery_RepMaterials_ToSubmit"); out <- a[2]
x <- as.data.table(suppressWarnings(suppressMessages(read_xlsx(file.path(raw, "data_raw/SelectiveBribery_DataRaw_ToSubmit.xlsx"),
                                                               guess_max = 10000))))
s <- x[Progress >= 90 & oblast != "Я живу за пределами Украины"]
stopifnot(nrow(s) == 3060, !anyDuplicated(s$Participant_ID))
w <- as.data.table(readRDS(file.path(raw, "data_clean/raked_weights.rds")))[, .(Participant_ID = ID, wt_fin)]
s <- merge(s, w, by = "Participant_ID", all.x = TRUE)
setorder(s, Participant_ID); s[, id := .I]
s[, order := fcoalesce(FL_39_DO, FL_40_DO)]
stopifnot(all(s$order %in% c("DLConjoint|MDConjoint", "MDConjoint|DLConjoint")))
yn <- function(v, ok) fifelse(is.na(v), NA_integer_, as.integer(v == ok))
cov <- s[, .(id, cov_gender = c("Женский" = "female", "Мужской" = "male")[`gender...149`],
             cov_age = as.integer(age), cov_education = ed, cov_survey_language = choice_lang,
             cov_native_language = lang, cov_oblast = oblast, cov_city_size = city_size, cov_income = inc,
             cov_attention_pass_1 = yn(screener1, "Никакое из вышеперечисленных"),
             cov_attention_pass_2 = yn(screener2, "Зеленый,Красный"),
             cov_duration_sec = as.numeric(`Duration (in seconds)`), cov_survey_weight = wt_fin)]
lev <- c("Абсолютно нет" = 1L, "Скорее всего нет" = 2L, "Наверно нет" = 3L, "И да, и нет" = 4L,
         "Наверно да" = 5L, "Скорее всего да" = 6L, "Абсолютно да" = 7L)
nm <- c("red_tape", "substitutes", "future", "other_bribers", "past", "risk", "enforced", "need",
        "bribe_size", "first_mover", "other_official")
build <- function(up, lo, offn, first) {
  r <- rbindlist(lapply(1:4, function(k) rbindlist(lapply(1:2, function(p) {
    ab <- c("a", "b")[p]; AB <- c("A", "B")[p]
    tr <- tstrsplit(s[[sprintf("%s_traits%d%s", lo, k, ab)]], "|", fixed = TRUE)
    stopifnot(length(tr) == 11)
    d <- data.table(id = s$id, screen = k, profile = p,
                    fc = s[[sprintf("%s%d_FC_1", up, k)]],
                    rating = unname(lev[s[[sprintf("%s%d_q1_%s", up, k, AB)]]]),
                    rating_self = unname(lev[s[[sprintf("%s%d_q2_%s", up, k, AB)]]]),
                    attr_citizen_name = tstrsplit(s[[sprintf("%s_citnames%d", lo, k)]], "|", fixed = TRUE)[[1]],
                    attr_official_name = tstrsplit(s[[sprintf("%s_%s%d", lo, offn, k)]], "|", fixed = TRUE)[[1]],
                    first = s$order == first)
    for (j in 1:11) set(d, j = paste0("attr_", nm[j]), value = trimws(tr[[j]]))
    d
  }))))
  r <- r[!is.na(fc)]
  stopifnot(all(r$fc %in% c("Сценарий А", "Сценарий Б")))
  r[, choice := as.integer((profile == 1 & fc == "Сценарий А") | (profile == 2 & fc == "Сценарий Б"))]
  r[, task := screen + fifelse(first, 0L, 4L)][, trial_block_first := as.integer(first)]
  stopifnot(r[, .N, .(id, task)][, all(N == 2)], r[, sum(choice), .(id, task)][, all(V1 == 1)])
  ac <- grep("^attr_", names(r), value = TRUE)
  stopifnot(!anyNA(r[, ..ac]), all(r[, sapply(.SD, function(v) all(nzchar(v))), .SDcols = ac]))
  r <- merge(r[, c("id", "task", "profile", "choice", "rating", "rating_self", ac, "trial_block_first"), with = FALSE],
             cov, by = "id")
  setorder(r, id, task, profile)
  r
}
fwrite(build("DL", "dl", "drivernames", "DLConjoint|MDConjoint"), file.path(out, "erlich_2025_bribery_license.csv"))
fwrite(build("MD", "md", "docnames", "MDConjoint|DLConjoint"), file.path(out, "erlich_2025_bribery_clinic.csv"))
