##Job-offer conjoint (governors' COVID-19 responses) from
##Nelson, M. J., & Witko, C. (2020). Government reputational effects of COVID-19 public health
##actions: A job opportunity evaluation conjoint experiment. Journal of Behavioral Public
##Administration, 3(1). https://doi.org/10.30636/jbpa.31.174
##Replication data: Harvard Dataverse doi:10.7910/DVN/GOWG6K, CC0 1.0, no restricted files.
##File read: NelsonWitko_JBPA_ReplicationDataset.csv (original of the .tab; raw Qualtrics CSV).
##NelsonWitko_JBPA_Replication.R read as text for the code -> level mapping and the rating recode.
##Displayed text: the article (open access), Figure 1 (an example trial, image) and note 6.
##Same authors and same Qualtrics layout as nelson_2022.R (a different, 2019 experiment).
##Usage: Rscript nelson_2020.R <raw dir> <output dir>
##
##984 MTurk respondents (April 2020; the article says "about 1,000"). Each saw 15 pairs of
##hypothetical job offers ("Job Offer 1" = profile 1, "Job Offer 2" = profile 2), 6 attributes,
##"all fully randomized across job offers" (article). Task t shows profile 1 from the Qualtrics
##fields <attr>(2t-1)_DO and profile 2 from <attr>(2t)_DO, as in the authors' code; the _DO value
##is the index of the level shown. Task and profile are recorded.
##Intro: "For the next few minutes, we are going to show you pairs of job offers. Imagine that you
##are currently looking for a new job and have received both offers. You are deciding which offer
##you will accept. For each pair, please indicate your feelings toward the two offers and which one
##you would be more likely to accept, even if you aren't entirely sure. ..."
##Outcomes:
##  choice: accept_t (1 = Job Offer 1, 2 = Job Offer 2); "select which of the two job offers was
##    most attractive" (article paraphrase); forced choice, no opt-out.
##  rating: offer1_t / offer2_t, attractiveness of each offer on a 5-point scale "ranging from
##    'Very attractive' to 'Not at all attractive'". Raw Qualtrics codes are not in scale order;
##    the authors recode 1->5, 2->4, 5->3, 3->2, 4->1 and that recode is applied here, so
##    5 = Very attractive, 1 = Not at all attractive (chosen offers average higher; checked below).
##Attribute text (code order from the authors' recode lines):
##  local_news: "As COVID-19 (Coronavirus) began to rapidly spread in the state, the Governor" +
##    1 proclamation / 2 delegate to cities / 3 limit gatherings / 4 stay at home; full sentences
##    from the article (Figure 1 confirms levels 1 and 2 verbatim, incl. the comma).
##  location: 1 "Rural Area", 3 "Mid-size city" as in Figure 1; 2 "Small college town" and
##    4 "Major metropolitan area" are from the article prose ("a small college town", "a major
##    metropolitan area"), not seen displayed.
##  company_size: "10 Employees" / "2,500 Employees" / "500,000 Employees" (Figure 1 format).
##  political_climate: 1 "In a state that voted heavily for Hillary Clinton in 2016" and 2 "In a
##    state that Hillary Clinton barely won in 2016" (Figure 1); 3/4 the Trump versions are
##    written by analogy (article: voted heavily for / barely won, Clinton or Trump).
##  salary: $75,000 / $90,000 / $105,000. company_culture: the four statements of note 6
##    (1 variety, 2 feedback, 3 advancement, 4 talent; two confirmed in Figure 1).
##Attribute row order in Figure 1: local news, location, size, political climate, salary,
##culture; whether it was randomized is not documented (no order fields in the export).
##Covariates: cov_birth_year (YRBORN as entered; two entries 1880/1881 that the authors read as
##1980/1981 are kept as entered), cov_party_id7_code (the authors' 7-point party-ID construction
##from PID2/PID3/PID4, kept as CODES: the deposit labels neither the PID items nor the 7 points;
##the authors' code only groups them as 1-3 Democrat, 4 independent, 5-7 Republican, so the
##text of each point, e.g. strong vs lean, is undocumented), cov_covid_concern (Q299, "How concerned are you
##about a coronavirus epidemic here in the United States?", raw code; the authors treat 1-2 as
##concerned, 3-4 as not concerned, 5 as don't know). Other demographics are unlabelled Qualtrics
##codes and are dropped, as are the timing fields and the authors' derived variables.
##PII in the deposit (dropped): Qualtrics ResponseId. Ids are re-keyed to row order.
##Rows with neither a choice nor a rating are omitted.
##N: 984 respondents (article: about 1,000 MTurkers).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
pre <- "As COVID-19 (Coronavirus) began to rapidly spread in the state, the Governor "
lv <- list(bs = paste0(pre, c("issued a proclamation thanking healthcare workers for their \"dedication and sacrifice\"",
                              "decided to allow cities and local governments in the states to determine appropriate public health measures",
                              "recommended that individuals limit gatherings to a small number of people and practice social distancing",
                              "issued a stay at home order which required all citizens to remain in their homes except to exercise or obtain life-sustaining products and services (groceries, pharmaceuticals and healthcare)")),
           rural = c("Rural Area", "Small college town", "Mid-size city", "Major metropolitan area"),
           size = c("10 Employees", "2,500 Employees", "500,000 Employees"),
           pol = c("In a state that voted heavily for Hillary Clinton in 2016", "In a state that Hillary Clinton barely won in 2016",
                   "In a state that Donald Trump barely won in 2016", "In a state that voted heavily for Donald Trump in 2016"),
           sal = c("$75,000", "$90,000", "$105,000"),
           comp = c("You will have the ability to work on a variety of tasks and develop your skills in many areas",
                    "The company seeks to provide employees with constructive feedback to foster their career growth",
                    "Employees are given many opportunities for advancement within the organization",
                    "You will have many opportunities to collaborate with talented people"))
an <- c(bs = "local_news", rural = "location", size = "company_size", pol = "political_climate", sal = "salary", comp = "company_culture")
rec <- c(5L, 4L, 2L, 1L, 3L)  # authors' recode 1=5;2=4;5=3;3=2;4=1
s <- fread(file.path(raw, "NelsonWitko_JBPA_ReplicationDataset.csv"))
stopifnot(nrow(s) == 984)
s[, id := seq_len(.N)]
pid <- rep(NA_integer_, nrow(s))
pid[s$PID2 %in% 1] <- 1L; pid[s$PID2 %in% 2] <- 2L; pid[s$PID4 %in% 2] <- 3L; pid[s$PID4 %in% 3] <- 4L
pid[s$PID4 %in% 1] <- 5L; pid[s$PID3 %in% 2] <- 6L; pid[s$PID3 %in% 1] <- 7L
rows <- list()
for (t in 1:15) for (p in 1:2) {
  j <- 2L * t - 2L + p
  r <- data.table(id = s$id, task = t, profile = p)
  acc <- s[[paste0("accept_", t)]]
  r[, choice := fifelse(is.na(acc), NA_integer_, as.integer(acc == p))]
  r[, rating := rec[s[[paste0("offer", p, "_", t)]]]]
  for (k in names(lv)) { code <- s[[paste0(k, j, "_DO")]]; stopifnot(all(code %in% seq_along(lv[[k]]))); r[, paste0("attr_", an[[k]]) := lv[[k]][code]] }
  r[, cov_birth_year := as.integer(s$YRBORN)][, cov_party_id7_code := pid][, cov_covid_concern := as.integer(s$Q299)]
  rows[[length(rows) + 1]] <- r
}
d <- rbindlist(rows)
d <- d[!(is.na(choice) & is.na(rating))]
stopifnot(all(d$choice %in% c(NA, 0:1)), all(d$rating %in% c(NA, 1:5)))
stopifnot(d[!is.na(choice), .(s = sum(choice), n = .N), .(id, task)][, all(s == 1 & n == 2)])
stopifnot(d[choice == 1, mean(rating, na.rm = TRUE)] > d[choice == 0, mean(rating, na.rm = TRUE)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "nelson_2020_covid_job_offers.csv"))
