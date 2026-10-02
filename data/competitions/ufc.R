## UFC fights 1993-2026, scraped from ufcstats.com by neelagiriaditya
## https://www.kaggle.com/datasets/neelagiriaditya/ufc-datasets-1994-2025
## Licence: CC0 Public Domain (Kaggle API licenseName, checked 2026-09-30).
##
## Ported from the old id_1/id_2/resp layout to the competition standard. The Kaggle
## release no longer ships UFC.csv; this reads fight.csv, event.csv and fighter.csv.
## - agent_a is the red corner, agent_b the blue corner. The red corner is the
##   promotion's billing of the favourite/champion (it wins about two thirds of
##   fights), not a venue advantage, so homefield is left blank.
## - No-contests have no outcome and are dropped; draws are kept as "draw".
## - There are no scores. Agents are fighter names; the 8 names shared by two fighters
##   get the ufcstats fighter id appended so each agent is one person.

cache <- path.expand("~/.cache/irw-comps/ufc-datasets-1994-2025")
if (!file.exists(file.path(cache, "fight.csv"))) {
    dir.create(cache, showWarnings = FALSE, recursive = TRUE)
    zip <- paste0(cache, ".zip")
    download.file("https://www.kaggle.com/api/v1/datasets/download/neelagiriaditya/ufc-datasets-1994-2025",
                  zip, mode = "wb")
    unzip(zip, exdir = cache)
}
f <- read.csv(file.path(cache, "fight.csv"), stringsAsFactors = FALSE)
e <- read.csv(file.path(cache, "event.csv"), stringsAsFactors = FALSE)
p <- read.csv(file.path(cache, "fighter.csv"), stringsAsFactors = FALSE)

dup <- p$fighter_name %in% p$fighter_name[duplicated(p$fighter_name)]
p$agent <- ifelse(dup, paste0(p$fighter_name, " (", p$fighter_id, ")"), p$fighter_name)

f <- f[f$result_status %in% c("win", "draw"), ]
df <- data.frame(agent_a = p$agent[match(f$r_id, p$fighter_id)],
                 agent_b = p$agent[match(f$b_id, p$fighter_id)])
df$date <- as.numeric(as.POSIXct(e$date[match(f$event_id, e$event_id)], format = "%Y-%m-%d", tz = "UTC"))
df$homefield <- ""
df$winner <- ifelse(f$result_status == "draw", "draw",
             ifelse(f$winner_id == f$r_id, "agent_a", "agent_b"))
df$weight_class <- f$weight_class
df$title_fight <- f$title_fight
df$method <- f$method
df$finish_round <- f$round
stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), !anyNA(df$date),
          all(f$winner_id[f$result_status == "win"] %in% c(f$r_id, f$b_id)))
df <- df[order(df$date), ]

write.csv(df, "ufc_1993_2026.csv", row.names = FALSE)
