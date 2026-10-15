##Glyphosate policy choice experiment (France), cost-vector treatment, from
##Martinet, V., David, M., Mermet-Bijon, V., & Crastes dit Sourd, R. (2025). Cost vector effects in forced-choice
##discrete choice experiments: Assessing the acceptability of future glyphosate policies. Journal of Choice Modelling.
##https://doi.org/10.1016/j.jocm.2025.100550 (article not read; N not compared: 1,000 respondents here).
##Data: Recherche Data Gouv doi:10.57745/0VNN1B (v2), licence Etalab 2.0 (Dataverse record license field).
##Files read: database.tab (Dataverse tab export of database.csv), the authors' Apollo script "Glypho2 - MMNL - 2c ana -
##ln - B3.R" (as text: survey1 == 0 is block B3) and the choice-card PNGs B3_1..B3_8 / B4_1 (viewed as images) and
##Script_French.docx (survey text, as text).
##Usage: Rscript martinet_2025.R <dir holding database.tab> <output dir>
##
##1,000 French adults (online), 6 forced choices each (CT 1..6) among three options: option 1 = a total BAN of
##glyphosate (100% reduction, price +3 EUR/week in block B3, +4 EUR in B4; no tax revenue), options 2 and 3 = a
##TAX on glyphosate with a reduction of the farmers' glyphosate use (75/85/95%), a rise in the weekly food basket
##price (+1/+2/+3 EUR per week) and a use of the tax revenue. No opt-out ("Quelle est votre option préférée?").
##Option 1's instrument (ban) and options 2-3 (tax) are fixed by position and not stored as an attribute.
##Treatment: the cost vector (price levels) differs between two blocks: B3 (survey1 = 0, ban costs +3, tax prices
##1-2) and B4 (survey1 = 1, ban costs +4, tax prices 1-3), 500 respondents each, stored in trial_cost_vector; the
##authors pool them in the "Pooled2" scripts, level text identical.
##Attributes (French, as on the cards): reduction of glyphosate use by farmers (%); rise in the price of your food
##basket ("+N€ par semaine"; the data store N); use of the tax revenue (the four dummies env/health/budg/farmers:
##"Programme environnemental", "Programme de santé", "Augmentation du budget général de l'Etat", "Aide additionnelle
##aux agriculteurs"; option 1: "Il n'y a pas de revenu de la taxe (interdiction du glyphosate)"). red is stored as the
##deviation from 100 (-15 -> 85%); verified against cards B3_1 to B3_5 and B4_1 (e.g. B3_1 option 2: 85%, +1€, farmers aid).
##Restrictions (observed): exactly one revenue use per tax option; B3 reduction/price pairs 95% +2, 85% +1, 75% +1/+2.
##Level weights: unknown. Task order = CT (recorded); profile = option position.
##Covariates: cov_age (years), cov_gender_code (0/1) and cov_education_code (1-3): no codebook ships, codes kept.
##Dropped: the other survey items, lexico_cost and always_sq flags, rankings and benchmark answers.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "database.tab"))
stopifnot(nrow(x) == 6000, uniqueN(x$ID) == 1000, x[, .N, ID][, all(N == 6)], all(x$choice %in% 1:3))
use <- function(env, health, budg, farm, k) {
  if (k == 1) return(rep("Il n'y a pas de revenu de la taxe (interdiction du glyphosate)", length(env)))
  stopifnot(all(env + health + budg + farm == 1))
  fifelse(env == 1, "Programme environnemental", fifelse(health == 1, "Programme de santé",
      fifelse(budg == 1, "Augmentation du budget général de l'Etat", "Aide additionnelle aux agriculteurs")))
}
long <- rbindlist(lapply(1:3, function(k) {
  g <- function(n) x[[paste0(n, k)]]
  if (k == 1) { env <- health <- budg <- farm <- rep(0L, nrow(x)) } else { env <- g("env"); health <- g("health"); budg <- g("budg"); farm <- g("farmers") }
  data.table(id = x$ID, task = x$CT, profile = k, choice = as.integer(x$choice == k),
    attr_glyphosate_reduction = paste0(100 + g("red"), "%"),
    attr_food_basket_price_rise = paste0("+", g("price"), "€ par semaine"),
    attr_tax_revenue_use = use(env, health, budg, farm, k),
    trial_cost_vector = c("B3", "B4")[x$survey1 + 1L],
    cov_age = as.integer(x$age), cov_gender_code = x$gender, cov_education_code = x$education)
}))
stopifnot(!anyNA(long), long[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(long, id, task, profile)
fwrite(long, file.path(out, "martinet_2025_glyphosate_policy.csv"))
