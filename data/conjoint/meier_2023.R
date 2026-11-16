##US adults' comfort with placing a child in a hypothetical school district ("Greenwood School District") described by
##three randomized performance figures (effectiveness, equity, efficiency), 3x3x3 factorial vignette, two experiments, from
##Meier, K. J., Davis, J., & Xu, X. (2023). Effectiveness, efficiency, and equity tradeoffs in public programs: A citizen
##experiment. Public Administration Review, 83(6), 1462-1477. https://doi.org/10.1111/puar.13690
##Data: Meier, K., Davis, J., & Xu, X. (2023). Replication Data for: Effectiveness, Efficiency and Equity Tradeoffs in
##Public Programs: A Citizen Experiment. Harvard Dataverse. https://doi.org/10.7910/DVN/0I991V (CC0 1.0; no terms,
##no restricted files).
##Files read (Stata originals): "Experiment 1-Low Income.dta", "Experiment 2-Race.dta"; codebook.pdf and "do file.do"
##(read as text).
##Usage: Rscript meier_2023.R <dir holding the two .dta files> <output dir>
##
##Tables: meier_2023_school_district_income (Experiment 1, equity framed by low-income students; 1,645 rows) and
##meier_2023_school_district_race (Experiment 2, equity framed by race; 884 rows). Separate experiments with different
##equity content and separate data files -> separate tables. One vignette per respondent; the files hold no respondent
##id: id = row number, task = 1, profile = 1.
##CODED ATTRIBUTES (#3474). The vignette text and units are not deposited (codebook names the variables only; the
##article is behind Wiley's wall). Each attribute is stored as the deposit's numeric level, which is exactly one-to-one
##with the authors' 3-level factor (checked: 75/80/85 = Effectiveness 1/2/3, 65/70/75 = Equity 1/2/3, 9.328/9.95/10.572 =
##Efficiency 1/2/3, value labels "Low/Medium/High <attribute>"):
##  attr_effectiveness_code: effectiveness, 75 / 80 / 85 (a performance figure; unit, presumably percent, not stated);
##  attr_equity_code: equity, 65 / 70 / 75 (unit not stated);
##  attr_efficiency1000_code: efficiency1000, "efficiency/1000" per the codebook, 9.328 / 9.95 / 10.572 (the deposited
##    efficiency figure divided by 1000; the original variable is not in the files; unit not stated).
##The authors' Low/Medium/High labels are the deposit's coarse names; Low Efficiency goes with the smallest figure.
##Outcome: rating = comfort, "If you were in need of a new school district, how comfortable would you be placing your
##child in Greenwood School District?" (codebook; Stata label says "you relative"), 1 = Very uncomfortable ...
##5 = Very comfortable (value labels; Stata label "(1-5 higher is better)"). Stored raw. Respondents with no comfort
##answer dropped (2 + 3).
##Dropped: f_efficiency, f_effective, f_redtape, f_equality (factor scores of perception items whose items are not
##deposited: derived); Equeffec, equeffec, Effieffec, effieffec (derived ratios); republican, woman (derived dummies);
##the 1-3 factor versions of the attributes (duplicates of the numeric levels).
##Covariates (value labels): cov_age (free-typed: values outside 18-110, e.g. typed birth years 1992, set to NA); cov_gender (Woman -> female, Man -> male, Non-binary/Other -> other);
##cov_race; cov_education; cov_party_id ("Political Party": Democrat/Republican/Independent\No Party Affiliation/Other);
##cov_income (bracket text). No exclusions applied.
##Counts vs the paper: not checked (paywalled).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) as.character(as_factor(x, levels = "labels"))
mk <- function(f, tab, n) {
  d <- as.data.table(read_dta(file.path(raw, f))); stopifnot(nrow(d) == n)
  stopifnot(all(d$effectiveness == c(75, 80, 85)[d$Effectiveness]), all(d$equity == c(65, 70, 75)[d$Equity]),
            all(round(d$efficiency1000, 3) == c(9.328, 9.95, 10.572)[d$Efficiency]))
  d[, id := .I]; d <- d[!is.na(comfort)]
  g <- lab(d$gender)
  o <- d[, .(id, task = 1L, profile = 1L, rating = as.integer(comfort),
             attr_effectiveness_code = as.integer(effectiveness), attr_equity_code = as.integer(equity),
             attr_efficiency1000_code = round(efficiency1000, 3), cov_age = fifelse(Age >= 18 & Age <= 110 & Age == round(Age), as.integer(Age), NA_integer_))]
  o[, `:=`(cov_gender = fcase(g == "Woman", "female", g == "Man", "male", g %in% c("Non-binary", "Other"), "other"),
           cov_race = lab(d$race), cov_education = lab(d$education), cov_party_id = lab(d$party), cov_income = lab(d$income))]
  setorder(o, id, task, profile); fwrite(o, file.path(out, paste0(tab, ".csv")))
  cat(tab, nrow(o), "\n")
}
mk("Experiment 1-Low Income.dta", "meier_2023_school_district_income", 1645L)
mk("Experiment 2-Race.dta", "meier_2023_school_district_race", 884L)
