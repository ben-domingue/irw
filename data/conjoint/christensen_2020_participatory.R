##Participatory-process conjoint (Finland) from
##Christensen, H. S. (2020). How citizens evaluate participatory processes: A conjoint analysis.
##European Political Science Review, 12(2), 239-253. https://doi.org/10.1017/S1755773920000107
##Replication data: OSF project "evaluating democratic innovations", https://osf.io/cjn6u/
##(doi:10.17605/OSF.IO/CJN6U), CC BY 4.0 (node licence). File read: Researchdata.dta (the .csv twin
##is the same data). Design facts below come from the SocArXiv preprint of the article
##(osf.io/preprints/socarxiv/5t72a), Table 1 and pp. 6-8.
##Usage: Rscript christensen_2020_participatory.R <dir holding Researchdata.dta> <output dir>
##
##1,050 Finnish adults (Qualtrics online panel, quotas on age, gender, place of living), 5 comparisons of
##two participatory processes each = 10,500 rows, as in the article. Respondents indicated which
##alternative they prefer; forced choice, exactly one chosen per pair (checked). choice = `choice`.
##Seven attributes. The survey text shown to respondents (presumably Finnish) is not deposited; levels are
##stored as the English wording of the article's Table 1 (level text after the attribute stem), mapped from
##the .dta value labels:
##  policy issue ("The decision concerns..."), inclusiveness ("The participants are..."), efficiency
##  ("The process involves the following number of gatherings"), transparency ("All gatherings in the
##  process..."), transferability ("All gatherings take place..."), considered judgement ("Participants
##  make up their minds based on..."), popular control ("After reaching a decision, the outcome will...").
##The article's "(Easy)/(Hard)" issue tags and "RF" reference marks are analysis labels and not stored.
##"No restrictions were added to the randomization" (preprint p. 8); footnote 5: "The ordering differed in
##the actual presentations in Qualtrics to make the alternatives more intuitive" (attribute order fixed but
##not the Table 1 order). No survey weight.
##task: `id` numbers the comparisons consecutively within respondent (respid); task = rank of id within
##respid (inferred from id order). profile = row order within id (inferred; the file has no position
##column). Both checked: every respondent has 5 ids of 2 rows each.
##Dropped: procesprefdiko (the authors' dichotomized process-preference item; the 0-10 source item is not
##deposited). Respondent ids = respid (integers).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- read_dta(file.path(raw, "Researchdata.dta"))
stopifnot(nrow(r) == 10500, length(unique(r$respid)) == 1050)
d <- data.table(id = as.integer(r$respid), pair = as.integer(r$id), choice = as.integer(r$choice), row = seq_len(nrow(r)))
txt <- list(
  at1policy = c("Vegan food in schools", "Wolf protection", "Regional government reforms",
                "Measures to ensure long-term sustainable economic growth"),
  at2inclu = c("All citizens willing to take part", "A group of citizens selected to reflect the general population",
               "Key stakeholders with an interest in the topic"),
  at3effic = c("A single instance", "2-5 instances", "6-10 instances"),
  at4transp = c("take place behind closed doors to allow for sensitive discussions",
                "are open to the public to allow for public scrutiny"),
  at5transfer = c("online via official government platform", "in a public building"),
  at6judg = c("Their own judgement and preferences", "Credible information from independent experts before deciding",
              "a moderated exchange of arguments between participants"),
  at7contr = c("be implemented directly", "serve as advice to elected officials who make the final decision"))
## value labels these replace, in code order (checked below)
vl <- list(at1policy = c("Vegan meals in schools", "Protection of wolves", "Regional government reforms", "Long-term economic growth"),
           at2inclu = c("All willing to take part", "Representative sample", "Key stakeholders"),
           at3effic = c("A single instance", "2-5 instances", "6-10 instances"),
           at4transp = c("Behind closed doors", "Open to public"), at5transfer = c("Online", "Offline"),
           at6judg = c("Own judgement", "Expert information", "Moderated discussions"),
           at7contr = c("Directly implemented", "Advisory"))
nm <- c(at1policy = "policy_issue", at2inclu = "inclusiveness", at3effic = "efficiency", at4transp = "transparency",
        at5transfer = "transferability", at6judg = "considered_judgement", at7contr = "popular_control")
for (v in names(txt)) {
  lab <- attr(r[[v]], "labels"); stopifnot(identical(unname(names(lab)[order(lab)]), vl[[v]]), identical(as.integer(unname(sort(lab))), seq_along(vl[[v]])))
  d[, paste0("attr_", nm[v]) := txt[[v]][as.integer(zap_labels(r[[v]]))]]
}
stopifnot(!anyNA(d))
d[, task := frank(pair, ties.method = "dense"), by = id]
d[, profile := seq_len(.N), by = .(id, pair)]
stopifnot(d[, .N, .(id, pair)][, all(N == 2)], d[, uniqueN(pair), id][, all(V1 == 5)],
          d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, all(diff(row) == 1L), .(id, pair)][, all(V1)])
d[, c("pair", "row") := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "christensen_2020_participatory.csv"))
