##Paris Agreement naming-and-shaming survey experiments (US) from
##Tingley, D., & Tomz, M. (2021). The effects of naming and shaming on public support for compliance with
##international agreements: an experimental analysis of the Paris Agreement. International Organization,
##76(2), 445-468. https://doi.org/10.1017/S0020818321000394
##Replication data: Harvard Dataverse doi:10.7910/DVN/JVKQLC, CC0 1.0, no restricted files. Files read:
##raw_wave1and2.tab, raw_wave4.tab, raw_wave5.tab, raw_wave6.tab (displayed vignette text, q94, demographics)
##and prepped_wave*.tab (authors' attention-check flag attn_passed and pid7), joined on the panel's rid;
##prep_wave*.do and analysis.do read as text. Usage: Rscript tingley_2021.R <dir> <output dir>, where <dir> holds
##the eight files renamed raw12.tab raw4.tab raw5.tab raw6.tab and w12.tab w4.tab w5.tab w6.tab.
##
##Each respondent (US online panel, 2018-09 to 2021-01) read ONE short vignette about a US government that joined
##the Paris Agreement and pledged a 25% cut, then what it did, and rated it: one task, one profile; id = new
##integer (rid is a panel respondent id). Three experiments = three tables (different attribute sets):
##  tingley_2021_paris_shaming  waves 1, 2, 5 (n = 3,012 + 635): did the US pass laws (and with what emissions cut
##    and energy-price rise), and did many countries criticize it (text varies; "(not shown)" = no criticism).
##    Wave 5 always shows criticism and only the 25% cut; pooled as the authors' shaming experiment (trial_wave).
##  tingley_2021_paris_reply    wave 4 (n = 3,013): same action attributes, always criticized, and the US reply:
##    defiance ("no right to meddle") versus regret ("other countries were right. It apologized").
##  tingley_2021_paris_shamers  wave 6, 2021 (n = 3,525): the US always passed laws with a 5% cut; price rise 4%
##    or 10% and WHO criticized (none / many countries / allies / non-allies / both).
##Attributes: new_laws = passed new laws / did not pass any (the sentence respondents saw, HTML stripped); emissions_cut
##5%/25% and energy_price 4%/10% (ex-ante "Experts agreed that the new laws would increase U.S. energy prices by
##X% and reduce U.S. carbon emissions by Y%") exist only when laws passed: "(not shown)" otherwise (the vignette says
##it did not affect prices or emissions). Criticism text: "Many countries said the U.S. should be ashamed of itself.
##They criticized the U.S. for doing nothing / so little to reduce U.S. emissions[, and for violating the promises it
##made when it joined the Paris Agreement]" is stored in full; its wording follows the action in part (no laws ->
##"doing nothing"), so it is not independent of new_laws. Wave 4's criticism and reply are split at "The U.S.
##government responded".
##Outcome: rating = q94 "Taking into account all the decisions the U.S. government made in the passage you read,
##would you approve or disapprove of what U.S. government did overall?" 1 Approve strongly, 2 Approve somewhat,
##3 Neither, 4 Disapprove somewhat, 5 Disapprove strongly. HIGHER = LESS approval; stored raw (the authors' a_overall
##recodes 1..5 to 100..0; verified identical mapping).
##The authors analyse only attentive respondents (attn_passed = 1, >= 80% correct); all respondents are kept here
##with cov_attention_pass = the authors' flag. Party weights are computed in analysis.do (wt5, Pew targets): not kept.
##Covariates: cov_gender (malefemale per prep .do: 1 Male, 0 Female; wave 6 adds 2 Other), cov_age (age_sel + 17 as
##in prep .do), cov_education (educ, six option labels from prep .do comments), cov_party_id7 (authors' pid7 label),
##cov_attention_pass. Dropped: starttime, free text (pid_1_text, race_text, q90), state, race, attention items, hc2/ff2.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
strip <- function(x) trimws(gsub("<[^>]+>", "", x))
edu <- c("Did not graduate from high school", "High school graduate", "Some college, but no degree (yet)",
         "2-year college degree", "4-year college degree", "Postgraduate degree (MA, MBA, MD, JD, PhD, etc)")
p7 <- c("Str Dem", "Weak Dem", "Lean Dem", "Don't Lean", "Lean Rep", "Weak Rep", "Str Rep")
load1 <- function(w) {
  r <- fread(file.path(raw, paste0("raw", w, ".tab")), quote = "\"", fill = TRUE, colClasses = list(character = c("shame", "action")))
  p <- fread(file.path(raw, paste0("w", w, ".tab")))
  stopifnot(nrow(r) == nrow(p), !anyDuplicated(r$rid), all(r$rid %in% p$rid))
  r <- merge(r, p[, .(rid, attn_passed, pid7, a_overall)], by = "rid")
  stopifnot(all(r$a_overall == c(100, 75, 50, 25, 0)[r$q94]))
  laws <- grepl("passed new laws", r$action)
  r[, `:=`(attr_new_laws = fifelse(laws, "passed new laws to reduce carbon dioxide emissions",
                                   "did not pass any new laws to reduce carbon dioxide emissions"),
           attr_emissions_cut = fifelse(laws, paste0(emiss, "%"), "(not shown)"),
           attr_energy_price = fifelse(laws, paste0(energy, "%"), "(not shown)"),
           rating = as.integer(q94), cov_gender = c("female", "male", "other")[malefemale + 1L],
           cov_age = as.integer(age_sel) + 17L, cov_education = edu[educ], cov_party_id7 = p7[pid7],
           cov_attention_pass = as.integer(attn_passed), trial_wave = as.integer(wave))]
  r }
fin <- function(d, attrs, name) {
  d[, `:=`(task = 1L, profile = 1L)]
  d <- d[, c("rid", "task", "profile", "rating", attrs, "cov_gender", "cov_age", "cov_education", "cov_party_id7",
             "cov_attention_pass", "trial_wave"), with = FALSE]
  d[, id := .GRP, by = rid]; d[, rid := NULL]
  setcolorder(d, c("id", "task", "profile", "rating"))
  stopifnot(!anyNA(d[, attrs, with = FALSE]), d$rating %in% 1:5)
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv"))) }
# experiment 1: shaming (waves 1, 2, 5)
d <- rbindlist(list(load1("12"), load1("5")), fill = TRUE)
d[, attr_shaming := fifelse(shame == "", "(not shown)", strip(shame))]
fin(d, c("attr_new_laws", "attr_emissions_cut", "attr_energy_price", "attr_shaming"), "tingley_2021_paris_shaming")
# experiment 2: reply (wave 4)
d <- load1("4"); s <- strip(d$shame)
i <- regexpr("The U.S. government responded", s, fixed = TRUE); stopifnot(all(i > 0))
d[, attr_criticism := trimws(substr(s, 1, i - 1))][, attr_reply := trimws(substr(s, i, nchar(s)))]
fin(d, c("attr_new_laws", "attr_emissions_cut", "attr_energy_price", "attr_criticism", "attr_reply"), "tingley_2021_paris_reply")
# experiment 3: who shames (wave 6)
d <- load1("6")
stopifnot(all(d$attr_new_laws == "passed new laws to reduce carbon dioxide emissions"), all(d$attr_emissions_cut == "5%"))
d[, attr_shamers := fifelse(shame == "", "(not shown)", strip(shame))]
fin(d, c("attr_energy_price", "attr_shamers"), "tingley_2021_paris_shamers")
