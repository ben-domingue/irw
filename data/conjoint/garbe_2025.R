##Digital ID policy conjoint (Kenya) from
##Garbe, L., McMurry, N., Scacco, A., & Zhang, K. W. (2025). Who wants to be legible? Digitalization
##and intergroup inequality in Kenya. Comparative Political Studies, 58(9), 1803-1853.
##https://doi.org/10.1177/00104140241276971 (online first 2024)
##Replication data: Harvard Dataverse doi:10.7910/DVN/EGVC5Q, CC0 1.0. File read: eID_data.tab (saved
##as data.tab; SurveyCTO wide export, only the columns below are read). Read as text only:
##eID_codebook.xlsx (SurveyCTO form: survey + choices sheets), eID_cjoint_clean.R, eID_paper_sup_material.R;
##article (EconStor OA copy) and the authors' 2023 WZB working paper (EconStor 10419/274672), whose
##questionnaire appendix prints the showcard text.
##Usage: Rscript garbe_2025.R <dir holding data.tab> <output dir>
##
##Face-to-face survey (tablets, SurveyCTO) of Kenyan citizens in Nairobi, Mt. Kenya, Nyanza and Garissa.
##Sample as in the authors' code: consent == 1 and Status == "Approved" (other rows are interviews the
##survey firm rejected: incomplete, too-short conjoint, not interviewed, ...), first row of the one
##duplicated instanceID: 2,072 respondents = article.
##3 rounds (tasks) x 2 digital-ID policies (Policy 1/2 = rd_rand_a/_b = profile 1/2), 5 binary
##attributes shown on showcards with pictures, read out by the enumerator. Level text = showcard
##wording (WP appendix "Conjoint Attributes"; the article's Figure 1 prints it as an image): code 1
##(image *_yes.jpg) = column A, code 0 = column B:
##  social_protection: "The digital ID would be used for social protection transfers, including pensions,
##    social protection, and other assistance for Kenyans. People eligible for government benefits would
##    apply online using their digital ID and receive payments directly." / "Digital IDs would NOT be
##    linked directly to social protection transfers from the government."
##  public_services, security, tax_registration, voting: see `lv` below.
##Levels were drawn independently with p = 1/2 (form: round(random())), and draws where the two
##policies were identical were discarded (form `concat_draws`; article "Only pairs with identical
##profiles were excluded"). Attribute order randomized once per respondent (form *_order, fixed across
##rounds): attrpos_* = position 1-5.
##Outcomes (form labels; DK -998 and refusal -999 set NA on the ratings):
##  choice: "Which of the following two policy proposals for a new Digital ID would you prefer?"
##    (enumerator: if neither, ask which one they least dislike). A refusal (-999) was followed by "Are you
##    sure? Even if you don't like either policy, we would like to know which policy you dislike the least";
##    the confirmed answer is used (authors' choice_final). 17 tasks still refused: choice NA on both
##    profiles (ratings kept). Forced choice otherwise.
##  rating_support: "Under this policy, how supportive would you be of the digital ID program?" 1 Not at all
##    supportive - 4 Very supportive.
##  rating_register: "Under this policy, how likely would you be to register for the digital ID program?"
##    1 Not at all likely - 4 Very likely.
##  Round 1 only (NA in rounds 2-3), 1 Strongly disagree - 4 Strongly agree: rating_easier_access ("Under
##    this policy, the program would make it easier for people like me to access government services"),
##    rating_privacy_protected ("... the privacy of my data would be adequately protected"),
##    rating_worry_punished ("If this policy were enacted, I would be worried about being punished for
##    expressing my political views"), rating_worry_vote_counted ("... worried about my vote being
##    counted"), rating_worry_police_info ("... worried about the police using my personal information").
##    For the three worry items higher = more worried.
##The two manipulation-check items (rounds 1-2) are dropped. 2 tasks with no outcome at all are dropped:
##12,428 rows (article: "12,300 profiles evaluated"; not reconciled).
##Covariates (form choices sheet / authors' recode code): cov_gender (selected_gender, 1 Male, 2 Female, 26 NA;
##eID_cjoint_clean.R L662-663), cov_age (selected_age, years), cov_county (county list), cov_education
##(edu_level list text; -999 refusal -> NA), cov_mother_tongue (mother_tongue list text; 97 "Other (please
##specify)"; -999 -> NA). No survey weight.
##PII: the export holds device IDs, SIM/subscriber IDs, device phone numbers, GPS coordinates, enumerator
##names/ids and free text; none of it is read. id = row order of the kept interviews.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c("social_prot", "public_service", "security", "tax_reg", "voting")
rr <- c("", "_2_1", "_3_1")
cols <- c("instanceID", "consent", "Status", "selected_gender", "selected_age", "county", "edu_level", "mother_tongue",
          paste0(attrs, "_order"),
          as.vector(outer(c("rd_rand_a_", "rd_rand_b_"), as.vector(outer(attrs, c("_1", "_2_1", "_3_1"), paste0)), paste0)),
          "rd_policy_choice_1", "rd_policy_choice_confirm_1", "rd_policy_choice_2_1", "rd_policy_choice_2_confirm_1",
          "rd_policy_choice_3_1", "rd_policy_choice_3_confirm_1",
          "digital_id_supportive", "likely_register_digital_id", "digital_id_supportive_1_2", "likely_register_digital_id_1_2",
          paste0(rep(c("digital_id_supportive_", "likely_register_digital_id_"), each = 4), c("2_1", "2_2", "3_1", "3_2")),
          "easy_access_govt_services", "adequate_data_privacy", "worry_punished_view", "worry_vote_counted", "worry_personal_info",
          paste0(c("easy_access_govt_services", "adequate_data_privacy", "worry_punished_view", "worry_vote_counted", "worry_personal_info"), "_1_2"))
s <- fread(file.path(raw, "data.tab"), select = cols, na.strings = c("", "NA"))
s <- s[consent == 1 & Status == "Approved"][!duplicated(instanceID)]
stopifnot(nrow(s) == 2072)
s[, id := .I]
lv <- list(
  social_prot = c("Digital IDs would NOT be linked directly to social protection transfers from the government.",
                  "The digital ID would be used for social protection transfers, including pensions, social protection, and other assistance for Kenyans. People eligible for government benefits would apply online using their digital ID and receive payments directly."),
  public_service = c("The government would NOT share data from digital IDs with ministries in order to improve the quality of services.",
                     "The government would share data from digital IDs with relevant ministries in order to help improve the quality of public services like schools and health clinics in your local community."),
  security = c("Government agencies, for example the police, would NOT have direct access to biometric photos of citizens from the digital ID. To gain access to this data they need consent from the individual concerned or a court. This would make video surveillance more difficult.",
               "Government agencies, for example the police, would have automatic access to biometric photos stored in a single database. This would make video surveillance easier, because information from this photo database can be linked to video footage from surveillance cameras."),
  tax_reg = c("Digital IDs would NOT automatically be linked to a tax identification number at birth. Instead, individuals separately apply for a tax number when a person turns 18.",
              "Digital IDs would be linked to tax identification numbers at birth. This tax identification would be automatically activated when a person turns 18."),
  voting = c("A digital ID card would not be required to register to vote. Alternative forms of identification would continue to be accepted.",
             "A digital ID card would be required if you want to register to vote. Alternative forms of ID would no longer be accepted."))
onm <- c(social_prot = "social_protection", public_service = "public_services", security = "security", tax_reg = "tax_registration", voting = "voting")
r4 <- function(x) { x <- as.integer(x); fifelse(x %in% 1:4, x, NA_integer_) }
sup <- list(c("digital_id_supportive", "digital_id_supportive_1_2"), c("digital_id_supportive_2_1", "digital_id_supportive_2_2"),
            c("digital_id_supportive_3_1", "digital_id_supportive_3_2"))
reg <- lapply(sup, sub, pattern = "digital_id_supportive", replacement = "likely_register_digital_id")
mech <- c(easier_access = "easy_access_govt_services", privacy_protected = "adequate_data_privacy", worry_punished = "worry_punished_view",
          worry_vote_counted = "worry_vote_counted", worry_police_info = "worry_personal_info")
L <- list()
for (t in 1:3) {
  sfx <- c("_1", "_2_1", "_3_1")[t]
  ch0 <- as.integer(s[[paste0("rd_policy_choice", c("_1", "_2_1", "_3_1")[t])]])
  cf <- as.integer(s[[c("rd_policy_choice_confirm_1", "rd_policy_choice_2_confirm_1", "rd_policy_choice_3_confirm_1")[t]]])
  chf <- fifelse(ch0 == -999L, cf, ch0)
  chf[!chf %in% 1:2] <- NA_integer_
  for (p in 1:2) {
    x <- s[, .(id, task = t, profile = p, choice = as.integer(chf == p),
               rating_support = r4(get(sup[[t]][p])), rating_register = r4(get(reg[[t]][p])))]
    for (m in names(mech)) x[, paste0("rating_", m) := if (t == 1) r4(s[[if (p == 1) mech[m] else paste0(mech[m], "_1_2")]]) else NA_integer_]
    for (at in attrs) {
      code <- as.integer(s[[paste0("rd_rand_", c("a", "b")[p], "_", at, sfx)]])
      x[, paste0("attr_", onm[at]) := lv[[at]][code + 1L]]
      x[, paste0("attrpos_", onm[at]) := as.integer(s[[paste0(at, "_order")]])]
    }
    L[[length(L) + 1]] <- x
  }
}
d <- rbindlist(L)
ac <- grep("^attr_", names(d), value = TRUE)
##tasks whose attribute draws were not saved cannot be kept
miss <- unique(d[!complete.cases(d[, ..ac]), .(id, task)])
d <- d[!miss, on = .(id, task)]
oc <- c("choice", grep("^rating_", names(d), value = TRUE))
d <- d[d[, rowSums(!is.na(.SD)) > 0, .SDcols = oc]]
d <- d[d[, .N, .(id, task)][N == 2], on = .(id, task)][, N := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(is.na(V1) | V1 == 1)], !anyNA(d[, ..ac]))
##identical policies within a pair never occur
stopifnot(d[, uniqueN(do.call(paste, .SD)), .(id, task), .SDcols = ac][, all(V1 == 2)])
cty <- c("Nairobi", "Kirinyaga", "Murang'a", "Nyandarua", "Nyeri", "Homa Bay", "Kisumu", "Migori", "Siaya", "Garissa")
edu <- c("No formal schooling", "Informal schooling only (including Koranic schooling)", "Some primary schooling",
         "Primary school completed", "Intermediate school or some secondary school / high school",
         "Secondary school / high school completed",
         "Post-secondary qualifications other than university, e.g. a diploma or degree from a polytechnic college",
         "Some university", "University completed", "Post-graduate")
mt <- c("English", "Luo", "Kalenjin", "Maasai/Samburu", "Somali", "Swahili", "Luhya", "Kisii", "Mijikenda", "Pokot", "Kikuyu",
        "Kamba", "Meru/Embu", "Taita", "Turkana", "Don't know")
stopifnot(all(s$selected_gender %in% c(1:2, NA)), all(s$county %in% 1:10), all(s$edu_level %in% c(1:10, -998, -999)),
          all(s$mother_tongue %in% c(1:16, 97, -999, NA)))
cv <- s[, .(id, cov_gender = c("male", "female")[selected_gender], cov_age = as.integer(selected_age), cov_county = cty[county],
            cov_education = fcase(edu_level %in% 1:10, edu[pmax(edu_level, 1L)], edu_level == -998, "Don’t know", default = NA_character_),
            cov_mother_tongue = fcase(mother_tongue %in% 1:16, mt[pmax(mother_tongue, 1L)], mother_tongue == 97, "Other (please specify)",
                                      default = NA_character_))]
d <- merge(d, cv, by = "id")
cat("respondents", uniqueN(d$id), "rows", nrow(d), "tasks dropped (attributes missing)", nrow(miss),
    "tasks with refused choice", d[is.na(choice), uniqueN(paste(id, task))], "\n")
setorder(d, id, task, profile)
fwrite(d, file.path(out, "garbe_2025_digital_id.csv"))
