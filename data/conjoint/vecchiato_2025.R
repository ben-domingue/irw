##Text and visual (Twitter-profile) candidate conjoints from
##Vecchiato, A., & Munger, K. (2025). Introducing the visual conjoint, with an application to
##candidate evaluation on social media. Journal of Experimental Political Science, 12(1), 57-71.
##https://doi.org/10.1017/XPS.2024.15
##Replication data: Harvard Dataverse doi:10.7910/DVN/TIBNLH, CC0 1.0, no restricted files.
##File read: STAN0156_OUTPUT.csv (Dataverse "original format" download of STAN0156_OUTPUT.tab,
##the YouGov export). standard.RData and image.RData (the authors' reshaped files) are used only
##as checks, not as the source. Design facts from the article (Experimental design, Table 1) and
##its online appendix (survey instrument Q66/Q68; App. C, D).
##Usage: Rscript vecchiato_2025.R <raw dir> <output dir>
##
##500 YouGov America respondents (Facebook or Twitter users; matched down from 653; fielded
##early 2022). Every respondent did BOTH conjoints, 10 pairs each, of hypothetical Members of
##Congress with the same 9 dimensions (Table 1). The two modalities are separate designs, so
##TWO TABLES:
##  vecchiato_2025_candidates_text   : standard box conjoint (source conj<t><A|B>_<attr>,
##     conjointq_<t> = "Profile A"/"Profile B"); task = t, profile 1 = A.
##  vecchiato_2025_candidates_visual : each profile is a mock Twitter profile image (bio text,
##     official photo of a low-profile member of Congress, follower/like counts, two partisan
##     tweets). Source imageconjfilename1-20 (images 2t-1 and 2t form pair t) and
##     imageconj<t> = "Profile 1"/"Profile 2"; task = t, profile 1 = image 2t-1 (verified against
##     the authors' image.RData: same choices).
##Outcome (both): "Which of these politicians would you rather have as your Representative in
##Congress?" (instrument Q68; intro: "tell us which politician you'd prefer to be your
##representative in Congress"). Forced choice, no opt-out. 8 visual tasks were "skipped"
##(no answer) and are omitted (the authors' image.RData keeps them with choice 0 on both).
##The article says "five candidate-pair (tasks)" but also 10,000 observations per conjoint for
##500 respondents; the data have 10 pairs per conjoint per respondent, as stored here.
##Attributes, text conjoint: level text as exported (Generation Boomer/Millennial, Gender, Race,
##Party, Military "Served"/"Not Served", Education High School/College/Ivy League, religion
##(source column `ideo`; the authors rename it Religion), Profession, Feedback "A few"/"A lot").
##Attributes, visual conjoint: decoded from the image file names, written with the authors'
##Table 1 level labels so that the two tables line up. In the image, gender is shown by the
##photo and the "Congressman"/"Congresswoman" title, race only by the photo, generation by
##birth year in the bio (1955 / 1971) and photo, party/education/profession/military/religion
##in the bio text ("Iservedinthemilitary" absent = "Not Served"; religion absent from the bio
##= "No Religion", the authors' coding), feedback by follower/like/retweet counts drawn from
##level-specific ranges (App. D). The two tweet-variant codes in each file name (one of two
##tweets per slot, drawn from party-specific lists; text not deposited) are DROPPED: the
##authors keep them as controls only, and no label survives. Which photo was used is not
##recorded beyond race x gender.
##The authors' image.RData codes profession differently from the file names for 919 profiles
##(753 "lawyer" images coded Entrepreneur, 166 "farmer" images coded Lawyer); the file names are
##what respondents saw and are used here. Choices and all other attributes agree with image.RData.
##The text table reproduces the authors' standard.RData level counts exactly.
##Spot check (weighted LPM, SE clustered by id): served in military +0.076 (text), +0.045
##(visual); the article reports veterans preferred in both (Fig. 2).
##Restrictions: yes. App. C: "some professions require high levels of education, and
##therefore could not be uniformly paired" (doctor, lawyer, teacher appear about half as often).
##Attribute row order: not documented, not in the data.
##Covariates: YouGov profile items as exported text (birth year, gender, race, education,
##marital status, children, employment, income, state, region, party id 3/7, registration,
##2020 turnout and vote, ideology, news interest, 2016 vote, religion items), social-media
##use (social_media_1-5, 99 = none), q1 Twitter/FB use frequency, q2_a-f internet skills (1 = No
##understanding .. 5 = Full understanding), q3_a-g power-user items (-3 = Strongly disagree ..
##3 = Strongly agree); weight -> cov_survey_weight (the authors weight their AMCEs).
##Dropped: YouGov caseid (re-keyed to 1..500), consent, attention checks, free-text "other"
##fields (employ_t, pid3_t, religpew_t), start/end timestamps.
##N = 500 matches the article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "STAN0156_OUTPUT.csv"), na.strings = c("", "__NA__"))
stopifnot(nrow(s) == 500, !anyDuplicated(s$caseid))
setorder(s, caseid)
s[, rid := .I]
covs <- c(paste0("social_media_", c(1:5, 99)), "q1", paste0("q2_", letters[1:6]), paste0("q3_", letters[1:7]),
          "birthyr", "gender_demo", "race", "educ_demo", "marstat", "child18", "employ", "faminc_new", "inputstate",
          "region", "pid3", "pid7", "votereg", "turnout20post", "presvote20post", "ideo5", "newsint", "presvote16post",
          "pew_bornagain", "pew_religimp", "pew_churatd", "pew_prayer", "religpew", "religpew_protestant")
cv <- s[, c("rid", "weight", covs), with = FALSE]
setnames(cv, c("rid", "weight", covs), c("rid", "cov_survey_weight", paste0("cov_", sub("_demo$", "", covs))))

## text conjoint
at <- c(generation = "gen", gender = "gender", race = "race", party = "party", military = "military",
        education = "education", religion = "ideo", profession = "profession", feedback = "feedback")
tx <- rbindlist(lapply(1:10, function(t) rbindlist(lapply(c("A", "B"), function(p) {
  d <- data.table(rid = s$rid, task = t, profile = match(p, c("A", "B")),
                  choice = as.integer(s[[paste0("conjointq_", t)]] == paste("Profile", p)))
  for (v in names(at)) d[, paste0("attr_", v) := s[[paste0("conj", t, p, "_", at[[v]])]]]
  d[is.na(s[[paste0("conjointq_", t)]]), choice := NA]
}))))
stopifnot(all(s[, unlist(.SD), .SDcols = paste0("conjointq_", 1:10)] %in% c("Profile A", "Profile B")),
          tx[, sum(choice), .(rid, task)][, all(V1 == 1)], !anyNA(tx))

## visual conjoint
lab <- list(race = c(Bl = "Black", Wh = "White"), gender = c(man = "Male", woman = "Female"),
            party = c(democrat = "Democrat", republican = "Republican"),
            generation = c(boomer = "Boomer", millennial = "Millennial"), feedback = c(high = "High", low = "Low"),
            military = c(Iservedinthemilitary = "Served", none = "Not Served"),
            education = c(HighSchoolgraduate = "High School", Collegegraduate = "College", IvyLeaguegraduate = "Ivy League"),
            profession = c(acardealer = "Used Car Dealer", adoctor = "Doctor", afarmer = "Farmer", alawyer = "Lawyer",
                           anenterpreneur = "Entrepreneur", ateacher = "Teacher"),
            religion = c(Catholic = "Catholic", Jewish = "Jewish", Mormon = "Mormon", Protestant = "Protestant",
                         none = "No Religion"))
im <- rbindlist(lapply(1:20, function(k) {
  f <- sub("\\.png$", "", s[[paste0("imageconjfilename", k)]])
  p <- tstrsplit(f, "_", fixed = TRUE); stopifnot(length(p) == 11)
  t <- (k + 1L) %/% 2L; pr <- 2L - k %% 2L; ans <- s[[paste0("imageconj", t)]]
  d <- data.table(rid = s$rid, task = t, profile = pr,
                  choice = ifelse(ans == "skipped", NA_integer_, as.integer(ans == paste("Profile", pr))))
  tok <- list(race = p[[1]], gender = p[[2]], party = p[[3]], generation = p[[4]], feedback = p[[5]],
              military = p[[6]], education = p[[7]], profession = p[[8]], religion = p[[9]])
  for (v in names(tok)) { x <- tok[[v]]; x[x == ""] <- "none"; stopifnot(all(x %in% names(lab[[v]])))
    d[, paste0("attr_", v) := unname(lab[[v]][x])] }
  d
}))
im <- im[!is.na(choice)]
stopifnot(im[, sum(choice), .(rid, task)][, all(V1 == 1)], im[, .N, .(rid, task)][, all(N == 2)])
setcolorder(im, names(tx))

for (x in list(list(tx, "vecchiato_2025_candidates_text"), list(im, "vecchiato_2025_candidates_visual"))) {
  d <- merge(x[[1]], cv, by = "rid")
  setnames(d, "rid", "id")
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(x[[2]], ".csv")))
}
