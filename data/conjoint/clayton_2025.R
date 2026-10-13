##Electoral gender quotas and democratic legitimacy: factorial vignette experiment in 12 democracies from
##Clayton, A., O'Brien, D. Z., & Piscopo, J. M. (2025). Electoral gender quotas and democratic legitimacy.
##American Political Science Review. https://doi.org/10.1017/S0003055425000176
##Replication data: Harvard Dataverse doi:10.7910/DVN/D67GRI, CC0 1.0. Files read (Data/Raw): Argentina.csv, Brazil.csv,
##Mexico.csv, NZ.csv, Peru.csv, USA.csv, Portugal.tab, Spain.tab, UK.tab, AusNorFrance.tab (Australia, France and
##Norway, one Ipsos file); documentation: "Question Wording and Codebook.docx", README.rtf and the authors' Code/Data
##processing/*.R, read as text. (The README says 12 democracies; the Raw files are these ten files = 12 countries.)
##Usage: Rscript clayton_2025.R <dir holding the ten raw files> <output dir>
##
##One vignette per respondent (id = a running number over the pooled file; task = profile = 1). A news item about a
##neighbouring municipality's newly elected eight-member council. Two randomized attributes (the codebook's six
##vignettes = 3 compositions x 2 issues, shown in bold):
##  attr_council_composition  (treatments 1/4, 2/5, 3/6)
##    "all men"; "four men and four women"; "four women and four men, following a new rule that requires all parties
##    to run equal numbers of male and female candidates" (the codebook's bracketed wording; the headline says
##    "All-Male" or "Gender-Balanced" Council)
##  attr_policy_issue (treatments 1-3 / 4-6): "sexual harassment" or "animal mistreatment" policy (training requirement).
##Assignment is read from the survey-platform columns Vignettes_DO_treat1..6 (non-missing = shown; Portugal, Spain, UK:
##the Vignettes_DO text "treat1".."treat6"; AusNorFrance: QSAMPLE21..23 = 1; the authors' code comments: treat 1 = all-male,
##2 = gender-balanced, 3 = quota gender-balanced). Australia, France and Norway only had the harassment vignettes (1-3).
##Attribute levels are stored in English from the codebook, whatever the respondent's language (Spanish, Portuguese, English;
##French and Norwegian display language is not documented in the deposit, whose Ipsos file holds English text).
##Outcomes (all stored as the authors' 1-4 coding from their processing scripts; text answers mapped by the
##exact strings in those scripts), asked of the same vignette:
##  rating_right_citizens  "The council made the right decision for all local citizens." 1 strongly disagree .. 4 strongly agree
##  rating_right_target    "The council made the right decision for women [harassment] / the treatment of animals" same 1-4
##  rating_fair_target     "How fair was this decision to women / for the treatment of animals?" 1 very unfair .. 4 very fair
##  rating_fair_process    "Thinking for a moment about the gender composition of the council, how fair was the decision-making
##                         process?" 1 very unfair .. 4 very fair
##  rating_overturn        "The council's decision should be overturned." 1 strongly disagree .. 4 strongly agree, STORED RAW
##                         (the authors reverse it for their scale; higher here = less legitimacy)
##  rating_trust           "The council can be trusted to make decisions that are right for local citizens." 1-4 agree
##The two Ipsos-based files (AusNorFrance) have only citizens/women/fair_target/process (no overturn or trust).
##Answer strings: English Strongly disagree/Disagree/Agree/Strongly agree and Very unfair/Unfair/Somewhat fair/Very fair,
##the Spanish and Portuguese equivalents; English 'Somewhat disagree'/'Somewhat agree'/'Somewhat unfair' (Ipsos file) = 2/3/2 as in the
##authors' script. Source value "0" in the Ipsos file (2-8 cases per item) is not an answer category: set to NA.
##Not filtered (the authors drop speeders and respondents failing the manipulation check, which the exports keep):
##cov_manipulation_pass = 1 if the recommended-action check named training for the right issue, 0 otherwise (text
##match on 'training'/'capacit'/'treinamento'; NA for AusNorFrance, which has no check in the file); cov_duration_sec = whole-survey
##duration (Duration (in seconds)) for the other files; cov_module_sec = module duration SECT12 for Ipsos. The authors' cut-offs were
##Portugal/Spain/UK > 300 s, Mexico > 350 s, Peru > 600 s, Ipsos module > 10 s.
##Covariates: cov_country; cov_gender (gender: Male/Man/Hombre/Masculino = male, Female/Woman/Mujer/Feminino = female,
##'Otro/ No binario' = other; NZ file has no gender item); cov_age_group (age bands as in the source, Spanish/English text;
##the Ipsos files have cov_age instead = RESPAGE); cov_survey_weight (Ipsos WEIGHT only; other files have none). Spain/Portugal .tab
##files were ingested with garbled accents ('85 o m..s' is repaired to '85 o más'); no other texts in the table are affected.
##Dropped: IP address, latitude/longitude (PII FOUND), response ids, recipient fields, dates, all other items (party, ideology,
##knowledge, attitudes, ethnicity, religion, income...), and the authors' derived indices.
##Counts: the files hold 17,037 raw rows; 16,427 have a vignette and at least one answer (this table). The paper reports over 17,000
##surveyed and an analytic sample of 13,274 after its exclusions (manipulation check, speeders), which are not applied here.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
norm <- function(x) tolower(gsub("\\s+", " ", trimws(as.character(x))))
code <- c("muy en desacuerdo" = 1, "discordo totalmente" = 1, "strongly disagree" = 1, "muy injusta" = 1, "muy injusto" = 1,
          "muito injusta" = 1, "muito injusto" = 1, "very unfair" = 1,
          "algo en desacuerdo" = 2, "discordo" = 2, "disagree" = 2, "somewhat disagree" = 2, "algo injusta" = 2, "algo injusto" = 2,
          "um pouco injusta" = 2, "um pouco injusto" = 2, "unfair" = 2, "somewhat unfair" = 2,
          "algo de acuerdo" = 3, "concordo" = 3, "agree" = 3, "somewhat agree" = 3, "algo justa" = 3, "algo justo" = 3,
          "um pouco justa" = 3, "um pouco justo" = 3, "um pouca justa" = 3, "um pouca justo" = 3, "somewhat fair" = 3, "fair" = 3,
          "muy de acuerdo" = 4, "concordo totalmente" = 4, "strongly agree" = 4, "muy justa" = 4, "muy justo" = 4,
          "muito justa" = 4, "muito justo" = 4, "very fair" = 4)
num <- function(x) {
  x <- gsub('"', "", norm(x)); r <- unname(code[x]); r[x == "0"] <- NA
  bad <- unique(x[is.na(r) & !x %in% c("", "0", "na")]); if (length(bad)) stop("unmapped: ", paste(bad, collapse = " | "))
  as.integer(r)
}
first <- function(d, v) if (v %in% names(d)) d[[which(names(d) == v)[1]]] else rep(NA_character_, nrow(d))
last <- function(d, v) { i <- which(names(d) == v); if (length(i)) d[[i[length(i)]]] else rep(NA_character_, nrow(d)) }
gen <- function(x) { x <- norm(x); ifelse(x %in% c("male", "man", "hombre", "masculino"), "male",
        ifelse(x %in% c("female", "woman", "mujer", "feminino"), "female", ifelse(grepl("otro|other", x), "other", NA))) }
files <- list(
  list("Argentina.csv", "Argentina", "flag"), list("Brazil.csv", "Brazil", "flag"), list("Mexico.csv", "Mexico", "flag"),
  list("NZ.csv", "New Zealand", "flag"), list("Peru.csv", "Peru", "flag"), list("USA.csv", "United States", "flag"),
  list("Portugal.tab", "Portugal", "do"), list("Spain.tab", "Spain", "do"), list("UK.tab", "United Kingdom", "do"))
res <- list()
for (f in files) {
  d <- fread(file.path(raw, f[[1]]), encoding = "UTF-8", showProgress = FALSE)
  if (f[[3]] == "flag") {
    tr <- sapply(1:6, function(k) !is.na(d[[paste0("Vignettes_DO_treat", k)]]) & d[[paste0("Vignettes_DO_treat", k)]] == 1)
    treat <- apply(tr, 1, function(r) if (sum(r) == 1) which(r) else NA_integer_)
  } else treat <- suppressWarnings(as.integer(sub("treat", "", d$Vignettes_DO)))
  tg <- ifelse(treat %in% 1:3, "h", "a")
  harass_chk <- grepl("training|capacit|treinamento", first(d, "decide_harass"), ignore.case = TRUE)
  animal_chk <- grepl("training|capacit|treinamento", last(d, "decide_animal.1") , ignore.case = TRUE)
  if (f[[1]] %in% c("Argentina.csv", "Brazil.csv", "Mexico.csv", "NZ.csv", "Peru.csv", "USA.csv")) animal_chk <- grepl("training|capacit|treinamento", last(d, "decide_animal"), ignore.case = TRUE)
  r <- data.table(country = f[[2]], treat = treat,
    r_cit = num(first(d, "decide_citizen")),
    r_tgt = ifelse(tg == "h", num(first(d, "decide_women")), num(first(d, "decide_animal"))),
    f_tgt = ifelse(tg == "h", num(first(d, "fair_women")), num(first(d, "fair_animal"))),
    f_proc = num(first(d, "decisionprocess")), over = num(first(d, "overturn")), trust = num(first(d, "council_trust")),
    gender = gen(first(d, "gender")), age_group = sub("^85 o m.*s$", "85 o más", first(d, "age")), age = NA_integer_,
    weight = NA_real_, dur = as.integer(d[[grep("^Duration", names(d))[1]]]), module = NA_integer_,
    manip = as.integer(ifelse(tg == "h", harass_chk, animal_chk)))
  res[[f[[1]]]] <- r
}
d <- fread(file.path(raw, "AusNorFrance.tab"), encoding = "UTF-8", showProgress = FALSE)
tr <- cbind(d$QSAMPLE21 == 1, d$QSAMPLE22 == 1, d$QSAMPLE23 == 1)
treat <- apply(tr, 1, function(r) if (sum(r, na.rm = TRUE) == 1) which(r) else NA_integer_)
ctry <- gsub('"', "", d$QCOUNTRY)
res[["ANF"]] <- data.table(country = ctry, treat = treat, r_cit = num(d$Q13I1_0), r_tgt = num(d$Q13I1_1), f_tgt = num(d$Q13I1I2),
  f_proc = num(d$Q13I2), over = NA_integer_, trust = NA_integer_, gender = gen(d$GENDER), age_group = NA_character_,
  age = as.integer(d$RESPAGE), weight = d$WEIGHT, dur = NA_integer_, module = as.integer(d$SECT12), manip = NA_integer_)
x <- rbindlist(res)
x <- x[!is.na(treat) & !(is.na(r_cit) & is.na(r_tgt) & is.na(f_tgt) & is.na(f_proc) & is.na(over) & is.na(trust))]
comp <- c("all men", "four men and four women",
          "four women and four men, following a new rule that requires all parties to run equal numbers of male and female candidates")
o <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L,
  rating_right_citizens = x$r_cit, rating_right_target = x$r_tgt, rating_fair_target = x$f_tgt, rating_fair_process = x$f_proc,
  rating_overturn = x$over, rating_trust = x$trust,
  attr_council_composition = comp[(x$treat - 1L) %% 3L + 1L],
  attr_policy_issue = ifelse(x$treat <= 3, "sexual harassment", "animal mistreatment"),
  cov_country = x$country, cov_gender = x$gender, cov_age = x$age, cov_age_group = x$age_group, cov_survey_weight = x$weight,
  cov_duration_sec = x$dur, cov_module_sec = x$module, cov_manipulation_pass = x$manip)
stopifnot(!anyNA(o$attr_council_composition))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "clayton_2025_gender_quotas.csv"))
