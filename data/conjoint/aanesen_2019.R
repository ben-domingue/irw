##Coastal-zone regulation discrete choice experiment, WITHOUT-JOBS half (Arctic Norway), from
##Aanesen, M., & Armstrong, C. W. (2019). Trading off co-produced marine ecosystem services:
##Natural resource industries versus other use and non-use ecosystem service values.
##Frontiers in Marine Science, 6, 102. https://doi.org/10.3389/fmars.2019.00102
##Replication data: DataverseNO doi:10.18710/OP8NGC, CC0 1.0, no restricted files, no terms.
##Files read: Recreation_Values_Without_Job.csv (no header, ';'-separated, 71 columns),
##00_ReadMeFile.txt, Variable_Explanation_Recreational_Values (.tab), Questionnaire_Without_Jobs.pdf
##(Norwegian, pdftotext) for the displayed wording.
##Usage: Rscript aanesen_2019.R <raw dir> <output dir>
##
##SIBLING TABLE: the same electronic survey of residents of Nordland, Troms and Finnmark had a
##split sample (ReadMe): half saw five attributes including new jobs (deposited separately as
##doi:10.18710/OFG1XW = aanesen_2018_coastal_recreation), half the same four attributes without
##jobs. This deposit holds the without-jobs half, a different attribute set, hence its own table
##(aanesen_2019_marine_tradeoffs): 490 respondents (PartNo), 24 rows each.
##Each respondent saw the same 8 choice cards (CardNo 1-8; one fixed design in the data: 24
##card x alternative combinations, checked) with 3 scenarios: "Miljoreguleringer som i dag"
##(current regulation; AltNo 1, identical on every card: both facilities, 50% more waste, 5 kg
##less catch, no tax) and "Strengere miljoregulering A/B" (AltNo 2-3). The status quo shows
##attribute levels, so it is profile 1, not an opt-out. profile = AltNo, task = CardNo (card
##order as numbered; whether the order was randomized is not stated).
##Attributes: codes from the Variable Explanation, text = the questionnaire's Norwegian card
##wording (demonstration card; small variants between printed cards, e.g. "5 kg mindre per
##fiskedag fra bat", normalised to the demonstration card's text), as in aanesen_2018.R:
##  attr_landscape (view; the row also had a picture): 0 "Oppdretts- og fisketurismeanlegg endrer
##    kystlandskapet", 1 "Kun oppdrettsanlegg endrer kystlandskapet", 2 "Kun fisketurismeanlegg
##    endrer kystlandskapet";
##  attr_waste: "Ingen okning i soppel", "25%/50% okning i soppel";
##  attr_catch: "Ingen reduksjon i fangst per fiskedag fra bat", "2 kg/5 kg mindre fangst per
##    fiskedag fra bat";
##  attr_tax: "0" (as printed on cards 1-8; the demonstration card prints "Ingen okning"),
##    "500/1000/2000/3000 kroner mer pr husstand pr ar".
##CAVEAT (same as the with-jobs deposit): the alternatives printed on the questionnaire's cards
##1-8 do not match the data's cards (e.g. data card 1 A = both facilities, 25% more waste, 2 kg
##less, 3000 kr; questionnaire card 1 A = both, 25%, no reduction, 2000 kr), although the level
##sets agree. The questionnaire is probably another block/version; level meanings rest on the
##Variable Explanation codes; the column order (view, waste, harvest, cost) is confirmed by the
##status quo, which carries the stated levels on all 8 cards.
##Outcome: choice = Choice, "Hva foretrekker du?" (which do you prefer; respondents were told
##to tick the alternative they dislike least if they like none), one of three incl. status quo.
##Dropped: 75 tasks with no choice recorded; NoTot (survey-company respondent number),
##Kommunenr (municipality); cabin, recreation, perception, attendance and attitude blocks.
##Covariates (personal block = last 9 columns; Variable Explanation codes): cov_gender (1 man ->
##male, 2 woman -> female); cov_age_group ("18-30", "30-67", "67+" for codes 1-3, codebook bands
##"between 18-30", "between 30-67", "above 67"); cov_education (codebook text); cov_county
##(17 Nordland, 18 Troms, 19 Finnmark); cov_personal_income / cov_household_income keep codes
##(10 resp. 9 = do not want to answer -> NA); cov_member_recreation / cov_member_environment
##(1 yes, 2 no, 3 don't know). No survey weight deposited.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Recreation_Values_Without_Job.csv"), header = FALSE, sep = ";", quote = "", colClasses = "character")
x[, V1 := gsub('"', "", V1)][, V71 := gsub('"', "", V71)]
stopifnot(ncol(x) == 71)
num <- function(v) as.integer(x[[v]])
s <- data.table(part = num("V2"), card = num("V3"), alt = num("V5"), choice = num("V6"), view = num("V7"),
                waste = num("V8"), harvest = num("V9"), cost = num("V10"),
                mem_rec = num("V63"), mem_env = num("V64"), county = num("V65"), gender = num("V66"),
                pinc = num("V68"), educ = num("V69"), hinc = num("V70"), age = num("V71"))
stopifnot(s[, .N, part][, all(N == 24)], all(s$county %in% 17:19), all(s$gender %in% 1:2), all(s$age %in% 1:3))
stopifnot(s[alt == 1, all(view == 0 & waste == 50 & harvest == 5 & cost == 0)])
stopifnot(nrow(unique(s[, .(card, alt, view, waste, harvest, cost)])) == 24)
s[, nch := sum(choice), .(part, card)]
stopifnot(sum(s$nch == 0) / 3 == 75, all(s$nch %in% 0:1))
s <- s[nch == 1]
lk <- function(v, codes, txt) { stopifnot(all(v %in% codes)); txt[match(v, codes)] }
d <- s[, .(id = part, task = card, profile = alt, choice,
           attr_landscape = lk(view, 0:2, c("Oppdretts- og fisketurismeanlegg endrer kystlandskapet",
                                            "Kun oppdrettsanlegg endrer kystlandskapet", "Kun fisketurismeanlegg endrer kystlandskapet")),
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
fwrite(d, file.path(out, "aanesen_2019_marine_tradeoffs.csv"))
cat("rows", nrow(d), "resp", uniqueN(d$id), "\n")
print(d[profile > 1, .(share = mean(choice)), attr_tax][order(attr_tax)])
print(d[, .(share = mean(choice)), .(sq = profile == 1)])
