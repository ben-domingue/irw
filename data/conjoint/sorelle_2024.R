##Student-loan borrower deservingness conjoint (US) from
##SoRelle, M. E., & Laws, S. (2024). Deservingness and the politics of student debt relief.
##Perspectives on Politics, 22(2), 372-390. https://doi.org/10.1017/S1537592723001457
##Replication data: Harvard Dataverse doi:10.7910/DVN/MW6ZNF, CC0 1.0, no restricted files.
##Files read: 1-replication data.tab (Dataverse "original format" .dta), 3-codebook.xlsx
##(question wording, level text). 2-do file.do and 4-log.docx read as text (not run).
##Usage: Rscript sorelle_2024.R <dir holding data.dta> <output dir>
##
##Prolific, May 20-26, 2022, 1,500 respondents in the file (article: 1,503; census-matched
##quotas). About half were assigned to this borrower conjoint: 746 answered the choices (747
##gave ratings). Six pairs of hypothetical borrowers were shown (task 1-6, of which 1-4 are kept; profile 1 = borrower A,
##2 = B), 8 attributes: occupation, race, employment status, type of college, level of debt
##(undergraduate/graduate), amount still owed, time in repayment, repayment history.
##The source file has 12 identical rows per respondent (the authors' long "iteration" copies);
##one row per respondent is read and reshaped from the wide choice<t>_* columns.
##Outcomes, same tasks, one table:
##  choice = "Which borrower most deserves to have a significant portion of their outstanding
##    student loan debt forgiven?" Borrower A / Borrower B, forced; no opt-out.
##  rating = "How deserving of student loan debt forgiveness do you think each borrower
##    described above is?" 1 = Very Undeserving .. 5 = Very Deserving.
##  Setup text: "Policymakers are considering a proposal to forgive student loan debt for
##  certain types of borrowers. Please consider the following two people with student loan
##  debt:" (codebook).
##RACE IS ONLY IN TASKS 1-4: the deposit has no choice5_Race*/choice6_Race* columns, and the
##authors' do-file and AMCE models use tasks 1-4 only (n = 5,968 choice rows = 746 x 8, log).
##The deposit does not say whether race was not displayed in tasks 5-6 or was displayed but not
##saved. A blank attr_ means "not shown" in this standard, so tasks 5-6 are DROPPED rather than
##stored with a blank race that may be false; the table holds tasks 1-4, as the authors analyse.
##Level text is from the codebook "Values" column (e.g. "Ivy League College"; the authors'
##do-file labels are shorter). Article: "Each of the attribute levels was fully randomized ...
##every possible borrower profile was equally likely"; attribute order not recorded.
##Respondents assigned to the other arm answered a debt-relief-plan conjoint
##(choice<t>_plan, plan<k>_vote) whose attributes are NOT in the deposit; it is not built.
##Their attribute columns hold randomized values they never saw and are ignored.
##Covariates (codebook codes): cov_gender (1 Male, 2 Female, 3 Other/prefer not), cov_age
##(years), cov_inc (1-7), cov_educ (1-7), cov_race (1 White .. 7 other), cov_sl_debt (ever had
##student loan debt: 1 Yes, 2 No, 3 Can't remember), cov_pid4 (1 Dem, 2 Ind, 3 Rep, 4 Other),
##cov_pid_lean (1 Lean Rep, 2 Lean Dem, 3 Neither), cov_relief_student (support government
##relief of student loan debt, 1 Strongly oppose .. 5 Strongly support). The framing
##experiment's arms and outcome (support_*, cancel_support) are a separate experiment, dropped.
##id = the authors' id_no (assigned; the source Prolific IDs are not in the deposit).
##Rows with neither a choice nor a rating are omitted.
##AUTHORS' CODE BUG: the do-file builds borrower B's repayment history from borrower A's column
##(borrower2_default = choice<t>_Default1 for iterations 7-12), so in the published models
##both profiles of a pair carry A's repayment history. This table uses the correct
##choice<t>_Default2. With that bug imitated, the authors' Figure 2 choice AMCEs (Stata log,
##n = 5,968, tasks 1-4) reproduce exactly from this table (e.g. teacher .188, server .137,
##Black .110); with the correct column they move slightly (teacher .184, Black .111).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "data.dta"))))
v <- setdiff(names(k), c("id_no", "iteration"))
stopifnot(k[, .N, id_no][, all(N == 12)])
w <- k[iteration == 1]
lv <- list(Occupation = c("Doctor", "Small Business Owner", "High School Teacher", "Restaurant Server"),
           Race = c("White", "Black", "Hispanic", "Asian"),
           Employ = c("Employed", "Unemployed and looking for work", "Unemployed and not looking for work"),
           Type = c("Ivy League College", "Private, Not-for-profit College", "Public 2- or 4-year College", "For-profit College"),
           Grad = c("Undergraduate", "Graduate/ Professional", "Both"),
           Unpaid = c("<$10,000", "$10,000-25,000", "$25,000-50,000", "$50,000-75,000", "$75,000+"),
           Repay = c("Hasn't begun repayment", "1-5 years", "5-10 years", "More than 10 years"),
           Default = c("Never missed a payment", "Missed a few payments", "Is currently behind on repayment",
                       "Is in default on repayment"))
an <- c(Occupation = "occupation", Race = "race", Employ = "employment", Type = "college_type", Grad = "debt_level",
        Unpaid = "amount_owed", Repay = "time_in_repayment", Default = "repayment_history")
d <- rbindlist(lapply(1:6, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = as.integer(w$id_no), task = t, profile = p,
                  choice = as.integer(w[[sprintf("choice%d_borrower", t)]] == p),
                  rating = as.integer(w[[sprintf("choice%d_borr%d_deserv", t, p)]]))
  for (n in names(lv)) {
    col <- sprintf("choice%d_%s%d", t, n, p)
    x[, paste0("attr_", an[[n]]) := if (col %in% names(w)) lv[[n]][w[[col]]] else NA_character_]
  }
  x
}))))
d <- d[!is.na(choice) | !is.na(rating)]
stopifnot(d[task <= 4, !anyNA(attr_race)], d[task > 4, all(is.na(attr_race))],
          !anyNA(d[, setdiff(paste0("attr_", an), "attr_race"), with = FALSE]),
          d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)], d[, all(rating %in% 1:5 | is.na(rating))])
cv <- w[, .(id = as.integer(id_no), cov_gender = gender, cov_age = age, cov_inc = inc, cov_educ = educ, cov_race = race,
            cov_sl_debt = sl_debt, cov_pid4 = pid4, cov_pid_lean = pid_lean, cov_relief_student = relief_student)]
d <- d[task <= 4]
d <- merge(d, cv, by = "id")
stopifnot(uniqueN(d[!is.na(choice)]$id) == 746, uniqueN(d$id) == 747)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "sorelle_2024_student_debt.csv"))
