##Spotted hyena dominance interactions, Talek clan, Masai Mara (Mara Hyena Project).
##Strauss, E. D., & Holekamp, K. E. (2019). Inferring longitudinal hierarchies: framework
##and methods for studying the dynamics of dominance. Journal of Animal Ecology, 88(4),
##521-536.
##https://doi.org/10.1111/1365-2656.12951
##Data: Dryad doi:10.5061/dryad.5p9m3q2, read from its Zenodo mirror, record 5009497
##(https://zenodo.org/records/5009497), FinalSubmissionDryad.zip, object
##3.hyena_data.RData (the authors' "tidy data file (start here)").
##Licence: Zenodo API for the record, "license": {"id": "cc-zero"} (CC0 1.0), checked
##2026-10-01.
##
##The deposit holds adult-female and adult-male interactions as separate hierarchies
##(female.interactions, male.interactions), so each sex is its own table. Per the authors'
##2.prep_empirical_data.R, a row is an aggression in which the recipient did not ignore or
##counterattack; the aggressor is the winner.
##
##One row per interaction, in source order. agent_a = winner (aggressor), agent_b = loser
##(recipient), so winner is always "agent_a". The tidy file keeps only the year, so there
##is no `date`; `year` is the source's period. Agents are the Mara Hyena Project's hyena
##codes. homefield is blank. (A dated female subset, 8,482 rows restricted to animals
##present on that day, is in 12.hyena_data_daily_period.RData; it is not used here.)

cache <- path.expand("~/.cache/irw-comps/discovery-1001/5009497")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
z <- file.path(cache, "FinalSubmissionDryad.zip")
if (!file.exists(z))
  download.file("https://zenodo.org/api/records/5009497/files/FinalSubmissionDryad.zip/content", z, mode = "wb")
stopifnot(unname(tools::md5sum(z)) == "898151ddefed1dd932774d30811b797e")
e <- new.env()
load(unzip(z, "FinalSubmissionDryad/3.hyena_data.RData", exdir = tempdir()), e)

for (sex in c("female", "male")) {
  x <- get(paste0(sex, ".interactions"), e)
  df <- data.frame(agent_a = x$winner, agent_b = x$loser, homefield = "", winner = "agent_a",
                   year = x$period)
  stopifnot(!anyNA(df), df$agent_a != df$agent_b)
  out <- paste0("talek_hyenas_", sex, "s_", min(df$year), "_", max(df$year), ".csv")
  write.csv(df, out, row.names = FALSE, na = "")
  cat(out, nrow(df), "interactions,", length(unique(c(df$agent_a, df$agent_b))), "hyenas\n")
}
