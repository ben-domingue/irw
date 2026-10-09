##Factorial vignette experiment on satisfaction with municipal services from
##Prokop, C., & Tepe, M. (2022). Talk or type? The effect of digital interfaces on
##citizens' satisfaction with standardized public services. Public Administration,
##100(2), 427-433. https://doi.org/10.1111/padm.12739 (online 2021)
##Replication data: Harvard Dataverse doi:10.7910/DVN/1NQPEZ, CC0 1.0. Files read:
##data.xlsx (Dataverse serves it as the ingested tab file; saved here as data.tab),
##Qualtrics_Survey_Questionnaire.docx and Qulatrics_Survey_Flow.docx (wording and
##randomization, read as text), stata_syntax.do (authors' coding, read as text).
##Usage: Rscript prokop_2021.R <dir holding data.tab> <output dir>
##
##German online panel (Qualtrics, December 2019, all text in German). Each respondent read
##three vignettes ("Bitte stellen Sie sich folgende Situation vor:"), one profile per task.
##Three factors, each drawn anew for every vignette by a Qualtrics BlockRandomizer
##("Evenly Present Elements", 3 levels, so levels are balanced and factors independent):
##  attr_service   = verwaltungsvorgang: passport / certificate of good conduct / social-
##                   housing permit ("Sie möchten einen Reisepass beantragen." ...)
##  attr_interface = komebene: municipal app / self-service terminal / clerk in the
##                   citizens' office (sentence as displayed)
##  attr_quality   = serviceebene: pick-up works / delayed a day / delayed a day with an
##                   apology for a system error. The sentence names the service
##                   (${e://Field/wasesist}), so the stored text has 3 x 3 = 9 versions.
##  attr_image     = the picture shown under the vignette (interact). The questionnaire's image
##                   credits name three pictures: Smartphone, Self-Service-Terminal, Schreibtisch
##                   (desk). Image IDs are mapped to those names from their pairing with the
##                   interface text in vignettes 1-2 and their sizes (phone 118x240). In vignette 3
##                   the survey flow pairs the self-service-terminal text with the desk picture
##                   (IM_a9jeKzkXkRyNP2l, the clerk image): 707 task-3 vignettes show that
##                   mismatch. Kept as displayed; the authors' analysis ignores it.
##Outcomes ("Wie zufrieden wären Sie..."), 9-point scale stored as the Qualtrics codes 1-9
##(1 = "-4 - gar nicht zufrieden", 9 = "4 - sehr zufrieden"; higher = more satisfied):
##  rating_procedure = "... mit dem Ablauf?" (vign<k>_1), rating_result = "... mit dem
##  Ergebnis?" (vign<k>_2). The authors average the two (sat); that derived score is dropped.
##Sample: 2,118 Qualtrics records; 2,086 reached the end, but only 1,255 have any vignette
##rating (the rest left the survey before the vignettes, apparently quota screen-outs: the
##authors' .do drops "quota fails"). All 1,255 are kept (12 did not finish; rows with
##no rating are omitted). The authors' sample (Progress = 100, all three vignettes and all
##12 technology-attitude items answered) is 1,234 respondents; cov_progress allows that filter.
##Dropped: IP address, ResponseId, panel token (tic), empty recipient/location columns,
##timers, free-text "other" answers, the multi-select online-use and service-experience
##strings. Covariates: cov_age (alter, years), cov_gender (geschlecht 1 Weiblich = female,
##2 Männlich = male; questionnaire), cov_state (bula, Bundesland text from the
##questionnaire codes), cov_income (eink, questionnaire text), cov_duration_sec (whole survey,
##Qualtrics Duration), cov_progress; cov_expect_procedure/_result (pre-vignette general
##satisfaction with municipal services, same 1-9 codes), cov_techaff_1..12 (1-5 agreement),
##cov_atis_1..4 (1-6), cov_psm_1..5 (1-5), cov_smartphone (14 Ja, 17 Nein), cov_exp_app /
##cov_exp_sst (1 Ja, 2 Nein), cov_frequency (behoerde, 0 monthly .. 3 less than yearly),
##cov_public_sector (oed, 0 Ja, 1 Nein), cov_left_right (lr, 0 ganz links .. 10 ganz rechts),
##all codes as in the questionnaire. No survey weight. Vignette order = task (1-3).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.tab"), encoding = "UTF-8")
s[, id := .I]
img <- c(IM_23lz6jBix8wvnxP = "Smartphone", IM_dcyRotzLNLBZJVb = "Self-Service-Terminal", IM_a9jeKzkXkRyNP2l = "Schreibtisch")
bula <- c("1" = "Baden-Württemberg", "4" = "Bayern", "5" = "Berlin", "6" = "Brandenburg", "7" = "Bremen", "8" = "Hamburg",
          "9" = "Hessen", "10" = "Mecklenburg-Vorpommern", "11" = "Niedersachsen", "12" = "Nordrhein-Westfalen",
          "13" = "Rheinland-Pfalz", "14" = "Saarland", "15" = "Sachsen", "16" = "Sachsen-Anhalt", "17" = "Schleswig-Holstein",
          "18" = "Thüringen")
eink <- c("unter 2.000 Euro", "2.000 bis 4.000 Euro", "4.000 und mehr")
d <- rbindlist(lapply(1:3, function(k) {
  im <- sub('.*IM=(IM_[A-Za-z0-9]+).*', "\\1", s[[paste0("interact", k)]])
  stopifnot(all(im %in% names(img)))
  data.table(id = s$id, task = k, profile = 1L,
             rating_procedure = as.integer(s[[paste0("vign", k, "1")]]),
             rating_result = as.integer(s[[paste0("vign", k, "2")]]),
             attr_service = s[[paste0("verwaltungsvorgang", k)]],
             attr_interface = s[[paste0("komebene", k)]],
             attr_quality = s[[paste0("serviceebene", k)]],
             attr_image = unname(img[im]))
}))
d <- d[!is.na(rating_procedure) | !is.na(rating_result)]
stopifnot(d[, all(nzchar(attr_service) & nzchar(attr_interface) & nzchar(attr_quality))],
          d[, all(c(rating_procedure, rating_result) %in% c(1:9, NA))], uniqueN(d$attr_quality) == 9)
cv <- s[, .(id, cov_age = as.integer(alter), cov_gender = c("female", "male")[geschlecht],
            cov_state = unname(bula[as.character(bula)]), cov_income = eink[eink],
            cov_duration_sec = as.integer(`Duration(inseconds)`), cov_progress = as.integer(Progress),
            cov_expect_procedure = exp1, cov_expect_result = exp2)]
stopifnot(all(s$geschlecht %in% c(1, 2, NA)), all(is.na(s$bula) | as.character(s$bula) %in% names(bula)))
for (j in 1:12) cv[, paste0("cov_techaff_", j) := s[[paste0("technik", (j - 1) %/% 6 + 1, (j - 1) %% 6 + 1)]]]
for (j in 1:4) cv[, paste0("cov_atis_", j) := s[[paste0("atis", j)]]]
for (j in 1:5) cv[, paste0("cov_psm_", j) := s[[paste0("psm", j)]]]
cv[, `:=`(cov_smartphone = s$mediennutzung, cov_exp_app = s$erfahrungapp, cov_exp_sst = s$erfahrungsst,
          cov_frequency = s$behoerde, cov_public_sector = s$oed, cov_left_right = s$lr1)]
d <- merge(d, cv, by = "id")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "prokop_2021_digital_services.csv"))
