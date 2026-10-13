##Food-waste tendency vignette conjoint (Minnesota State Fair, 2016) from
##Dusoruth, V., & Peterson, H. H. (2020). Food waste tendencies: Behavioral response to cosmetic
##deterioration of food. PLOS ONE, 15(5), e0233287. https://doi.org/10.1371/journal.pone.0233287
##Replication data: Peterson, H. H. (2020). D2D 2016 Food Study. Data Repository for the
##University of Minnesota, doi:10.13020/0m0p-tt02, CC0 1.0. Files read: D2D2016FoodStudy_data.csv
##(saved as data.csv), D2D2016FoodStudy_definition.csv, Readme.txt. The attribute descriptions
##and the outcome wording come from the PLOS ONE article (read on the journal site), because the
##deposit only has variable labels. Usage:
##  Rscript dusoruth_2020_food_waste.R <dir holding data.csv> <output dir>
##
##333 visitors of the 2016 Minnesota State Fair (the article reports N = 333) answered a
##tablet survey with two blocks of four product scenarios (8 scenarios; one block ground beef
##and one packaged fresh spinach; non-meat eaters saw two spinach blocks; 38 respondents have
##no beef rows). Each scenario shows ONE product (profile = 1), so the table is single-profile:
##task = row order within respondent (INFERRED from file order: no task column; beef block first
##for everyone as far as the file shows; the order within a block is not documented). Four
##respondents have 7 rows (README: 2,661 rows, the file has 2,660; 2 respondents have 3 beef
##rows) - kept as is.
##Outcome (rating, no choice): the authors ask "what percentage of this product are you and/or
##your household likely to eat" (0-100% slider; article wording) and store percent_discard
##= food waste tendency (score 0-100; the article defines it as 100 minus the percentage
##likely to eat). HIGHER = more discarding (less favourable); stored raw, 0-100, as in the file.
##Attributes (12 orthogonal fractional-factorial profiles per product in three blocks of four):
##  product: Ground beef / Spinach (beef = 1);
##  appearance: three levels of cosmetic deterioration shown as PHOTOGRAPHS (Fig 1 of the
##    article; the image sets are on request): level 1 shows no flaws, levels 2 and 3 show
##    increasing flaws (browning for beef; blemishes, spots, wilting for spinach). The text
##    stored is a description of the image, not displayed text.
##  date label: "Best by" (bestby = 1), "Use by" (useby = 1), else "Best if used by" (the third
##    level named in the article; assigned when both dummies are 0);
##  days to expiration (beef 1, 2, 3 days; spinach 1, 3, 7 days);
##  package size: beef 1 lb / 2 lb; spinach 5 oz / 10 oz (small/large mapping from the article);
##  price per package (USD, rounded to cents: 6 price points per product, 12 in all).
##No combination restriction is stated beyond the orthogonal design; level weights are not
##stated (counts are near-equal).
##Covariates: cov_age_midpoint (the deposit stores the centre of the age band: 21, 29.5, ...,
##84.5; not an exact age), cov_income_10k (household income in $10,000s, as stored; band
##centres), cov_household_size. Not kept: the authors' dummies (female with other recoded 0,
##bachelor's, children, nonwhite), the latent class and the survey-item batteries.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "data.csv"))
stopifnot(nrow(s) == 2660, uniqueN(s$person_id) == 333, s[, all(percent_discard %in% 0:100)],
          s[, all(bestby + useby <= 1)], s[, all(level2 + level3 <= 1)])
s[, id := as.integer(factor(person_id, levels = unique(person_id)))][, task := seq_len(.N), id]
d <- s[, .(id, task = as.integer(task), profile = 1L, rating = as.integer(percent_discard),
  attr_product = fifelse(beef == 1, "Ground beef", "Spinach"),
  attr_appearance = fifelse(level2 == 1, "Level 2 (image: some flaws)", fifelse(level3 == 1, "Level 3 (image: more flaws)", "Level 1 (image: no flaws)")),
  attr_date_label = fifelse(bestby == 1, "Best by", fifelse(useby == 1, "Use by", "Best if used by")),
  attr_days_to_expiration = paste(date_days, fifelse(date_days == 1, "day", "days")),
  attr_package_size = fifelse(beef == 1, fifelse(large == 1, "2 lb", "1 lb"), fifelse(large == 1, "10 oz", "5 oz")),
  attr_price = sprintf("$%.2f", price),
  cov_age_midpoint = age, cov_income_10k = income, cov_household_size = as.integer(hhld_size))]
stopifnot(d[, uniqueN(attr_price)] == 12, !anyNA(d))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dusoruth_2020_food_waste.csv"))
