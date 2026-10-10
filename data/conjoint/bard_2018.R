##Neuroenhancement contrastive-vignette experiments (10 European countries + USA, 2016) from
##Bard, I., Gaskell, G., Allansdottir, A., da Cunha, R. V., Eduard, P., Hampel, J., Hildt, E.,
##Hofmaier, C., Kronberger, N., Laursen, S., Meijknecht, A., Nordal, S., Quintanilha, A.,
##Revuelta, G., Saladié, N., Sándor, J., Santos, J. B., Seyringer, S., Singh, I., Somsen, H.,
##Toonders, W., Torgersen, H., Torre, V., Varju, M., & Zwart, H. (2018). Bottom up ethics -
##Neuroenhancement in education and employment. Neuroethics, 11(3), 309-322.
##https://doi.org/10.1007/s12152-018-9366-7
##Data: Zenodo record 1166066, doi:10.5281/zenodo.1166066, CC BY 4.0 (record licence; the
##record has no README). File read: bottom_up_ethics.sav (11,716 rows, one per respondent;
##SPSS value labels). Design and wording: the article (PMC6132847), Methods and Box 1.
##Usage: Rscript bard_2018.R <raw dir> <output dir>
##
##Online quota samples (~1,000 per country), Jan-Feb 2016, Respondi access panels (Austria,
##Denmark, Germany, Hungary, Italy, Netherlands, Portugal, Spain, UK, USA) and Gallup (Iceland);
##Qualtrics; national-language translations of an English master. N = 11,716, as in the article.
##Each respondent read TWO vignettes, one about employment and one about education ("The order
##of presentation of the two contexts was randomised"; the order is NOT in the data). Each
##vignette is a 2x2x2x2 factorial (16 versions), factors drawn at random per context:
##  gender of the protagonist (shown through a first name, "Paul/Jack/Emily/Sarah", adapted to
##    local equivalents; the data hold only the authors' gender coding),
##  enhancer (a pill / a device delivering "tiny electrical currents"; authors' labels Pill/tDCS),
##  performance (employment: work "met / failed to meet the company's expectations"; education:
##    results "good / below average"; authors' labels Good performance / Failing performance),
##  efficacy (about 10% / about 50% improvement; authors' labels Low / High efficacy).
##ONE TABLE, bard_2018_neuroenhancement: the same four factors in two contexts answered by the
##same respondents, with the authors' (context-free) level labels. task 1 = employment vignette,
##task 2 = education vignette (task = context, NOT display order), trial_context names it;
##profile = 1. Countries pooled with cov_country (the article analyses the pooled sample; the
##level labels are the same in every country).
##Outcome: rating = "In (name of protagonist)'s shoes, would you make the same choice?" (EmpShoes,
##EduShoes), an 11-point scale that the article describes as -5 to +5; the deposit stores 0-10,
##kept raw. Higher = more willing (the article reports higher efficacy and lower performance
##raise willingness, and the 0-10 means move that way). End labels are not given.
##Covariates: cov_country (Country label), cov_gender (Female 1/0 = female/male, value labels),
##cov_age_group (age_grp), cov_uni_degree (unieduc label), and the 14 attitude claims asked after
##both vignettes, 0-10 raw (claim wording in the .sav variable labels, -5..+5 strongly disagree..
##strongly agree in the article) as cov_claim_<name>. Dropped: country and age dummies, the
##condition codes EmpCond/EduCond (same information as the factors), the PCA scales scale1/2.
##No respondent ID in the deposit: id = row order. No weight.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- read_sav(file.path(raw, "bottom_up_ethics.sav"))
stopifnot(nrow(x) == 11716L)
lab <- function(v) trimws(as.character(as_factor(v, levels = "labels")))
num <- function(v) as.integer(zap_labels(v))
mk <- function(pre, t, ctx) {
  d <- data.table(id = seq_len(nrow(x)), task = t, profile = 1L, rating = num(x[[paste0(pre, "Shoes")]]),
                  trial_context = ctx,
                  attr_gender = lab(x[[paste0(pre, "Male")]]), attr_enhancer = lab(x[[paste0(pre, "Pill")]]),
                  attr_performance = lab(x[[paste0(pre, "Good")]]), attr_efficacy = lab(x[[paste0(pre, "High")]]))
  ## the 16-condition code must agree with the four factor columns
  cond <- lab(x[[paste0(pre, "Cond")]])
  g <- ifelse(substr(cond, 1, 1) == "M", "Male", "Female")
  stopifnot(all(g == d$attr_gender), all(grepl("Pill", cond) == (d$attr_enhancer == "Pill")),
            all(grepl("High performance", cond) == (d$attr_performance == "Good performance")),
            all(grepl("High efficacy", cond) == (d$attr_efficacy == "High efficacy")))
  d
}
d <- rbind(mk("Emp", 1L, "employment"), mk("Edu", 2L, "education"))
stopifnot(!anyNA(d), all(d$rating %in% 0:10))
claims <- c("naturalability", "transgress", "achievement", "fascinating", "copedemands", "wayout", "control",
            "onlymedical", "protection", "commercial", "neverkids", "NE2all", "competition", "cohesion")
cv <- data.table(id = seq_len(nrow(x)), cov_country = lab(x$Country),
                 cov_gender = c("male", "female")[match(num(x$Female), 0:1)],
                 cov_age_group = lab(x$age_grp), cov_uni_degree = lab(x$unieduc))
for (v in claims) cv[, paste0("cov_claim_", tolower(v)) := num(x[[v]])]
d <- merge(d, cv, by = "id")
setcolorder(d, c("id", "task", "profile", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bard_2018_neuroenhancement.csv"))
