##Democracy-concept conjoint in six countries from
##Chu, J. A., Williamson, S., & Yeung, E. S. F. (2024). People consistently view elections and
##civil liberties as key components of democracy. Science, 386(6719), 291-296.
##https://doi.org/10.1126/science.adp1274
##Replication data: Harvard Dataverse doi:10.7910/DVN/WUJCBO, CC0 1.0, no restricted files.
##Files read: data_cleaning/raw_US.tab, raw_EG.tab, raw_IN.tab, raw_IT.tab, raw_JP.tab, raw_TH.tab
##(Qualtrics exports with the displayed conjoint text in F-<task>-<profile>-<position> columns).
##Read as text: README.txt, clean_raw_XX.R (authors' cleaning: attribute names -> concepts,
##gender recode), main_analysis.R (pooling, tie removal), labels_original_*.tab.
##Not used: df_XX.tab (the authors' reshaped files, same content plus English recodes).
##Usage: Rscript chu_2024.R <raw dir> <output dir>
##
##Respondents in the United States, Egypt, India, Italy, Japan and Thailand each compared 3 pairs
##of hypothetical countries (Country A / Country B) described by 9 three-level attributes about
##elections, civil liberties, executive constraints, populism, obedience, economic and gender
##equality, expert influence and direct democracy. SIX TABLES, one per country
##(chu_2024_democracy_us/_eg/_in/_it/_jp/_th): the authors pool the countries in their main
##analysis, but every sample saw the attribute text in its own language (English, Arabic, Hindi,
##Italian, Japanese, Thai) and the stored text is what was displayed, so it cannot be shared.
##Attribute columns use the authors' concept names (clean_raw_XX.R rename): attr_election,
##attr_civil, attr_leader, attr_populist, attr_obedient, attr_econ, attr_gender_equality
##(authors' "gender": equality of the rights of men and women, not a profile gender),
##attr_expert, attr_direct. Level text is the displayed text, trimmed of surrounding spaces.
##Attribute order: the position of each attribute is recorded in F-<task>-<position>; it is
##randomized per respondent and kept as attrpos_* (1 = top row).
##Outcomes (question text from the export's question-text header row, per country):
##  choice "Which of the two countries do you think is more democratic?" (US wording; Country A
##         / Country B, forced; exactly one chosen in every task)
##  rating "How democratic would you say is Country A/B?" 1 = Not at all Democratic ...
##         10 = Completely Democratic (US wording), stored as answered.
##No opt-out. The design restrictions are not documented in the deposit (restrictions unknown).
##Dropped: 1 Thai respondent whose conjoint attributes were not saved (all F- cells blank).
##Kept: the one Thai task with identical profiles (main_analysis.R drops it as a "complete tie").
##Covariates: cov_gender (female/male from the authors' recode in clean_raw_XX.R; non-binary /
##third gender and "not listed" -> other; prefer not to say -> NA), cov_age (typed number;
##values > 100 set to NA: one Indian respondent typed 110), cov_education (answer text),
##cov_party_id (pid_main: US "Republican/Democrat/Independent/Other"; elsewhere the party the
##respondent feels closest to, answer text), cov_ideology (political, answer text),
##cov_minority (answer text), cov_china_us (china_us1, answer text), cov_pol_interest
##(polinterest, answer text), cov_democracy_importance (democracy_impt_1, as recorded).
##Empty answers are NA. Dropped: Qualtrics ResponseId (re-keyed), all *_TEXT free-text fields,
##timers, the other attitude batteries. No survey weight in the deposit (the authors' weighting
##in main_analysis.R is a post-hoc minority-share reweighting computed in the analysis).
##Counts: US 1,024, Egypt 1,008, India 1,022, Italy 1,047, Japan 1,012, Thailand 1,036
##respondents (1,037 minus the unsaved one) = 6,149.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
concept <- list(
  US = c(econ = "The economic situations of the rich and the poor are", populist = "When making policies, politicians",
         direct = "The people vote directly on policy decisions", civil = "Citizens’ individual liberties",
         gender_equality = "The rights of men and women are", expert = "Independent, non-elected experts have",
         obedient = "When citizens dislike their government’s policies", election = "Elections for political leadership",
         leader = "When making decisions, the country’s leader"),
  EG = c(econ = "الأوضاع الاقتصادية للأغنياء والفقراء", populist = "عند وضع السياسات والسياسيين", direct = "الشعب يصوت مباشرة",
         civil = "الحريات الفردية للمواطنين", gender_equality = "حقوق الرجل والمرأة", expert = "الخبراء المستقلون",
         obedient = "عندما يكره المواطنون", election = "انتخابات القيادة السياسية", leader = "عند اتخاذ القرارات"),
  IN = c(econ = "अमीरों और गरीबों की आर्थिक स्थिति", populist = "नीतियाँ बनाते समय राजनीतिज्ञ", direct = "लोग नीतिगत फैसलों पर सीधे वोट",
         civil = "नागरिकों की व्यक्तिगत स्वतंत्रता", gender_equality = "पुरुषों और महिलाओं के अधिकार", expert = "स्वतंत्र, गैर-निर्वाचित विशेषज्ञों",
         obedient = "जब नागरिक अपनी सरकार", election = "इस देश में राजनीतिक नेतृत्व", leader = "निर्णय लेते समय, देश के लीडर"),
  IT = c(econ = "Le situazioni economiche", populist = "Nella definizione delle politiche", direct = "Il popolo vota direttamente",
         civil = "Le libertà individuali", gender_equality = "I diritti degli uomini e delle donne", expert = "Gli esperti indipendenti",
         obedient = "Quando i cittadini non sono d'accordo", election = "Le elezioni per la leadership", leader = "Nel prendere decisioni"),
  JP = c(econ = "裕福な人たちと貧乏な人たちの経済状況", populist = "政策策定時に、政治家", direct = "人々が政策決定に直接投票",
         civil = "言論・宗教・集会の自由", gender_equality = "男性と女性の権利", expert = "選挙で選出されていない独立した専門家",
         obedient = "市民が政府の政策を気に入らない", election = "この国の政治指導者の選挙", leader = "決定を下すとき"),
  TH = c(econ = "สถานการณ์ทางเศรษฐกิจระหว่างคนรวยกับคนจน", populist = "เมื่อต้องกำหนดนโยบาย นักการเมือง", direct = "ประชาชนลงคะแนนโดยตรง",
         civil = "เสรีภาพส่วนบุคคลของพลเมือง", gender_equality = "สิทธิของชายและหญิง", expert = "ผู้เชี่ยวชาญอิสระ",
         obedient = "เมื่อประชาชนไม่ชอบนโยบายของรัฐบาล", election = "การเลือกตั้งผู้นำทางการเมือง", leader = "เมื่อต้องตัดสินใจ ผู้นำประเทศ"))
# gender answers: female, male (authors' recode in clean_raw_XX.R), other, refused
gmap <- list(
  US = list(f = "Female", m = "Male", o = c("Non-binary/third gender", "Not listed (please specify)"), na = "Prefer not to say"),
  EG = list(f = "أنثى", m = "ذكر", o = c("جنس آخر/ثالث", "غير مدرج في القائمة (يرجى التحديد)"), na = "أفضل عدم الإفصاح"),
  IN = list(f = "महिला", m = "पुरुष", o = c("सूचीबद्ध नहीं (कृपया निर्दिष्ट करें)", "नॉन-बाइनरी/तीसरा लिंग"), na = "कुछ नहीं कहना चाहूँगा"),
  IT = list(f = "Femmina", m = "Maschio", o = c("Non binario/terzo genere", "Non elencato (per favore, specifica)"), na = "Preferisco non rispondere"),
  JP = list(f = "女性", m = "男性", o = c("ノンバイナリー／第三の性", "記載なし（具体的にご記入ください）"), na = "答えたくない"),
  TH = list(f = "หญิง", m = "ชาย", o = c("นอน-ไบนารี / เพศที่สาม", "อื่น ๆ (โปรดระบุ)"), na = "ไม่ประสงค์ที่จะระบุ"))
for (cc in names(concept)) {
  r <- fread(file.path(raw, paste0("raw_", cc, ".tab")), colClasses = "character", encoding = "UTF-8", na.strings = NULL)
  r <- r[-(1:2)]                       # question-text / import-id header rows
  r[, rid := .I]
  # respondents whose conjoint attributes were not saved
  fcols <- grep("^F-[1-3]-[12]-[1-9]$", names(r), value = TRUE)
  bad <- r[, rowSums(.SD == "") > 0, .SDcols = fcols]
  stopifnot(sum(bad) == (cc == "TH"), r[bad, all(rowSums(.SD == "") == length(fcols)), .SDcols = fcols])
  r <- r[!bad]
  stopifnot(uniqueN(r$ResponseId) == nrow(r))
  ch <- c("Q1.1", "Q1.5", "Q1.9"); ra <- list(c("Q1.2", "Q1.3"), c("Q1.6", "Q1.7"), c("Q1.10", "Q1.11"))
  opts <- sort(unique(c(r$Q1.1, r$Q1.5, r$Q1.9))); stopifnot(length(opts) == 2)
  # option A is the label whose text matches the rating question's A side; fixed per language:
  A <- c(US = "Country A", EG = "البلد أ", IN = "देश ए", IT = "Paese A", JP = "国A", TH = "ประเทศ ก")[[cc]]
  stopifnot(A %in% opts)
  rows <- list()
  for (t in 1:3) for (p in 1:2) {
    x <- data.table(rid = r$rid, task = t, profile = p,
                    choice = as.integer((r[[ch[t]]] == A) == (p == 1)),
                    rating = as.integer(r[[ra[[t]][p]]]))
    for (k in 1:9) {
      nm <- trimws(r[[sprintf("F-%d-%d", t, k)]])
      cpt <- vapply(nm, function(s) { h <- names(concept[[cc]])[startsWith(s, concept[[cc]])]; if (length(h) == 1) h else NA_character_ }, "")
      stopifnot(!anyNA(cpt))
      lv <- trimws(r[[sprintf("F-%d-%d-%d", t, p, k)]])
      x[, paste0("v_", k) := lv][, paste0("c_", k) := cpt]
    }
    rows[[length(rows) + 1]] <- x
  }
  x <- rbindlist(rows)
  long <- melt(x, id.vars = c("rid", "task", "profile"), measure.vars = patterns(lv = "^v_", cp = "^c_"), variable.name = "pos")
  stopifnot(long[, .N, .(rid, task, profile, cp)][, all(N == 1)])
  w <- dcast(long, rid + task + profile ~ cp, value.var = "lv")
  ps <- dcast(long, rid + task + profile ~ cp, value.var = "pos")
  setnames(w, names(concept[[cc]]), paste0("attr_", names(concept[[cc]])), skip_absent = FALSE)
  setnames(ps, names(concept[[cc]]), paste0("attrpos_", names(concept[[cc]])))
  for (v in grep("^attrpos_", names(ps), value = TRUE)) ps[, (v) := as.integer(get(v))]
  o <- x[, .(rid, task, profile, choice, rating)][w, on = .(rid, task, profile)][ps, on = .(rid, task, profile)]
  stopifnot(o[, sum(choice), .(rid, task)][, all(V1 == 1)], !anyNA(o$rating), all(o$rating %in% 1:10))
  stopifnot(!anyNA(o[, .SD, .SDcols = patterns("^attr_")]), o[, all(nchar(attr_election) > 0)])
  # covariates
  g <- gmap[[cc]]; stopifnot(all(r$gender %in% c(g$f, g$m, g$o, g$na)))
  cv <- r[, .(rid, cov_gender = fifelse(gender == g$f, "female", fifelse(gender == g$m, "male", fifelse(gender %in% g$o, "other", NA_character_))),
              cov_age = suppressWarnings(as.integer(age)), cov_education = edu, cov_party_id = pid_main, cov_ideology = political,
              cov_minority = minority, cov_china_us = china_us1, cov_pol_interest = polinterest,
              cov_democracy_importance = democracy_impt_1)]
  cv[!(cov_age %between% c(15, 100)), cov_age := NA]
  for (v in names(cv)[-1]) if (is.character(cv[[v]])) cv[get(v) == "", (v) := NA]
  o <- cv[o, on = "rid"]
  o[, id := match(rid, sort(unique(rid)))][, rid := NULL]
  setcolorder(o, c("id", "task", "profile", "choice", "rating"))
  setorder(o, id, task, profile)
  fwrite(o, file.path(out, paste0("chu_2024_democracy_", tolower(cc), ".csv")))
  cat(cc, "rows", nrow(o), "resp", uniqueN(o$id), "attr order varies within resp:",
      long[, .(k = paste(cp[order(pos)], collapse = "|")), .(rid, task, profile)][, uniqueN(k), rid][, mean(V1 > 1)], "\n")
}
