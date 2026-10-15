##Parents' vaccine choices in Shanghai: two discrete choice experiments (A: vaccine attributes, B: vaccine programme)
##Wagner, A. (2018). 2017 Shanghai Vaccine Hesitancy Scale [Data set]. figshare. (no journal article identified in
##the deposit; the authors' English attribute tables and questionnaire are in it).
##Data: figshare doi:10.6084/m9.figshare.6463304 (v1, 2018), CC BY 4.0 (figshare API). Files read from "figshare
##upload.zip": data.xlsx (long: clinic, id, set, alternative, alternativeno, choice) and, as text, data.sas (cross-check
##only), "attribute tables en.docx", "qaire pt 2 vacc hesitancy en.docx", and the printed Chinese choice cards A1-A4.pdf
##and B1-B4.pdf (text layer read with pdftotext). Usage: Rscript wagner_2018.R <dir holding data.xlsx> <output dir>
##(the card lookup below is embedded; the PDFs are not needed at run time).
##
##About 600 parents of children under 7 months interviewed at 40 Shanghai vaccination clinics in 2017 (the figshare
##title carries 2017; sample details are in the unseen paper). Each parent (key = clinic x id; 608 distinct) answered
##both experiments on paper: DCE A, 4 choice sets, "choose Choice A or Choice B" (the card header says to pick the vaccine
##you would prioritise); DCE B, 5 choice sets, "Which situation would you choose?" (both options give the same
##protection). Forced choice between two options on every card, no opt-out. Fixed blocked design: A cards are printed in 4
##questionnaire versions x 4 sets, B in 4 x 4 (+1 repeated or common set: each parent has 5 sets); the data give only the
##card ids ('alternativeno', printed on every card under 'official use'), so a parent's sets are not necessarily the
##printed ones of one version.
##LEVEL TEXT: decoded from the printed cards, not from the numeric design in data.sas. Every data row's alternativeno
##(e.g. ra111) is printed under the card it identifies, so cards -> English text is a direct lookup (embedded below,
##32 + 32 alternatives). The text is MY ENGLISH TRANSLATION of the Chinese card text, using the authors' English
##attribute table wording where it exists. Differences from the authors' attribute tables: the cards show only 2 of the 4
##severity levels, 2 prevalence levels (1%, 10%), cost levels 100/400/800/1200 RMB (table: 100/200/400/800) and waiting
##times 20/40/60/90 minutes (table: 5/10/20/40); disease communicability is in the table but not on the cards (not
##stored). Hybrid attributes (manufacturer, testing) are one card row, attr_vaccine_origin (3 levels). Location: the
##cards read 'community health service centre vaccination clinic' and 'special-needs clinic'; the authors' table calls
##them 'Government-run immunization clinic' and 'Private hospital' (used here).
##DISCREPANCIES to know: the data.sas design codes disagree with the printed cards for DCE A prevalence on 7 of 32
##alternatives (the cards are followed) and for DCE B visit schedule on 4 of 31 (rb411, rb412, rb421, rb422); the
##printed B4 cards may differ from the SAS design. N and clinic counts not compared with a paper (unidentified).
##Tables: wagner_2018_vaccine_attributes (DCE A), wagner_2018_vaccine_program (DCE B). id is one integer key shared by
##both tables (the same parent). trial_clinic = clinic number. No respondent covariates kept (demographic columns d*
##are recorded on single rows and disagree between the A and B forms for 422 parents).
##Cleaning: sets with no recorded choice are omitted (453 sets), plus 2 sets with both or neither alternative marked
##(26_1 DCE A set 4, 31_11 DCE B set 3); the 'r' prefix of alternativeno is missing for some clinics (e.g. 26) and is
##normalised; parents 15_16 (DCE B rows duplicated) and 20_1 (rows of
##both forms duplicated/inconsistent) dropped.
##Rows: choice = 1 on the chosen of the two alternatives; profile = alternative 1/2 (Choice A / Choice B).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lookA <- data.table(
  alt_id = c("ra111","ra112","ra121","ra122","ra131","ra132","ra141","ra142","ra211","ra212","ra221","ra222","ra231","ra232","ra241","ra242","ra311","ra312","ra321","ra322","ra331","ra332","ra341","ra342","ra411","ra412","ra421","ra422","ra431","ra432","ra441","ra442"),
  attr_severity = c("Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Does not require hospitalization, child will be home sick for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Requires hospitalization for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days","Does not require hospitalization, child will be home sick for two days","Requires hospitalization for two days","Does not require hospitalization, child will be home sick for two days"),
  attr_prevalence = c("1%","10%","1%","10%","10%","10%","1%","1%","1%","10%","1%","10%","10%","10%","1%","1%","10%","1%","1%","1%","1%","10%","1%","10%","1%","1%","1%","10%","10%","10%","10%","1%"),
  attr_cost = c("100 RMB","100 RMB","100 RMB","400 RMB","800 RMB","400 RMB","800 RMB","400 RMB","1200 RMB","1200 RMB","100 RMB","800 RMB","100 RMB","400 RMB","800 RMB","400 RMB","1200 RMB","1200 RMB","1200 RMB","400 RMB","800 RMB","100 RMB","100 RMB","800 RMB","800 RMB","1200 RMB","400 RMB","100 RMB","800 RMB","1200 RMB","400 RMB","1200 RMB"),
  attr_fever_risk = c("30%","10%","30%","30%","10%","30%","30%","10%","10%","30%","30%","10%","10%","30%","30%","10%","30%","10%","10%","10%","30%","10%","30%","10%","30%","10%","10%","10%","10%","30%","30%","30%"),
  attr_effectiveness = c("85%","95%","85%","85%","85%","85%","95%","95%","85%","95%","85%","85%","95%","85%","95%","95%","95%","85%","85%","95%","95%","95%","85%","85%","95%","85%","95%","95%","85%","95%","85%","95%"),
  attr_vaccine_origin = c("A foreign vaccine, tested in Chinese children","A Chinese vaccine","A Chinese vaccine","A foreign vaccine, tested in Chinese children","A Chinese vaccine","A foreign vaccine, not tested in Chinese children","A foreign vaccine, tested in Chinese children","A foreign vaccine, not tested in Chinese children","A Chinese vaccine","A foreign vaccine, tested in Chinese children","A Chinese vaccine","A foreign vaccine, not tested in Chinese children","A foreign vaccine, not tested in Chinese children","A foreign vaccine, tested in Chinese children","A foreign vaccine, not tested in Chinese children","A Chinese vaccine","A Chinese vaccine","A foreign vaccine, not tested in Chinese children","A foreign vaccine, not tested in Chinese children","A foreign vaccine, not tested in Chinese children","A foreign vaccine, tested in Chinese children","A Chinese vaccine","A foreign vaccine, tested in Chinese children","A Chinese vaccine","A Chinese vaccine","A Chinese vaccine","A Chinese vaccine","A foreign vaccine, not tested in Chinese children","A foreign vaccine, not tested in Chinese children","A foreign vaccine, tested in Chinese children","A foreign vaccine, tested in Chinese children","A foreign vaccine, tested in Chinese children")
)
lookB <- data.table(
  alt_id = c("rb321","rb322","rb141","rb142","rb121","rb122","rb111","rb112","rb431","rb432","rb331","rb332","rb341","rb342","rb241","rb242","rb131","rb132","rb231","rb232","rb421","rb422","rb311","rb312","rb221","rb222","rb411","rb412","rb441","rb442","rb211","rb212"),
  attr_wait = c("20 minutes","40 minutes","20 minutes","40 minutes","20 minutes","90 minutes","60 minutes","20 minutes","60 minutes","40 minutes","90 minutes","60 minutes","90 minutes","90 minutes","90 minutes","20 minutes","40 minutes","90 minutes","20 minutes","40 minutes","60 minutes","60 minutes","40 minutes","60 minutes","60 minutes","40 minutes","40 minutes","20 minutes","20 minutes","90 minutes","90 minutes","60 minutes"),
  attr_location = c("Government-run immunization clinic","Government-run immunization clinic","Government-run immunization clinic","Private hospital","Private hospital","Government-run immunization clinic","Private hospital","Private hospital","Government-run immunization clinic","Government-run immunization clinic","Private hospital","Private hospital","Government-run immunization clinic","Private hospital","Private hospital","Private hospital","Government-run immunization clinic","Private hospital","Government-run immunization clinic","Government-run immunization clinic","Private hospital","Government-run immunization clinic","Private hospital","Government-run immunization clinic","Private hospital","Private hospital","Private hospital","Private hospital","Government-run immunization clinic","Government-run immunization clinic","Government-run immunization clinic","Government-run immunization clinic"),
  attr_schedule = c("3 visits: months 2, 4, 6","5 visits: months 2, 3, 4, 5, 6","3 visits: months 2, 4, 6","3 visits: months 2, 4, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","5 visits: months 2, 3, 4, 5, 6","3 visits: months 2, 4, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","3 visits: months 2, 4, 6","5 visits: months 2, 3, 4, 5, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","3 visits: months 2, 4, 6","7 visits: months 2, 3, 3.5, 4, 4.5, 5, 6","5 visits: months 2, 3, 4, 5, 6","5 visits: months 2, 3, 4, 5, 6","7 visits: months 2, 3, 3.5, 4, 4.5, 5, 6","7 visits: months 2, 3, 3.5, 4, 4.5, 5, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","5 visits: months 2, 3, 4, 5, 6","7 visits: months 2, 3, 3.5, 4, 4.5, 5, 6","7 visits: months 2, 3, 3.5, 4, 4.5, 5, 6","8 visits: months 2, 3, 3.5, 4, 4.5, 5, 5.5, 6","3 visits: months 2, 4, 6","3 visits: months 2, 4, 6","5 visits: months 2, 3, 4, 5, 6","7 visits: months 2, 3, 3.5, 4, 4.5, 5, 6","5 visits: months 2, 3, 4, 5, 6","5 visits: months 2, 3, 4, 5, 6","3 visits: months 2, 4, 6"),
  attr_cost_per_visit = c("200 RMB per visit","100 RMB per visit","200 RMB per visit","400 RMB per visit","100 RMB per visit","400 RMB per visit","200 RMB per visit","800 RMB per visit","100 RMB per visit","800 RMB per visit","800 RMB per visit","400 RMB per visit","400 RMB per visit","800 RMB per visit","100 RMB per visit","800 RMB per visit","100 RMB per visit","100 RMB per visit","400 RMB per visit","800 RMB per visit","400 RMB per visit","800 RMB per visit","200 RMB per visit","800 RMB per visit","200 RMB per visit","400 RMB per visit","200 RMB per visit","100 RMB per visit","400 RMB per visit","200 RMB per visit","200 RMB per visit","100 RMB per visit"),
  attr_injections = c("4 injections per visit","3 injections per visit","4 injections per visit","2 injections per visit","2 injections per visit","1 injection per visit","3 injections per visit","1 injection per visit","1 injection per visit","4 injections per visit","3 injections per visit","4 injections per visit","1 injection per visit","3 injections per visit","4 injections per visit","1 injection per visit","3 injections per visit","4 injections per visit","3 injections per visit","4 injections per visit","4 injections per visit","2 injections per visit","1 injection per visit","2 injections per visit","3 injections per visit","2 injections per visit","1 injection per visit","2 injections per visit","3 injections per visit","2 injections per visit","2 injections per visit","1 injection per visit")
)
x <- as.data.table(read_excel(list.files(raw, pattern = "data[.]xlsx$", full.names = TRUE)[1], guess_max = 1e5, na = c(".", "")))
x <- x[, .(clinic, version, id, set, alternative, alternativeno, choice)]
stopifnot(nrow(x) == 10680)
x[, rid := paste(clinic, id, sep = "_")]
x <- x[!rid %in% c("15_16", "20_1")]
stopifnot(x[, .N, .(rid, version, set, alternative)][, all(N == 1)], x[, all(alternative %in% 1:2)])
x[, key := match(rid, sort(unique(rid)))]
s <- x[, .(nch = sum(choice, na.rm = TRUE), nna = sum(is.na(choice)), n = .N), .(key, version, set)]
stopifnot(s[, all(n == 2)])
cat("sets dropped: unanswered", s[nna == 2, .N], "; both or neither marked", s[nna == 0 & nch != 1, .N], "\n")
x <- merge(x, s[nna == 0 & nch == 1, .(key, version, set)], by = c("key", "version", "set"))
x[, alternativeno := sub("^r?", "r", alternativeno)]
build <- function(ver, look, tname, pre) {
  d <- merge(x[version == ver], look, by.x = "alternativeno", by.y = "alt_id")
  d[, `:=`(id = key, task = as.integer(set), profile = as.integer(alternative), choice = as.integer(choice), trial_clinic = as.integer(clinic))]
  keep <- c("id", "task", "profile", "choice", grep("^attr_", names(look), value = TRUE), "trial_clinic")
  d <- d[, ..keep]
  stopifnot(!anyNA(d), d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)])
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tname, ".csv")))
}
stopifnot(x[version == "a", all(grepl("^ra", alternativeno))], x[version == "b", all(grepl("^rb", alternativeno))])
build("a", lookA, "wagner_2018_vaccine_attributes")
build("b", lookB, "wagner_2018_vaccine_program")
