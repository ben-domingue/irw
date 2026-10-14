##Factorial survey on administrative burdens in German unemployment benefits (ALG II / "Hartz IV") from
##Sievert, M., & Bruder, J. (2024). Unpacking the effects of burdensome state actions on citizens' policy perceptions.
##Public Administration, 102(3), 915-935. https://doi.org/10.1111/padm.12957
##Replication data: Harvard Dataverse doi:10.7910/DVN/Q2WLFS, CC0 1.0 (OSF twin osf.io/7p8am, CC BY, same files). Files read:
##Burden_Data.csv, Vignettes.pdf (the three information pages as displayed, German), Variables.pdf (item wording), and the
##open-access manuscript PDF from the OSF twin (design, sample, group sizes, manipulation check).
##Usage: Rscript sievert_2024.R <dir holding Burden_Data.csv> <output dir>
##
##German panel (SoSci Panel, Nov 2020). Each respondent read short general information on ALG II, then was randomly assigned to one of
##8 groups (2 x 2 x 2): each of three information pages imitating the Arbeitsagentur website is either shown or withheld:
##  attr_learning_demands    page "Arbeitslosengeld II beantragen" (download site with forms and information material to consider before applying)
##  attr_compliance_demands  page "Voraussetzungen fuer Arbeitslosengeld II" (apply, disclose income/assets/housing, first interview, accept any
##                           work, be reachable daily, permission to leave the place of residence, medical examination)
##  attr_sanctions           page "Folgen von Pflichtverletzungen" (benefit reduction of 10 or 30 percent for 3 months, warning box)
##Level text = the German page text from Vignettes.pdf (bullet lines joined with "; "). A page that was withheld is "(not shown)".
##One vignette set per respondent: id = respondent (row number of the file re-keyed), task = profile = 1.
##GROUP-TO-LEVEL MAPPING (INFERRED, then CONFIRMED against the paper): the deposit stores only treat_group 1-8 and no document maps it. Group 1 is
##the control and group 5 saw only sanctions (paper; manipulation-check means reverse to the paper's: 8 - 4.02 = 3.98, 8 - 4.21 = 3.79, SD 1.74).
##Binary coding: groups 1..8 = none, L, C, LC, S, LS, CS, LCS (L = even groups, C = groups 3,4,7,8, S = groups 5-8). Check: OLS of the stored
##outcomes on the three shown/withheld dummies reproduces the magnitudes of the paper's Table 2 coefficients exactly (general support: sanctions
##0.186, learning 0.064, compliance 0.053; spending 0.084, 0.024, 0.015; first-order legitimacy 0.145, 0.044, 0.090; second-order 0.036, 0.048,
##0.150) and only with this assignment of learning and compliance to the two low bits (the swap would exchange those columns). The paper's text
##extraction has no minus signs, so only magnitudes were compared; the signs of my fit are those of the paper's text (sanctions lower approval).
##Sample: 1,748 rows; as the authors, keep respondents who passed both attention checks (AC_benefit == 2 and AC_condition == 1): N = 1,602,
##group sizes 187,181,203,209,206,202,208,206 = the paper's Table 1. cov_attention_pass is therefore 1 for all rows (not stored).
##Outcomes (all ratings of the same vignette set, raw; numeric codes with the paper's directions; item wording from Variables.pdf, German with
##English gloss; the 7-point agreement anchors are not stated in the deposit):
##  rating                   PS_general  approval of ALG II, 1-7 (7 point Likert; the paper's coefficients say higher = more approval)
##  rating_spending          PS_spending federal spending on ALG II: 1 less, 2 same, 3 more (paper: sanctions raise support for spending)
##  rating_prejudice_*       PU01_01..05 estimated number of 100 recipients who (seeking_job) really look for a job, (more_than_work) get more than if
##                           working, (unwilling) do not want to work, (satisfied) are satisfied with support, (illicit) work illicitly. Slider stored
##                           as 1-101 (the file's own *_n columns are value - 1 = the 0-100 count); stored raw.
##  rating_legit_*           LE01_01..09 Alexiou & Wiggins legitimacy items, 1-7; column order follows Variables.pdf (inter-item correlations agree:
##                           the first two, "general public approves" and "most people think practices morally correct", form their own cluster).
##Dropped: the authors' derived scales (prejudices_means, PU*_n, PU*_nreverse), manipulation check (MC), attention checks, ZG01_CP (duration-like
##code), IV01_01 (block order), FL01 literacy items, education (10 unlabelled codes), income (unlabelled), employment, job security, ALG II
##experience, free-text education and employment (SD_edu_other, CV_empl_stat_other).
##PII FOUND: none (free-text fields dropped as a precaution).
##Covariates: cov_gender (1 female, 2 male, 3 other: 948 of 1,602 = 59.0% coded 1, as the paper's 948 women; Table 1 label "1 = female"), cov_age
##(SD_age, 16-84), cov_left_right_code (pol_ideology 1 left .. 10 right per the paper).
##No survey weight, no opt-out.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "Burden_Data.csv"), encoding = "Latin-1", showProgress = FALSE)
stopifnot(nrow(x) == 1748)
x <- x[AC_benefit == 2 & AC_condition == 1]
stopifnot(nrow(x) == 1602, identical(as.integer(x[, .N, treat_group][order(treat_group)]$N), c(187L,181L,203L,209L,206L,202L,208L,206L)))
LD <- "Arbeitslosengeld II beantragen: Arbeitslosengeld II beantragen Sie in Ihrem zuständigen Jobcenter. Alle notwendigen Informationen und Formulare finden Sie auf dieser Seite. Für weitere Informationen kontaktieren Sie bitte Ihr zuständiges Jobcenter. Downloads: Merkblatt zum Arbeitslosengeld II und Sozialgeld.pdf; Antrag auf Arbeitslosengeld II.pdf; Ausfüllhinweise zum Antrag auf Arbeitslosengeld II.pdf; Weiterbewilligungsantrag (WBA) online (Stellen Sie den Weiterbewilligungsantrag für Arbeitslosengeld II online. Den Online-Zugang erhalten Sie bei Ihrem Jobcenter.); Anlage zur Einkommenserklärung (EK).pdf; Anlage für Unterhaltsansprüche gegenüber getrennt Lebenden (UH1).pdf; Anlage zu weiteren Personen der Bedarfsgemeinschaft.pdf; Anlage zu Kosten der Unterkunft und Heizung (KDU).pdf; Anlage zum Mehrbedarf für kostenaufwändigere Ernährung (MEB).pdf"
CD <- "Voraussetzungen für Arbeitslosengeld II: Um die Leistungen des ALG II zu erhalten, müssen Sie einen Antrag beim zuständigen Jobcenter stellen; müssen Sie Ihre Einkommens-, Vermögens- und Wohnverhältnisse offenlegen; müssen Sie nach erfolgreichem Antrag ein Erstgespräch mit Ihrem Jobcenter absolvieren. Während des Leistungsempfangs müssen Sie jede Arbeit annehmen, zu der Sie geistig, seelisch und körperlich in der Lage sind; das Jobcenter bei Bedarf täglich aufsuchen können; sich bei Verlassen des Wohnorts (Ortsabwesenheit) die Zustimmung des Jobcenters einholen (die Ortsabwesenheit ist im Regelfall auf 3 Wochen pro Jahr beschränkt); gegebenenfalls zu einer ärztlichen oder psychologischen Untersuchung erscheinen, wenn das Jobcenter Sie dazu auffordert."
SA <- "Folgen von Pflichtverletzungen: Kommen Sie einer Meldeaufforderung des Jobcenters (Einladung) nicht nach, ohne hierfür einen wichtigen Grund zu haben, beträgt die Minderung 10 Prozent des für Sie maßgebenden Regelbedarfes. Kommen Sie einer anderen Pflicht nicht nach, zum Beispiel der Verpflichtung eine zumutbare Arbeit aufzunehmen, ohne hierfür einen wichtigen Grund zu haben, beträgt die Minderung 30 Prozent des für Sie maßgebenden Regelbedarfes. Eine Minderung wird zunächst für 3 Monate ausgesprochen. Wenn Sie Ihre verletzte Pflicht nachholen, kann sich diese verkürzen. BITTE BEACHTEN SIE: Kommen Sie Ihren Pflichten ohne wichtigen Grund nicht nach, hat dies weitreichende Folgen. Sie müssen mit einer Minderung Ihrer Leistung bis zu 30 Prozent rechnen."
g <- x$treat_group - 1L
NS <- "(not shown)"
d <- data.table(id = seq_len(nrow(x)), task = 1L, profile = 1L, rating = x$PS_general, rating_spending = x$PS_spending)
pj <- c(seeking_job = "PU01_01", more_than_work = "PU01_02", unwilling = "PU01_03", satisfied = "PU01_04", illicit = "PU01_05")
for (n in names(pj)) d[[paste0("rating_prejudice_", n)]] <- x[[pj[[n]]]]
lg <- c(public_approves = 1, morally_correct = 2, common_good = 3, ethical_standards = 4, appropriate_rules = 5, better_world = 6,
        creates_value = 7, in_stakeholder_interest = 8, benefits_stakeholders = 9)
for (n in names(lg)) d[[paste0("rating_legit_", n)]] <- x[[sprintf("LE01_%02d", lg[[n]])]]
d[, `:=`(attr_learning_demands = ifelse(bitwAnd(g, 1L) > 0, LD, NS), attr_compliance_demands = ifelse(bitwAnd(g, 2L) > 0, CD, NS),
         attr_sanctions = ifelse(bitwAnd(g, 4L) > 0, SA, NS),
         cov_gender = c("female", "male", "other")[x$SD_gender], cov_age = as.integer(x$SD_age), cov_left_right_code = as.integer(x$pol_ideology))]
stopifnot(d[, .N, .(attr_learning_demands, attr_compliance_demands, attr_sanctions)][, .N] == 8)
d <- d[rowSums(!is.na(d[, .SD, .SDcols = patterns("^rating")])) > 0]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "sievert_2024_burden_perceptions.csv"))
cat(nrow(d), "rows\n")
