##Candidate-selection conjoint among Tunisian local election candidates from
##Sasmaz, A. (2026). Organizational cohesion and unequal political selection: Evidence from
##Tunisia's secular-Islamist competition. Perspectives on Politics, 1-23.
##https://doi.org/10.1017/S1537592725103721 (open access, CC BY 4.0; online 2026 per Crossref, the deposit says "PoP 2025")
##Replication data: Harvard Dataverse doi:10.7910/DVN/1PT7FZ, CC0 1.0. File read (inside
##"Sasmaz PoP 2025 Replication Files.zip"): lecs_forconjointanalyses.xlsx. Also read as
##text: CODEBOOK.pdf (dataset "lecs_conjoint.xlsx"), TunLECS_English_QuestionForm.pdf
##(Conjoint 3), PoP_Conjoint.R (the author's recode, not run).
##Usage: Rscript sasmaz_2026.R <dir holding the .xlsx> <output dir>
##
##Local Election Candidates Survey (LECS), Tunisia 2018 (Blackman, Clark & Sasmaz),
##April-May 2018, 1,907 candidates in 100 municipalities on lists for the May 2018 municipal
##elections, contacted by enumerators (the article says by phone; the draft form mentions a
##paper handout). Conjoint 3 ("Candidate selection"): "During the preparations for
##elections, important decisions have been made about who will be included in the lists.
##Imagine that these two people have been suggested to you to be included in your list.
##Which person would you contact first to offer a place in your list?" (English
##questionnaire; respondents saw Arabic). 3 rounds x 2 profiles (S/T, U/V, W/X); st_can,
##uv_can, wx_can = 1 if the first profile was chosen, 0 if the second. Forced choice; 41,
##28 and 34 rounds have no answer and are omitted (rows with no outcome).
##1,907 rows in the file; 11 respondents answered no round, leaving 1,896 respondents. The article's conjoint figures
##use only Nidaa and Ennahda candidates who are registered party members (a subset). The
##article's 1,907 candidates match the file. Spot check: among those party members, the
##choice rate for 5-year members vs independents is 57 vs 44 (Nidaa) and 52 vs 50 (Ennahda),
##the pattern the article describes (Figure 5 values are an image, not compared).
##Attributes (5): party affiliation, sex, age, background, profession. Levels are stored as
##the ARABIC TEXT in the file (what respondents saw). The fielded levels differ from the
##English questionnaire: ages are 25/33/41/49/57 (form: 25-65 by 10), and the profession
##level "وظيفة عمومية" ("public-sector job") appears where the form lists "Lawyer"; the
##author's recode maps it to "lawyer". Stored as displayed.
##Each cell s0..s4 holds one attribute's level; which attribute sits in which column varies
##across respondents (120 orders, i.e. all permutations) but is the same for all 6 profiles
##of a respondent, so attribute ORDER WAS RANDOMIZED per respondent. attrpos_<attr> = the
##column index + 1, read as the row position shown (inferred from the column order; the
##codebook does not say so). Attributes are identified by their level text.
##Randomization restrictions are not documented; level shares in the table look uniform.
##Covariates: cov_list_class (Ennahda / Nidaa / Independent / Third Party),
##cov_party_member_nidaa, cov_party_member_ennahda (1 = registered member).
##Dropped: resp_id (a Qualtrics ResponseId), re-keyed to integers in file order (ids of the 11 non-answering rows are skipped).
library(openxlsx); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read.xlsx(file.path(raw, "lecs_forconjointanalyses.xlsx")))
stopifnot(nrow(s) == 1907, !anyDuplicated(s$resp_id))
s[, id := .I]
cls <- function(x) fifelse(grepl("^[0-9]+$", x), "age",
                   fifelse(x %in% c("ذكر", "أنثى"), "sex",
                   fifelse(grepl("منخرط|مستقل", x), "party",
                   fifelse(grepl("^ذو|^منحدر", x), "background", "profession"))))
prof_lv <- c("أستاذ تعليم ثانوي", "رجل/سيدة أعمال", "عاطل عن العمل", "فلاح", "وظيفة عمومية")
P <- c("s", "t", "u", "v", "w", "x"); ch <- c("st_can", "uv_can", "wx_can")
rows <- list()
for (i in seq_along(P)) {
  p <- P[i]; tk <- (i + 1L) %/% 2L; pr <- 2L - i %% 2L
  d <- data.table(id = s$id, task = tk, profile = pr)
  y <- as.integer(s[[ch[tk]]]); d[, choice := if (pr == 1L) y else 1L - y]
  for (k in 0:4) {
    x <- s[[paste0(p, k)]]; stopifnot(!anyNA(x))
    cl <- cls(x); stopifnot(all(cl != "profession" | x %in% prof_lv))
    for (at in unique(cl)) {
      w <- cl == at
      d[w, paste0("attr_", at) := x[w]]; d[w, paste0("attrpos_", at) := k + 1L]
    }
  }
  rows[[i]] <- d
}
d <- rbindlist(rows, use.names = TRUE)
stopifnot(!anyNA(d[, .(attr_age, attr_sex, attr_party, attr_background, attr_profession)]))
stopifnot(d[, uniqueN(paste(attrpos_age, attrpos_sex, attrpos_party, attrpos_background, attrpos_profession)), id][, all(V1 == 1)])
d <- d[!is.na(choice)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 1896)
cv <- s[, .(id, cov_list_class = list_class, cov_party_member_nidaa = as.integer(party_member_ni),
            cov_party_member_ennahda = as.integer(party_member_en))]
d <- cv[d, on = "id"]
setcolorder(d, c("id", "task", "profile", "choice", "attr_party", "attr_sex", "attr_age", "attr_background", "attr_profession",
                 "attrpos_party", "attrpos_sex", "attrpos_age", "attrpos_background", "attrpos_profession"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "sasmaz_2026_candidate_selection.csv"))
