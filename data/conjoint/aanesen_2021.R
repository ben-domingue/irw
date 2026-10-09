##Cold-water coral protection DCE (Ireland, deliberative workshops) from
##Aanesen, M., Armstrong, C., & van Rensburg, T. M. (2021). Do we choose differently after a
##discussion? Results from a deliberative valuation study in Ireland. Land Economics, 97(1),
##207-223. https://doi.org/10.3368/wple.97.1.100719-0144R
##Replication data: DataverseNO doi:10.18710/XG6CYW, CC0 1.0, no restricted files, no terms.
##Files read: Irish_Pooled_Data.tab (original-format download; semicolon-separated text),
##01_ReadMe_Irish_CWC_survey.txt (codebook), 02_Questionnaire_Irish_CWC_survey.pdf (pdftotext;
##attribute and level wording, the 12 printed choice cards).
##Usage: Rscript aanesen_2021.R <raw dir> <output dir>
##
##139 participants in 7 valuation workshops in 7 Irish municipalities, autumn 2014. Each filled
##in 12 choice cards individually before a group discussion and the same 12 cards again after it
##(ReadMe: 2 x 12 = 24 choices). task = Card for the first round and 12 + Card for the second;
##trial_round = "before discussion" / "after discussion" (Seq); trial_repeat_of = Card on the
##second-round tasks (same cards, same alternative order). The order the cards were shown in is
##taken to be the card number.
##Each card: Alternative 1, Alternative 2, Alternative 3 "(same as today)", all with displayed
##levels, so all three are profiles (profile = alternative). "I prefer" one of the three; no
##other opt-out (the status quo is profile 3). Attributes, as printed on the cards:
##  attr_size      Size of the protected area: 5.000 km2 / 10.000 km2; status quo 2.500 km2
##                 (codebook size 5 / 10; the data's status-quo code 2.445 is not the printed text)
##  attr_business  Attractiveness to business activity, from the codebook's two dummies oil.k and
##                 fish.k (1 = protected area important for the oil sector / for fisheries):
##                 oil 1 fish 1 "Attractive to oil/gas and fisheries"; oil 0 fish 1 "Attractive to
##                 fisheries"; oil 1 fish 0 "Attractive to oil/gas"; 0/0 "No, not attractive to
##                 any business activity"; status quo "Some attractiveness to both oil/gas and
##                 fisheries" (data 0/0, card text used)
##  attr_habitat   Importance as habitat and refuge for fish: Important / Not important; status
##                 quo "Some importance"
##  attr_cost      Costs per household per year: 7 / 15 / 35 / 75 EUR/year; status quo "0"
##(Questionnaire capitalization "Not Important" / "oil/ gas" variants normalized to one spelling.)
##TWO CARD VERSIONS: 99 participants (municipalities 3-7) saw the cards printed in the
##questionnaire (checked: all 12 match); 40 (municipalities 1-2) saw another set of 12 cards,
##whose level text is built from the codes with the same wording. In that set, card 2
##alternative 2 has cost 15 in the first round and cost "2" (not a design level) in the second;
##those 40 second-round tasks are dropped. Also dropped: 12 tasks with no choice and 4 with two
##choices (Choice.1-3). trial_card_version = "A" (municipalities 1-2) / "B" (questionnaire).
##  choice = Choice.k, "Please ... select your preferred alternative (where it says 'I prefer')".
##Covariates (ReadMe codes): cov_gender (sex 1 man, 2 woman), cov_age (years), cov_education
##(edu: primary school / high school / lower university level / higher university level / other,
##ReadMe text), cov_municipality (muni 1-7, workshop), cov_engo (ENGO member 0/1), cov_work and
##cov_occupation (codes, ReadMe), cov_adults / cov_children (household members >= 18 / < 18),
##cov_income_personal / cov_income_household (codes 1-9, ReadMe euro bands), cov_quiz_score
##(1-8), trial_score_feedback (Treat: told the quiz score, 1 = yes), cov_certainty_before /
##cov_certainty_after (CertB / Cert, 1 very uncertain - 10 very certain, about the round's
##choices; Cert is taken from the second-round rows). Background answers are constant within a
##participant except: participant 5's first-round rows and participant 67's second-round rows
##differ in one or two answers, and participant 91's two card-1 rows carry participant 90's
##background values; each covariate is the participant's most frequent value over the 24 rows.
##Dropped: NoTot (row-group index), high (derived from Score), Choice (summary).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
z <- fread(file.path(raw, "Irish_Pooled_Data.tab"))
stopifnot(z[, .N, Indi][, all(N == 24)], all(z$Seq %in% 0:1), all(z$Card %in% 1:12))
z[, task := Card + 12L * Seq]
z[, ver := fifelse(muni %in% 1:2, "A", "B")]
nch <- z$Choice.1 + z$Choice.2 + z$Choice.3
bad2 <- z$cost.2 == 2 | z$cost.1 == 2
cat("dropped: no choice", sum(nch == 0), "two choices", sum(nch == 2), "cost '2'", sum(bad2), "\n")
z <- z[nch == 1 & !bad2]
bus <- function(o, f) fcase(o == 1 & f == 1, "Attractive to oil/gas and fisheries", o == 0 & f == 1, "Attractive to fisheries",
                            o == 1 & f == 0, "Attractive to oil/gas", o == 0 & f == 0, "No, not attractive to any business activity")
rows <- list()
for (p in 1:2) {
  g <- function(v) z[[paste0(v, ".", p)]]
  stopifnot(all(g("size") %in% c(5, 10)), all(g("cost") %in% c(7, 15, 35, 75)), all(g("hab") %in% 0:1))
  rows[[p]] <- data.table(Indi = z$Indi, task = z$task, profile = p, choice = g("Choice"),
    attr_size = c("5.000 km2", "10.000 km2")[match(g("size"), c(5, 10))],
    attr_business = bus(g("oil"), g("fish")), attr_habitat = c("Not important", "Important")[g("hab") + 1L],
    attr_cost = paste(g("cost"), "EUR/year"))
}
stopifnot(all(z$size.3 == 2.445), all(z$cost.3 == 0))
rows[[3]] <- data.table(Indi = z$Indi, task = z$task, profile = 3L, choice = z$Choice.3, attr_size = "2.500 km2",
  attr_business = "Some attractiveness to both oil/gas and fisheries", attr_habitat = "Some importance", attr_cost = "0")
d <- rbindlist(rows)
d[, attr_size := trimws(attr_size)]
# version B must match the questionnaire's printed card 1 (alt 1: 5.000 km2, oil/gas and fisheries, Not important, 15)
stopifnot(nrow(d[Indi %in% z[ver == "B", Indi] & task == 1 & profile == 1 &
  !(attr_size == "5.000 km2" & attr_business == "Attractive to oil/gas and fisheries" & attr_habitat == "Not important" & attr_cost == "15 EUR/year")]) == 0)
z0 <- fread(file.path(raw, "Irish_Pooled_Data.tab"))   # all rows, for respondent-level answers
md <- function(x) { u <- unique(x); u[which.max(tabulate(match(x, u)))] }
r <- z0[, lapply(.SD, md), by = Indi, .SDcols = c("Treat", "Score", "CertB", "sex", "age", "muni", "ENGO", "edu", "work", "occ", "old", "young", "incP", "incH")]
r <- z0[Seq == 1, .(Cert = md(Cert)), by = Indi][r, on = "Indi"]
r[, ver := fifelse(muni %in% 1:2, "A", "B")]
stopifnot(!anyDuplicated(r$Indi), all(r$sex %in% 1:2), all(r$edu %in% 1:5))
d <- r[d, on = "Indi"]
d[, `:=`(id = Indi, trial_round = fifelse(task > 12, "after discussion", "before discussion"),
         trial_repeat_of = fifelse(task > 12, task - 12L, NA_integer_), trial_card_version = ver,
         trial_score_feedback = Treat,
         cov_gender = c("male", "female")[sex], cov_age = age,
         cov_education = c("primary school", "high school", "lower university level", "higher university level", "other")[edu],
         cov_municipality = muni, cov_engo = ENGO, cov_work = work, cov_occupation = occ, cov_adults = old,
         cov_children = young, cov_income_personal = incP, cov_income_household = incH, cov_quiz_score = Score,
         cov_certainty_before = CertB, cov_certainty_after = Cert)]
d <- d[, c("id", "task", "profile", "choice", grep("^(attr|trial|cov)_", names(d), value = TRUE)), with = FALSE]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "aanesen_2021_cold_water_coral.csv"))
