##Republican primary candidate conjoint (US) from
##Arceneaux, K., & Truex, R. (2023). Donald Trump and the lie. Perspectives on Politics,
##21(3), 863-879. https://doi.org/10.1017/S1537592722000901
##Replication data: Harvard Dataverse doi:10.7910/DVN/4PCVQP, CC0 1.0. File read: conjoint.csv
##(raw Qualtrics export of the panel survey). Read as text: ELTS Questionnaire and Codebook.docx,
##read.me.docx, "Donald Trump and the Lie - R Analysis File v POP Final.R". data.RData was
##inspected for weights only (none stored; see below).
##Usage: Rscript arceneaux_2023.R <dir holding conjoint.csv> <output dir>
##
##Daily cross-sections of US registered voters (Toluna panel via Qualtrics, Nov 2020 onward;
##"Day" = fielding day). The conjoint block was shown only to respondents who called
##themselves Republican or Independent (codebook survey flow) and only on later days
##(the authors keep Day > 34). 1,974 respondents have conjoint profiles; 1,883 answered at
##least one task and are kept (all from days 35-40). The authors' sample is good completes
##(gc = 1) with Day > 34: cov_good_complete == 1 gives 1,481 respondents (1,883 kept here;
##of the other 402, 6 are flagged speeders and 396 have no completion code). The authors
##analyse Republicans (P2a = 1, 1,096 kept) and Independent/Other (787) separately (cov_party).
##Question (codebook Q189-Q191, 3 tasks): "Suppose you are voting in a primary election between
##two Republican candidates who are running for Congress. Which candidate do you prefer?"
##Candidate 1 / Candidate 2, no opt-out. choice = 1 for the preferred candidate.
##Attributes (7, Qualtrics CBCONJOINT cells, text as displayed, fixed row order in the
##codebook): Profession, Military Service, Religion, Race/Ethnicity, Gender, Age, Election
##Opinion (Trump lost vs won the 2020 election, with certification vote).
##Randomization restrictions are not documented; level shares are uneven (Protestant 40%,
##Jewish 32%, Catholic 28%; Age 36 = 20% vs 60 = 14%), so the Qualtrics design weights were
##probably not uniform.
##Covariates (codebook codes): cov_gender (D1: 1 Male, 2 Female, 3 Something else, 4 No
##answer), cov_birth_year (D3, free-text year; non-numeric answers set missing),
##cov_education (D4: 1 no HS ... 6 postgraduate, 7 No answer), cov_race (D5: 1 White,
##2 Black, 3 Hispanic, 4 Asian, 5 Native American, 6 Middle Eastern, 7 Other, 8 No answer),
##cov_party (P2a: 1 Republican, 2 Democrat, 3 Independent, 4 Other, 5 No answer),
##cov_party_strength (P2b: 1 Strong, 2 Not very strong Republican), cov_party_lean (P2d:
##1 Republican, 2 Democratic, 3 Neither), cov_election_legitimate (E3: "Do you accept the
##election results as legitimate?" 1 Yes, 2 No, 3 No answer), cov_survey_day (Day),
##cov_good_complete (gc == 1).
##The authors' weights (entropy balancing inside their script) are not stored in the deposit.
##Dropped: panel identifiers (rid, RISN, QPMID, TolunaEnc, ...), dates, all free-text word
##association answers (WUSA, WDJT, ...), D5a (free text), D2 (state), timers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "conjoint.csv"), colClasses = "character", encoding = "UTF-8", check.names = FALSE)
cb <- grep("_CBCONJOINT$", names(s), value = TRUE)
cb <- cb[cb != "vers_CBCONJOINT"]
s <- s[get(cb[1]) != ""]
stopifnot(nrow(s) == 1974)
s[, id := seq_len(.N)]
uuid <- c(profession = "b516a009", military = "347bb331", religion = "b1737a5c", race = "d4263278",
          gender = "c0a15296", age = "16aaee94", election_opinion = "25620c8d")
qs <- c("Q189", "Q190", "Q191")
num <- function(x) suppressWarnings(as.integer(x))
rows <- list()
for (t in 1:3) for (p in 1:2) {
  d <- s[, .(id, task = t, profile = p, ans = get(qs[t]))]
  for (v in names(uuid)) {
    col <- grep(paste0("^", uuid[[v]], ".*\\.", t, "\\.", p, "_CBCONJOINT$"), names(s), value = TRUE)
    stopifnot(length(col) == 1)
    d[, paste0("attr_", v) := s[[col]]]
  }
  rows[[length(rows) + 1L]] <- d
}
d <- rbindlist(rows)
d <- d[ans %in% c("1", "2")]
d[, choice := as.integer(as.integer(ans) == profile)][, ans := NULL]
by <- num(s$D3)
cv <- s[, .(id, cov_gender = num(D1), cov_birth_year = fifelse(by %between% c(1900L, 2002L), by, NA_integer_),
            cov_education = num(D4), cov_race = num(D5), cov_party = num(P2a), cov_party_strength = num(P2b),
            cov_party_lean = num(P2d), cov_election_legitimate = num(E3), cov_survey_day = num(Day),
            cov_good_complete = as.integer(gc == "1"))]
d <- merge(d, cv, by = "id")
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
          !anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, all(.SD != ""), .SDcols = patterns("^attr_")])
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "arceneaux_2023_republican_primary.csv"))
