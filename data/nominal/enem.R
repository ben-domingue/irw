# ENEM nominal tables (issue #1353).
#
# text = the letter the examinee actually marked: A-E, plus the two documented
# INEP codes "." (blank / omitted) and "*" (double mark). Both are kept verbatim
# rather than mapped to NA, so an omission stays distinguishable from a wrong
# answer -- ENEM has real position/speededness effects and the omits are the
# evidence for them. n_categories is therefore 7, not 5.
#
# resp is retained alongside text as the scored 0/1, per the nominal standard
# and the precedent in borges_brazil.R / himmelstein.R / wilmer.R / asap20.R.
# "." and "*" score 0, which is what INEP does.
#
# NB: the 52 delivered files were generated on FarmShare from the same frames as
# the warehouse tables, and shipped as .Rdata -- these tables are ~45M rows each,
# so write.table(sep="|") across all 52 would be ~90 GB. This wrapper is the
# reproducible path from the published tables.

for (y in 2013:2025) for (a in c("lc", "ch", "cn", "mt")) {
  nm <- sprintf("enem_%d_1mil_%s", y, a)
  df <- irw::irw_fetch(nm)
  df$text <- df$resp_raw
  df$resp_raw <- NULL
  write.table(df, nm, quote = FALSE, row.names = FALSE, sep = "|")
}
