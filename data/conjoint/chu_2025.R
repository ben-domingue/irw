##Democracy-tradeoff country conjoints (Egypt, India, Italy, Japan, Thailand, United States) from
##Chu, J. A., Williamson, S., & Yeung, E. S. F. (2025). Are people willing to trade away democracy
##for desirable outcomes? Experimental evidence from six countries. Comparative Political Studies.
##https://doi.org/10.1177/00104140251392539 (online 2025-11-11; design read from the OSF preprint
##v2, doi:10.31219/osf.io/w46uf_v2, "Research procedures" and Table 1).
##Replication data: Harvard Dataverse doi:10.7910/DVN/WUDAWV, CC0 1.0, no restricted files.
##Files read: raw_data_<CC>.csv (?format=original; Qualtrics exports with 2 extra header rows) for
##CC = EG, IN, IT, JP, TH, US. data_cleaning_<CC>.R, main_analysis.R and README.txt read as text.
##Usage: Rscript chu_2025.R <dir holding raw_data_*.csv> <output dir>
##
##Qualtrics panels with quotas on age, gender, education: US May 2023 (English), the others
##September 2023 in the national language (India: Hindi or English, UserLanguage HI/EN). N =
##1,008 (EG), 1,022 (IN), 1,047 (IT), 1,012 (JP), 1,037 (TH), 1,024 (US), as in the paper; all
##passed an attention check before the conjoint (attention_pass = 1 for every row).
##Each respondent chose between 3 pairs of hypothetical countries (Country A / Country B) described
##in a table by 10 attributes; levels drawn independently with equal probability (paper). The
##authors pool the six samples in main_analysis.R, but the attribute text was shown in six
##languages, so there is ONE TABLE PER COUNTRY (chu_2025_democracy_tradeoff_<cc>).
##Attribute text = the Conjoint SDT export columns F-<task>-<profile>-<k> (as displayed, in the
##survey language). India: the export holds the Hindi text for every respondent, including the
##622 who took the survey in English (UserLanguage EN), so for them the stored text may not be what
##was on screen; one respondent-wealth level ("अधिकतम से ज़्यादा", wealthier than most) occurs in two
##Unicode spellings (16 rows), kept as stored (data_cleaning_IN.R merges them). Japan: by an
##administrative error, profiles drawn as "somewhat dangerous" or "very dangerous" showed both
##descriptors (paper, Figure 1 note); the export stores that as one level "やや危険”, “非常に危険",
##kept as displayed, so Japanese public safety has 3 levels. Attribute k is fixed
##(the authors name k = 1..10 in data_cleaning_<CC>.R): 1 leader selection, 2 civil liberties,
##3 leader constraints, 4 corruption in politics, 5 national economy, 6 respondent wealth, 7 public
##safety, 8 health care, 9 minority treatment, 10 respondent identity. The table rows carried a
##stem before each level (paper Table 1, e.g. "Political leaders come to power through [free and
##fair elections]"); the level fragment is stored. The order of attributes was randomized per
##respondent (paper); the deposit records only where the democracy block was placed,
##democ_tradeoff_position = top / middle / bottom (trial_democracy_position), which also decides
##which of three question copies holds the answers (US <t>_trade_<top|mid|btm>_*; others
##<t>_DV_tradeoff / <t>_Q49 / <t>_Q53 for choice, _tradeoff_a / _Q50 / _Q54 for rating A,
##_tradeoff_b / _Q51 / _Q55 for rating B; checked: exactly the copy matching the position is
##filled). Exact row positions are not recorded: no attrpos_ columns.
##Outcomes (US wording from the export's question text; other languages are translations of it):
##  choice: "If you had to choose, which country would you prefer to be born and grow up in?"
##    Country A / Country B (forced, no opt-out); profile 1 = Country A.
##  rating: "Now just think about Country A [B]. How happy would you be to have been born and
##    grown up in this country?" 1 = Extremely unhappy .. 7 = Extremely happy (the leading digit of
##    the exported answer text, e.g. "1Extremely unhappy").
##Covariates (answer text as exported, trimmed): cov_age (years), cov_gender: female / male from the
##authors' recode (data_cleaning_<CC>.R), the other three options of the same five-option question
##(non-binary/third gender; not listed, please specify -> "other"; prefer not to say -> NA) mapped by
##their text, which follows the English instrument's options; cov_education (edu), cov_ideology
##(political, left-right self-placement), cov_party_id (pid_main: US party identification; elsewhere
##the party the respondent feels closest to, including "close to no party"), cov_minority
##(minority: belongs to a minority group, yes/no/not sure), cov_survey_language (UserLanguage),
##cov_duration_sec (Qualtrics "Duration (in seconds)", whole survey).
##Dropped: IPAddress, LocationLatitude/LocationLongitude, ResponseId, panel IDs (workerId, rid, uid,
##RISN, transaction_id, ...): PII / platform IDs; free-text fields; other survey items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs <- c("leader_selection", "civil_liberties", "leader_constraints", "corruption", "national_economy",
           "respondent_wealth", "public_safety", "health_care", "minority_treatment", "respondent_identity")
gmap <- list(
  US = c("Female" = "female", "Male" = "male", "Non-binary/third gender" = "other", "Not listed (please specify)" = "other", "Prefer not to say" = NA),
  EG = c("أنثى" = "female", "ذكر" = "male", "جنس آخر/ثالث" = "other", "غير مدرج في القائمة (يرجى التحديد)" = "other", "أفضل عدم الإفصاح" = NA),
  IN = c("महिला" = "female", "पुरुष" = "male", "नॉन-बाइनरी/तीसरा लिंग" = "other", "सूचीबद्ध नहीं (कृपया निर्दिष्ट करें)" = "other", "कुछ नहीं कहना चाहूँगा" = NA),
  IT = c("Femmina" = "female", "Maschio" = "male", "Non binario/terzo genere" = "other", "Non elencato (per favore, specifica)" = "other", "Preferisco non rispondere" = NA),
  JP = c("女性" = "female", "男性" = "male", "ノンバイナリー／第三の性" = "other", "記載なし（具体的にご記入ください）" = "other", "答えたくない" = NA),
  TH = c("หญิง" = "female", "ชาย" = "male", "นอน-ไบนารี / เพศที่สาม" = "other", "อื่น ๆ (โปรดระบุ)" = "other", "ไม่ประสงค์ที่จะระบุ" = NA))
nresp <- c(EG = 1008, IN = 1022, IT = 1047, JP = 1012, TH = 1037, US = 1024)
tx <- function(v) { v <- trimws(v, whitespace = "[\\h\\v]"); fifelse(v == "", NA_character_, v) }
for (cc in names(nresp)) {
  x <- fread(file.path(raw, sprintf("raw_data_%s.csv", cc)), encoding = "UTF-8", colClasses = "character")[-(1:2)]
  stopifnot(nrow(x) == nresp[[cc]], !anyDuplicated(x$ResponseId), all(x$attention_pass == "1"),
            all(x$democ_tradeoff_position %in% c("top", "middle", "bottom")), all(x$gender %in% names(gmap[[cc]])))
  x[, id := .I]
  pos <- match(x$democ_tradeoff_position, c("top", "middle", "bottom"))
  cols <- if (cc == "US") lapply(c(force = "force", a = "a", b = "b"), function(s) paste0("_trade_", c("top", "mid", "btm"), "_", s)) else
    list(force = c("_DV_tradeoff", "_Q49", "_Q53"), a = c("_tradeoff_a", "_Q50", "_Q54"), b = c("_tradeoff_b", "_Q51", "_Q55"))
  get <- function(t, s) { m <- sapply(paste0(t, cols[[s]]), function(cn) x[[cn]]); m[cbind(seq_len(nrow(x)), pos)] }
  for (t in 1:3) for (s in names(cols)) { m <- sapply(paste0(t, cols[[s]]), function(cn) x[[cn]] != ""); stopifnot(all(m[cbind(seq_len(nrow(x)), pos)]), all(rowSums(m) == 1)) }
  rows <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
    fc <- get(t, "force"); stopifnot(uniqueN(fc) == 2)
    r <- get(t, c("a", "b")[p])
    d <- data.table(id = x$id, task = t, profile = p, fc = fc, rating = as.integer(substr(r, 1, 1)))
    for (k in 1:10) set(d, j = paste0("attr_", attrs[k]), value = tx(x[[sprintf("F-%d-%d-%d", t, p, k)]]))
    d
  }))))
  ## the "Country A" option label in each language (IN: the authors' recode "देश ए" -> "Country A")
  labA <- c(US = "Country A", EG = "البلد أ", IN = "देश ए", IT = "Paese A", JP = "国A", TH = "ประเทศ ก")[[cc]]
  stopifnot(uniqueN(rows$fc) == 2, labA %in% rows$fc)
  rows[, choice := as.integer(xor(profile == 2, fc == labA))][, fc := NULL]
  stopifnot(rows[, sum(choice), .(id, task)][, all(V1 == 1)], all(rows$rating %in% 1:7))
  ac <- grep("^attr_", names(rows), value = TRUE); stopifnot(!anyNA(rows[, ..ac]))
  cv <- x[, .(id, trial_democracy_position = democ_tradeoff_position, cov_age = as.integer(age),
              cov_gender = unname(gmap[[cc]][gender]), cov_education = tx(edu), cov_ideology = tx(political),
              cov_party_id = tx(pid_main), cov_minority = tx(minority), cov_survey_language = UserLanguage,
              cov_duration_sec = as.numeric(`Duration (in seconds)`))]
  d <- merge(rows, cv, by = "id")
  setcolorder(d, c("id", "task", "profile", "choice", "rating", ac)); setorder(d, id, task, profile)
  fwrite(d, file.path(out, sprintf("chu_2025_democracy_tradeoff_%s.csv", tolower(cc))))
}
