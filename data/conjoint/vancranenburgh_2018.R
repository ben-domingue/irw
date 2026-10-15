##Small value-of-time route choice experiment, Netherlands, from
##van Cranenburgh, S., Rose, J. M., & Chorus, C. G. (2018). On the robustness of efficient experimental designs towards
##the underlying decision rule. Transportation Research Part A, 109, 50-64. https://doi.org/10.1016/j.tra.2018.01.001
##Data: 4TU.ResearchData doi:10.4121/uuid:1ccca375-68ca-4cb6-8fc0-926712f50404 (van Cranenburgh & Chorus, 2018), CC0.
##Files read: VoT_21-Jun-2016_11-20_full_data.dat (tab-separated) and Meta_data.txt (codebook, Latin-1/cp1252 text).
##The article (Elsevier, behind a bot wall) could not be fetched: the codebook is the only source for the wording.
##Usage: Rscript vancranenburgh_2018.R <dir holding the two files> <output dir>
##
##Online route choice experiment in the Netherlands: 106 respondents x 10 choice sets of three unlabelled route alternatives,
##each described by travel time (TT) and travel cost (TC) (codebook: "Unlabeled Route choice experiment with 3 alternatives
##and 2 attributes"). Fixed design: every respondent saw the same 10 sets with the same alternatives (4 sets from a
##utility-maximisation (RUM) efficient design, 4 from a regret-minimisation (RRM) efficient design, 1 in common, 3 extra:
##trial_in_rum_design, trial_in_rrm_design, 0/1). Forced choice among the three, no opt-out. Outcome: "Choice across
##alternatives 1,2,3" (the codebook gives no question wording). Task = CS (choice set number, recorded; the display order is
##not stated), profile = alternative 1-3.
##Attributes: attr_travel_time 23|27|31|35 and attr_travel_cost 3|4|5|6, stored as the bare numbers of the file.
##LABELS: units are NOT documented in the deposit (minutes and euros are the obvious reading, but only the numbers are stored).
##Restrictions: none documented. Level weights: efficient (non-random) design, no probabilities.
##Covariates: cov_gender (Sex 1 Male, 2 Female; 88888 missing = NA), cov_age (years; 88888 NA), cov_education (Edu codes
##2..7 mapped to the codebook's text; 88888 NA), cov_income (IncHH 1..27 mapped to the codebook's household-income band text;
##28 "I do not know" stays as text, 29 "I don't want to tell" is NA; none occur in the data), cov_social_class (SClass: "A (high)",
##"B1", "B2", "C", "D (low)"), cov_urbanisation_code (Urb 1 low ... 5 high, numeric, no value labels beyond the ends).
##Dropped: OBS (row counter). ID is already 1..106.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "VoT_21-Jun-2016_11-20_full_data.dat"), sep = "\t", fill = TRUE)
x <- x[, 1:18]
stopifnot(nrow(x) == 1060, uniqueN(x$ID) == 106, x[, .N, ID][, all(N == 10)], x$Choice %in% 1:3,
  names(x)[1:18] == c("OBS", "ID", "CS", "CSRUM", "CSPRRM", "TT1", "TC1", "TT2", "TC2", "TT3", "TC3", "Choice", "Sex", "Age", "Edu", "IncHH", "Urb", "SClass"))
m <- readLines(file.path(raw, "Meta_data.txt"), encoding = "latin1", warn = FALSE)
m <- iconv(m, "CP1252", "UTF-8")
i0 <- grep("^IncHH", m); i1 <- grep("^Urb", m)
ib <- m[(i0 + 1):(i1 - 1)]; ib <- ib[grepl("==", ib)]
code <- as.integer(sub("^\\s*([0-9]+) ==.*$", "\\1", ib)); txt <- trimws(sub("^\\s*[0-9]+ == ", "", ib))
txt <- gsub("\\s+", " ", gsub(" tot ", " to ", txt)); txt <- gsub("^Less than € ", "Less than €", txt)
txt <- gsub("€ ", "€", txt); txt <- gsub(" of meer", " or more", txt)
stopifnot(length(code) == 29, !anyNA(code), !any(grepl("�", txt)))
inc <- setNames(txt, code); inc[c("29")] <- NA
edu <- c("2" = "No education", "3" = "Elementary school", "4" = "Lower education", "5" = "Middle education", "6" = "Higher education", "7" = "University education")
sc <- c("1" = "A (high)", "2" = "B1", "3" = "B2", "4" = "C", "5" = "D (low)")
na <- function(v) replace(v, v == 88888, NA)
cov <- x[, .(id = ID, cov_gender = c("male", "female")[na(Sex)], cov_age = na(Age),
  cov_education = unname(edu[as.character(na(Edu))]), cov_income = unname(inc[as.character(na(IncHH))]),
  cov_social_class = unname(sc[as.character(SClass)]), cov_urbanisation_code = Urb, task = CS)]
d <- rbindlist(lapply(1:3, function(p) data.table(id = x$ID, task = x$CS, profile = p, choice = as.integer(x$Choice == p),
  attr_travel_time = as.character(x[[paste0("TT", p)]]), attr_travel_cost = as.character(x[[paste0("TC", p)]]))))
d <- merge(d, cov, by = c("id", "task"))
d[, `:=`(trial_in_rum_design = x$CSRUM[match(paste(id, task), paste(x$ID, x$CS))], trial_in_rrm_design = x$CSPRRM[match(paste(id, task), paste(x$ID, x$CS))])]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 3)])
setorder(d, id, task, profile)
setcolorder(d, c("id", "task", "profile", "choice"))
fwrite(d, file.path(out, "vancranenburgh_2018_value_of_time.csv"))
