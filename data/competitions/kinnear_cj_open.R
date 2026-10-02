##Comparative-judgement sessions from the Kinnear, Jones & Davies CJ meta-analysis whose
##original data deposits are openly licensed (irw#2692). The meta-analysis repo
##(https://github.com/georgekinnear/cj-meta-analysis, commit f2b6dd5) has no licence, so
##nothing is read from it: every table below is built from the study's own open deposit,
##and the repo is used only to identify the studies and to cross-check counts.
##Kinnear, G., Jones, I., & Davies, B. (2025). Comparative judgement as a research tool: a
##meta-analysis of application and reliability. https://doi.org/10.31219/osf.io/c9q3b_v1
##
##Ruling (Ben, 2026-10-01, #2692): build the sessions from openly licensed studies now;
##email the authors of the rest. Per-study rights: oneoff/comps-ingest-2026-09-30/
##kinnear_cj_rights.md. Licences re-checked 2026-10-01 on each deposit's API.
##
##Tables (one per study; agent_a = the representation chosen, so winner is always
##"agent_a", as in bramley_vitello_gcse.R; homefield blank; rater = judge, re-keyed):
##
##  clark_2018_strength_study2  Clark et al. (2018), PLoS ONE 13(1) e0190393,
##      doi:10.1371/journal.pone.0190393. Data: Brunel figshare 4902977,
##      doi:10.17633/rd.brunel.4902977.v1, "license": {"name": "CC BY 4.0"}.
##      EloStrengthData.zip -> Study2Pairwise.csv: which of two photos of men looks
##      physically stronger. Study 1 is NOT built: it is already in IRW as
##      elochoice_physical (the EloChoice `physical` data, 4,592 contests, 82 stimuli,
##      56 raters, the same as Study1Pairwise.csv). rater_age / rater_sex are the
##      source's columns; `trial` is its running index (`index`). No date. 22 rows
##      that pair a photo with itself (11 raters) are dropped, as they are not a
##      comparison; 7,835 of the source's 7,857 rows remain.
##
##  ramos_2021_proof_explanation  Mejia Ramos, Evans, Rittberg & Inglis (2021),
##      Axiomathes, doi:10.1007/s10516-021-09545-8. Data: Loughborough figshare
##      12458486, doi:10.17028/rd.lboro.12458486.v1, "license": {"name": "CC BY-NC 4.0"}
##      (NonCommercial; carried into Derived License). Decisions-combined.csv: which of
##      two proofs is more explanatory. Agents are the proof names from ModelledRes.csv
##      (the "candidate codes" are mapped through it). group: the source's Group, A =
##      Auckland (320 decisions) and R = Rutgers (440), as the meta-analysis lists the
##      two sessions. date = createdAt (dd/mm/yyyy HH:MM, read as UTC); time_taken =
##      timeTaken / 1000 (seconds; the source gives milliseconds).
##
##  sangwin_2021_proof_rigour_insight  Sangwin & Kinnear (2021), EdArXiv,
##      doi:10.35542/osf.io/egks4. Data: Zenodo 4893915, doi:10.5281/zenodo.4893915
##      (licence id "other-open"); the archived repo's LICENSE.md is "MIT License,
##      Copyright (c) 2021 George Kinnear", which is used as the licence (MIT data is
##      accepted precedent: kalimahnorms_alzahrani_2025, zorowitz_2023_marsib).
##      data-out/judgement_data_all.csv: students judged pairs of proofs of the same
##      theorem on one criterion per session. session = study x dimension (7 sessions:
##      study1 rigour/insight; study2 rigour/insight/simple/understanding/marks).
##      Each session uploaded the proofs under its own script ids; proof_names.csv maps
##      them to the proof number, so agents are proofs ("proof_1".."proof_15") and are
##      shared across sessions. excluded = 1 for the judges the authors dropped as
##      "nonserious" (median time per judgement < 5 s, 01-judgements.Rmd); the remaining
##      3,485 decisions are the ones the authors (and the meta-analysis) analyse.
##      time_taken = TimeTaken (seconds). No date.
##
##  jones_2020_cme_complexity  Jones, Scott, Barnard, Highfield, Lintott & Baeten (2020),
##      Space Weather 18(10) e2020SW002556, doi:10.1029/2020SW002556. Data: figshare
##      7808693, doi:10.6084/m9.figshare.7808693.v1, "Protect our Planet from Solar
##      Storms: Data", "license": {"name": "CC BY 4.0"}. The meta-analysis cites a
##      private share link; this public record holds the same classifications (the
##      decision counts, 246,692 and 163,197, and the first rows match the meta-analysis
##      files exactly). Zooniverse citizen scientists chose which of two coronal mass
##      ejection images "looks the most complicated". session = "main" (classifications_
##      complete, 2018) or "brightness_equalised" (2019-20, the same 1,111 images after
##      brightness equalisation), so agents (image file names) are shared across
##      sessions. "Image on the left" = asset_0. side_chosen = left/right. date =
##      created_at (UTC). rater = re-keyed Zooniverse user name (keyed jointly across the
##      two sessions); rater_logged_in = 0 for "not-logged-in-<hash>" users, whose hash
##      is per browser session, so one person may appear as several raters. user ids,
##      names, IP hashes and browser metadata are not kept.
##
##Not built (open-looking deposits; see the rights file): Zucco2019 (CC0) is already in IRW
##as zucco2019_portfoliosalience. Davies2020a (figshare 8940149, CC BY-NC) and Bisson2019
##(figshare 5845683, CC BY-NC) deposits hold only scores/measures, not the decisions; the
##decisions exist only in the unlicensed meta-analysis repo. Luckett2018 and Daal2017 (OSF,
##no licence stated) and Jones2019 (private figshare link) wait with the email group.

library(data.table)
cache <- path.expand("~/.cache/irw-comps/kinnear_cj")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
get <- function(url, fn, md5) {
    f <- file.path(cache, fn)
    if (!file.exists(f)) download.file(url, f, mode = "wb")
    stopifnot(unname(tools::md5sum(f)) == md5)
    f
}
fs <- function(id) paste0("https://ndownloader.figshare.com/files/", id)
rekey <- function(x, prefix) paste0(prefix, match(x, unique(x)))
check <- function(df) {
    stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), df$agent_a != df$agent_b,
              df$winner == "agent_a", !anyNA(df$rater))
    df
}

## ---- Clark et al. 2018, Study 2 -----------------------------------------------------
f <- get(fs(8243918), "EloStrengthData.zip", "334fac271f43aba7dd737f8e29a1991c")
x <- read.csv(unz(f, "EloStrengthData/Study2Pairwise.csv"), stringsAsFactors = FALSE)
stopifnot(nrow(x) == 7857, sum(x$winner == x$loser) == 22)
x <- x[x$winner != x$loser, ]
clark <- check(data.frame(agent_a = x$winner, agent_b = x$loser, winner = "agent_a",
                          homefield = "", rater = paste0("r", x$rater),
                          rater_age = x$age, rater_sex = x$sex, trial = x$index))

## ---- Mejia Ramos et al. 2021 -----------------------------------------------------------
x <- read.csv(get(fs(23062304), "ramos_Decisions-combined.csv", "0d025582aa01fb841e7506b96124f6ad"),
              check.names = FALSE, stringsAsFactors = FALSE)
key <- read.csv(get(fs(23062166), "ramos_ModelledRes.csv", "9af091dcf242a8b275b0b871866a34ba"),
                stringsAsFactors = FALSE)
stopifnot(nrow(x) == 760, setequal(c(x[["Candidate Chosen"]], x[["Candidate Not Chosen"]]), key$individual),
          x$Group %in% c("A", "R"), sum(x$Group == "A") == 320)
nm <- setNames(key$name, key$individual)
ramos <- check(data.frame(agent_a = unname(nm[x[["Candidate Chosen"]]]),
                          agent_b = unname(nm[x[["Candidate Not Chosen"]]]),
                          winner = "agent_a", homefield = "", rater = rekey(x$Judge, "j"),
                          date = as.numeric(as.POSIXct(x$createdAt, format = "%d/%m/%Y %H:%M", tz = "UTC")),
                          time_taken = x$timeTaken / 1000,
                          group = ifelse(x$Group == "A", "Auckland", "Rutgers")))
stopifnot(!anyNA(ramos$date), length(unique(ramos$rater)) == 38)

## ---- Sangwin & Kinnear 2021 ------------------------------------------------------------
f <- get("https://zenodo.org/records/4893915/files/georgekinnear/rigour-insight-students-1.0.zip?download=1",
         "sangwin.zip", "6989c6b0ae94aee804b2c1f25e28d88b")
d <- "georgekinnear-rigour-insight-students-dbe3fb6/data-out/"
x <- read.csv(unz(f, paste0(d, "judgement_data_all.csv")), stringsAsFactors = FALSE)
pn <- read.csv(unz(f, paste0(d, "proof_names.csv")))
stopifnot(nrow(x) == 3969, !anyDuplicated(pn$id), c(x$Won, x$Lost) %in% pn$id)
med <- tapply(x$TimeTaken, x$JudgeID, median)
excl <- as.integer(med[as.character(x$JudgeID)] < 5)
stopifnot(sum(excl == 0) == 3485)
pr <- setNames(paste0("proof_", pn$proof), pn$id)
sangwin <- check(data.frame(agent_a = unname(pr[as.character(x$Won)]), agent_b = unname(pr[as.character(x$Lost)]),
                            winner = "agent_a", homefield = "", rater = paste0("j", x$JudgeID),
                            session = paste(x$study, x$dimension, sep = "_"),
                            time_taken = x$TimeTaken, excluded = excl))

## ---- Jones et al. 2020 (Protect our Planet from Solar Storms) ----------------------------
rd <- function(id, fn, md5) {
    ## fread leaves the CSV's doubled quotes inside the JSON fields, so the patterns take "+
    z <- fread(get(fs(id), fn, md5), select = c("user_name", "created_at", "annotations", "subject_data"))
    side <- sub('.*"+value"+:"+Image on the (left|right)"+.*', "\\1", z$annotations)
    a0 <- sub('.*"+asset_0"+:"+([^"]+)"+.*', "\\1", z$subject_data)
    a1 <- sub('.*"+asset_1"+:"+([^"]+)"+.*', "\\1", z$subject_data)
    stopifnot(side %in% c("left", "right"), grepl("\\.jpg$", a0), grepl("\\.jpg$", a1))
    data.frame(user = z$user_name, chosen = ifelse(side == "left", a0, a1),
               other = ifelse(side == "left", a1, a0), side_chosen = side,
               date = as.numeric(as.POSIXct(z$created_at, format = "%Y-%m-%d %H:%M:%S", tz = "UTC")))
}
m <- rd(21923409, "solar_classifications_complete.csv", "cd0d4c26ffc7ce39c48aa52e8856bc74")
b <- rd(21923403, "solar_classifications_brightness_equalised.csv", "b7b30fc1882a1a363c06c39ddb4dcc99")
stopifnot(nrow(m) == 246692, nrow(b) == 163197)
x <- rbind(cbind(m, session = "main"), cbind(b, session = "brightness_equalised"))
jones <- check(data.frame(agent_a = x$chosen, agent_b = x$other, winner = "agent_a", homefield = "",
                          rater = rekey(x$user, "u"),
                          rater_logged_in = as.integer(!startsWith(x$user, "not-logged-in")),
                          date = x$date, session = x$session, side_chosen = x$side_chosen))
stopifnot(!anyNA(jones$date), length(unique(c(jones$agent_a, jones$agent_b))) == 1111)

out <- list(clark_2018_strength_study2 = clark, ramos_2021_proof_explanation = ramos,
            sangwin_2021_proof_rigour_insight = sangwin, jones_2020_cme_complexity = jones)
for (n in names(out)) {
    write.csv(out[[n]], file = paste0(n, ".csv"), row.names = FALSE, na = "")
    cat(n, nrow(out[[n]]), "decisions,", length(unique(c(out[[n]]$agent_a, out[[n]]$agent_b))), "agents,",
        length(unique(out[[n]]$rater)), "raters\n")
}
