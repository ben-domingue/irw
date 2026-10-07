##Consumer product choice conjoint (country of origin) from
##Bankert, A., Powers, R., & Sheagley, G. (2023). Trade politics at the checkout lane:
##Ethnocentrism and consumer preferences. Political Science Research and Methods, 11(3),
##605-612. https://doi.org/10.1017/psrm.2022.40
##Replication data: Harvard Dataverse doi:10.7910/DVN/3TGWGG, CC0 1.0. File read:
##final_w1w2.dta (Dataverse "original format" download). Design details (base prices, the
##example task) from the article's online appendix (Cambridge supplementary .docx, Table A3
##and Figure A1); no code from the deposit was run.
##Usage: Rscript bankert_2023.R <dir holding final_w1w2.dta> <output dir>
##
##bankert_2023_consumer_origin: the wave-2 conjoint of a two-wave Bovitz/Forthright US panel
##  (June 2020). 996 respondents (the paper says 995 in the text and 996 in Table A1), each
##  10 tasks of 2 products (rows of the 543 wave-1-only respondents, who never saw the
##  conjoint, are dropped). 4 attributes as in Figure A1: product (12 products, the same
##  product on both profiles of a task, no product repeated within respondent), average
##  rating from past customers ("3/4/5 out of 5 stars"), price, and "Product made in"
##  (United States, Germany, China, "A country outside the United States").
##  Price: the deposit holds only the mark-up (0, 25, 50, 100 percent over the product's
##  baseline price). The displayed dollar price is rebuilt as baseline x (1 + mark-up), rounded
##  to the cent, with the baselines from appendix Table A3 (butter $3.00, cheese $3.50, coffee
##  $7.00, paper towels $4.00, detergent $12.00, skillet $30.00, toaster $30.00, microwave
##  $100.00, washing machine $500.00, super glue $6.00, duct tape $7.50, screen protector
##  $8.50); Figure A1 shows "$4.38" for cheese at +25%, which this reproduces. Whether the
##  survey printed $1000.00 with a thousands separator is not documented. The mark-up (what the
##  authors analyse) is not stored: it is recoverable from product and price.
##  Outcome: choice = profile_chosen, "If you had to purchase one of the products above, which
##  one would it be?" (Product A / Product B, forced, no opt-out). Five tasks with no answer are
##  omitted. The follow-up 5-point purchase-likelihood rating shown in Figure A1 is NOT in the
##  deposit.
##  PROFILE POSITION IS NOT RECORDED: the deposit has no Product A/B column and the two rows of
##  a task are not adjacent in the file. profile here is the order of the two rows in the
##  source file, which may not be the screen position; do not use it for position effects.
##  Attribute order fixed as in Figure A1 (no attrpos_). Randomization restrictions: none
##  documented beyond the product rule above.
##  Covariates (deposit codes; the deposit carries no value labels except educ and pid3):
##  cov_age (years), cov_gender (1/2, undocumented), cov_race (1-7, undocumented), cov_educ
##  (1 HS or less ... 5 prof degree/PhD as labelled), cov_income (1-?, undocumented),
##  cov_pid3_lean (wave-2, 1 Democrat 2 Pure Independent 3 Republican as labelled),
##  cov_ft_* (0-100 wave-1 feeling thermometers toward the US, China, Mexico, UK, Germany,
##  Japan, Puerto Rico), cov_ethno1..6 (wave-1 ethnocentrism items, 1-5, wording not in the
##  deposit). Dropped: the authors' ethnocentrism scale and bins, college dummy, wave-1 pid,
##  undocumented items q2/q5/q11_*/q22/Q14_*, the *_cat recodes.
##  The Lucid replication (lucid_formatted.dta, 1,117 ids, countries US/Canada/Japan/China/
##  India) is NOT built: it carries no product column, so the displayed price cannot be rebuilt.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(zap_labels(read_dta(file.path(raw, "final_w1w2.dta"))))
k[, r := .I]
m <- k[is.na(wave1_only)]
stopifnot(uniqueN(m$id) == 996, m[, .N, .(id, task_num)][, all(N == 2)], m[, uniqueN(product), .(id, task_num)][, all(V1 == 1)])
m <- m[!is.na(profile_chosen)]
base <- c("1 pound of butter" = 3, "1 pound of cheese" = 3.5, "1 pound of coffee" = 7, "4 rolls of paper towels" = 4,
          "96 oz laundry detergent" = 12, "12-inch non-stick skillet" = 30, "Toaster" = 30, "Microwave" = 100,
          "Washing Machine" = 500, "Small bottle of super glue" = 6, "Roll of black duct tape" = 7.5,
          "Cell phone screen protector" = 8.5)
stopifnot(all(m$product %in% names(base)), all(m$mark_up %in% c(0, .25, .5, 1)))
setorder(m, id, task_num, r)
cents <- floor(base[m$product] * (1 + m$mark_up) * 100 + 0.5 + 1e-6)
d <- m[, .(id = as.integer(id), task = as.integer(task_num), choice = as.integer(profile_chosen),
           attr_product = product, attr_rating = rating, attr_price = sprintf("$%.2f", cents / 100),
           attr_country = country,
           cov_age = as.integer(age), cov_gender = as.integer(gender), cov_race = as.integer(race), cov_educ = as.integer(educ),
           cov_income = as.integer(inc), cov_pid3_lean = as.integer(pid3_lean_w2),
           cov_ft_us = ft_us, cov_ft_china = ft_china, cov_ft_mexico = ft_mexico, cov_ft_uk = ft_UK, cov_ft_germany = ft_germ,
           cov_ft_japan = ft_japan, cov_ft_puerto_rico = ft_PR,
           cov_ethno1 = ethno1, cov_ethno2 = ethno2, cov_ethno3 = ethno3, cov_ethno4 = ethno4, cov_ethno5 = ethno5, cov_ethno6 = ethno6)]
d[, profile := seq_len(.N), .(id, task)]
setcolorder(d, c("id", "task", "profile"))
stopifnot(any(d$attr_price == "$4.38"), uniqueN(d[, .(attr_product, attr_price)]) == 48)
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 19910)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bankert_2023_consumer_origin.csv"))
