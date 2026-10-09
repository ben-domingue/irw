##Foreign-loan conjoints (project loans and bailout loans) in nine countries from
##Bulman, D., Leng, N., & Ratigan, K. (2025). Foreign borrowing, sovereignty, and public opinion
##in the Global South: Traditional lenders or China? The Review of International Organizations.
##https://doi.org/10.1007/s11558-025-09602-6
##Replication data: Harvard Dataverse doi:10.7910/DVN/YTLM5U, CC0 1.0, no restricted files.
##File read: ForeignBorrowingPublicOpinion_CleanData.dta (Dataverse "original format"; the wide
##file with the displayed conjoint text d<k>c<task>_attrib<j>_name / _project<p>).
##Read as text: ..._ProjectLoanCleaning.do and ..._BailoutLoanCleaning.do (attribute-name
##translations, reshape: choice = loan number), ..._Analysis.do; Supplementary Materials .pdf
##(survey details, Table A1, Figures B1/B2 = English screenshots of both conjoints).
##Not used: ..._ProjectLoan/_BailoutLoan/_ConjointMerged.dta (the authors' reshaped files with
##English recodes). Same authors' different study: bulman_2025_fdi_* (doi:10.7910/DVN/YGXPVC).
##Usage: Rscript bulman_2025_loans.R <raw dir> <output dir>
##
##TGM Research online panels in Kenya, Nigeria, South Africa, Indonesia, Malaysia, Philippines,
##Argentina, Colombia and Peru; 8,762 respondents after the authors removed those failing two
##attention checks (supplement A, Table A1; the deposit holds exactly these). Each respondent was
##assigned to ONE of two conjoints (split sample) and saw 5 pairs of loans (task 1-5; Loan 1 /
##Loan 2 = profile 1/2):
##  project loans (d1, debt_conjoint1_*; 4,415 respondents), "foreign loans for infrastructure
##    projects", 5 attributes: purpose (Highway network / 5G telecommunications network),
##    interest rate (2% / 6% / 10%), collateral (natural resources below market price /
##    exclusive rights to land / nothing but lose future borrowing), lender (World Bank /
##    Chinese government / US government / private commercial banks), condition (no conditions /
##    cut government spending / increase transparency / use labour and materials from the
##    lender's country);
##  bailout loans (d2, debt_conjoint2_*; 4,347 respondents), "facing a financial crisis", 4
##    attributes: interest rate, collateral, lender (IMF instead of World Bank), condition (no
##    lender-country labour level).
##Outcome: choice, "Which foreign loan would you prefer for <country>?" Loan 1 / Loan 2, forced
##(supplement Figures B1/B2; exactly one chosen in every task, checked).
##TABLES: per experiment, grouped by displayed text (8 tables). The authors pool the nine
##countries, so countries whose displayed level text is identical share a table with cov_country
##(checked: same level set per attribute in every pooled country): bulman_2025_<project|bailout>_en
##(Kenya, Nigeria, South Africa, Philippines; English) and _es (Argentina, Peru, Colombia;
##Spanish). Indonesia (Indonesian) and Malaysia (mixed: Malay 390/433, English 69/51, Chinese
##21/18 respondents in project/bailout) keep their own tables (_indonesia, _malaysia); the
##Malaysian table keeps trial_language = language of the displayed attribute names (en, ms, zh;
##"Pinjaman ini disediakan oleh:" is the same in Indonesian and Malay, the language is taken from
##the other rows). The question text names the country ("...prefer for the Philippines?").
##Attribute text = d<k>c<task>_attrib<j>_project<p> as displayed (trimmed); the row's attribute
##is identified from the displayed name via the authors' translation table. Attribute row order
##is randomized per respondent and recorded -> attrpos_<attr> (1 = top row); checked constant
##across a respondent's tasks.
##Covariates (codes; labels from the .dta variable labels): cov_gender_code (d_female, variable
##label "Gender, 1=female"; NOT mapped to cov_gender because the supplement's Table A1 gender
##counts are the reverse of the data in every country, e.g. Kenya Table A1 female 522 / male
##458 vs d_female 1 = 458 / 0 = 523, so either the label or the table is swapped), cov_college, cov_unemployed,
##cov_urban (1 = urban), cov_age_group_code (d_age 1-4, no value labels), cov_income_code,
##cov_region_code (country-specific, no labels), cov_vote_incumbent (c_vote_win), cov_debt_harm_
##imf/chn/priv/usa (past economic harm by lender, 1 = yes), cov_duration_sec (whole survey),
##cov_user_language (Qualtrics UserLanguage), cov_country (ISO code). Dropped: responseid (Qualtrics; re-keyed 1..N in
##file order across the deposit), the other debt attitude items. No survey weight deposited.
##Counts: respondents per country as in Table A1 (e.g. Kenya 981 = 492 project + 489 bailout).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d0 <- read_dta(file.path(raw, "ForeignBorrowingPublicOpinion_CleanData.dta"))
ctry <- as.character(as_factor(d0$country))   # value labels of the .dta
d <- as.data.table(zap_labels(d0)); rm(d0)
d[, ctry := ctry]
stopifnot(nrow(d) == 8762, !anyDuplicated(d$responseid))
cn <- c("Kenya", "Nigeria", "SouthAfrica", "Philippines", "Argentina", "Peru", "Colombia", "Malaysia", "Indonesia")
# country codes: labels from the .dta (checked against Table A1 counts)
stopifnot(all(d$ctry %in% cn), d[, .N, ctry][ctry == "Kenya", N] == 981, d[, .N, ctry][ctry == "Peru", N] == 1036)
d[, rid := seq_len(.N)]
an <- list(
  purpose = c(en = "This loan is for:", es = "Este préstamo es para construir una:", id = "Pinjaman ini untuk:",
              ms = "Pinjaman ini adalah untuk:", zh = "这项贷款的项目是:"),
  interest_rate = c(en = "The interest rate for this loan is:", es = "La tasa de interés para este préstamo es:",
                    id = "Tingkat bunga untuk pinjaman ini adalah:", ms = "Kadar faedah untuk pinjaman ini adalah:", zh = "贷款利率为:"),
  collateral = c(en = "If your government cannot repay this loan, they will instead repay the lenders with:",
                 es = "Si su gobierno no puede pagar este préstamo, tendrán que pagar a los acreedores con:",
                 id = "Jika pemerintah Anda tidak dapat membayar kembali pinjaman ini, mereka akan membayar kembali pemberi pinjaman dengan:",
                 ms = "Jika kerajaan anda tidak dapat membayar balik pinjaman ini, mereka akan sebaliknya membayar balik pemberi pinjaman dengan:",
                 zh = "如果你的政府无力偿还该项贷款，后果如下:"),
  lender = c(en = "The loan is provided by:", es = "El préstamo será proporcionado por:", ms = "Pinjaman ini disediakan oleh:", zh = "贷款方为:"),
  condition = c(en = "In order to get this loan, the lenders require your government to:",
                es = "Para conseguir este préstamo, el acreedor requiere que su gobierno:",
                id = "Untuk mendapatkan pinjaman ini, pemberi pinjaman mengharuskan pemerintah Anda untuk:",
                ms = "Untuk mendapatkan pinjaman ini, pemberi pinjaman memerlukan kerajaan anda untuk:",
                zh = "想要得到这笔贷款，贷款方提出如下附带条款:"))
nmap <- rbindlist(lapply(names(an), function(k) data.table(attr = k, lang = names(an[[k]]), name = unname(an[[k]]))))
stopifnot(!anyDuplicated(nmap$name))
nmap[name == "Pinjaman ini disediakan oleh:", lang := NA]   # same in Indonesian and Malay
exps <- list(project = list(p = "d1", ch = "debt_conjoint1_", k = 5L), bailout = list(p = "d2", ch = "debt_conjoint2_", k = 4L))
for (ex in names(exps)) {
  e <- exps[[ex]]; s <- d[!is.na(get(paste0(e$ch, 1)))]
  K <- e$k
  for (t in 2:5) for (j in 1:K) stopifnot(all(s[[sprintf("%sc%d_attrib%d_name", e$p, t, j)]] == s[[sprintf("%sc1_attrib%d_name", e$p, j)]]))
  nm <- sapply(1:K, function(j) trimws(s[[sprintf("%sc1_attrib%d_name", e$p, j)]]))
  ia <- matrix(nmap$attr[match(nm, nmap$name)], ncol = K)
  want <- if (K == 5) names(an) else setdiff(names(an), "purpose")
  stopifnot(!anyNA(ia), all(apply(ia, 1, function(r) setequal(r, want))))
  lg <- matrix(nmap$lang[match(nm, nmap$name)], ncol = K)
  s[, trial_language := apply(lg, 1, function(r) { u <- unique(na.omit(r)); stopifnot(length(u) == 1); u })]
  L <- list()
  for (t in 1:5) for (p in 1:2) {
    ch <- s[[paste0(e$ch, t)]]; stopifnot(all(ch %in% 1:2))
    x <- data.table(rid = s$rid, task = t, profile = p, choice = as.integer(ch == p))
    for (j in 1:K) {
      v <- trimws(s[[sprintf("%sc%d_attrib%d_project%d", e$p, t, j, p)]])
      for (at in want) {
        sel <- ia[, j] == at
        x[sel, paste0("attr_", at) := v[sel]]
        x[sel, paste0("attrpos_", at) := j]
      }
    }
    L[[length(L) + 1]] <- x
  }
  o <- rbindlist(L)
  stopifnot(o[, sum(choice), .(rid, task)][, all(V1 == 1)])
  ac <- grep("^attr_", names(o), value = TRUE)
  stopifnot(!anyNA(o[, ..ac]), o[, all(sapply(.SD, function(z) all(nchar(z) > 0))), .SDcols = ac])
  cv <- s[, .(rid, ctry, trial_language, cov_gender_code = as.integer(d_female), cov_college = as.integer(d_college),
              cov_unemployed = as.integer(d_unemployed), cov_urban = as.integer(d_urban), cov_age_group_code = as.integer(d_age),
              cov_income_code = as.integer(d_income), cov_region_code = as.integer(d_region), cov_vote_incumbent = as.integer(c_vote_win),
              cov_debt_harm_imf = as.integer(debt_harm_imf), cov_debt_harm_chn = as.integer(debt_harm_chn),
              cov_debt_harm_priv = as.integer(debt_harm_priv), cov_debt_harm_usa = as.integer(debt_harm_usa),
              cov_duration_sec = as.integer(durationinseconds), cov_user_language = userlanguage)]
  o <- cv[o, on = "rid"]
  setcolorder(o, c("rid", "task", "profile", "choice", ac, grep("^attrpos_", names(o), value = TRUE), "trial_language"))
  # groups: countries whose displayed text is in one shared language are pooled (cov_country);
  # Indonesia and Malaysia (own language / mixed languages) keep their own table
  grp <- list(en = c("Kenya", "Nigeria", "SouthAfrica", "Philippines"), es = c("Argentina", "Peru", "Colombia"),
              indonesia = "Indonesia", malaysia = "Malaysia")
  iso <- c(Kenya = "KE", Nigeria = "NG", SouthAfrica = "ZA", Philippines = "PH", Argentina = "AR", Peru = "PE",
           Colombia = "CO", Indonesia = "ID", Malaysia = "MY")
  for (g in names(grp)) {
    z <- o[ctry %in% grp[[g]]]
    if (length(grp[[g]]) > 1) {
      stopifnot(uniqueN(z$trial_language) == 1)
      # the displayed level text is identical across the pooled countries: same level set per attribute
      for (v in ac) { lv <- z[, .(l = list(sort(unique(get(v))))), ctry]$l; stopifnot(all(vapply(lv, identical, TRUE, lv[[1]]))) }
    }
    if (g != "malaysia") { stopifnot(uniqueN(z$trial_language) == 1); z[, trial_language := NULL] }
    z[, cov_country := iso[ctry]][, ctry := NULL]
    setnames(z, "rid", "id"); setorder(z, id, task, profile)
    tn <- paste0("bulman_2025_", ex, "_", g)
    fwrite(z, file.path(out, paste0(tn, ".csv")))
    cat(tn, "rows", nrow(z), "resp", uniqueN(z$id), "countries", z[task == 1 & profile == 1, paste(names(table(cov_country)), table(cov_country), collapse = " ")], "\n")
  }
}
