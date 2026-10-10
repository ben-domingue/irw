##Universal basic income (UBI) design conjoint (Germany) from
##Becker, B., & Schwander, H. (2025). Who wants what, and why? Attitude polarization and political
##viability of UBI. Journal of European Social Policy. https://doi.org/10.1177/09589287251400044
##Replication data: Harvard Dataverse doi:10.7910/DVN/6EBZTP, CC0 1.0. Files read:
##replication_data.Rdata (an RDS file despite the name: one wide data.frame, 3,076 respondents x 96)
##and replication_script.Rmd (read as text; source of attribute names and the 0-10 recode).
##No questionnaire or codebook ships and the article could not be read: outcome wording is a
##PARAPHRASE.
##Usage: Rscript becker_2025_basic_income.R <dir holding replication_data.Rdata> <output dir>
##
##3,076 German respondents (online survey; the Rmd describes no panel or dates; the source IDs are
##mixed panel/platform strings and are re-keyed to 1..N), 5 tasks, each a pair of UBI proposals
##("Vorschlag A" / "Vorschlag B"), 6 attributes as German text in the data (VGL_<task><A|B>_<k>):
##  attr_citizenship (k=1: Alle / EU-Staatsbürger / Deutsche Staatsbürger), attr_residence (k=2:
##  Keine / Ein Jahr / Fünf Jahre), attr_jurisdiction (k=3: Deutschland / Hamburg), attr_requirements
##  (k=4: 4 levels), attr_generosity (k=5: monthly amount with its reference, e.g. "550€ (angelehnt
##  an Bürgergeld-Regelsatz)"), attr_financing (k=6: 4 levels). Names follow the authors' Rmd.
##task = t of VGL_t?, profile = A (1) / B (2): RECORDED.
##Outcomes (both asked of every pair):
##  choice: which proposal the respondent prefers (v_16_t, "Vorschlag A"/"Vorschlag B"; forced
##    choice, no opt-out) (paraphrase).
##  rating: support for each proposal, 0 "(0) Auf keinen Fall" (not at all) to 10 "(10) Voll und
##    ganz" (completely) (v_17_t for A, v_18_t for B; integer taken from the label as in the Rmd;
##    higher = more support) (paraphrase).
##Restrictions/level weights/attribute order are not documented; level shares look equal.
##Covariates: cov_gender (männlich -> male, weiblich -> female, divers -> other), cov_age (years as
##stored), cov_vote_intention (answer text; "ohne Angabe" -> NA; the deposit's partyID_en is the same
##variable in English and is left out; this is vote intention, not party ID), cov_income_cat
##(individual income band as stored), cov_ubi_support3 (the authors' grouping into Opponents /
##Indifferent / Proponents, their main moderator; source question not deposited). The open-text
##argument recodes (pro_*/con_*) are dropped.
##Spot-check: choice marginal mean of 2,300EUR generosity (cregg mm, printed below).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "replication_data.Rdata")))
stopifnot(nrow(x) == 3076, uniqueN(x$ID) == 3076)
x[, id := seq_len(.N)]
nm <- c("citizenship", "residence", "jurisdiction", "requirements", "generosity", "financing")
num <- function(f) as.integer(sub("^\\((\\d+)\\).*", "\\1", as.character(f)))
d <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:2, function(p) {
  ab <- c("A", "B")[p]
  y <- x[, c("id", paste0("VGL_", t, ab, "_", 1:6), paste0("v_16_", t), paste0(c("v_17_", "v_18_")[p], t)), with = FALSE]
  setnames(y, c("id", paste0("attr_", nm), "ch", "rt"))
  for (v in paste0("attr_", nm)) set(y, j = v, value = as.character(y[[v]]))
  y[, `:=`(task = t, profile = p, choice = as.integer(as.character(ch) == paste("Vorschlag", ab)), rating = num(rt))]
  y[, c("ch", "rt") := NULL]
}))))
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$rating %in% 0:10))
cv <- x[, .(id, cov_gender = c(männlich = "male", weiblich = "female", divers = "other")[as.character(gender)],
            cov_age = as.integer(age),
            cov_vote_intention = fifelse(vote_intention == "ohne Angabe", NA_character_, as.character(vote_intention)),
            cov_income_cat = as.character(income_ind_cat), cov_ubi_support3 = as.character(ubi_support3))]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
cat("rows", nrow(d), "respondents", uniqueN(d$id), "\n")
print(d[, .(mm_choice = round(mean(choice), 3), mean_rating = round(mean(rating), 2)), attr_generosity])
fwrite(d, file.path(out, "becker_2025_basic_income.csv"))
