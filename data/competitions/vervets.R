##Wild vervet monkey dyadic aggressive interactions, 2015-2017. Vilette, C., Bonnell, T.,
##Henzi, P., & Barrett, L. (2020). Comparing dominance hierarchy methods using a
##data-splitting approach with real-world data. Behavioral Ecology, 31(6), 1379-1390.
##https://doi.org/10.1093/beheco/araa095
##Data: Dryad doi:10.5061/dryad.612jm641s, read from its Zenodo mirror, record 4725846
##(https://zenodo.org/records/4725846), file dominance.data.csv.
##Licence: Zenodo API for the record, "license": {"id": "cc-by-4.0"} (CC BY 4.0), checked
##2026-10-01. The deposit also contains a GPL-3 LICENSE file; it belongs to the bundled R
##package rankReliability (its DESCRIPTION: "License: GPL-3") and covers that code, not
##the data. Only dominance.data.csv is read here.
##
##One row per interaction, in source order, keeping the source orientation: agent_a =
##`from` (the aggressor), agent_b = `to` (the recipient). The source's `result` is kept and
##sets winner (README: "Win = 1 - Loss =2 - Draw = 3", from the aggressor's side):
##  1 -> "agent_a"; 2 -> "agent_b"; 3 (draw = TRUE in the source) -> "draw";
##  4 (undocumented; winner and loser are both 0 in the source, i.e. no outcome) -> "draw".
##So "draw" covers both native draws and undecided interactions; use `result` (3 vs 4) to
##tell them apart. date = date in Unix seconds, UTC midnight. day_nb, max_agg_aggressor and
##max_agg_victim (the most intense behaviour by each side) are kept. homefield is blank.
##One source row (2017-08-24) has the same animal as aggressor and recipient (sash v
##sash), an entry error; it is dropped.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/4725846")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "dominance.data.csv")
if (!file.exists(f))
  download.file("https://zenodo.org/api/records/4725846/files/dominance.data.csv/content", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "7d40492c1b5e6be9d187d6bb4e985ad7")
x <- read.csv(f, stringsAsFactors = FALSE, na.strings = "")
stopifnot(all(x$result %in% 1:4), all(x$draw == (x$result == 3)))
self <- x$from == x$to
stopifnot(sum(self) == 1)
x <- x[!self, ]

df <- data.frame(agent_a = x$from, agent_b = x$to,
                 date = as.numeric(as.POSIXct(x$date, format = "%Y-%m-%d", tz = "UTC")),
                 homefield = "",
                 winner = c("agent_a", "agent_b", "draw", "draw")[x$result],
                 result = x$result, day_nb = x$day_nb,
                 max_agg_aggressor = x$Max.Agg.Aggressor, max_agg_victim = x$Max.agg.victim)
stopifnot(!anyNA(df$date), df$agent_a != df$agent_b,
          all(x$winner[x$result == 1] == x$from[x$result == 1]),
          all(x$winner[x$result == 2] == x$to[x$result == 2]))
out <- "vervets_2015_2017.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "interactions,", length(unique(c(df$agent_a, df$agent_b))), "monkeys;",
    sum(df$result == 3), "draws,", sum(df$result == 4), "undecided\n")
