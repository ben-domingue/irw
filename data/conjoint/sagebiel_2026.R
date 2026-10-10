##Tofu choice experiment with information treatments (Sweden, 2021) from
##Sagebiel, J., Castellari, E., Rommel, J., Weigel, M., & Welling, M. (in press). Swedish
##consumers' preferences for tofu sustainability characteristics: A choice experiment with
##information treatments. German Journal of Agricultural Economics (GJAE); not yet in print, no
##article DOI. Abstract (Zenodo record): "a choice experiment with around 1,400 Swedish consumers".
##Data: Zenodo record 22649882, doi:10.5281/zenodo.22649882, CC BY 4.0 (record licence; the
##creators are the article's authors; migrated from OSF project a986e, which shows no licence).
##Preregistration osf.io/gvxkt (not read).
##Files read: tofu_main_swe_tofu.xlsx (sheet "data": one row per respondent x choice set;
##sheet "dictionary": Swedish question and level text) and tofu_main_swe_covariates.xlsx (sheets
##"data", "dictionary"). Design facts from tofu_questionnaire_english.pdf (SurveyEngine export)
##and choiceset.png (an English screenshot of one choice set).
##Usage: Rscript sagebiel_2026.R <raw dir holding the two xlsx files> <output dir>
##
##Online panel survey in Sweden (SurveyEngine), 13 Jan - 26 Feb 2021. Each respondent saw 9
##choice sets ("Choice Set k of 9"): two variants of a 400 g piece of natural tofu (profile 1 =
##"Variant 1", 2 = "Variant 2") plus a third option "I would not buy any of the variants"
##(opt-out: choice = 0 on both profiles). task = SEQ (display order; equal to SCENARIO here).
##Question (dictionary, Swedish, as shown): "Vilken produkt skulle du föredra?"; the English
##screenshot reads "Which would you choose?".
##Attributes (Swedish text from the dictionary sheet, the language respondents saw; the English
##screenshot shows the same card as a grid): attr_production_country "Landet där tofuen
##tillverkas" (Sverige / Annat land inom EU / Land utanför EU); attr_soy_origin
##"Sojabönornas ursprungsland" (same three levels); attr_cultivation "Kultivering av sojabönorna"
##(Ekologiska metoder / Icke-ekologiska konventionella metoder); attr_price "Pris per 400g"
##(15, 20, 25, 30, 35, 40, 50, 60 SEK).
##Design: FIXED design of 27 rows (DESIGN_ROW); each choice set drew a "random design row"
##(questionnaire). In every row the two variants differ on every attribute (variant 2's level is
##variant 1's shifted by one, checked: no task shares a level), a restriction across profiles.
##Respondents who started under survey version 7 (13-14 Jan 2021, 104 ids) got a slightly
##different version of 11 design rows (the two variants' levels swapped within a row); the stored
##levels are what each respondent saw. cov_survey_version keeps VERSION.
##Information treatment (trial_info_treatment; covariates `split`, a 4-card deck): shown before
##the choice sets: 1 = Environment (CO2 text), 2 = Health, 3 = Recipe, 4 = Control (no
##treatment page; questionnaire display conditions $split==1/2/3).
##Respondents: the choice file has 1,574 ids; 67 unanswered choice sets (pref1 missing) are
##omitted, which removes 33 ids with no answered set, leaving 1,541 (1,459 status Complete, 80
##"System initiated timeout", 2 "User initiated timeout"; cov_status). The article's sample
##("around 1,400") is presumably after exclusions not reproduced here (e.g. completes only, or
##the attention item, which only 50% of rows pass).
##Covariates (codes -> text from the covariates dictionary sheet): cov_gender (Kvinna -> female,
##Man -> male, Övrigt -> other, "Föredrar att inte svara" -> NA); cov_age (age_other, typed
##whole-number age; NA when "prefer not to say"); cov_education (q55, Swedish answer text,
##refusal -> NA); cov_diet (q56; "Övrigt" kept, its free text dropped; refusal -> NA);
##cov_shop_frequency (shoptofu: how often the respondent shops groceries, text); cov_buys_<cat>
##(eattofu_1-6, "which of these do you buy", 1 = selected, 0 = not); cov_device (devicetype
##text); cov_store_type (q83, refusal -> NA, free text dropped); cov_tofu_price_guess (costest_other,
##SEK; NA if refused or non-numeric); cov_dce_random/sure/realistic/store_like/attributes_matter
##(dce_followup_1-5, 1 = Håller inte med alls .. 7 = Håller med helt); cov_attention_pass
##(dce_followup_6 "Vänligen besvara denna fråga med 'håller mycket med'": 1 if 7, 0 otherwise,
##NA if not answered); cov_knew_tofu, cov_knowledge_increased, cov_tofu_tastes_good,
##cov_tofu_green, cov_tofu_healthy, cov_organic_green, cov_organic_healthy (q65_1-7, 1-7 as
##above); cov_no_buy_reason (q152, asked of those who mostly opted out; text; free text dropped);
##cov_duration_sec (DURATION, whole survey, seconds).
##Dropped (PII FOUND in tofu_main_swe_covariates.xlsx): IP ("pseudo IP"), HTTP_URL (survey links
##with session tokens and the survey owner's account name), SESSION, EXTID (panel invitation id),
##browser user agent; also START timestamps, *_RAND option orders, respondent_state, SRC,
##datacon (consent), the forced-correct comprehension questions q115-q117, the unused duplicate
##questions q225/q228/costest2/q232 (empty for these respondents) and all free text.
##No survey weight. No repeated task.
suppressMessages({library(readxl); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_excel(file.path(raw, "tofu_main_swe_tofu.xlsx"), "data"))
cv <- as.data.table(read_excel(file.path(raw, "tofu_main_swe_covariates.xlsx"), "data", col_types = "text"))
stopifnot(uniqueN(x$RID) == 1574L, all(x$SEQ == x$SCENARIO), !anyDuplicated(x[, .(RID, SEQ)]),
          all(x$pref1 %in% c(1:3, NA)), all(x$DESIGN_ROW %in% 1:27))
x <- x[!is.na(pref1)]
place <- c("Sverige", "Annat land inom EU", "Land utanför EU")
cult <- c("Ekologiska metoder", "Icke-ekologiska konventionella metoder")
price <- paste(c(15, 20, 25, 30, 35, 40, 50, 60), "SEK")
lv <- function(v, l) { stopifnot(all(v %in% seq_along(l))); l[v] }
d <- rbindlist(lapply(1:2, function(p) {
  g <- function(k) x[[sprintf("a%d_x%d", p, k)]]
  x[, .(rid = RID, task = as.integer(SEQ), profile = p, choice = as.integer(pref1 == p),
        attr_production_country = lv(g(1), place), attr_soy_origin = lv(g(2), place),
        attr_cultivation = lv(g(3), cult), attr_price = lv(g(4), price))]
}))
# the two variants never share a level on any attribute
stopifnot(x[, all(a1_x1 != a2_x1 & a1_x2 != a2_x2 & a1_x3 != a2_x3 & a1_x4 != a2_x4)])
stopifnot(d[, sum(choice), .(rid, task)][, all(V1 <= 1)])
# covariates
cv <- cv[as.numeric(RID) %in% d$rid]
stopifnot(nrow(cv) == uniqueN(d$rid), !anyDuplicated(cv$RID))
num <- function(v) suppressWarnings(as.numeric(v))
code <- function(v, l, na = integer()) { v <- as.integer(v); stopifnot(all(v %in% c(seq_along(l), NA))); v[v %in% na] <- NA; l[v] }
agree <- function(v) { v <- as.integer(v); stopifnot(all(v %in% c(1:7, NA))); v }
age <- ifelse(cv$age == "2" & grepl("^[0-9]+$", cv$age_other), num(cv$age_other), NA)
age[!is.na(age) & (age < 18 | age > 110)] <- NA
price_guess <- ifelse(cv$costest == "2" & grepl("^[0-9]+([.,][0-9]+)?$", cv$costest_other),
                      num(sub(",", ".", cv$costest_other)), NA)
st <- c("7" = "Complete", "9" = "User initiated timeout", "10" = "System initiated timeout")
stopifnot(all(cv$STATUS %in% names(st)), all(cv$split %in% as.character(1:4)))
cov <- data.table(rid = as.numeric(cv$RID),
  trial_info_treatment = c("Environment", "Health", "Recipe", "Control")[as.integer(cv$split)],
  cov_status = unname(st[cv$STATUS]), cov_survey_version = as.integer(cv$VERSION),
  cov_gender = code(cv$gender, c("female", "male", "other", NA), na = 4L),
  cov_age = as.integer(age),
  cov_education = code(cv$q55, c("Lägre än grundskola.", "Grundskola, realskola, folkskola eller motsvarande.",
                                 "Gymnasium, folkhögskola eller motsvarande.", "Universitet, högskola eller motsvarande.", NA), na = 5L),
  cov_diet = code(cv$q56, c("Jag äter kött regelbundet.", "Jag äter kött ibland (flexitarian).", "Jag äter aldrig kött (vegetarian).",
                            "Jag äter aldrig djurprodukter (vegan).", NA, "Övrigt"), na = 5L),
  cov_shop_frequency = code(cv$shoptofu, c("Aldrig", "En gång i månaden eller mer sällan", "Två till tre gånger i månaden",
                                           "En gång i veckan eller oftare")),
  cov_device = code(cv$devicetype, c("Android phone", "iPhone", "other smartphone", "Android tablet", "iPad",
                                     "Windows tablet", "desktop device")),
  cov_store_type = code(cv$q83, c("Lågprisbutik (t.ex. Lidl).", "Välsorterad livsmedelsbutik (t.ex. ICA).",
                                  "Direktförsäljning (t.ex. gårdsbutik, marknad, REKO-ring).", NA, "Övrigt."), na = 4L),
  cov_tofu_price_guess = price_guess,
  cov_no_buy_reason = code(cv$q152, c("Produkterna var för dyra.", "Jag är inte intresserad av tofu.",
                                      "Produkterna och dess egenskaper var inte attraktiva.", "Jag förstod inte uppgiften.",
                                      "Jag brydde mig inte om uppgiften.", "Valalternativen var inte realistiska.", "Övrigt:")),
  cov_attention_pass = ifelse(is.na(cv$dce_followup_6), NA_integer_, as.integer(cv$dce_followup_6 == "7")),
  cov_duration_sec = num(cv$DURATION))
buys <- c("bread", "canned", "eggs_dairy", "dry_goods", "meat", "meat_alternatives")
for (k in 1:6) { v <- as.integer(cv[[paste0("eattofu_", k)]]); stopifnot(all(v %in% c(1:2, NA))); cov[, paste0("cov_buys_", buys[k]) := v - 1L] }
fu <- c("dce_random", "dce_sure", "dce_realistic", "dce_store_like", "dce_attributes_matter")
for (k in 1:5) cov[, paste0("cov_", fu[k]) := agree(cv[[paste0("dce_followup_", k)]])]
q65 <- c("knew_tofu", "knowledge_increased", "tofu_tastes_good", "tofu_green", "tofu_healthy", "organic_green", "organic_healthy")
for (k in 1:7) cov[, paste0("cov_", q65[k]) := agree(cv[[paste0("q65_", k)]])]
d <- merge(d, cov, by = "rid")
d[, id := as.integer(rid)][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "sagebiel_2026_tofu.csv"))
