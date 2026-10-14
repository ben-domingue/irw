##2x3 factorial vignette of a Senate candidate (US) from the replication data of
##Banda, K. K., & Sievert, J. How Filibuster Rhetoric Informs Perceptions of Politicians (article DOI not stated in the deposit;
##the deposit is dated by the Qualtrics fielding, 22 March - 14 April 2022).
##Replication data: Harvard Dataverse doi:10.7910/DVN/QFWEE6, CC0 1.0, no restricted files. Files read: experiment.rds,
##Experiment Codebook.pdf (vignette texts, items, value labels). Not used: CCES22 common content (observational), scripts, senator positions.
##Usage: Rscript banda_2022_filibuster.R <dir holding experiment.rds> <output dir>
##
##4,906 respondents (Qualtrics, 2022), one vignette each (between-subject; each row is a respondent, id = row number): "Daniel Reid is a
##[Democratic/Republican] candidate for a U.S. Senate seat in another state. At a campaign rally, he said the following: 'America is a
##great nation and I want to help make it better. [The only way to ensure that Americans can get what they want from government is to
##eliminate / protect the filibuster.] Send me to the Senate and I'll work for you to get it done.'" Arm = which Filibuster_DO_* display-order
##indicator is 1 (exactly one per respondent, checked). Attributes: candidate party (Democratic/Republican), filibuster stance (no
##statement (control) / eliminate the filibuster / protect the filibuster). Level text from the codebook wording. The control arm
##(no stance sentence) has the stance clause omitted: attr_filibuster_stance = "(not shown)".
##Outcomes (codebook, same candidate): rating = favorability "How favorably or unfavorably do you view Daniel Reid?" 1 Very unfavorable ..
##5 Very favorable; rating_supports_elimination = "How supportive or unsupportive is Daniel Reid of eliminating the filibuster?" 1 Very
##unsupportive .. 5 Very supportive (a manipulation check); rating_ideology = "Where would you place Daniel Reid's political ideology"
##1 Very liberal .. 7 Very conservative.
##Covariates: cov_party_id (pid1 value labels), cov_gender (Man/Woman -> male/female; "Some other way" -> other), cov_birth_year
##(the file's `age` holds year of birth), cov_education (value-label text), cov_ideology (ideoself value-label text).
##Dropped: strength/leaner party items, race, income. Count check: article N not read; 4,906 = file.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(readRDS(file.path(raw, "experiment.rds")))
arms <- c("fildemcon", "filrepcon", "fildemelim", "filrepelim", "fildempro", "filreppro")
m <- as.matrix(d[, paste0("Filibuster_DO_", arms), with = FALSE]); m[is.na(m)] <- 0
stopifnot(nrow(d) == 4906, all(rowSums(m) == 1))
arm <- arms[max.col(m, ties.method = "first")]
lab <- function(x) { l <- attr(x, "labels"); unname(names(l)[match(as.numeric(x), l)]) }
gen <- lab(d$gender)
r <- data.table(id = seq_len(nrow(d)), task = 1L, profile = 1L,
  rating = as.integer(d$filfav), rating_supports_elimination = as.integer(d$filcheck), rating_ideology = as.integer(d$filideo),
  attr_party = ifelse(grepl("^fildem", arm), "Democratic", "Republican"),
  attr_filibuster_stance = c(con = "(not shown)", elim = "Eliminate the filibuster", pro = "Protect the filibuster")[sub("^fil(dem|rep)", "", arm)],
  cov_party_id = lab(d$pid1), cov_gender = ifelse(gen == "Man", "male", ifelse(gen == "Woman", "female", ifelse(is.na(gen), NA_character_, "other"))),
  cov_birth_year = as.integer(d$age), cov_education = lab(d$education), cov_ideology = lab(d$ideoself))
stopifnot(!anyNA(r$attr_filibuster_stance))
r <- r[!is.na(rating) | !is.na(rating_supports_elimination) | !is.na(rating_ideology)]
cat("by arm:\n"); print(r[, .N, .(attr_party, attr_filibuster_stance)])
cat("birth year range:", range(r$cov_birth_year, na.rm = TRUE), "\n")
setorder(r, id, task, profile)
fwrite(r, file.path(out, "banda_2022_filibuster.csv")); cat("rows", nrow(r), "\n")
