##2x2x3 factorial news-release vignette on an autocratizing proposal and elite democratic defence (NL, DE, FR), from
##van Lit, J., & Meijers, M. J. (2025). Defending democracy: Investigating the efficacy of elite democratic defence in a competitive
##information environment. West European Politics. https://doi.org/10.1080/01402382.2025.2525601
##Replication data: Harvard Dataverse doi:10.7910/DVN/RFC3WQ, CC BY 4.0, no restricted files. Files read: demojudges.tab
##(downloaded with format=original; a CSV), data preparation.R and main.R (as text). Wording of the treatments and outcomes from
##chapter 6 (sections 3.1-3.3) of van Lit (2025), Beautiful Spark of Democracy (Radboud University, open access,
##doi:10.54195/9789465150840), the same experiment; the vignette image (Figure 6.2) is not machine-readable.
##Usage: Rscript vanlit_2025.R <dir holding demojudges.tab> <output dir>
##
##9,672 respondents in the Netherlands (3,107), Germany (3,395) and France (3,170), one news-release vignette each (each row is a
##respondent; id = row number; ResponseId dropped), randomly one of 12 treatment groups (about 800 each): Norway's prime minister
##proposes a new organization (members appointed by the PM) with, depending on the arm, the power to withdraw public broadcasters'
##media licences or to dismiss Supreme Court judges. Attributes (data columns action, justification, demdef):
##  attr_action: media / judiciary; attr_justification: none (not shown) / corruption (the proposal is needed to combat rising
##    corruption in the [media/judiciary]) / self-serving (the proposal is needed to increase the government's control over the
##    [media/judiciary]); attr_democratic_defence: none (not shown) / the Supreme Court has issued a strongly negative opinion,
##    opposing the proposal.
##LABELS: paraphrased from the thesis chapter (Section 3.1.1); the verbatim vignette sentences are in an image (Figure 6.2) and the
##deposit's scripts. The three countries are pooled as the authors do (cov_country); the level text is the
##English paraphrase shared by all, while respondents saw their national language.
##Outcomes: rating = dv_eval, "To what extent do you think this action would make Norway more or less democratic?", 7-point,
##higher = more democratic; rating_ambiguity = dv_ambi, "what do you personally think is more important in a democratic country?"
##six options between fighting corruption / that the government is in control (raw 1) and that judges cannot be easily dismissed /
##that media licences cannot easily be withdrawn (raw 6): STORED as in the deposit, after the authors' reversal in data
##preparation.R (stored 6 = the corruption/government-control end, labelled by the authors 'higher = more ambiguity');
##rating_defender_credibility = dv_cred, "if you had to choose, what is the most likely motivation of the Supreme Court behind their
##opinion on the new organization?" 6 options, stored reversed so that higher = more committed to democracy (more credible); asked
##only of respondents who saw a democratic defence, and (coding error per the thesis) only in the Netherlands (1,544 answers).
##Not built: the seven-item protest/participation battery (dv_protest*, post_agree) and manipulation checks.
##Covariates: cov_country, cov_gender (man/woman -> male/female), cov_birth_year, cov_education_level (authors' high/medium/low
##grouping), cov_survey_weight (weight, NA for 286). Dropped: StartDate/EndDate/RecordedDate/ResponseId, income, geo, employment
##dummies, vote, trust/attitude batteries, age bands, derived scales.
##Count check: 12 groups x ~750 per the thesis = about 9,000; file 9,672 (article N not read).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "demojudges.tab"), na.strings = c("NA", ""))
stopifnot(nrow(d) == 9672, !anyNA(d[, .(action, justification, demdef, dv_eval)]), nrow(unique(d[, .(action, justification, demdef)])) == 12)
d[, id := .I]
tg <- ifelse(d$action == "media", "the media", "the judiciary")
act <- c(media = "Proposal to create a new organization, with members appointed by the prime minister, that has the power to withdraw the licences of public broadcasters",
         judiciary = "Proposal to create a new organization, with members appointed by the prime minister, that has the power to dismiss Supreme Court judges")
just <- ifelse(d$justification == "none", "(not shown)",
        ifelse(d$justification == "corruption", paste0("The proposal is needed to combat rising corruption in ", tg), paste0("The proposal is needed to increase the government's control over ", tg)))
r <- data.table(id = d$id, task = 1L, profile = 1L, rating = as.integer(d$dv_eval), rating_ambiguity = as.integer(d$dv_ambi),
  rating_defender_credibility = as.integer(d$dv_cred),
  attr_action = unname(act[d$action]), attr_justification = just,
  attr_democratic_defence = ifelse(d$demdef == "yes", "Norway's Supreme Court has issued a strongly negative opinion, opposing the proposal", "(not shown)"),
  cov_country = d$country, cov_gender = c(man = "male", woman = "female")[d$sex], cov_birth_year = as.integer(d$byear),
  cov_education_level = d$edu, cov_survey_weight = as.numeric(d$weight))
print(r[, .N, .(substr(attr_action, 70, 90), substr(attr_justification, 1, 40), substr(attr_democratic_defence, 1, 20))])
print(summary(r$cov_birth_year)); print(r[, .N, cov_country]); print(r[!is.na(rating_defender_credibility), .N, cov_country])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "vanlit_2025_democratic_defence.csv")); cat("rows", nrow(r), "\n")
