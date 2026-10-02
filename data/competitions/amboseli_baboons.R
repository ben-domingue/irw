##Adult male baboon dominance interactions, Amboseli Baboon Research Project, five social
##groups. Franz, M., McLean, E., Tung, J., Altmann, J., & Alberts, S. C. (2015).
##Self-organizing dominance hierarchies in a wild primate population. Proceedings of the
##Royal Society B, 282, 20151512. https://doi.org/10.1098/rspb.2015.1512
##Data: Dryad doi:10.5061/dryad.d0g0d, read from its Zenodo mirror, record 4968348
##(https://zenodo.org/records/4968348), file ago_data.csv.
##Licence: Zenodo API for the record, "license": {"id": "cc-zero"}; Dryad API
##"license": "https://spdx.org/licenses/CC0-1.0.html" (CC0 1.0), checked 2026-10-01.
##
##Animal ids restart at 1 in every group (the same number is a different male in another
##group), so each group is its own actor pool and its own table (amboseli_baboons_g1 ... _g5).
##
##One row per agonistic interaction with a clear winner, in source order. agent_a = Winner,
##agent_b = Loser, so winner is always "agent_a" (the source records no draws). There is
##no calendar date: the source's Date column is a day count (starting at 0; the deposit does not give the calendar origin),
##kept as `day`. homefield is blank. The source's per-interaction covariates are kept and
##renamed to the a/b orientation: hybrid_a/b (genetic hybrid score), age_a/b (years),
##lag_day_a/b (days since that male's previous interaction), aggr_index.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/4968348")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "ago_data.csv")
if (!file.exists(f))
  download.file("https://zenodo.org/api/records/4968348/files/ago_data.csv/content", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "e2d8c21a9422f7e98658c17c562b56c7")
x <- read.csv(f, sep = ";")
stopifnot(nrow(x) == 15917, all(x$Winner != x$Loser))

for (g in sort(unique(x$Group))) {
  y <- x[x$Group == g, ]
  df <- data.frame(agent_a = y$Winner, agent_b = y$Loser, homefield = "", winner = "agent_a",
                   day = y$Date, hybrid_a = y$hybrid_w, hybrid_b = y$hybrid_l,
                   age_a = y$Age_w, age_b = y$Age_l, lag_day_a = y$Lag_day_w,
                   lag_day_b = y$Lag_day_l, aggr_index = y$aggr_index)
  out <- paste0("amboseli_baboons_g", g, ".csv")
  write.csv(df, out, row.names = FALSE, na = "")
  cat(out, nrow(df), "interactions,", length(unique(c(df$agent_a, df$agent_b))), "males\n")
}
