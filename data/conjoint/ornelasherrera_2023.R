##Circular-farming food labels choice experiment (N2C project) from
##Ornelas Herrera, S. I., & Kallas, Z. (2023). European consumers' preference and willingness to pay for food products labelled as obtained by
##a circular farming system - in relation to environmental attitudes and consumption behaviours [Data set]. Zenodo (CREDA-UPC-IRTA, N2C project). No article DOI.
##Deposit: Zenodo doi:10.5281/zenodo.8338014 (version record; concept DOI 10.5281/zenodo.8338013), CC BY 4.0 (record licence cc-by-4.0).
##Files read: "N2C_Consumers WTP.csv" (semicolon-separated, UTF-8 BOM) and N2C_Consumers_Readme.xlsx (sheet 2, the codebook, read as XML text).
##Usage: Rscript ornelasherrera_2023_circular_farming.R <dir holding the two files> <output dir>
##
##5,362 consumers in Belgium, Croatia, Hungary, Italy, Poland and Spain (cov_country; Q = online questionnaire in 7 languages). Each respondent
##answered, for each product they purchase (pork, cows' milk, sliced bread), 4 purchase situations: choose among three labelled products
##(Organic / Conventional / Circular farming, each with a price) or "None of these". Tasks 1-4 = pork (Q3.2-3.5), 5-8 = milk (Q6.2-6.5),
##9-12 = bread (Q9.2-9.5), numbered in survey order; tasks of a product the respondent does not purchase (code 0 = not asked; Q2.2/Q5.2/Q8.2 = No)
##are absent. Fixed design: all respondents saw the same 4 sets per product (prices in the codebook D-column text). Profiles 1-3 are the codebook
##option codes 1 Organic, 2 Conventional, 3 Circular; "None of these" (code 4) has no levels, so it is the opt-out (no profile row, choice = 0 on all).
##Attributes: attr_farming_system (the alternative's label) and attr_price (codebook text, euro sign written as EUR: "EUR 18.00 per 500g"; milk per 1 liter,
##bread per 450g). trial_product = pork / milk / bread. Restrictions and level weights: unknown.
##Outcome: choice = "WHICH PRODUCT WOULD YOU prefer to buy?" Purchase situation k (codebook Q3.2...).
##Covariates (codebook sheet 2): cov_country (Country code list), cov_gender (1 Male, 2 Female, 3 Other), cov_age_group (age code list; code 1 never occurs),
##cov_education (Q16.6 answer list), cov_birth_year (Q16.1, plausible 1920-2010 else NA). Respondent id = the record identifier IDT (unique; the
##"ID" column repeats across countries and is dropped). Dropped: the open-ended quantity questions at each price (OCE), attitude batteries, diet,
##leftovers, employment, income, household and the authors' derived attitude scores, free text. No survey weight in the deposit. Article not identified,
##so N is not checked against a paper.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "N2C_Consumers WTP.csv"), sep = ";", encoding = "UTF-8")
stopifnot(nrow(d) == 5362, uniqueN(d$IDT) == 5362)
sets <- list(
  pork  = list(cols = paste0("Q3.", 2:5),  p = rbind(c(18, 8, 9), c(12, 7, 8), c(16, 6, 7), c(14, 5, 10)), u = "500g", f = "%.2f"),
  milk  = list(cols = paste0("Q6.", 2:5),  p = rbind(c(1.6, .9, 1), c(1.7, 1.1, 1.2), c(1.4, 1, 1.1), c(1.5, .8, 1.3)), u = "1 liter", f = "%.2f"),
  bread = list(cols = paste0("Q9.", 2:5),  p = rbind(c(2.5, 1.7, 1.9), c(2.1, 1.6, 1.7), c(2.3, 1.4, 1.8), c(2.7, 1.5, 1.6)), u = "450g", f = "%.2f"))
sys <- c("Organic farming", "Conventional farming", "Circular farming")
rows <- list(); tk <- 0L
for (pr in names(sets)) {
  s <- sets[[pr]]
  for (j in 1:4) {
    tk <- tk + 1L
    ch <- d[[s$cols[j]]]
    ok <- ch %in% 1:4
    for (k in 1:3)
      rows[[length(rows) + 1L]] <- data.table(id = d$IDT[ok], task = tk, profile = k, choice = as.integer(ch[ok] == k),
        attr_farming_system = sys[k], attr_price = sprintf(paste0("EUR ", s$f, " per ", s$u), s$p[j, k]), trial_product = pr)
  }
}
r <- rbindlist(rows)
cv <- d[, .(id = IDT,
  cov_country = c("1" = "Belgium", "2" = "Croatia", "4" = "Hungary", "6" = "Italy", "8" = "Poland", "9" = "Spain")[as.character(Country)],
  cov_gender = c("male", "female", "other")[Q1.2],
  cov_age_group = c("Under 18 years old", "18-24 years", "25-34 years", "35-44 years", "45-54 years", "More than 55 years")[Q1.3],
  cov_education = c("Not completed elementary studies", "Elementary studies", "Secondary studies", "University studies")[fifelse(Q16.6 %in% 1:4, Q16.6, NA_integer_)],
  cov_birth_year = fifelse(Q16.1 >= 1920 & Q16.1 <= 2010, as.integer(Q16.1), NA_integer_))]
stopifnot(!anyNA(cv$cov_country))
r <- merge(r, cv, by = "id")
# re-key to consecutive integers
r[, id := as.integer(factor(id))]
# every task: exactly one of 3 chosen, or none (opt-out)
stopifnot(r[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(r, id, task, profile)
fwrite(r, file.path(out, "ornelasherrera_2023_circular_farming.csv"))
