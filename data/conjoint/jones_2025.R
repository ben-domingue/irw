##Authoritarian-reform vignette conjoints (US public) from
##Jones, C. W. (2025). Authoritarian reforms and external legitimacy. International Organization.
##https://doi.org/10.1017/S0020818325101197
##Replication data: Harvard Dataverse doi:10.7910/DVN/H3UOKG, CC0 1.0. Files read (Dataverse
##"original" CSV downloads): Study2_Data.tab, Study3_Data.tab. Read as text, not run: README.docx,
##Study1-3 and Study3KSA .do files. No questionnaire ships and the article was not read: the vignette
##template and the outcome wording are not deposited (outcomes PARAPHRASED from the do-file labels).
##Usage: Rscript jones_2025.R <dir holding Study2_Data.csv and Study3_Data.csv> <output dir>
##
##Single-profile text vignettes: each task describes an unnamed authoritarian country; respondents
##rated it on five 7-point items. Two experiments, two tables (different reform sets, samples and
##years; the author analyses them separately):
##  jones_2025_reform_legitimacy_s2: Study 2, Lucid US sample, Oct 2020, 1,891 respondents x 5 tasks.
##  jones_2025_reform_legitimacy_s3: Study 3, Lucid US sample, Jul 2023, 1,441 respondents x 4 tasks
##    (524 rows with no outcome omitted; 124 respondents drop out entirely: 1,317 kept).
##Study 1 (single manipulated factor, a survey experiment) is not a conjoint and is not built. Study
##3's fifth task, which named the country as Saudi Arabia (Study3KSA files; the author's Figure 10),
##is a different design (named country, separate outcome columns) and is left out.
##Attributes, stored as the text inserted into the vignette (the source holds the inserted fragments;
##the surrounding template sentence is not deposited):
##  attr_reform: the full reform sentence shown in that task (source reform<t>a / preform<t>a, e.g.
##    "However, the rulers recently announced plans to join global initiatives addressing carbon
##    emissions and climate change." or "The rulers have not pursued any reforms to date."); checked
##    against the author's key `reform`/`preform` (one key -> one sentence in S2; in S3 two keys have two
##    wordings each, both kept as shown).
##  attr_experts: "The reform efforts will be led by the government." / "The reform efforts will be
##    led by the ruler and an experienced team of experts." (source experts<t>a + experts<t>b; the
##    author's key: "the ruler" / "experts"); "(not shown)" in no-reform tasks (sentence absent).
##  attr_expert_nationality: American / Chinese / international / local, the word inserted for the
##    expert team (author's label "Expert nationality"); "(not shown)" when the experts sentence is
##    absent or names no experts (source blank exactly then; the exact insertion point is inferred).
##  attr_critics_response: "Critics are eager to watch how this country develops." / "Critics are
##    skeptical of any reform efforts because of the country's history and human rights record.";
##    "(not shown)" in no-reform tasks.
##  attr_culture ("very conservative" / "somewhat liberal"), attr_wealth ("very" / "not very"),
##  attr_resources ("oil and other fossil fuels" / "natural resources"), attr_government (3
##  fragments), attr_tourism (2), attr_us_relations (2), attr_democracy (2): fragments as stored.
##  S2 attr_resources is blank in every task-5 row (the author drops oil as duplicative of wealth);
##  coded "(not shown)" there (inferred from the pattern).
##  S3 also holds a region fragment (pregion<t>: "the Middle East" for 1,358 respondents, blank in all
##  tasks for 83): left OUT, because whether blank means not shown or not saved is undocumented and the
##  author does not analyse it.
##Outcomes, 1-7, "Very unfavorable" (1) .. "Very favorable" (7) (do-file favorableLabels; S2 stores
##the label text, mapped here to 1-7; S3 stores 1-7). Higher = more favourable to the item as worded:
##  rating (fav): favorability toward the country; rating_trade: trade with the country;
##  rating_cut: cutting off relations; rating_boycott: a boycott; rating_visit: visiting the country.
##  For cut/boycott a higher value is MORE hostile to the country. Wording paraphrased.
##Covariates: cov_age (Lucid_age, years, the panel's profile age), cov_race (S2: Q4 answer text) /
##cov_race_code (S3: Q4 stored as an unlabelled code), Lucid profile codes without a deposited
##codebook kept with _code suffix: cov_gender_code (Lucid_gender), cov_education_code
##(Lucid_eduation), cov_party_code (Lucid_political_party), cov_hhi_code (Lucid_hhi);
##cov_duration_sec (Durationinseconds, whole survey). All respondents passed the attention check.
##Dropped PII: IPAddress, LocationLatitude/Longitude, Lucid_zip, Lucid_rid, ResponseId (re-keyed).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- c("Very unfavorable", "Unfavorable", "Somewhat unfavorable", "Neutral", "Somewhat favorable", "Favorable", "Very favorable")
pick <- function(d, stem, suffix = "a") { v <- character(nrow(d)); for (t in unique(d$Task_No)) { i <- d$Task_No == t; v[i] <- d[[paste0(stem, t, suffix)]][i] }; trimws(v) }
ns <- function(x) fifelse(is.na(x) | x == "", "(not shown)", x)
build <- function(d, p, outcomes_text) {
  d <- d[!(fav %in% c(NA, "") & trade %in% c(NA, "") & cut %in% c(NA, "") & boycott %in% c(NA, "") & visit %in% c(NA, ""))]
  g <- function(v) d[[paste0(p, v)]]
  rt <- pick(d, paste0(p, "reform")); e1 <- pick(d, paste0(p, "experts")); e2 <- pick(d, paste0(p, "experts"), "b")
  rs <- pick(d, paste0(p, "response"))
  ctrl <- g("reform") == "control"
  stopifnot(all(rt != ""), all((e1 == "") == ctrl), all((rs == "") == ctrl),
            all((g("experts") == "experts") == grepl("team of$", e1)), all((g("response") == "skeptical response") == grepl("skeptical", rs)),
            all((g("nationality") != "") == (g("experts") == "experts")))
  ex <- fifelse(e1 == "", "", trimws(paste(e1, e2)))
  num <- function(x) if (outcomes_text) match(x, lab) else as.integer(x)
  o <- d[, .(id = as.integer(factor(ResponseId, levels = unique(ResponseId))), task = Task_No, profile = 1L,
             rating = num(fav), rating_trade = num(trade), rating_cut = num(cut), rating_boycott = num(boycott), rating_visit = num(visit))]
  o[, `:=`(attr_reform = rt, attr_experts = ns(ex), attr_expert_nationality = ns(g("nationality")), attr_critics_response = ns(rs),
           attr_culture = g("conservative"), attr_wealth = g("wealth"), attr_resources = ns(g("oil")), attr_government = g("govtype"),
           attr_tourism = g("tourism"), attr_us_relations = g("ally"), attr_democracy = g("critics"))]
  if (outcomes_text) o[, cov_race := fifelse(d$Q4 == "", NA_character_, d$Q4)] else o[, cov_race_code := d$Q4]
  o[, `:=`(cov_age = as.integer(d$Lucid_age), cov_gender_code = d$Lucid_gender,
           cov_education_code = d$Lucid_eduation, cov_party_code = d$Lucid_political_party, cov_hhi_code = d$Lucid_hhi,
           cov_duration_sec = as.integer(d$Durationinseconds))]
  for (v in grep("^attr_", names(o), value = TRUE)) stopifnot(!anyNA(o[[v]]), all(o[[v]] != ""))
  setorder(o, id, task, profile); o
}
s2 <- fread(file.path(raw, "Study2_Data.csv"), encoding = "UTF-8")
stopifnot(nrow(s2) == 9455, uniqueN(s2$ResponseId) == 1891, all(s2$attentionPass == "passed"), all(s2$fav %in% lab))
stopifnot(all(s2[Task_No == 5, oil] == ""), all(s2[Task_No < 5, oil] != ""))
o2 <- build(s2, "", TRUE)
cat("S2 rows", nrow(o2), "resp", uniqueN(o2$id), "\n")
print(round(coef(lm(rating ~ I(attr_reform == "The rulers have not pursued any reforms to date."), o2))[2], 3))
fwrite(o2, file.path(out, "jones_2025_reform_legitimacy_s2.csv"))
s3 <- fread(file.path(raw, "Study3_Data.csv"), encoding = "UTF-8")
stopifnot(nrow(s3) == 5764, uniqueN(s3$ResponseId) == 1441)
o3 <- build(s3, "p", FALSE)
cat("S3 rows", nrow(o3), "resp", uniqueN(o3$id), "\n")
fwrite(o3, file.path(out, "jones_2025_reform_legitimacy_s3.csv"))
