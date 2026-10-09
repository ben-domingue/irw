##Coastal-zone regulation discrete choice experiment (Arctic Norway) from
##Aanesen, M., Falk-Andersson, J., Vondolia, G. K., Borch, T., Navrud, S., & Tinch, D. (2018).
##Valuing coastal recreation and the visual intrusion from commercial activities in Arctic
##Norway. Ocean & Coastal Management, 153, 157-167. https://doi.org/10.1016/j.ocecoaman.2017.12.017
##Replication data: DataverseNO doi:10.18710/OFG1XW, CC0 1.0, no restricted files, no terms.
##Files read: Recreation_Values_With_Job.csv (no header, ';'-separated), 01_ReadMe
##_Recreation_Values_Data.txt, Variable_Explanation_Recreational_Values (xlsx original), and
##Questionnaire .pdf (Norwegian, pdftotext) for the displayed wording.
##Usage: Rscript aanesen_2018.R <raw dir> <output dir>
##
##Electronic survey of residents of Nordland, Troms and Finnmark. Split sample (ReadMe): half
##saw five attributes including new jobs, half the same without jobs. ONLY THE WITH-JOBS HALF
##IS DEPOSITED (the ReadMe describes a "without job data long" file that is not in the
##dataset), so this table is the jobs version: 518 respondents (PartNo; ReadMe "1 to 519").
##Each respondent saw the same 8 choice cards (CardNo 1-8; one fixed design in the data) with
##3 scenarios: "Miljoreguleringer som i dag" (current regulation; AltNo 1, identical on every
##card: both facilities, 500 jobs, 50% more waste, 5 kg less catch, no tax) and "Strengere
##miljoregulering A/B" (AltNo 2-3). The status quo shows attribute levels, so it is profile 1,
##not an opt-out. profile = AltNo, task = CardNo (card order as numbered; whether the order
##was randomized is not stated).
##Attributes: codes from the Variable Explanation, text = the questionnaire's Norwegian card
##wording (demonstration card and cards 1-8; small wording variants between cards, e.g.
##"5 kg mindre per fiskedag fra bat", are normalised to the demonstration card's text):
##  attr_landscape (view; the card row also had a picture): 0 "Oppdretts- og fisketurismeanlegg
##    endrer kystlandskapet" (both aquaculture and tourism facilities visible), 1 "Kun
##    oppdrettsanlegg endrer kystlandskapet" (only aquaculture), 2 "Kun fisketurismeanlegg endrer
##    kystlandskapet" (only tourism facilities);
##  attr_jobs (new jobs in Northern Norway): "100/250/350/500 nye jobber";
##  attr_waste (waste in drift-collecting coves): "Ingen okning i soppel", "25%/50% okning i soppel";
##  attr_catch (recreational boat catch): "Ingen reduksjon i fangst per fiskedag fra bat",
##    "2 kg/5 kg mindre fangst per fiskedag fra bat";
##  attr_tax (extra tax per household per year): "0" (as printed on the cards), "500/1000/2000/3000
##    kroner mer pr husstand pr ar".
##  (Norwegian letters are written in the data as in the questionnaire; ASCII here.)
##CAVEAT: none of the 16 non-status-quo alternatives printed on the questionnaire's cards 1-8
##matches an alternative of the data's cards 1-8 on all five attributes (e.g. data card 1 A =
##350 jobs, no waste increase, no catch reduction, 3000 kr; questionnaire card 1 A = 350 jobs, no
##waste increase, 5 kg less, 500 kr), although the level sets agree. The questionnaire is
##probably another version/block; level meanings rest on the Variable Explanation codes, and
##the column order of the CSV (view, jobs, waste, harvest, cost) is confirmed by the status quo,
##which carries the stated levels on all 8 cards.
##Outcome: choice = Choice, "Hva foretrekker du?" (which do you prefer; respondents told to tick
##the alternative they dislike least if they like none), one of three, status quo included.
##Dropped: 81 tasks with no choice recorded and 1 task with two choices (rows with no valid
##outcome); NoTot (survey-company respondent number); Kommunenr (municipality); the cabin,
##recreation, perception, attribute-attendance and attitude blocks (the ReadMe's follow-up
##block has 6 columns but the Variable Explanation lists 5, so those columns cannot be
##named reliably; the personal block, the last 9 columns, is unaffected).
##Covariates (Variable Explanation codes): cov_gender (gender 1 = man -> male, 2 = woman ->
##female); cov_age_group (age 1 = "18-30", 2 = "30-67", 3 = "67+"; the codebook's bands
##"between 18-30", "between 30-67", "above 67"); cov_education (codebook text: primary,
##secondary, Vocational, University - four years, university more than four years); cov_county
##(17 Nordland, 18 Troms, 19 Finnmark, as text); cov_personal_income and cov_household_income
##keep the codes (bands in NOK, see codebook; 10 resp. 9 = do not want to answer -> NA);
##cov_member_recreation / cov_member_environment 1 = yes, 2 = no, 3 = don't know.
##No survey weight is deposited. 517 respondents keep at least one valid task. N vs paper not
##checked (article full text not reachable). Spot check: choice shares fall with tax (500 kr 0.43
##.. 2000-3000 kr 0.24-0.32) and with waste (none 0.47, 50% 0.23), as the abstract describes.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Recreation_Values_With_Job.csv"), header = FALSE, sep = ";", quote = "", colClasses = "character")
x[, V1 := gsub('"', "", V1)][, V73 := gsub('"', "", V73)]
stopifnot(ncol(x) == 73)
num <- function(v) as.integer(x[[v]])
s <- data.table(part = num("V2"), card = num("V3"), alt = num("V5"), choice = num("V6"), view = num("V7"),
                jobs = num("V8"), waste = num("V9"), harvest = num("V10"), cost = num("V11"),
                mem_rec = num("V65"), mem_env = num("V66"), county = num("V67"), gender = num("V68"),
                pinc = num("V70"), educ = num("V71"), hinc = num("V72"), age = num("V73"))
stopifnot(s[, .N, part][, all(N == 24)], all(s$county %in% 17:19), all(s$gender %in% 1:2), all(s$age %in% 1:3))
# status quo identical on every card
stopifnot(s[alt == 1, all(view == 0 & waste == 50 & jobs == 500 & harvest == 5 & cost == 0)])
# one fixed design: each card x alternative has one level combination
stopifnot(nrow(unique(s[, .(card, alt, view, waste, jobs, harvest, cost)])) == 24)
s[, nch := sum(choice), .(part, card)]
stopifnot(sum(s$nch == 0) / 3 == 81, sum(s$nch == 2) / 3 == 1)
s <- s[nch == 1]
lk <- function(v, codes, txt) { stopifnot(all(v %in% codes)); txt[match(v, codes)] }
d <- s[, .(id = part, task = card, profile = alt, choice,
           attr_landscape = lk(view, 0:2, c("Oppdretts- og fisketurismeanlegg endrer kystlandskapet",
                                            "Kun oppdrettsanlegg endrer kystlandskapet", "Kun fisketurismeanlegg endrer kystlandskapet")),
           attr_jobs = lk(jobs, c(100L, 250L, 350L, 500L), paste(c(100, 250, 350, 500), "nye jobber")),
           attr_waste = lk(waste, c(0L, 25L, 50L), c("Ingen økning i søppel", "25% økning i søppel", "50% økning i søppel")),
           attr_catch = lk(harvest, c(0L, 2L, 5L), c("Ingen reduksjon i fangst per fiskedag fra båt",
                                                     "2 kg mindre fangst per fiskedag fra båt", "5 kg mindre fangst per fiskedag fra båt")),
           attr_tax = lk(cost, c(0L, 500L, 1000L, 2000L, 3000L), c("0", paste(c(500, 1000, 2000, 3000), "kroner mer pr husstand pr år"))),
           cov_gender = c("male", "female")[gender],
           cov_age_group = c("18-30", "30-67", "67+")[age],
           cov_education = lk(educ, 1:5, c("primary", "secondary", "Vocational", "University - four years", "university more than four years")),
           cov_county = c("Nordland", "Troms", "Finnmark")[county - 16L],
           cov_personal_income = fifelse(pinc == 10L, NA_integer_, pinc),
           cov_household_income = fifelse(hinc == 9L, NA_integer_, hinc),
           cov_member_recreation = mem_rec, cov_member_environment = mem_env)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "aanesen_2018_coastal_recreation.csv"))
