##Gombe chimpanzee dominance interactions (winner/loser as recorded in the deposit),
##Gombe National Park, Tanzania. Foerster, S., Franz, M., Murray, C. M.,
##Gilby, I. C., Feldblum, J. T., Walker, K. K., & Pusey, A. E. (2016). Chimpanzee females
##queue but males compete for social status. Scientific Reports, 6, 35404.
##https://doi.org/10.1038/srep35404
##Data: Dryad doi:10.5061/dryad.r4g74, read from its Zenodo mirror, record 4945588
##(https://zenodo.org/records/4945588), files male_ago.xls and female_ago.xls.
##Licence: Zenodo API for the record, "license": {"id": "cc-zero"} (CC0 1.0), checked
##2026-10-01.
##
##Males and females are analysed as separate hierarchies in the paper and the ids are numbered
##separately in each file, so each sex is its own table (_males_1978_2011, _females_1969_2013).
##
##One row per interaction, in source order (sheet "male_ago" / "female_ago": Date,
##Winner, Loser). agent_a = Winner, agent_b = Loser, so winner is always "agent_a" (the
##source records no draws). date = Date (dd.mm.yyyy) in Unix seconds, UTC midnight.
##homefield is blank.

library(readxl)
cache <- path.expand("~/.cache/irw-comps/discovery-1001/4945588")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
md5 <- c(male_ago.xls = "cb678a0413b9abc849fa1cefaa370b11", female_ago.xls = "aeadddb7b8616c4d0feb7de18847ac87")

for (sex in c("male", "female")) {
  fn <- paste0(sex, "_ago.xls")
  f <- file.path(cache, fn)
  if (!file.exists(f))
    download.file(paste0("https://zenodo.org/api/records/4945588/files/", fn, "/content"), f, mode = "wb")
  stopifnot(unname(tools::md5sum(f)) == md5[[fn]])
  x <- as.data.frame(read_excel(f, sheet = paste0(sex, "_ago"), col_types = "text"))
  df <- data.frame(agent_a = as.integer(x$Winner), agent_b = as.integer(x$Loser),
                   date = as.numeric(as.POSIXct(x$Date, format = "%d.%m.%Y", tz = "UTC")),
                   homefield = "", winner = "agent_a")
  stopifnot(!anyNA(df), df$agent_a != df$agent_b)
  yrs <- format(as.POSIXct(range(df$date), origin = "1970-01-01", tz = "UTC"), "%Y")
  out <- paste0("gombe_chimpanzees_", sex, "s_", yrs[1], "_", yrs[2], ".csv")
  write.csv(df, out, row.names = FALSE, na = "")
  cat(out, nrow(df), "interactions,", length(unique(c(df$agent_a, df$agent_b))), "animals\n")
}
