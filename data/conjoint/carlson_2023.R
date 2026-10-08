##Political-conversation (opinion expression) rating conjoint from
##Carlson, T. N., & Settle, J. E. (2023). Freedom of expression in interpersonal interactions.
##PS: Political Science & Politics, 56(2), 245-249. https://doi.org/10.1017/S1049096522001342
##Replication data: Harvard Dataverse doi:10.7910/DVN/FNHEVD, CC0 1.0, no restricted files.
##Files read: free_expression_data.tab (as the original free_expression_data.csv) and
##free_expression_data_mm.tab (as free_expression_data_mm.csv; only its author labels, used to
##confirm the code -> level mapping). Level text, outcome wording and design facts are from the
##article's supplementary material (S1049096522001342sup001.pdf, the pre-registration: Table 1
##"Conjoint Design", Table 2 coding, Table 3 covariates). The authors' .R file was read as text.
##Usage: Rscript carlson_2023.R <raw dir> <output dir>
##
##2,802 US adults (Ipsos KnowledgePanel, summer 2021, module on a Knight Foundation survey).
##Each saw 5 discussion scenarios (task = convoNum 1-5, recorded), ONE profile per task (profile
##= 1 always: a single-profile rating conjoint), 8 attributes describing the conversation
##partner and setting. Outcome:
##  rating: "Imagine that you were having a conversation about politics in the scenario
##    described above. How likely would you be to express your true opinions in that
##    conversation?" Very unlikely / Unlikely / Neither unlikely nor likely / Likely / Very
##    likely, stored 1-5 (5 = very likely) from the answer text. The source stores it rescaled
##    0-1 (Q69E: 0, .25, .5, .75, 1, which agree 1:1 with the answer text). 207 tasks with no
##    answer ("-1") are omitted (13,803 rows remain). No choice question.
##Attributes (source code -> text in pre-registration Table 1; the mm file's author labels agree
##1:1 with each code): relationship HidAttribute1; context HidAttribute2; party HidAttribute3
##(text); knowledge HidAttribute4; news HidAttribute5; engagement HidAttribute6; race
##HidAttribute7 (text); gender HidAttribute8 (text).
##Randomization RESTRICTED (pre-registration): all attributes uniform, except that the
##"mainstream partisan" news level names Fox News when the partner is (Strong) Republican, MSNBC
##when (Strong) Democrat, and either one at random when Independent. The data record only
##"mainstream partisan" (code 1), so for Independent partners the outlet shown is unknown: the
##stored text there is "...mainstream partisan sources, such as Fox News or MSNBC (outlet not
##recorded)". News levels are NOT uniform in the data (partisan about 66%, mainstream and fringe
##about 17% each), although the pre-registration says "fully randomized" over the three. Race "Latino/a" was shown as "Latino" for
##male and "Latina" for female partners (pre-registration Table 1), rebuilt here from gender.
##The pre-registration's example screen reads "heavily engaged"; its level table reads "highly
##engaged" (used). Attribute order fixed (as in the example screen); not recorded.
##Covariates: cov_age (years), cov_gender, cov_race_ethnicity (Ipsos text), cov_party (QPID100
##text; "-1" set missing), cov_political_participation (Q33, 0-4 count of acts), cov_social_media_
##news (Q34, 0-3 mean of two items), cov_trust_media (Q45, 0 = not at all .. 3 = great deal; half
##the sample got "the news media", half "...to report the news even-handedly"), cov_local_
##conversation (Q46_6, 0 = never .. 4 = daily). Dropped: ppeduc5 (Ipsos codes, labels not in the
##deposit) and the authors' derived variables (co_pid, close_relationship, co_ethnicity2/3,
##express_dum, att_* dummies etc.). No survey weight is deposited.
##N: the source has 2,802 respondents; 25 answered no task, so the table has 2,777. The article
##is paywalled and its N was not checked. Spot check: the
##authors' baseline lm (rating rescaled 0-1, their dummies) gives copartisan 0.0721, as the
##authors' code comment says (.072094).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "free_expression_data.csv"))
m <- fread(file.path(raw, "free_expression_data_mm.csv"))
stopifnot(s[, .N, ID][, all(N == 5)], s[, uniqueN(convoNum) == 5, ID][, all(V1)])
x <- merge(s, m[, .(ID, convoNum, relationship, context, knowledge, mediapref, engage)], by = c("ID", "convoNum"))
stopifnot(nrow(x) == nrow(s),
          x[, all((HidAttribute1 == 1) == (relationship == "Close Relationship") & (HidAttribute2 == 1) == (context == "Face-to-Face") &
                  (HidAttribute4 == 1) == (knowledge == "More Knowledgeable Discussant") & (HidAttribute6 == 1) == (engage == "Highly Engaged Discussant") &
                  (HidAttribute5 == 0) == (mediapref == "Mainstream") & (HidAttribute5 == 1) == (mediapref == "Partisan") &
                  (HidAttribute5 == 2) == (mediapref == "Fringe"))])
ans <- c(Veryunlikely = 1L, Unlikely = 2L, Neitherunlikelynorlikely = 3L, Likely = 4L, Verylikely = 5L)
x[, rating := ans[trimws(Q69E_nospace)]]
stopifnot(x[!is.na(rating), all(abs((rating - 1) / 4 - Q69E) < 1e-9)], x[is.na(rating), all(trimws(Q69E_nospace) == "-1")])
x <- x[!is.na(rating)]
news <- function(code, party) {
  partisan <- fifelse(party %like% "Republican", "This person typically gets their news from mainstream partisan sources, such as Fox News",
              fifelse(party %like% "Democrat", "This person typically gets their news from mainstream partisan sources, such as MSNBC",
                      "This person typically gets their news from mainstream partisan sources, such as Fox News or MSNBC (outlet not recorded)"))
  fifelse(code == 0, "This person typically gets their news from mainstream sources, such as USA Today",
  fifelse(code == 2, "This person typically gets their news from fringe news sources that are often discredited by fact-checking organizations", partisan))
}
d <- x[, .(id = as.integer(ID), task = as.integer(convoNum), profile = 1L, rating,
           attr_relationship = fifelse(HidAttribute1 == 1, "You have a close relationship with the person",
                                       "You have met the person before, but don't consider them to be close"),
           attr_context = fifelse(HidAttribute2 == 1, "The conversation occurs face-to-face", "The conversation occurs on social media"),
           attr_party = HidAttribute3,
           attr_knowledge = fifelse(HidAttribute4 == 1, "This person knows a lot more about politics than you",
                                    "This person knows a lot less about politics than you"),
           attr_news = news(HidAttribute5, HidAttribute3),
           attr_engagement = fifelse(HidAttribute6 == 1, "This person is highly engaged in politics", "This person is not engaged in politics at all"),
           attr_race = fifelse(HidAttribute7 == "Latino/a", fifelse(HidAttribute8 == "Female", "Latina", "Latino"), HidAttribute7),
           attr_gender = HidAttribute8,
           cov_age = as.integer(ppage), cov_gender = ppgender, cov_race_ethnicity = ppethm,
           cov_party = fifelse(QPID100 == "-1", NA_character_, QPID100),
           cov_political_participation = Q33, cov_social_media_news = Q34, cov_trust_media = Q45, cov_local_conversation = as.integer(Q46_6))]
stopifnot(d[, uniqueN(attr_party)] == 5, d[, uniqueN(attr_race)] == 5, d[, uniqueN(attr_gender)] == 2, d[, uniqueN(attr_news)] == 5)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "carlson_2023_free_expression.csv"))
