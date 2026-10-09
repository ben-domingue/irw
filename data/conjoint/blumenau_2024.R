##Politician-representation text conjoints (UK, US, Germany) from
##Blumenau, J., Wolkenstein, F., & Wratil, C. (2024). Citizens' preferences for multidimensional
##representation. Perspectives on Politics, 23(2), 588-610. https://doi.org/10.1017/S1537592724001373
##Replication data: Harvard Dataverse doi:10.7910/DVN/EZDPNP, CC0 1.0, no restricted files.
##Files read: the three Qualtrics exports (Dataverse "original format" .csv, renamed uk.csv, us.csv,
##de.csv: "Measuring+Multidimensional+Representation+-+Conjoint+{UK,USA,DE}_February+9,+2023_*").
##Read as text, not run: plumber_uk.R, plumber_us.R, plumber_de.R (the randomizer that generated
##the profile texts: levels and probabilities), 01_prep_fa.r, 03_prep_conjoint.r, README.txt.
##Usage: Rscript blumenau_2024.R <raw dir> <output dir>
##
##THREE TABLES, one per country (separate samples, attribute texts, parties and issues; the authors
##prepare and analyse each country separately): blumenau_2024_representation_uk / _us / _de.
##Online quota samples recruited through Lucid, 21 May - 5 September 2021 (manuscript.tex; the
##export's column is named PROLIFIC_PID but holds panel IDs). Each respondent read 5 pairs of politician descriptions (task 1-5;
##"Politician 1" = profile 1, "Politician 2" = profile 2) and answered "Which of these politicians
##do you think would better represent you in politics?" (DE: "Welcher dieser Politiker würde Sie
##ihrer Meinung nach besser in der Politik vertreten?"). Forced choice, no opt-out.
##Presentation: text. Each politician is a list of six sentences ("Politician 1..." then
##"...is a man and working class.", "...is the Labour Member of Parliament for your constituency.",
##etc.); the order of the six sentences was drawn once per respondent (plumber: rows <- sample(2:7),
##same for all 5 pairs; verified) -> attrpos_* = sentence position 1-6.
##Attributes (text as displayed, HTML <strong> tags and the leading "..." removed):
##  gender, characteristic: the descriptive sentence "is a man and working class" names the gender
##    (UK/US man/woman; DE Mann/Frau) and ONE further characteristic drawn per pair from ethnicity,
##    sexuality or class (e.g. "working class", "homosexual", "Black"; DE "kommt aus der
##    Mittelschicht", "hat einen türkischen Migrationshintergrund", "ist homosexuell"). In DE the
##    ethnicity level "no migration background" is an empty string, so the sentence reads only
##    "ist ein Mann."; attr_characteristic is then "(not shown)".
##  party, mandate: the surrogation sentence names the party (UK Conservative/Labour; US
##    Republican/Democrat; DE CDU/CSU, SPD, Bündnis 90/Grüne) and the bolded constituency phrase
##    (UK "for your constituency" / "but not for your constituency"; US congressional district;
##    DE five Direkt-/Listenmandat phrases, e.g. "für einen anderen Wahlkreis in Ihrem Bundesland").
##  justification, responsiveness (interview quote), personalization, substantive (supports/opposes
##    an issue; the ISSUE is the same for both politicians of a pair, the position varies): full
##    sentence. DE personalization sentences use "seiner"/"ihrer" Wähler following the
##    politician's gender (plumber_de), so 2 of its 6 levels have masculine and feminine wordings;
##    DE justification is always the feminine wording ("ihrer") in the data (the plumber's gender test
##    never matches; checked).
##Level probabilities are unequal by design (plumber files): ethnicity UK Black .065 / Asian .075 /
##White .86; US White .63, Black .13, Asian .06, Hispanic .18; DE no migration background .8, each
##other .2/3; sexuality heterosexual .9 / homosexual .1; others uniform.
##Kept: consenting respondents with Progress 100 and tasks with an answer; tasks whose sentences are
##missing are dropped. Not applied (recorded instead): the authors' speeder rule (duration < 300 s;
##cov_duration_sec) and attention check (pers_rep1_5 must be "Agree" / "Stimme zu";
##cov_attention_pass). Many completes have no conjoint answers (they were not routed to it).
##N check: respondents with cov_attention_pass == 1 and cov_duration_sec >= 300 number UK 2,202 /
##US 2,175 / DE 2,121 vs the article's analysis samples 2,204 / 2,178 / 2,049 (the DE prep also
##drops missing education and unfinished cases; the US prep times "Duration (in seconds)").
##Covariates (answer text as exported): cov_gender (Male/Female, DE Männlich/Weiblich -> male/female;
##blank NA), cov_birth_year (plausible 1900-2005), cov_education, cov_class, cov_sexuality,
##cov_ethnicity (UK/US; DE cov_migration_background), cov_vote_last (gen_election_retro; US
##house_election_retro), cov_ideology (general_ideology), cov_region (UK result.0.region or
##result.0.country, US State, DE Region), cov_attention_pass, cov_duration_sec (Q_TotalDuration).
##The authors' raking weights are computed in 01_prep_fa.r, not deposited (survey_weight not_kept).
##PII in the exports, not read: Prolific IDs, postcodes, UK parliamentary constituency, free-text
##answers (rep_chosen). No IP addresses. Respondents re-keyed to integers in export order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
strip <- function(s) trimws(gsub("\\s+", " ", gsub("^\\.\\.\\.", "", gsub("<[^>]+>", "", s))))
bold <- function(s) sapply(regmatches(s, gregexpr("<strong>[^<]*</strong>", s)), function(m) gsub("</?strong>", "", m), simplify = FALSE)
cfg <- list(
  uk = list(f = "uk.csv", lab = "Politician", surr = "Member of Parliament", resp = "said in a recent interview",
            subst = "<strong>(supports|opposes)</strong>", just = "^\\.\\.\\.regularly", pers = "party leadership|party instructions",
            gender = c(man = "male", woman = "female"), vote = "gen_election_retro", region = "result.0.region",
            g = c(Male = "male", Female = "female"), att = "Agree", eth = "Ethnicity"),
  us = list(f = "us.csv", lab = "Politician", surr = "congress", resp = "said in a recent interview",
            subst = "<strong>(supports|opposes)</strong>", just = "^\\.\\.\\.regularly", pers = "party leadership|party instructions",
            vote = "house_election_retro", region = "State", g = c(Male = "male", Female = "female"), att = "Agree", eth = "Ethnicity"),
  de = list(f = "de.csv", lab = "Politiker", surr = "Bundestagsabgeordnete", resp = "sagte kürzlich in einem Interview",
            subst = "<strong>(befürwortet|lehnt)</strong>", just = "^\\.\\.\\.(betont|erklärt|rechtfertigt)", pers = "kritisiert und stimmt|stimmt in der Regel",
            vote = "gen_election_retro", region = "Region", g = c("Männlich" = "male", Weiblich = "female"), att = "Stimme zu", eth = "Migr_back"))
types <- c("descriptive", "surrogation", "justification", "responsiveness", "personalization", "substantive")
for (cc in names(cfg)) {
  C <- cfg[[cc]]
  sc <- c(outer(outer(1:2, 1:7, function(p, k) paste0("mp_", p, "_sentence_", k)), 1:5, function(pk, t) paste0(pk, "_", t, ".0")))
  keep <- c("ResponseId", "Consent", "Progress", "Gender", "Birth", "Education", "Class", "Sexuality", C$eth, C$vote, "general_ideology",
            C$region, "pers_rep1_5", "Q_TotalDuration", paste0("conjoint_", 1:5), sc, if (cc == "uk") "result.0.country")
  x <- fread(file.path(raw, C$f), select = keep, encoding = "UTF-8", colClasses = "character")[-(1:2)]
  x <- x[Progress == "100" & Consent != "" & !grepl("do not want|möchte nicht", Consent) & conjoint_1 != ""]
  x[, rid := .I]
  # sentence types from task 1, politician 1; the same order must hold for every task and politician
  ty <- function(s) fifelse(grepl(C$surr, s), "surrogation", fifelse(grepl(C$resp, s), "responsiveness", fifelse(grepl(C$subst, s), "substantive",
          fifelse(grepl(C$just, s), "justification", fifelse(grepl(C$pers, s), "personalization", "descriptive")))))
  pos <- sapply(2:7, function(k) ty(x[[paste0("mp_1_sentence_", k, "_1.0")]]))
  stopifnot(all(apply(pos, 1, function(r) setequal(r, types))))
  L <- list()
  for (t in 1:5) for (p in 1:2) {
    ch <- x[[paste0("conjoint_", t)]]
    r <- data.table(rid = x$rid, task = t, profile = p,
                    choice = fifelse(ch == "", NA_integer_, as.integer(ch == paste(C$lab, p))))
    S <- sapply(2:7, function(k) x[[paste0("mp_", p, "_sentence_", k, "_", t, ".0")]])
    ok <- rowSums(S == "" | is.na(S)) == 0
    stopifnot(all(sapply(1:6, function(k) all(ty(S[ok, k]) == pos[ok, k]))))
    get <- function(tp) { o <- character(nrow(S)); kk <- integer(nrow(S))
      for (k in 1:6) { w <- pos[, k] == tp; o[w] <- S[w, k]; kk[w] <- k }; list(o, kk) }
    de_ <- get("descriptive"); su <- get("surrogation")
    b <- bold(de_[[1]])
    r[, attr_gender := sapply(b, function(v) if (length(v)) v[1] else NA_character_)]
    if (cc == "de") {
      rest <- sub("^\\.\\.\\.ist eine? <strong>(Mann|Frau)</strong>( und )?", "", de_[[1]])
      r[, attr_characteristic := fifelse(rest == ".", "(not shown)", strip(sub("\\.$", "", rest)))]
    } else r[, attr_characteristic := sapply(b, function(v) if (length(v) == 2) v[2] else NA_character_)]
    bs <- bold(su[[1]])
    r[, attr_party := sapply(bs, `[`, 1)][, attr_mandate := sapply(bs, function(v) v[length(v)])]
    for (tp in c("justification", "responsiveness", "personalization", "substantive")) r[, paste0("attr_", tp) := strip(get(tp)[[1]])]
    r[, `:=`(attrpos_gender = de_[[2]], attrpos_characteristic = de_[[2]], attrpos_party = su[[2]], attrpos_mandate = su[[2]],
             attrpos_justification = get("justification")[[2]], attrpos_responsiveness = get("responsiveness")[[2]],
             attrpos_personalization = get("personalization")[[2]], attrpos_substantive = get("substantive")[[2]])]
    L[[length(L) + 1]] <- r[ok]
  }
  d <- rbindlist(L)
  d <- d[!is.na(choice)]
  d <- d[d[, .N, .(rid, task)][N == 2], on = .(rid, task)][, N := NULL]
  stopifnot(d[, sum(choice), .(rid, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr")]))
  stopifnot(d[, uniqueN(sub("( ab)?\\.$", "", sub("^.*?(supports|opposes|befürwortet|lehnt) ", "", attr_substantive))), .(rid, task)][, all(V1 == 1)])
  bl <- function(v) { v <- trimws(v); v[v == ""] <- NA; v }
  by <- suppressWarnings(as.integer(x$Birth)); by[!is.na(by) & (by < 1900 | by > 2005)] <- NA
  reg <- bl(x[[C$region]]); if (cc == "uk") reg[is.na(reg)] <- bl(x$result.0.country)[is.na(reg)]
  cv <- data.table(rid = x$rid, cov_gender = unname(C$g[x$Gender]), cov_birth_year = by, cov_education = bl(x$Education),
                   cov_class = bl(x$Class), cov_sexuality = bl(x$Sexuality), cov_vote_last = bl(x[[C$vote]]),
                   cov_ideology = bl(x$general_ideology), cov_region = reg,
                   cov_attention_pass = fifelse(bl(x$pers_rep1_5) == C$att, 1L, 0L, NA_integer_),
                   cov_duration_sec = suppressWarnings(as.integer(x$Q_TotalDuration)))
  cv[, (if (cc == "de") "cov_migration_background" else "cov_ethnicity") := bl(x[[C$eth]])]
  d <- merge(d, cv, by = "rid")
  setnames(d, "rid", "id")
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0("blumenau_2024_representation_", cc, ".csv")))
}
