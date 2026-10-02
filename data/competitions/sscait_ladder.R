## SSCAIT (Student StarCraft AI Tournament & Ladder) bot ladder games, 2021-03 to 2024-01 (#2681).
##
## Source: https://sscaitournament.com/api/games.php?future=false&count=1000&page=<p>, the
## site's JSON game list (fields result, map, note, timestamp, host, guest, replay). The API
## serves 1,000 games per page, newest first; pages 1-116 hold 115,183 games, 2021-03-29 to
## 2024-01-06. No games have been played since: the home page says "games/tournaments are no
## longer played ... as this website was migrated to a new owner and host" (checked
## 2026-10-01), so the list is closed. The API does not reach the earlier ladder years.
## Pages are cached in ~/.cache/irw-comps/sscait/ (fetched 2026-10-01, 3 s apart).
##
## Licence: site footer, "The content on this page is released under Creative Commons license
## 4.0, except for the part(s) of this page that are explicitly stated to be under a different
## license (if any)", the link going to https://creativecommons.org/licenses/by-nc/4.0/
## (checked 2026-10-01). Non-commercial, accepted by Ben's 10-01 ruling on #2681; Derived
## License = CC BY-NC 4.0.
##
## Reference: Certicky, M., Churchill, D., Kim, K.-J., Certicky, M., & Kelly, R. (2018).
## StarCraft AI competitions, bots, and tournament manager software. IEEE Transactions on
## Games, 11(3), 227-237. doi:10.1109/TG.2018.2883499 (the citation the site asks for).
##
## Choices (rules page, https://sscaitournament.com/index.php?action=rules, checked 2026-10-01):
## - agent_a = host, agent_b = guest. result "1" = host won, "2" = guest won (every
##   "bot2_crashed" note has result 1, every "bot1_crashed" note result 2). homefield is
##   blank: host/guest is a slot, not a home side.
## - Every game has a winner. The rules: a bot "loses immediately" if it crashes, so crash
##   games are kept as decided games (crashed = "agent_a"/"agent_b" names the bot that
##   crashed). "Draw results are no longer possible": a game that hits the time limit (90
##   in-game minutes, or 5 real minutes with no unit dying) goes to the bot with the higher
##   kills+razings score. The API marks those games "draw;" in `note`; they are kept, with
##   timelimit = 1 and the score-decided winner. So winner is never "draw".
## - date = timestamp (already Unix seconds). map = the map file name without the
##   "maps/sscai/" folder. Agents are the ladder's bot names as the API gives them.
##   `replay` is null for every game and is dropped.

library(jsonlite)
cache <- path.expand("~/.cache/irw-comps/sscait")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
url <- "https://sscaitournament.com/api/games.php?future=false&count=1000&page=%d"
pages <- list()
p <- 1
repeat {
    f <- file.path(cache, sprintf("page_%04d.json", p))
    if (!file.exists(f)) {
        download.file(sprintf(url, p), f, mode = "wb", quiet = TRUE)
        Sys.sleep(3)
    }
    g <- fromJSON(f, simplifyVector = TRUE)
    pages[[p]] <- g[, c("result", "map", "note", "timestamp", "host", "guest")]
    stopifnot(all(is.na(g$replay)) || is.null(g$replay))
    if (nrow(g) < 1000) break
    p <- p + 1
}
x <- do.call(rbind, pages)
stopifnot(nrow(x) == 115183, !anyDuplicated(x),
          setequal(unique(x$result), c("1", "2")),
          setequal(unique(x$note), c("", "bot1_crashed;", "bot2_crashed;", "draw;",
                                     "bot1_crashed;draw;", "bot2_crashed;draw;")))
c1 <- grepl("bot1_crashed", x$note, fixed = TRUE)
c2 <- grepl("bot2_crashed", x$note, fixed = TRUE)
## the crashing bot always loses
stopifnot(all(x$result[c1] == "2"), all(x$result[c2] == "1"))

df <- data.frame(agent_a = x$host, agent_b = x$guest,
                 winner = ifelse(x$result == "1", "agent_a", "agent_b"),
                 date = as.numeric(x$timestamp), homefield = "",
                 map = sub("maps/sscai/", "", x$map, fixed = TRUE),
                 timelimit = as.integer(grepl("draw;", x$note, fixed = TRUE)),
                 crashed = ifelse(c1, "agent_a", ifelse(c2, "agent_b", "")),
                 stringsAsFactors = FALSE)
df <- df[order(df$date, method = "radix"), ]
agents <- unique(c(df$agent_a, df$agent_b))
stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), !anyNA(df$date),
          df$agent_a != df$agent_b, trimws(df$agent_a) != "", trimws(df$agent_b) != "",
          df$date >= 1616976000, df$date <= 1704585600,  # 2021-03-29 .. 2024-01-07
          !grepl("/", df$map), length(agents) == 110)

write.csv(df, "sscait_ladder_2021_2024.csv", row.names = FALSE, na = "")
cat(nrow(df), "games,", length(agents), "bots,", sum(df$timelimit), "time-limit,",
    sum(df$crashed != ""), "crash\n")
