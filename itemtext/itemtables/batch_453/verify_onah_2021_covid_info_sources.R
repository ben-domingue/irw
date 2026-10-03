# verify_onah_2021_covid_info_sources.R -- batch_453
#
# Claim: item codes ARE the .sav column names (data/onah_2021_covid_literacy.py
# keeps them verbatim), so item_text<->item is tied at the source by the .sav's
# own variable labels. The inferred step is on the OTHER axis: the .sav stores
# 1='agree', 2='disagree' (value labels), the processing script recodes
# agree -> 1 and everything else -> 0, and the shipped option_text says
# resp 1 = "Agree", resp 0 = "Disagree". Route 9 (response-frequency matching):
# the per-item count of 'agree' in the deposit must equal the per-item count of
# resp==1 in the live table, and 'disagree' must equal resp==0, cell for cell.
# A flipped direction, or item_text attached to the wrong column, breaks it:
# the ten items' agree counts are all distinct (1259..5793).
#
# Counts hard-coded from SPSS-DATA-COVID-19.sav (Mendeley 10.17632/cf3s3v8wb3,
# v1), read with pyreadstat 2026-09-25; no missing values in any of the 10.
# What this does NOT establish: the wording itself (that rests on the deposit's
# questionnaire PDF and the .sav variable labels agreeing, checked by eye).

suppressMessages(library(irw))
TABLE <- "onah_2021_covid_info_sources"

SAV <- data.frame(
  item = c("WHO_website","NCDC_website","social_media","Television","Radio",
           "Newspapers","UNICEF_website","From_friends_and_family",
           "From_health_worker","From_church_or_mosque"),
  label = c("WHO website","NCDC website","Social media (facebook, twitter, etc)",
            "Television","Radio","Newspapers","UNICEF website",
            "From friends and family","From health worker","from church or mosque"),
  agree    = c(2544, 3758, 5765, 3779, 4025, 2615, 1259, 5793, 2184, 1353),
  disagree = c(5346, 4132, 2125, 4111, 3865, 5275, 6631, 2097, 5706, 6537),
  stringsAsFactors = FALSE)

# Shipped option_text -> resp, read back from the items CSV beside this script.
it <- read.csv("itemtables/batch_453/onah_2021_covid_info_sources__items.csv",
               stringsAsFactors = FALSE)
agree_resp    <- unique(it$resp[it$option_text == "Agree"])
disagree_resp <- unique(it$resp[it$option_text == "Disagree"])
cat(sprintf("shipped: Agree -> resp %s, Disagree -> resp %s\n",
            paste(agree_resp, collapse = ","), paste(disagree_resp, collapse = ",")))
stopifnot(length(agree_resp) == 1, length(disagree_resp) == 1)

d <- irw::irw_fetch(TABLE)
n_agree    <- tapply(d$resp == agree_resp,    d$item, sum)
n_disagree <- tapply(d$resp == disagree_resp, d$item, sum)

ok <- TRUE
cat(sprintf("\n%-24s %8s %8s   %8s %8s\n", "item", "sav_agr", "live", "sav_dis", "live"))
for (i in seq_len(nrow(SAV))) {
  a <- n_agree[SAV$item[i]]; b <- n_disagree[SAV$item[i]]
  hit <- isTRUE(a == SAV$agree[i]) && isTRUE(b == SAV$disagree[i])
  ok <- ok && hit
  cat(sprintf("%-24s %8d %8d   %8d %8d  %s\n", SAV$item[i], SAV$agree[i], a,
              SAV$disagree[i], b, if (hit) "ok" else "MISMATCH"))
}
# Each item's shipped item_text must match its own .sav variable label (modulo
# the questionnaire's added 'whatsapp' in the social-media example list).
norm <- function(x) gsub("[^a-z]", "", tolower(gsub("whatsapp|etc", "", x)))
txt <- unique(it[, c("item", "item_text")])
lab_ok <- norm(txt$item_text[match(SAV$item, txt$item)]) == norm(SAV$label)
cat(sprintf("\nitem_text agrees with its own .sav variable label: %d/%d\n",
            sum(lab_ok), nrow(SAV)))
ok <- ok && all(lab_ok)
cat("Not established here: literal wording beyond the label match.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
