##Deposit product design for financial inclusion of slum dwellers: paired choice with an opt-out ranking, Khulna (Bangladesh)
##Bari, M. A. (2025). Financial Inclusion Strategies Conjoint [Data set]. Mendeley Data, v1. No paper DOI listed.
##Deposit: doi:10.17632/mh7cwkn49t, CC BY 4.0 (Mendeley data_licence field). Files read: "Main Data Conjoint.dta" (saved as
##main.dta) and "Main Do Conjoint 14.05.25.do" (read as text, never run; it holds the value labels of the five attributes).
##Usage: Rscript bari_2025.R <dir holding main.dta> <output dir>
##
##250 slum-household respondents in Khulna rated 5 choice sets each (2,500 rows = 250 x 5 rounds x 2 alternatives A/B; the
##deposit describes "2500 choice responses from 250 respondents"). Each alternative is a hypothetical deposit product with
##5 attributes (labels from the .do value labels): documentation requirement (High, Low), service charge (BDT240, BDT120,
##BDT60), linked facility (Only Loan, Loan and Safety Net Allowance), help desk (No, Yes), return type (Interest Based,
##Profit Loss Sharing). Fixed blocked design: 10 choice sets (choiceid), each respondent saw 5 of them, A and B are not
##exchangeable (B always has the High documentation level; A never has BDT60). Hence restrictions = observed.
##Outcomes. The deposit's Choice column is a 3-digit code that, in all 1,250 tasks, is the rank (1 = best) of (A, B, no
##product): 123 -> A first, B second, none third; 231 -> none first, A second, B third; etc. This is INFERRED from its perfect
##agreement with InternalChoice (which of A/B ranks higher) and ExternalChoice (1 on both rows of a task when a product ranks
##above none). Stored: rating_rank = the rank of this profile (1 = most preferred of A, B and the no-product option; digit 1 =
##A, digit 2 = B); choice = the profile ranked first (0 on both profiles in the 45 tasks where no product was ranked first);
##choice_forced = InternalChoice (the preferred of A and B, always exactly one per task). The authors' ExternalChoice is
##therefore captured by choice. No question wording or option labels are in the deposit. opt_out = yes for choice,
##no for choice_forced.
##Covariates: cov_age (Q5, years), cov_gender_code (GenderM, 1 = male by variable name; no value labels, so a _code column).
##Dropped: Address (free-text addresses, PII FOUND), date and time stamps, household size, other survey answers (education,
##income, expenditure, programme participation, financial literacy, ...: numeric codes without labels or free text), all
##derived interaction columns, treat (unlabelled), randomizednumber, platform ids; ID re-keyed to integers.
suppressMessages({library(haven); library(data.table)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(file.path(raw, "main.dta")))
stopifnot(nrow(x) == 2500, uniqueN(x$ID) == 250, x[, .N, by = ID][, all(N == 10)])
lv <- list(doc = c("High", "Low"), charge = c("BDT240", "BDT120", "BDT60"), Facility = c("Only Loan", "Loan and Safety Net Allowance"),
           HelpDesk = c("No", "Yes"), ReturnType = c("Interest Based", "Profit Loss Sharing"))
for (v in names(lv)) stopifnot(all(x[[v]] %in% seq_along(lv[[v]])))
x[, ch := sprintf("%03d", as.integer(Choice))]
x[, rk := as.integer(ifelse(alternative == "A", substr(ch, 1, 1), substr(ch, 2, 2)))]
stopifnot(x[, sum(InternalChoice), by = .(ID, round)][, all(V1 == 1)],
          x[, all(rk[InternalChoice == 1] < rk[InternalChoice == 0]), by = .(ID, round)][, all(V1)],
          x[, .(e = uniqueN(ExternalChoice)), by = .(ID, round)][, all(e == 1)],
          x[ExternalChoice == 1 & InternalChoice == 1, all(rk == 1)],
          x[ExternalChoice == 0, all(rk[InternalChoice == 1] == 2)])
d <- x[, .(id = match(ID, sort(unique(ID))), task = as.integer(round), profile = ifelse(alternative == "A", 1L, 2L),
           choice = as.integer(ExternalChoice == 1 & InternalChoice == 1), choice_forced = as.integer(InternalChoice), rating_rank = rk,
           attr_documentation = lv$doc[doc], attr_service_charge = lv$charge[charge], attr_linked_facility = lv$Facility[Facility],
           attr_help_desk = lv$HelpDesk[HelpDesk], attr_return_type = lv$ReturnType[ReturnType],
           cov_age = as.integer(Age), cov_gender_code = as.integer(GenderM))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bari_2025_deposit_inclusion.csv"))
