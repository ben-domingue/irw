##Single-profile neighbour vignette (factorial survey) from
##Harris, A. S., & Honig, L. (2023). Mutual dependence and expectations of cooperation.
##The Journal of Politics, 85(1). https://doi.org/10.1086/720646
##Replication data: Harvard Dataverse doi:10.7910/DVN/K0BFAG, CC0 1.0 (no restricted files, no terms).
##Files read: harris_honig_jop_replication_data.dta (original format, ~531 MB, saved as hh.dta;
##only the columns below are read, via col_select). Read as text only: harris_honig_jop_replication_code.do
##(saved as code.do), LGPI 2019 Full Codebook.xlsx (does not cover the experiment), and the UCL accepted
##manuscript of the article (vignette and outcome wording, pp. 18-24).
##Usage: Rscript harris_2023.R <raw dir> <output dir>
##
##*** ONLY THE NON-CO-ETHNIC ARM IS IN THIS TABLE (Ben's ruling, 2026-10-08). ***
##The vignette's ethnic group was a randomized arm (lexp_q5: Coethnic / Non-Coethnic, randomized per
##respondent). In the co-ethnic arm (6,153 respondents) the respondent's own group was piped into the
##vignette and the deposit did not save the ethnic group shown to them (lexp_q1/q2 hold an unused draw
##there), so the displayed level is unknown and those respondents are EXCLUDED. The table therefore
##CANNOT estimate the co-ethnic vs non-co-ethnic contrast that the paper reports. The respondents kept
##(lexp_q5 = Non-Coethnic, 6,209) are a random subset of the sample by design, so effects of the other
##attributes within this arm are unbiased for that arm. In this arm the group shown is a random draw from
##a fixed country list (Malawi: lexp_q1; Zambia: lexp_q2), saved and labelled; the draw was not made to
##exclude the respondent's own group, so 108 respondents in this arm saw their own group (the authors'
##code in the do-file recodes these to co-ethnic). They are kept, as the text they saw is known.
##
##Sample: LGPI 2019 (Local Governance and Performance Index), face-to-face, May-October 2019, rural
##localities within 100 km of the Malawi-Zambia border (and of the Tanzania border); 12,362 respondents
##(6,798 Malawi, 5,564 Zambia; matches the paper). The paper's main analyses use the 7,242 respondents
##without a land title (cov_have_gov_title = 0), pooling the two countries with a Malawi dummy, so this
##is ONE table with cov_country: the attribute set and wording are shared, only the list of ethnic groups
##differs by country (Malawi: Chewa, Tumbuka, Ngoni, Lambya, Yao, Lomwe, Senga, Ndali; Zambia: Chewa,
##Tumbuka, Ngoni, Namwanga, Bemba, Senga, Bisa, Nyika). Survey language(s) are not documented.
##
##Vignette (manuscript p.19): "Imagine you have a neighbor, who is a [ethnic group] [man/woman], who is
##[25/50] years old, and whose family [has lived here for a very long time/migrated here only one year
##ago from elsewhere in the country]. Their income is [higher/the same/lower] than most people in the
##village. They [have access to their land from government papers, and do not rely on traditional
##leaders to provide land rights / rely on traditional leaders to provide their land rights and have no
##government papers]." One profile per respondent (task 1, profile 1). Levels uniform (manuscript fn 8).
##Level text = Stata value labels (stored verbatim):
##  attr_ethnic_group  lexp_q1 (Malawi) / lexp_q2 (Zambia)
##  attr_gender        lexp_q6  man / woman
##  attr_age           lexp_q7  25 / 50
##  attr_migration     lexp_q8  has lived here for a very long time / migrated here only one year ago
##                              from elsewhere in Malawi/Zambia  (the label itself says "Malawi/Zambia")
##  attr_income        lexp_q9  higher than / the same as / lower than  ("... most people in the village")
##  attr_title         lexp_q10 four labels: the title / no-title text with "her" or "his"/"him". The
##                              pronoun follows attr_gender (checked below), so restrictions = observed.
##
##Outcomes (raw codes; "Don't know" and "Refuse to answer" set to NA, as the authors drop them):
##  rating               lexp_q11 "Say you had loaned this neighbor some money, would you trust them to
##                                pay it back?" 1 No, 2 Yes (higher = more trust)
##  rating_donations     lexp_q14 "Imagine you are collecting donations to [add a new classroom to the
##                                local school OR repair the local health clinic], how likely do you think
##                                this person would be to help you collect donations?" 1 Very likely ...
##                                4 Not at all likely (higher = LESS likely)
##  rating_follow_headman lexp_q17 "If there were a conflict in the village that involved this neighbor,
##                                and people went to the headman/woman to resolve it, how likely do you
##                                think it is that this neighbor would follow the headman/woman's orders?"
##                                1-4 as above (higher = less likely)
##  rating_way_of_life   lexp_q18 "To what extent do you agree or disagree with the following statement:
##                                This neighbor is observing our way of life in this village/neighborhood."
##                                1 Agree, 2 Disagree
##  rating_share_well    lexp_q19 "Imagine that there was a well on this neighbor's land. How likely do you
##                                think it is that they would let you use their well?" 1-4 as above
##The first two were asked in random order, then the three mechanism questions in random order; the
##order is not saved. The donation purpose fill was randomized; the deposit has two purpose draws
##(lexp_q12, lexp_q13) and nothing says which one filled q14, so neither is kept. lexp_q15/q16 (authors'
##vote_neigh / neigh_contribute) are dropped: their wording is in neither the deposit nor the manuscript.
##lexp_q20 (does titling help/hurt the community) is not about the profile and is dropped. Respondents
##with no outcome are omitted.
##
##Covariates: cov_country (from mal_border / zam_border), cov_gender (demo_q1 value labels, mapping in
##code below: 1 male, 2 female), cov_age (the deposit's `age`, the authors' rename of demo_q2, years), cov_ethnic_group
##(demo_q4 value-label text, respondent's own group, kept verbatim incl. the combined label
##"Don't Know/Refuse to answer"), cov_have_gov_title (authors' 0/1
##indicator built in the do-file from land_q9/land_q10: holds a government/landlord title; their main
##sample is cov_have_gov_title = 0), cov_locality (the 1 km sampling grid `sqkm`, re-keyed to integers;
##the authors cluster standard errors on it). No survey weight in the deposit's analysis. The deposit's
##other ~6,800 survey columns were not read; id re-keys the
##respondents in source row order (the deposit has no respondent id column among those read).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cols <- c(paste0("lexp_q", c(1, 2, 5:11, 14, 17:19)), "mal_border", "zam_border",
          "demo_q1", "age", "demo_q4", "sqkm", "have_gov_title")
x <- read_dta(file.path(raw, "hh.dta"), col_select = dplyr::all_of(cols))
stopifnot(nrow(x) == 12362)
lab <- function(v) as.character(as_factor(v, levels = "labels"))
n <- function(v) as.integer(zap_labels(v))
stopifnot(identical(names(attr(x$lexp_q5, "labels")), c("Coethnic", "Non-Coethnic")),
          sum(n(x$lexp_q5) == 1) == 6153, sum(n(x$lexp_q5) == 2) == 6209)
x$row <- seq_len(nrow(x))
x <- x[n(x$lexp_q5) == 2, ]                       # non-co-ethnic arm only (see header)
mw <- n(x$mal_border) == 1; zm <- n(x$zam_border) == 1
stopifnot(all(xor(mw, zm)))
d <- data.table(id = x$row, task = 1L, profile = 1L)
rec <- function(v, keep) { v <- n(v); v[!(v %in% keep)] <- NA_integer_; v }
d[, rating := rec(x$lexp_q11, 1:2)]
d[, rating_donations := rec(x$lexp_q14, 1:4)]
d[, rating_follow_headman := rec(x$lexp_q17, 1:4)]
d[, rating_way_of_life := rec(x$lexp_q18, 1:2)]
d[, rating_share_well := rec(x$lexp_q19, 1:4)]
stopifnot(identical(names(attr(x$lexp_q11, "labels")), c("No", "Yes", "Don't know", "Refuse to answer")),
          identical(names(attr(x$lexp_q14, "labels"))[c(1, 4:6)], c("Very likely", "Not at all likely", "Don't know", "Refuse to answer")),
          identical(names(attr(x$lexp_q18, "labels")), c("Agree", "Disagree", "Don't know/Refuse to answer")))
d[, attr_ethnic_group := ifelse(mw, lab(x$lexp_q1), lab(x$lexp_q2))]
d[, attr_gender := lab(x$lexp_q6)]
d[, attr_age := lab(x$lexp_q7)]
d[, attr_migration := lab(x$lexp_q8)]
d[, attr_income := lab(x$lexp_q9)]
d[, attr_title := lab(x$lexp_q10)]
# pronoun in the title text follows the neighbour's gender
stopifnot(d[attr_gender == "woman", all(grepl("\\bher\\b", attr_title))],
          d[attr_gender == "man", all(grepl("\\bhis\\b|\\bhim\\b", attr_title))])
d[, cov_country := ifelse(mw, "Malawi", "Zambia")]
stopifnot(identical(names(attr(x$demo_q1, "labels")), c("male", "female")))
d[, cov_gender := c("male", "female")[n(x$demo_q1)]]
d[, cov_age := as.integer(zap_labels(x$age))]
d[, cov_ethnic_group := lab(x$demo_q4)]
d[, cov_have_gov_title := as.integer(zap_labels(x$have_gov_title))]
d[, cov_locality := as.integer(factor(as.character(zap_labels(x$sqkm))))]
ac <- grep("^attr_", names(d), value = TRUE)
stopifnot(!anyNA(d[, ..ac]), all(d[, ..ac] != ""))
oc <- grep("^rating", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..oc])) > 0]
d[, id := as.integer(factor(id))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "harris_2023_neighbor_cooperation.csv"))
