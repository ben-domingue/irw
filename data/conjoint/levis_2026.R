##Carbon-taxation vignettes (Germany, Poland): cost x policy x messenger, from
##Levis, A., Smith, E. K., & Pianta, S. (2026). Attitudes towards carbon taxation in the EU: Messenger effects vs. content effects.
##Journal of Public Policy. https://doi.org/10.1017/S0143814X26101226 (authors, journal, year from Crossref; the deposit's
##Rmd is titled "Messenger Effects vs. Content Effects in the EU")
##Replication data: Harvard Dataverse doi:10.7910/DVN/FFTR4S, CC0 1.0. Files read: Replication_Data_Messenger.csv (datafile
##14037133, 3,192 respondents x 434 columns; only the columns named below were read) and JPP_Messenger_Replication_Code.Rmd
##(datafile 14037134, as text). Usage: Rscript levis_2026.R <dir with Replication_Data_Messenger.csv> <output dir>
##
##Online survey, Germany (n = 1,597) and Poland (n = 1,595) (quota sample; German/Polish text). Each respondent read SEVEN
##short vignettes about a hypothetical EU carbon fuel tax, one per task, and rated support. The factors (the authors'
##recode in the Rmd, which classifies the displayed text by regular expressions; replicated here):
##  cost:      the tax raises the average price by 10%, 50% or 100% (cars 1.60 -> 1.75/2.40/3.20 euro per litre; flights
##             250 -> 275/375/500 euro; heating 1,000 -> 1,100/1,500/2,000 euro per year);
##  policy:    fuel tax for cars, aviation or heating;
##  messenger: the actor who "strongly supports" the plan and whose spokesperson is quoted: the European Commission, the
##             German government, or the Polish government (in the policy paragraph and in the quotation, which agree in
##             every round: checked);
##  wording:   which of six German or six Polish adjectives ("important", "significant", "necessary", ...) the quoted
##             spokesperson used about the policy (the authors' robustness factor rt; language-specific codes).
##Level text is the authors' English codes (the displayed text is German/Polish HTML, not stored as levels).
##Task order: rounds 1-5, then Qualtrics "round 0" (the authors rename it round 6), then a 7th vignette which in the Rmd
##reuses the attributes of round 1 (rp1, rc1, rs1, rt1 with sup7): it is a REPEAT of task 1 (same text, not swapped), so
##trial_repeat_of = 1 on task 7. Task and profile are recorded as column names; profile = 1 (single vignette).
##rating = support for the policy, m1_vign_k_supp, integers 1-6 (observed range 1-6; the Rmd treats >= 4 as "support", so
##higher = more support). The answer labels and question text are not in the deposit: paraphrase. No opt-out.
##Six belief ratings per vignette (m1_vign_k_matrix_1..6: personal costs, low-income households' costs, country costs, CO2
##efficiency, moral duty, air-pollution efficiency, 1-7 by the data) are NOT included: their wording and anchors are not in
##the deposit (only the authors' variable names).
##Out-of-scope risk (Ben to decide): the messenger is who backs the policy, a source cue, not a feature of the tax itself;
##cost and policy do describe the evaluated object.
##Covariates: cov_country (DE/PL), cov_gender (quota_gndr via the authors' recode: 1 Man -> male, 2 Woman -> female,
##3 Non_binary and 4 Other -> other), cov_age_group (quota_age via the recode: 18-29 .. 60-74), cov_education
##(authors' recode of quota_educ, in each country's own categories: German Ohne_Schulabschluss ... Fachhochscule_Berufsakademie,
##Polish Inc_Secondary ... Doctorate), cov_survey_weight (weights, per respondent).
##Dropped: ResponseId (Qualtrics, re-keyed), open-ended gender text, postcode, free-text comments, timing, browser metadata,
##all attitude/behaviour batteries and the six belief ratings.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
rd <- c(1:5, 0)
cols <- c("ResponseId", "cntry", "weights", "quota_gndr", "quota_age", "quota_educ", paste0("m1_vign_", 1:7, "_supp"),
          paste0("round", rd, "_cost"), paste0("round", rd, "_policy"), paste0("round", rd, "_support"), paste0("round", rd, "_supportRandomTextSnippet"))
d <- fread(file.path(raw, "Replication_Data_Messenger.csv"), select = cols, encoding = "UTF-8")
stopifnot(nrow(d) == 3192, uniqueN(d$ResponseId) == 3192)
rx <- list(
  cost = c(" 1.75| 275| 1100| 1.100" = "10% price increase", " 2.40| 375| 1500| 1.500" = "50% price increase", " 3.20| 500| 2000| 2.000" = "100% price increase"),
  support = c("European|Europejskiej|Europäischen" = "European Commission", "German Government|niemieckiego|deutsche" = "German government",
              "The spokesperson of the Polish Governmen|polskiego|polnischen" = "Polish government"),
  policy = c("cars|samochodów|Autos" = "cars", "aviation|lotnictwa|Flugverkehr" = "aviation", "heating|ogrzewania|Heizen" = "heating"),
  supportRandomTextSnippet = c("wichtig," = "important_de", "bedeutsam," = "significant_de", "notwendig," = "necessary_de",
    "entscheidender Bedeutung," = "deci_importance_de", "großer Bedeutung," = "great_importance_de", "zentraler Bedeutung," = "cent_importance_de",
    "istotna," = "essential_pl", "znacząca," = "significant_pl", "niezbędna," = "necessary_pl", "kluczowa," = "crucial_pl",
    "znaczenie," = "great_importance_pl", "ważna," = "important_pl"))
cls <- function(x, v) { r <- rep(NA_character_, length(x)); for (p in names(rx[[v]])) r[grepl(p, x)] <- rx[[v]][[p]]; r }
build <- function(k) {
  r <- if (k <= 5) k else if (k == 6) 0 else 1
  s <- if (k == 7) 7 else k
  x <- data.table(src = d$ResponseId, task = k, profile = 1L,
                  rating = as.integer(d[[paste0("m1_vign_", k, "_supp")]]),
                  attr_cost = cls(d[[paste0("round", r, "_cost")]], "cost"),
                  attr_policy = cls(d[[paste0("round", r, "_policy")]], "policy"),
                  attr_messenger = cls(d[[paste0("round", r, "_support")]], "support"),
                  attr_wording = cls(d[[paste0("round", r, "_supportRandomTextSnippet")]], "supportRandomTextSnippet"),
                  cov_country = d$cntry,
                  cov_gender = c("male", "female", "other", "other")[d$quota_gndr],
                  cov_age_group = c("18-29", "30-39", "40-49", "50-59", "60-74")[d$quota_age],
                  cov_survey_weight = d$weights)
  x[, trial_repeat_of := if (k == 7) 1L else NA_integer_]
  x
}
t <- rbindlist(lapply(1:7, build))
de <- c("Ohne_Schulabschluss", "Haupt_Volks_Schule", "Mittlere_Reife/Realschule", "Abitur_Fachabitur", "Berufsschule", "Fach_Oberschule", "Uni", "Fachhochscule_Berufsakademie")
pl <- c("Inc_Secondary", "Secondary", "Some_Uni_Vocational", "Vocational_Professional", "Uni", "Postgraduate", "Doctorate")
q <- rep(d$quota_educ, 7)
t[, cov_education := fifelse(cov_country == "DE", de[q], pl[q])]
t[, id := match(src, unique(src))][, src := NULL]
ac <- grep("^attr_", names(t), value = TRUE)
stopifnot(!anyNA(t[, ..ac]), !anyNA(t$rating))
setcolorder(t, c("id", "task", "profile", "rating"))
setorder(t, id, task, profile)
fwrite(t, file.path(out, "levis_2026_carbon_messenger.csv"))
