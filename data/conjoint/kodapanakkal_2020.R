##Big-data technology conjoint (six technology domains) from
##Kodapanakkal, R. I., Brandt, M. J., Kogler, C., & van Beest, I. (2020). Self-interest and data
##protection drive the adoption and moral acceptability of big data technologies: A conjoint
##analysis approach. Computers in Human Behavior, 108, 106303.
##https://doi.org/10.1016/j.chb.2020.106303
##Replication data: DataverseNL doi:10.34894/YUCT6Q. No licence field; the dataset's terms of use
##read only "CC-BY" (treated as CC BY 4.0); no restricted files, no guestbook.
##Files read: Processed Data Files/tech1a.csv ... tech6a.csv (choice) and tech1b.csv ...
##tech6b.csv (moral acceptability ratings); the Qualtrics survey file
##AdoptionOfBigDataTechnologies_fullsurvey.qsf from the authors' OSF materials component
##(osf.io/4m2rg, linked from the deposit's Metadata.xlsx via osf.io/wdgra), used only for the
##displayed level text (loop-and-merge tables) and question wording. Read as text:
##Documentation_datafiles.txt, Data Preparation Healthcare.R, Materials_qualtrics.pdf, codingamce.csv.
##Not used: RawData/rawdata.csv (the Qualtrics export; its embedded HTML breaks the CSV
##structure, and the authors built the processed files from a different, undeposited copy).
##Usage: Rscript kodapanakkal_2020.R <raw dir> <output dir>
##
##TurkPrime/MTurk, 19-27 February 2018 (Metadata.xlsx). Each respondent was assigned (condition
##1-12) to TWO of six technologies (criminal investigations surveillance, healthcare monitoring,
##bank purchase tracking, crime-prevention algorithm, employment algorithm, citizen scores) and,
##per technology, to a between-subjects framing (StatusQuo: Brand New / New but Used / Used),
##then saw the same 12 fixed pairs of technology versions (codingamce.csv; loop-and-merge with
##randomized loop order) varying three attributes: outcome favourability (2 levels), data
##sharing (Not Shared / Shared1 / Shared2) and data protection (2 levels).
##SIX TABLES, one per technology, as the authors analyse them (one processed file and one set of
##AMCEs per domain): the attribute text is domain-specific, and the processed files number
##respondents 1..n WITHIN each domain (Data Preparation *.R: ID <- 1:nrow(data) after filtering
##on that domain's framing variable), so the two domains a person answered cannot be linked.
##  kodapanakkal_2020_investigations, _healthcare, _banking, _crime_prevention, _employment,
##  _citizen_scores.
##task = the loop (pair) number 1-12 of the fixed design, NOT display order: loop order was
##randomized ("Subset" randomization of all 12 loops, qsf) and not recorded in the processed
##files. profile 1 = Technology version A (left column), 2 = version B: in the processed files the
##first row of each trial is version A (the authors bind codingamce rows in A/B order); checked
##here against the qsf loop tables, where fields 1/3/5 fill column A and 2/4/6 column B: the
##code -> text map is one-to-one in every domain.
##Attributes: attr_outcome, attr_data_sharing, attr_data_protection, text as displayed with the
##<b> markup removed. Shared1/Shared2 are the domain's two sharing partners (e.g. healthcare:
##pharmaceutical companies / academic researchers), recovered from the qsf.
##Outcomes:
##  choice  "If you have to make a choice between these versions of the technology, which one
##          would you choose?" Technology version A / Technology version B / Neither of these
##          (opt-out: choice 0 on both profiles).
##  rating  "On a scale of 0 to 100, how would you morally evaluate Technology version A/B?
##          (where 0 is morally unacceptable and 100 is morally acceptable)", slider, as stored.
##trial_framing = StatusQuo arm (the technology description: brand new / new but used elsewhere
##/ in use for a few years). No covariates in the processed files.
##Tasks whose choice is missing were removed from the a-files by the authors (na.omit); tasks
##with ratings but no choice are kept here with choice NA on both profiles (attribute text comes
##from the fixed design, framing from the b-file); a profile without a rating has rating NA.
library(data.table); library(jsonlite)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
q <- fromJSON(file.path(raw, "AdoptionOfBigDataTechnologies_fullsurvey.qsf"), simplifyVector = FALSE)
loops <- list()
for (e in q$SurveyElements) if (e$Element == "BL") for (b in e$Payload)
  if (is.list(b) && !is.null(b$Options$LoopingOptions$Static)) loops[[b$Description]] <- b$Options$LoopingOptions$Static
clean <- function(s) trimws(gsub("\\s+", " ", gsub("<[^>]+>|&nbsp;", " ", s)))
dom <- data.table(k = 1:6, block = paste0("T", 1:6),
                  domain = c("Criminal Investigations", "Healthcare", "Banking", "Crime prevention", "Employment", "Citizen scores"),
                  tab = c("investigations", "healthcare", "banking", "crime_prevention", "employment", "citizen_scores"))
for (i in 1:6) {
  st <- loops[[dom$block[i]]]; stopifnot(length(st) == 12)
  txt <- rbindlist(lapply(1:12, function(l) {
    f <- vapply(1:6, function(j) clean(st[[as.character(l)]][[as.character(j)]]), "")
    data.table(trial = l, version = 1:2, t_out = f[1:2], t_share = f[3:4], t_prot = f[5:6])
  }))
  ca <- fread(file.path(raw, sprintf("tech%da.csv", i)))
  cb <- fread(file.path(raw, sprintf("tech%db.csv", i)))
  stopifnot(all(ca$domain == dom$domain[i]), all(ca$response %in% 1:3))
  ca[, version := rowid(ID, trial)]
  stopifnot(all(ca$version %in% 1:2), ca[, .N, .(ID, trial)][, all(N == 2)])
  ca <- txt[ca, on = .(trial, version)]
  # one-to-one code <-> text
  for (p in list(c("OutcomeFavorability", "t_out"), c("DataSharing", "t_share"), c("DataProtection", "t_prot")))
    stopifnot(ca[, uniqueN(get(p[2])), by = get(p[1])][, all(V1 == 1)], ca[, uniqueN(get(p[1])), by = get(p[2])][, all(V1 == 1)])
  stopifnot(ca[, all(res == as.integer(response == version))])
  cb <- cb[, .(ID, trial, version, rating = as.integer(response), sqb = StatusQuo)]
  stopifnot(cb[, .N, .(ID, trial, version)][, all(N == 1)], all(cb$rating %between% c(0, 100)))
  nb <- nrow(cb[!ca, on = .(ID, trial, version)])
  o <- merge(ca[, .(ID, trial, version, res, StatusQuo)], cb, by = c("ID", "trial", "version"), all = TRUE)
  o[is.na(StatusQuo), StatusQuo := sqb]
  o <- txt[o, on = .(trial, version)]
  stopifnot(o[, .N, .(ID, trial)][, all(N == 2)], o[, uniqueN(StatusQuo), ID][, all(V1 == 1)],
            o[, uniqueN(is.na(res)), .(ID, trial)][, all(V1 == 1)])
  o <- o[, .(id = ID, task = trial, profile = version, choice = res, rating,
             attr_outcome = t_out, attr_data_sharing = t_share, attr_data_protection = t_prot,
             trial_framing = StatusQuo)]
  o[, id := match(id, sort(unique(id)))]
  setorder(o, id, task, profile)
  tn <- paste0("kodapanakkal_2020_", dom$tab[i])
  fwrite(o, file.path(out, paste0(tn, ".csv")))
  cat(tn, "rows", nrow(o), "resp", uniqueN(o$id), "tasks", o[, uniqueN(paste(id, task))],
      "optout", o[, sum(choice), .(id, task)][V1 == 0, .N], "rating NA", sum(is.na(o$rating)),
      "rating-only rows", nb, "\n")
}
