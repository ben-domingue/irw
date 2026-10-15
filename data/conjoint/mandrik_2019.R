##Breast cancer screening preferences, Belarus, from
##Mandrik, O., Yaumenenka, A., Herrero, R., & Jonker, M. F. (2019). Population preferences for breast cancer screening
##policies: Discrete choice experiment in Belarus. PLOS ONE, 14(11), e0224667. https://doi.org/10.1371/journal.pone.0224667
##Data: Sheffield Research Data Repository (figshare) doi:10.15131/shef.data.10029185.v1 (Mandrik et al., 2019), CC BY 4.0.
##Files read: BELA_dataset.xlsx (sheets data, characteristics, codes explained).
##Usage: Rscript mandrik_2019.R <dir holding BELA_dataset.xlsx> <output dir>
##
##Women aged 50-69 recruited in hospitals in six Belarus regions, interviewed in Russian. The deposit's data sheet holds
##427 respondents (the paper reports 428 completes of 434 who agreed, 490 invited; 63 'characteristics' rows have no DCE data).
##Each respondent: 18 choice sets (one of 4 design versions of 18 sets, Bayesian D-efficient; trial_version = version 1-4),
##each with program A, program B and a fixed opt-out "I don't choose anything of the proposed" WITHOUT attributes: opt_out =
##yes, the opt-out row (alt 3) is dropped; choice = 0 on both profiles when it was chosen (19% of tasks in the paper).
##Outcome (choice): "Which screening would you select: A or B?" (Fig 1) with the opt-out above.
##The deposit stores ten attributes as 0/1 dummy columns d_att1_2.. (no attribute names or level text in the file). The
##attribute names, order and levels are recovered from the paper: the dummies follow exactly the order of the paper's Table 4
##(telephone invitation, appointment right away, detailed information, combined with other health visits, travel time (3
##dummies), waiting time (2), not knowing the doctor, modality (2), sensitivity (3), cost (2)), whose "(vs. ...)" base levels
##give the level-1 text; the 0/1 direction was checked against Table 4's signs and against the design (exactly 3 attributes
##differ between program A and B in all 7,686 tasks, as the paper's level-overlap rule says: 7 of 10 attributes identical).
##Displayed text: taken from Fig 1 (survey screen) where it shows the level and otherwise from Tables 2 and 4 of the paper
##(paraphrased: appointment, information, combining visits). Level 1 / level 2 text:
##invitation "Postal letter" / "Telephone call"; appointment "Instructions on how to make an appointment" / "Appointment
##arranged right away"; information "No explanation about the process, effects and risk of the program" / "Detailed
##information on screening"; combining "No possibility to combine with other health visits" / "Combined with other health
##visits"; travel time "20|40|60|90 minutes"; waiting time "20|40|60 minutes"; doctor "You know or heard positively about" /
##"You never met or heard positively of before"; modality "Manual examination" / "Mammography" / "Manual examination and
##mammography"; sensitivity "60|70|80|90 out of 100 women"; cost "Nothing" (Fig 1; Table 2 says 0 BRB) / "20 BRB" / "40 BRB".
##Restrictions (documented): in each task 7 of 10 attributes are at the same level in both programs; the sensitivity of manual
##examination cannot exceed that of mammography (paper, Experimental design). Level weights: unknown (efficient design).
##Task = task (slide number given to the respondent, recorded); profile = alternative A/B (1/2).
##Covariates (characteristics sheet, joined by N_new = resp_id): cov_age (years, 59 missing), cov_education ("University (BSc) or
##higher" / "Lower than University"; High_education 1/2, as in the sheet's code list). Other columns are dummies of unclear use and
##were dropped. Respondents re-keyed 1..427 in resp_id order.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "BELA_dataset.xlsx")
x <- as.data.table(read_excel(f, sheet = "data")); ch <- as.data.table(read_excel(f, sheet = "characteristics"))
stopifnot(nrow(x) == 23058, uniqueN(x$resp_id) == 427, !anyNA(x), x[alt == 3, all(optout == 1)], x[alt != 3, all(optout == 0)],
  x[, sum(Y), .(resp_id, task)][, all(V1 == 1)])
lvl <- function(d, cols) { m <- as.matrix(d[, ..cols]); ifelse(rowSums(m) == 0, 1L, max.col(m, ties.method = "first") + 1L) }
p <- x[alt %in% 1:2]
L <- list(
  invitation = c("Postal letter", "Telephone call"),
  appointment = c("Instructions on how to make an appointment", "Appointment arranged right away"),
  information = c("No explanation about the process, effects and risk of the program", "Detailed information on screening"),
  combining = c("No possibility to combine with other health visits", "Combined with other health visits"),
  travel_time = c("20 minutes", "40 minutes", "60 minutes", "90 minutes"),
  waiting_time = c("20 minutes", "40 minutes", "60 minutes"),
  doctor = c("You know or heard positively about", "You never met or heard positively of before"),
  modality = c("Manual examination", "Mammography", "Manual examination and mammography"),
  sensitivity = paste(c(60, 70, 80, 90), "out of 100 women"),
  cost = c("Nothing", "20 BRB", "40 BRB"))
cols <- list(invitation = "d_att1_2", appointment = "d_att2_2", information = "d_att3_2", combining = "d_att4_2",
  travel_time = paste0("d_att5_", 2:4), waiting_time = paste0("d_att6_", 2:3), doctor = "d_att7_2",
  modality = paste0("d_att8_", 2:3), sensitivity = paste0("d_att9_", 2:4), cost = paste0("d_att10_", 2:3))
d <- p[, .(id = match(resp_id, sort(unique(resp_id))), task, profile = alt, choice = Y, trial_version = version, resp_id)]
for (nm in names(L)) d[[paste0("attr_", nm)]] <- L[[nm]][lvl(p, cols[[nm]])]
edu <- c("1" = "University (BSc) or higher", "2" = "Lower than University")
cv <- ch[, .(resp_id = as.numeric(N_new), cov_age = as.integer(Age), cov_education = unname(edu[as.character(High_education)]))]
d[, resp_id := as.numeric(resp_id)]; d <- merge(d, cv, by = "resp_id", all.x = TRUE); d[, resp_id := NULL]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]), d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
setcolorder(d, c("id", "task", "profile", "choice"))
fwrite(d, file.path(out, "mandrik_2019_breast_screening.csv"))
