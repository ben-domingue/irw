##Movement-party candidate conjoint (six European countries) from
##Mercea, D., & Santos, F. G. (2025). Policy over protest: Experimental evidence on the drivers
##of support for movement parties. Perspectives on Politics, 23(3), 901-923.
##https://doi.org/10.1017/S1537592724001439 (online November 2024; CC BY 4.0 article)
##Replication data: Harvard Dataverse doi:10.7910/DVN/CBKZL1, CC0 1.0, no restricted files,
##no terms. Files read: Denmark_PoP.sav, Germany_PoP.sav, Hungary_PoP.sav, Italy_PoP.sav,
##Romania_PoP.sav, UK_PoP.sav (wide, one row per respondent; SPSS value labels in the national
##language); readme.docx; the authors' Conjoint_PoP_replication.R read as text. Design and
##wording from the article (Research design section, introduction text, Table 2).
##Usage: Rscript mercea_2025.R <raw dir> <output dir>
##
##YouGov, 21 February - 11 March 2022: Denmark 1,001, Germany 2,024, Hungary 2,051, Italy
##2,101, Romania 946 (Romanian or Hungarian version), UK 2,224 = 10,347 respondents. Five
##screens, each with two hypothetical parliamentary candidates (no party shown) and five
##three-level attributes, randomly assigned to both candidates. Intro (article): "Please imagine
##that there are national parliamentary elections taking place next week. We would like to show
##you 5 pairs of profiles of potential candidates ... which one of the two candidates you would
##prefer to have representing you in [country's] parliament ..."
##ONE pooled table (cov_country), as the authors pool the six samples in the main analysis
##(country models only in the appendix). attr_ text is the ENGLISH instrument, not the national
##display text: the UK file's English labels (identical codes 1-3 in all six files; the code
##order was checked against every national label set), with two UK labels that SPSS truncated
##at 120 bytes completed from article Table 2 ("... volunteering in the local community
##regularly, for the last 12 years."; "... make them the first priority for the country."), and
##"The United Kingdom" in the migration levels replaced by "[COUNTRY]" (Table 2's placeholder;
##each country saw its own name). The national-language labels are truncated in the same way
##in several levels, which is why they are not used. Table 2 wording differs slightly from the
##UK labels (e.g. "Because corrupt elites ..." vs "Is running because ..."); the UK labels are kept.
##Outcomes (same tasks, one table):
##  choice: "If you had to choose between them, which candidate do you prefer?" (cjchoice_<t>,
##    Candidate 1 / Candidate 2; forced choice, no opt-out; no Skipped/Not Asked in the data).
##  rating: each candidate on 1-7, 1 = "Strongly disapprove", 7 = "Strongly approve" (UK
##    variable label; the article: "one indicated they strongly disapprove of the candidate and
##    seven that they strongly approve"); stored raw, higher = more approval. Prompt wording not
##    in the deposit (paraphrase in the design record).
##task = screen 1-5, profile = candidate 1/2 (source names src_<t>_attribut<a>_<p>; the label of
##  src_4_attribut4_1 says "Screen 5", a label typo: the variable sits in the screen-4 slot).
##Randomization: "all possible combinations were plausible", no restrictions (article).
##  Attribute order randomized in the first task and kept for the rest (article): per
##  respondent, NOT recorded in the deposit.
##Covariates: cov_country (ISO alpha-2), cov_past_vote (last national election vote, the
##  deposited answer text in the national file's labels; "Prefer not to say"/refusal labels ->
##  NA; "Don't know" kept; Northern Ireland respondents' UK19_ni answer used when UK19 is
##  missing), cov_survey_weight (W8, YouGov weight within country; the article's main results
##  are unweighted).
##Dropped: nothing but the per-country respondent ID (1..n in each file, collides across
##  files): id = country order DK, DE, HU, IT, RO, UK then source ID.
##N: 10,347 respondents and 51,735 tasks match the article.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
files <- c(DK = "Denmark", DE = "Germany", HU = "Hungary", IT = "Italy", RO = "Romania", GB = "UK")
vote <- c(DK = "DK19", DE = "DE21", HU = "HU18", IT = "IT18", RO = "RO20", GB = "UK19")
uk <- read_sav(file.path(raw, "UK_PoP.sav"))
eng <- lapply(1:5, function(k) {
  l <- attr(uk[[paste0("src_1_attribut", k, "_1")]], "labels"); l <- l[l %in% 1:3]
  setNames(names(l), l)[as.character(1:3)]
})
eng[[2]][["3"]] <- "Has never participated in any demonstration or march but has been volunteering in the local community regularly, for the last 12 years."
eng[[5]][["1"]] <- "Thinks the current policies to tackle climate change do not go far enough and proposes to make them the first priority for the country."
eng[[4]] <- sub("The United Kingdom", "[COUNTRY]", eng[[4]], fixed = TRUE)
stopifnot(!anyNA(unlist(eng)), grepl("for the$", names(attr(uk$src_1_attribut2_1, "labels"))[3]),
          grepl("priority f$", names(attr(uk$src_1_attribut5_1, "labels"))[1]))
anames <- c("institutional_experience", "extrainstitutional_experience", "reason_for_running",
            "migration_position", "environment_position")
refuse <- "^(Prefer not to say|Skipped$|Not Asked$)"
out_l <- list(); off <- 0L
for (cc in names(files)) {
  x <- read_sav(file.path(raw, paste0(files[[cc]], "_PoP.sav")))
  pv <- as.character(as_factor(x[[vote[[cc]]]], levels = "labels"))
  if (cc == "GB") { ni <- as.character(as_factor(x$UK19_ni, levels = "labels")); pv[is.na(pv)] <- ni[is.na(pv)] }
  pv[grepl(refuse, pv)] <- NA
  for (t in 1:5) for (p in 1:2) {
    ch <- as.integer(x[[paste0("cjchoice_", t)]])
    r <- data.table(src = as.integer(x$ID), task = t, profile = p, choice = as.integer(ch == p),
                    rating = as.integer(x[[paste0("cjrating_", t, "_", p)]]))
    for (k in 1:5) {
      v <- as.integer(x[[paste0("src_", t, "_attribut", k, "_", p)]])
      stopifnot(all(v %in% 1:3))
      r[, (paste0("attr_", anames[k])) := eng[[k]][as.character(v)]]
    }
    r[, `:=`(cov_country = cc, cov_past_vote = pv, cov_survey_weight = as.numeric(x$W8))]
    out_l[[length(out_l) + 1]] <- r
  }
}
d <- rbindlist(out_l)
d[, id := match(paste(cov_country, src), unique(paste(cov_country, src)))][, src := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
stopifnot(uniqueN(d$id) == 10347, d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 1:7))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "mercea_2025_movement_parties.csv"))
