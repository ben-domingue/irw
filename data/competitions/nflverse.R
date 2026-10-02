## nflverse NFL schedules and results, 1999-2025
## Source: https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv
##   (release "schedules" of nflverse/nflverse-data; the same file nflreadr::load_schedules()
##   reads). Downloaded 2026-09-30.
## Licence: CC BY 4.0. nflverse/nflverse-data has LICENSE.md, which is the full text of
##   "Attribution 4.0 International" ... "Creative Commons Attribution 4.0 International
##   Public License" (GitHub reports spdx_id CC-BY-4.0), checked 2026-09-30 at
##   https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md.
##   The upstream repo the schedule is maintained in, nflverse/nfldata (Lee Sharpe's
##   games.csv), has no licence file (GitHub API /license returns 404, checked 2026-09-30);
##   we rely on the CC BY 4.0 grant on the nflverse-data release we download from.
##
## Table:
##   nflverse_nfl_1999_2025  every NFL regular-season and playoff game, seasons 1999-2025
##
## Choices:
## - One row per game. agent_a = home_team, agent_b = away_team, as nflverse lists them.
##   homefield = "agent_a", except blank when location == "Neutral" (Super Bowls,
##   international games, the 2010 Metrodome-roof game at Ford Field, etc.).
## - score_a/score_b are the final scores, including overtime; winner follows the score,
##   so the 15 tied games are "draw".
## - Only completed seasons: the 2026 season is in progress and is dropped entirely
##   (its unplayed games have no score). No 1999-2025 game lacks a score.
## - date: gameday + gametime. nflverse documents gametime as kickoff in US Eastern time
##   whatever the venue, so it is read in America/New_York (DST-aware) and converted to
##   UTC. All 1999 games have no gametime: those get gameday at 00:00 UTC.
## - Team abbreviations are left as nflverse spells them. nflverse does NOT merge
##   relocated franchises: it uses the abbreviation of the time, so STL (1999-2015) and LA
##   (2016-), SD (1999-2016) and LAC (2017-), OAK (1999-2019) and LV (2020-) are separate
##   agents. WAS covers every Washington name. HOU starts in 2002 (expansion).
## - Covariates kept (blank when missing): game_id, season, game_type (REG/WC/DIV/CON/SB), week, overtime,
##   roof, surface (trailing spaces trimmed), temp, wind, div_game, stadium.
##   Dropped: all betting lines and odds (spread, moneyline, total line), which are
##   market predictions, plus ids, rest days, quarterbacks, coaches and referee.

cache <- path.expand("~/.cache/irw-comps/nflverse")
out <- path.expand("~/.cache/irw-comps/nflverse-openfootball-out")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
dir.create(out, showWarnings = FALSE, recursive = TRUE)
src <- file.path(cache, "games.csv")
if (!file.exists(src))
    download.file("https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv",
                  src, mode = "wb")

g <- read.csv(src, na.strings = c("", "NA"), stringsAsFactors = FALSE)
last <- 2025
n_future <- sum(g$season > last)
g <- g[g$season <= last, ]
stopifnot(!anyNA(g$home_score), !anyNA(g$away_score), !anyNA(g$gameday),
          g$location %in% c("Home", "Neutral"), !duplicated(g$game_id),
          is.na(g$gametime) == (g$season == 1999))

ko <- ifelse(is.na(g$gametime),
             as.numeric(as.POSIXct(g$gameday, tz = "UTC")),
             as.numeric(as.POSIXct(paste(g$gameday, g$gametime), format = "%Y-%m-%d %H:%M",
                                   tz = "America/New_York")))
stopifnot(!anyNA(ko))

t <- data.frame(
    agent_a = g$home_team, agent_b = g$away_team,
    date = ko,
    homefield = ifelse(g$location == "Neutral", "", "agent_a"),
    score_a = g$home_score, score_b = g$away_score,
    winner = ifelse(g$home_score > g$away_score, "agent_a",
                    ifelse(g$home_score < g$away_score, "agent_b", "draw")),
    game_id = g$game_id, season = g$season, game_type = g$game_type, week = g$week,
    overtime = g$overtime, roof = g$roof, surface = trimws(g$surface),
    temp = g$temp, wind = g$wind, div_game = g$div_game, stadium = g$stadium)
t <- t[order(t$date, t$game_id), ]

stopifnot(t$agent_a != t$agent_b, t$winner %in% c("agent_a", "agent_b", "draw"),
          all(table(t$season[t$game_type == "SB"]) == 1),
          ## a 1 pm ET Sunday kickoff in September is 17:00 UTC
          t$date[t$game_id == "2025_01_MIA_IND"] == as.numeric(as.POSIXct("2025-09-07 17:00", tz = "UTC")))
write.csv(t, file.path(out, "nflverse_nfl_1999_2025.csv"), row.names = FALSE, na = "")

yr <- t$season
pair <- paste(yr, pmin(t$agent_a, t$agent_b), pmax(t$agent_a, t$agent_b))
cat(sprintf(paste0("nflverse_nfl_1999_2025: %d rows, %d agents, %s to %s, %d draws, %d neutral; ",
                   "%d games from the %d+ season dropped; median meetings per pair-season %g\n"),
            nrow(t), length(unique(c(t$agent_a, t$agent_b))),
            format(as.POSIXct(min(t$date), origin = "1970-01-01", tz = "UTC"), "%Y-%m-%d"),
            format(as.POSIXct(max(t$date), origin = "1970-01-01", tz = "UTC"), "%Y-%m-%d"),
            sum(t$winner == "draw"), sum(t$homefield == ""), n_future, last + 1,
            median(table(pair))))
