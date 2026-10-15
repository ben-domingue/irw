##Instructor identity and course enrollment: paired conjoint of first-year seminar choices, from
##Liu, L.-Y., Brough, C., & Gaozhao, D. (2026). Before the first lecture: The effects of instructor identity on course
##enrollment. PS: Political Science & Politics, 59(4), 690-696. https://doi.org/10.1017/S1049096526102054
##Data: Harvard Dataverse doi:10.7910/DVN/DSOBOP, CC0 1.0 (API; no terms, files unrestricted). Files read: Data.tab and,
##as text, "Data Analysis.R" (attribute lists, baselines). Usage: Rscript liu_2026_instructor_identity.R <dir holding Data.tab> <output dir>
##
##240 respondents (sample details in the paper, not in the deposit), 5 paired tasks each (contest_no 1-5), 2 profiles
##per task: a first-year seminar described by SSC Theme (Social Activism / Sex and Relations / Religion and Common Good /
##Nuclear Power and War / Space and Technology), professor's last name (Dr. Chen / Williams / Garcia / Habib / Smith)
##and professor's pronouns (she/her/her [sic] / he/his/him / they/their/theirs). Outcome ChosenItem: 1 on the course
##chosen (exactly one per task, verified). No opt-out. The question wording is not in the deposit.
##Randomization: independent (the authors' makeDesign has no constraints; the same theme can appear on both
##profiles). Level weights: not stated, shares near equal. Attribute order: not recorded.
##Profile = the deposit's profile 1/2; task = contest_no (recorded). Respondent key CaseID is a running number 1-240.
##No covariates in the deposit. Trailing space trimmed from "Religion and Common Good ".
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Data.tab"), encoding = "UTF-8")
setnames(x, c("id", "task", "attr_theme", "attr_professor_name", "attr_professor_pronouns", "choice", "profile"))
stopifnot(nrow(x) == 2400, uniqueN(x$id) == 240, x[, .N, .(id, task)][, all(N == 2)], x[, sum(choice), .(id, task)][, all(V1 == 1)])
x[, attr_theme := trimws(attr_theme)]
d <- x[, .(id, task, profile, choice, attr_theme, attr_professor_name, attr_professor_pronouns)]
setorder(d, id, task, profile)
stopifnot(!anyNA(d))
fwrite(d, file.path(out, "liu_2026_instructor_identity.csv"))
