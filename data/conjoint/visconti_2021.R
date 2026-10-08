##Presidential-candidate conjoint (Santiago, Chile) from
##Visconti, G. (2021). Reevaluating the role of ideology in Chile. Latin American Politics
##and Society, 63(2), 1-25. https://doi.org/10.1017/lap.2021.1
##Replication data: Harvard Dataverse doi:10.7910/DVN/2ZKW5F, CC0 1.0, no restricted files.
##Files read: conjoint_cerrillos_LAPS.dta and survey_cerrillos_LAPS.dta (Dataverse "original
##format" downloads). Wording from the article's online supplement (Cambridge,
##S1531426X21000030sup001.pdf, Appendices C and M); the deposit's 000_read_me.txt and
##03_conjoint_analysis.R were read as text.
##Usage: Rscript visconti_2021.R <raw dir> <output dir>
##
##Face-to-face survey, 2017, random walk in low-to-middle-income neighbourhoods of Santiago
##(Cerrillos, Recoleta, Independencia). The deposit holds the 300 respondents of the pure
##control arm of a framing experiment that preceded the conjoint (vignette = 3), the arm the
##article analyses. Enumerators read: "This final section attempts to understand your
##political preferences. We will show you profiles of hypothetical presidential candidates
##(non-real). You should tell us who you prefer for president. Each candidate has three
##attributes: ideology, profession, and age. We will repeat this exercise 5 times." Then, per
##pair (e1-e5): "Who would you select for president?" (1) candidate 1 (2) candidate 2 (88) DK
##(99) DA. 5 tasks (pair) x 2 candidates (profile = candidate 1/2).
##choice: 1 = this candidate selected. OPT-OUT: the data also hold code 3 for 222 of the 1,500
##tasks, which the instrument does not list; the authors' outcome codes it 0 for both
##candidates and keeps those tasks in every model, i.e. a (volunteered) choice of neither.
##Kept as choice = 0 on both profiles; the meaning "neither" is INFERRED. Tasks answered DK
##(88, 2 tasks) or DA (99, 62 tasks) have no outcome and are omitted, as the authors do; this
##removes all 50 tasks of the 10 respondents flagged failcon = 1, so the table has 290
##respondents and 1,436 tasks.
##Attributes (3, levels as stored in the data, in Spanish as shown on the cards; the
##supplement gives them in English as left/right, gardener/teacher/engineer, 30/40/50):
##ideology izquierda/derecha; profession jardinero/profesor/ingeniero; age 30/40/50. The
##exact card layout is not deposited. Randomization restrictions: none documented.
##Covariates (codes per Appendix M): cov_interest_politics (a3) 1=a lot 2=some 3=a little
##4=none; cov_left_right (a5) 1=left .. 10=right, 88=DK, 99=DA (the article's left <= 4,
##centre 5-6, right >= 7, no identification = 88/99); cov_vote_intention (a10) 1=Pinera
##2=Sanchez 3=Guillier 4=Goic 5=Enriquez-Ominami 6=other 88=DK 99=DA; cov_voted_2013 (a11)
##1=yes 2=no 88=DK 99=DA; cov_age (b1, years); cov_education (b2, answer text as in the
##supplement's English rendering, Appendix M b2: Primary incomplete, Primary complete,
##Secondary incomplete, Secondary complete, Technical incomplete, Technical complete, College
##incomplete, College complete, Graduate studies; DK/DA codes 88/99 do not occur); cov_gender
##(b6 "Gender [DO NOT ASK]", recorded by the enumerator: (1) Male = male, (2) Female = female,
##Appendix M); cov_social_benefits_party (c1) and
##cov_iron_fist_party (c2) 1=left-wing politicians 2=right-wing politicians (3 occurs, not
##in the instrument) 88=DK 99=DA; cov_crime_policy (d2) 1=iron fist 2=rehabilitation (3
##occurs, not in the instrument) 88=DK 99=DA; cov_enumerator (1-4).
##Dropped: survey items with no wording in the supplement (a1, a2, a4, a6-a9, a12, b3-b5,
##d1), the block identifier cuadrante, failcon, vignette, the authors' derived outcome.
##N: the article's Appendix G samples (e.g. 694 rows of left-wing respondents) are rows after
##the same DK/DA drop; the table has exactly 694 rows with cov_left_right <= 4. Spot check:
##the Appendix H balance regression on the attributes reproduces Table A8 in magnitude (left
##0.024, teacher 0.029, engineer 0.015, 40 -0.018, 50 -0.022) with every sign flipped: the
##authors' 13_conjoint_diagnostic.R codes "female" as b6 == 1, whereas the instrument (1 Male,
##2 Female) and Table A3 (60% female = share with b6 == 2) say 2 = female, which is used here.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "conjoint_cerrillos_LAPS.dta"))))
s <- as.data.table(zap_labels(read_dta(file.path(raw, "survey_cerrillos_LAPS.dta"))))
lab <- function(x) as.character(as_factor(x))
kl <- read_dta(file.path(raw, "conjoint_cerrillos_LAPS.dta"))
k[, `:=`(ideo = lab(kl$atideology), prof = lab(kl$atprofession), agel = lab(kl$atage))]
stopifnot(nrow(s) == 300, all(k$vignette == 3), k[, .N, idnum][, all(N == 10)],
          all(k$outcome == as.integer(k$selected == k$candidate)))
k <- k[selected %in% 1:3]
stopifnot(uniqueN(k$idnum) == 290)
ids <- sort(unique(as.integer(k$idnum)))
stopifnot(all(k$b2 %in% 1:9), all(k$b6 %in% 1:2))
edu <- c("Primary incomplete", "Primary complete", "Secondary incomplete", "Secondary complete", "Technical incomplete",
         "Technical complete", "College incomplete", "College complete", "Graduate studies")
k[, id := match(as.integer(idnum), ids)]
d <- k[, .(id, task = as.integer(pair), profile = as.integer(candidate), choice = as.integer(selected == candidate),
           attr_ideology = ideo, attr_profession = prof, attr_age = agel,
           cov_interest_politics = as.integer(a3), cov_left_right = as.integer(a5), cov_vote_intention = as.integer(a10),
           cov_voted_2013 = as.integer(a11), cov_age = as.integer(b1), cov_education = edu[b2],
           cov_gender = c("male", "female")[b6], cov_social_benefits_party = as.integer(c1), cov_iron_fist_party = as.integer(c2),
           cov_crime_policy = as.integer(d2), cov_enumerator = as.integer(enumerator))]
stopifnot(setequal(d$attr_ideology, c("izquierda", "derecha")), setequal(d$attr_profession, c("jardinero", "profesor", "ingeniero")),
          setequal(d$attr_age, c("30", "40", "50")))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "visconti_2021_chile_candidates.csv"))
