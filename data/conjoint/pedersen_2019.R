##Danish municipal-candidate factorial vignette from
##Pedersen, R. T., Dahlgaard, J. O., & Citi, M. (2019). Voter reactions to candidate
##background characteristics depend on candidate policy positions. Electoral Studies, 61,
##102066. https://doi.org/10.1016/j.electstud.2019.102066
##Replication data: Harvard Dataverse doi:10.7910/DVN/B5SWDJ, CC0 1.0, no restricted files.
##File read: rawdata_voter_reactions.xlsx (Dataverse "original format" download, saved as
##raw.xlsx): sheet "Completed and partly completed" (responses) and sheet "Nummerering" (the
##full Danish text of all 54 vignettes, keyed by D_Q_Select). Voter_reactions.do (authors'
##Stata code) and README_voter_reactions.pdf read as text; design and measures from the
##accepted manuscript (CBS Research Portal), sections 4.1-4.2. Appendix B (questionnaire) was
##not available, so outcome wording is the manuscript's paraphrase.
##Usage: Rscript pedersen_2019.R <raw dir> <output dir>
##
##Voxmeter web panel, Denmark, October-November 2017 (before the 21 November municipal
##election). 2,597 started, 2,400 completed; each respondent read ONE description of a
##fictitious candidate, drawn from a full 2 x 3 x 3 x 3 factorial (54 texts, D_Q_Select 1-54).
##The deposit has no respondent id: id = row number in the combined sheet. task = 1, profile = 1.
##Attributes (Danish text as displayed, cut from the vignette text; checked against the
##authors' recodes of D_Q_Select in Voter_reactions.do):
##  attr_name     "Peter Nielsen" / "Anne Nielsen" (gender carried by first name and the pronoun
##                Han/Hun; authors' candidate_female: D_Q_Select > 27 = female)
##  attr_parents  "(not shown)" / "der begge var fabriksarbejdere" (factory workers) /
##                "der begge var overlæger" (doctors); appended to "... sammen med sine forældre,"
##  attr_job      "(not shown)" / "som lagerassistent" (warehouse assistant) / "som advokat"
##                (lawyer); appended to "... ved siden af sit arbejde"
##  attr_policy   "(not shown)" / the left-wing statement on elderly care ("En af mine mærkesager
##                er ældreområdet. På dette område bør man investere langt mere i offentlig
##                velfærd, ...") / the right-wing outsourcing statement ("... bør man udlicitere
##                langt flere opgaver, ..."), stored in full
##"(not shown)" = the clause was left out (the paper's "no information" arms). The rest of the
##text (age 47, moved to the municipality 30 years ago, generic motivation statement) is fixed.
##Outcomes (one rating each; "don't know"-type codes, which the authors set to missing, are NA:
##code 6 on the traits, 11 on Q4/Q5):
##  rating               Q5 likelihood of voting for the candidate if they ran in the
##                       respondent's municipality, 0 "very unlikely" - 10 "very likely"
##  rating_left_right    Q4 candidate's economic-policy position on an 11-point left-right
##                       scale 0-10 (0 = left: the left-policy arm averages 3.3, the right 6.4)
##  rating_<trait>       Q3_1_SQ_1-4 intelligent, competent, credible, knowledgeable and Q3_2_SQ_1-4
##                       likeable, conscientious, friendly, caring: "how well or poorly" the word
##                       describes the candidate, codes 1-5. Anchor wording is not in the deposit;
##                       5 = describes best is inferred (the paper reports the left-wing arm
##                       as warmer and more competent and the right-wing arm as less so; codes rise
##                       and fall accordingly, e.g. caring 3.9 left / 3.4 none / 3.1 right).
##The authors rescale all outcomes to 0-1 and build competence/warmth indices; those are not kept.
##Respondents who quit before the vignette (no D_Q_Select) or answered no outcome are omitted.
##Covariates (codes mapped from the authors' recodes in Voter_reactions.do): cov_gender (PB_Gender
##1 = male, 2 = female), cov_age (PB_Age, years), cov_region (PB_Region: Hovedstaden, Sjælland,
##Syddanmark, Midtjylland, Nordjylland), cov_education (PB_Higher_Education 1-8 as the authors'
##Danish labels; codes 9 and 10 both "Andet/Ved ikke", the authors' merged label), cov_vote_choice
##(Q1, party vote choice, 1-11 as the authors' labels "A: Socialdemokraterne" ... "Å:
##Alternativet"; 12-15 "Andet/Ved ikke", merged by the authors), cov_left_right (Q2 self-placement
##0-10; code 11 set to NA as by the authors), cov_completed (1 = completed the survey).
##N vs paper: 2,400 completed (manuscript p. 14); this table has 2,395 respondents with at least
##one non-missing outcome: 2,366 completers (34 completers answered "don't know" to every
##outcome and are omitted) and 29 partial completers. Vote-likelihood means
##by policy arm (0.37 left, 0.25 right on the authors' 0-1 scale, manuscript p. 18) reproduce.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "raw.xlsx")
r <- as.data.table(read_excel(f, sheet = "Completed and partly completed"))
vt <- as.data.table(read_excel(f, sheet = "Nummerering"))
stopifnot(identical(as.integer(vt$Nummer), 1:54))
tx <- vt$Tekst
pick <- function(pat) { m <- regmatches(tx, regexpr(pat, tx)); x <- rep("(not shown)", 54); x[grepl(pat, tx)] <- m; x }
lev <- data.table(D_Q_Select = 1:54,
  attr_name = sub(" stiller.*", "", tx),
  attr_parents = pick("der begge var (fabriksarbejdere|overlæger)"),
  attr_job = pick("som (lagerassistent|advokat)"),
  attr_policy = pick("En af mine mærkesager er ældreområdet\\..*[^\"]"))
lev[, attr_policy := sub("[\"”]$", "", attr_policy)]
## check against the authors' recodes of D_Q_Select
k <- 0:53
stopifnot(all(lev$attr_name == ifelse(k >= 27, "Anne Nielsen", "Peter Nielsen")),
          all(lev$attr_parents == c("(not shown)", "der begge var fabriksarbejdere", "der begge var overlæger")[(k %/% 9) %% 3 + 1]),
          all(lev$attr_job == c("(not shown)", "som lagerassistent", "som advokat")[(k %/% 3) %% 3 + 1]),
          all((lev$attr_policy == "(not shown)") == (k %% 3 == 0)),
          all(grepl("investere", lev$attr_policy) == (k %% 3 == 1)),
          all(grepl("udlicitere", lev$attr_policy) == (k %% 3 == 2)))
na_code <- function(x, dk) { x <- as.integer(x); x[x == dk] <- NA; x }
traits <- c(Q3_1_SQ_1 = "intelligent", Q3_1_SQ_2 = "competent", Q3_1_SQ_3 = "credible", Q3_1_SQ_4 = "knowledgeable",
            Q3_2_SQ_1 = "likeable", Q3_2_SQ_2 = "conscientious", Q3_2_SQ_3 = "friendly", Q3_2_SQ_4 = "caring")
r[, id := seq_len(.N)]
d <- r[, .(id, task = 1L, profile = 1L, D_Q_Select = as.integer(D_Q_Select),
           rating = na_code(Q5, 11L), rating_left_right = na_code(Q4, 11L))]
for (q in names(traits)) d[, paste0("rating_", traits[[q]]) := na_code(r[[q]], 6L)]
oc <- grep("^rating", names(d), value = TRUE)
d <- d[!is.na(D_Q_Select)][d[!is.na(D_Q_Select), rowSums(!is.na(.SD)) > 0, .SDcols = oc]]
stopifnot(all(unlist(d[, .SD, .SDcols = oc]) %in% c(NA, 0:10)))
d <- merge(d, lev, by = "D_Q_Select")[, D_Q_Select := NULL]
edu <- c("Grundskole", "Studentereksamen/HF", "HH/HTX/HHX", "Erhvervsfaglig uddannelse", "Kort videregående",
         "Mellemlang videregående", "Lang videregående", "Forskeruddannelse", "Andet/Ved ikke", "Andet/Ved ikke")
party <- c("A: Socialdemokraterne", "B: Det Radikale Venstre", "C: Det Konservative Folkeparti", "D: Nye Borgerlige",
           "F: Socialistisk Folkeparti", "I: Liberal Alliance", "K: Kristendemokraterne", "O: Dansk Folkeparti",
           "V: Venstre", "Ø: Enhedslisten", "Å: Alternativet", rep("Andet/Ved ikke", 4))
stopifnot(all(r$PB_Gender %in% c(NA, 1:2)), all(r$PB_Higher_Education %in% c(NA, 1:10)), all(r$Q1 %in% c(NA, 1:15)),
          all(r$PB_Region %in% c(NA, 1:5)))
cv <- r[, .(id, cov_gender = c("male", "female")[PB_Gender], cov_age = as.integer(PB_Age),
            cov_region = c("Hovedstaden", "Sjælland", "Syddanmark", "Midtjylland", "Nordjylland")[PB_Region],
            cov_education = edu[PB_Higher_Education], cov_vote_choice = party[Q1],
            cov_left_right = na_code(Q2, 11L), cov_completed = as.integer(Completed))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", oc))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "pedersen_2019_candidate_background.csv"))
