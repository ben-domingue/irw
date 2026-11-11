##US adults' choice between two dermatologists (Doctor A / Doctor B) described by race, patient rating, party,
##distance, medical school and gender, from
##O'Brian, N. A., & Kent, T. B. (2025). Partisanship and trust in personal doctors: Causes and consequences. British
##Journal of Political Science, 55, e34. https://doi.org/10.1017/S0007123424000607 (open access, CC BY 4.0)
##Data: O'Brian, N. (2025). Replication Data for Partisanship and Trust in Doctors: Causes and Consequences. Harvard
##Dataverse. https://doi.org/10.7910/DVN/UIBZSC (CC0 1.0; no terms, no restricted files).
##Files read: conjoint_bjps.dta (Stata original; 4,600 rows), Codebook.docx, READ ME.docx; bjps_mainmanuscript.do and
##bjps_mainmanuscript.R read as text only (never run). The other files (GSS trust series, prime and Zocdoc framing
##experiments) are not conjoint data and are not used.
##Usage: Rscript obrian_2025.R <dir holding conjoint_bjps.dta> <output dir>
##
##Design (article): each respondent saw two tables of Doctor A vs Doctor B ("Each respondent was shown two tables for a
##total of 2,299 choices"; one respondent answered only one table); attribute order varied across respondents but was
##fixed within respondent (not recorded); profiles shown as a table. Question: "Suppose you need to schedule a
##dermatology appointment and are choosing which dermatologist to go to. Which dermatologist are you more likely to
##schedule an appointment and visit? Doctor A or Doctor B?" Forced choice, opt_out = no.
##Task/profile: the deposit is a Stata -stack- of four profiles per respondent (_stack 1-4). _stack 1-2 and 3-4 are the
##two tasks: exactly one profile chosen in each of the 2,299 answered pairs (checked; the pairing 1-3/2-4 fails), and
##the one unanswered pair (choose missing) is dropped. task = 1 for _stack 1-2, 2 for 3-4; profile = 1 for odd _stack
##(Doctor A presumably), 2 for even. INFERRED from the stack order (no task/profile variable).
##CODED ATTRIBUTES (#3474). The article's Table 1 (the conjoint table) is an image that does not survive in the HTML
##text and the codebook gives only indicator definitions, so the displayed text is unknown (the article says race
##and gender were "perceived", i.e. possibly signalled by names or photos; star ratings are illustrated as numbers
##such as 3.9 and 4.1, distances as ten and thirty-five minutes). Codes as deposited, k-1 dummies collapsed:
##  attr_race_code: "hispanic" / "black" (codebook: doc is Hispanic / Black) or "ref" when both are 0 (article
##    Figure 4 note: White is the omitted category).
##  attr_rating_code: "lowstar" / "medstar" / "histar" (exactly one is 1 on every row; codebook: medium / high star
##    rating; article: High, Medium, Low patient ratings).
##  attr_dem_code: dem 0/1 (codebook: 1 = doc is a Democrat; article: Democrat or Republican).
##  attr_far_code: far 0/1 (codebook: 1 = doc is further away; article baseline "Nearby").
##  attr_ivy_code: ivy 0/1 (codebook: 1 = Ivy League school; article baseline "State school").
##  attr_male_code: male 0/1 (article Figure 4: "Male", baseline "Female"). Coded, so no crosswalk row.
##Covariates (deposit, codebook definitions): cov_white, cov_black, cov_hispanic (whitex/blackx/hispanicx, 1 = respondent
##is White/Black/Hispanic), cov_gender_code (malex, 1 = male respondent, 0 = not male; kept as code),
##cov_repdem (0 = Democrat, 1 = Republican, NA otherwise), cov_libcon (0 = liberal, 1 = conservative),
##cov_trump_ft (Trump minus Biden feeling thermometer), cov_votetrump (1 = Trump, 0 = Biden).
##Dropped: responseid (Qualtrics ResponseId; re-keyed to 1..N), trump (identical copy of trump_ft).
##Exclusions: the deposit holds only the 1,150 respondents who passed the attention check (article); the failures are
##not deposited. No further exclusions applied.
##Counts: 1,150 respondents and 2,299 choices = the article.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "conjoint_bjps.dta")))
setnames(d, "_stack", "stk")
stopifnot(nrow(d) == 4600L, d[, .N, responseid][, all(N == 4L)], d[, .N, .(responseid, stk)][, all(N == 1L)],
          identical(as.numeric(d$trump), as.numeric(d$trump_ft)))
d[, `:=`(task = as.integer((stk + 1) %/% 2), profile = as.integer(2 - stk %% 2))]
d <- d[!d[, .(bad = anyNA(choose)), .(responseid, task)][bad == TRUE], on = .(responseid, task)]
stopifnot(d[, sum(choose), .(responseid, task)][, all(V1 == 1)], nrow(d) == 4598L)
stopifnot(all(d$lowstar + d$medstar + d$histar == 1), all(d$hispanic + d$black <= 1))
o <- d[, .(id = match(responseid, sort(unique(responseid))), task, profile, choice = as.integer(choose),
           attr_race_code = fcase(hispanic == 1, "hispanic", black == 1, "black", default = "ref"),
           attr_rating_code = fcase(lowstar == 1, "lowstar", medstar == 1, "medstar", histar == 1, "histar"),
           attr_dem_code = as.integer(dem), attr_far_code = as.integer(far), attr_ivy_code = as.integer(ivy),
           attr_male_code = as.integer(male),
           cov_white = as.integer(whitex), cov_black = as.integer(blackx), cov_hispanic = as.integer(hispanicx),
           cov_gender_code = as.integer(malex), cov_repdem = as.integer(repdem), cov_libcon = as.integer(libcon),
           cov_trump_ft = as.numeric(trump_ft), cov_votetrump = as.integer(votetrump))]
setorder(o, id, task, profile)
fwrite(o, file.path(out, "obrian_2025_doctor_choice.csv"))
cat(nrow(o), uniqueN(o$id), "\n")
