##Spotted hyena aggressive interactions in three Masai Mara clans other than Talek
##(Mara Hyena Project): Happy Zebra, Serena North and Serena South as the deposit codes
##them (happy.zebra, serena.n, serena.s).
##McCormick, S. K., Laubach, Z. M., Strauss, E. D., Montgomery, T. M., & Holekamp, K. E.
##(2022). Evaluating drivers of female dominance in the spotted hyena. Frontiers in Ecology
##and Evolution, 10, 934659. https://doi.org/10.3389/fevo.2022.934659
##Data: Dryad doi:10.5061/dryad.w6m905qsw, read from its Zenodo mirror, record 7402457
##(https://zenodo.org/records/7402457), file tblAggression_AllClan_Age_Sex_Raw_Dryad.csv
##(95,626 acts in four clans). The authors' analysis code is Zenodo record 7327369,
##Dominance_Support_Special_Issue_for_Publication_(Dryad_Final).R.
##Licence: Zenodo API for record 7402457, "license": {"id": "cc-zero"} (CC0 1.0), checked
##2026-10-01. (The code record 7327369 is MIT; no code is copied here.)
##
##Talek is left out: it is already in talek_hyenas_females_* and talek_hyenas_males_*
##(Strauss & Holekamp 2019, data/competitions/talek_hyenas.R). Ben ruled 10-01 (#2673):
##the three other clans, one table per clan, CC0, same win/loss rule as talek_hyenas.R.
##
##WIN/LOSS RULE (the Talek rule, the authors' own). Strauss & Holekamp's
##2.prep_empirical_data.R (Zenodo 5009497, FinalSubmissionDryad.zip) keeps an aggression
##as a decided contest unless the recipient ignored or counterattacked:
##  excludeResponse <- c("ignores", "ignore", "ct", "counterattack", "counter",
##                       "counters", "counterattacks")
##  drop rows whose response1/2/3 is in excludeResponse, and rows whose context is
##  'ct'/'counter'/'counterattack'; every remaining row is aggressor = winner.
##McCormick's file has response1 only. Mapping its recipient response codes onto that rule
##(the deposit README does not decode the codes; the decoding below is from the two
##Mara Hyena Project scripts that use them):
##  DROPPED (recipient ignored or counterattacked):
##    response1 "ignore"        (in excludeResponse)
##    response1 "ct"            (counterattack; in excludeResponse beside its spellings)
##    Context  "counterattack"  (the act is itself a counterattack; dropped by both
##                               Strauss's script and McCormick's, line 39)
##  AGGRESSOR WINS (everything else), namely:
##    the twelve submissive responses McCormick's script scores as a win (its lines
##      59-71): bo, cc, dp, eb, grin, hb, run, sp, squeal, s1, s2, s3;
##    the other recorded responses, which the Talek rule does not exclude: gig, brt,
##      growl, scape, av w/ fd, squitter, groan, whoop, funny grin, alarm rumble, and
##      the stray numeric codes 1, 2, 3;
##    a blank response1 or "unknown": the Talek rule keeps these too (NA is not in
##      excludeResponse). McCormick drops them; users who want McCormick's stricter
##      reading can filter on `response1`.
##  So this table is NOT McCormick's "Win" variable (which scores non-submissive
##  responses as losses); it is the Talek rule, kept comparable with talek_hyenas_*.
##
##One row per act, in source order (Session, aggid). agent_a = aggressor (ID), agent_b =
##recipient, winner always "agent_a", homefield blank. The file has no date or year
##(sessions are coded "s<n>"; the session numbers in the deposit's count files use a
##different scheme and do not join), so there is no `date`. Kept from the source:
##session, aggid, context, location, sequence (0 alone, 1 coalition, 2 joined an ongoing
##aggression; a few out-of-range values kept as recorded), intensity (1-3), response1,
##and each party's sex, status (r resident / i immigrant) and age class. Hyena codes are
##the project's own; some hyenas appear in more than one clan's table (immigrant males
##and the Serena fission), with the same code.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/7402457")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
fn <- "tblAggression_AllClan_Age_Sex_Raw_Dryad.csv"
f <- file.path(cache, fn)
if (!file.exists(f))
  download.file(paste0("https://zenodo.org/api/records/7402457/files/", fn, "/content"), f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "994a2a56b2704c529f9b3709fdf8852f")
x <- read.csv(f, stringsAsFactors = FALSE, na.strings = "")
stopifnot(nrow(x) == 95626, !anyNA(x$ID), !anyNA(x$Recipient), x$ID != x$Recipient)

excl_response <- c("ignore", "ct")
known <- c(excl_response, "bo", "cc", "dp", "eb", "grin", "hb", "run", "sp", "squeal",
           "s1", "s2", "s3", "gig", "brt", "growl", "scape", "av w/ fd", "squitter", "groan",
           "whoop", "funny grin", "alarm rumble", "1", "2", "3", "unknown")
stopifnot(is.na(x$response1) | x$response1 %in% known)   # no unmapped code

clans <- c(happy.zebra = "happyzebra_hyenas", serena.n = "serena_n_hyenas",
           serena.s = "serena_s_hyenas")
for (cl in names(clans)) {
  d <- x[x$clan == cl, ]
  n0 <- nrow(d)
  d <- d[!(d$response1 %in% excl_response) & d$Context != "counterattack", ]
  df <- data.frame(agent_a = d$ID, agent_b = d$Recipient, homefield = "", winner = "agent_a",
                   session = d$Session, aggid = d$aggid, context = d$Context,
                   location = d$location, sequence = d$Sequence, intensity = d$Intensity,
                   response1 = d$response1,
                   agent_a_sex = d$Actor_Sex, agent_b_sex = d$Recipient_Sex,
                   agent_a_status = d$Actor_Status, agent_b_status = d$Recipient_Status,
                   agent_a_age_class = d$Actor_Age_Class, agent_b_age_class = d$Recipient_Age_Class)
  stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), !anyNA(df$context))
  out <- paste0(clans[[cl]], ".csv")
  write.csv(df, out, row.names = FALSE, na = "")
  cat(out, nrow(df), "interactions (", n0 - nrow(df), "ignored/counterattack dropped ),",
      length(unique(c(df$agent_a, df$agent_b))), "hyenas\n")
}
