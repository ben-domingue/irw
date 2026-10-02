## FiveThirtyEight game files (https://github.com/fivethirtyeight/data), one row per game
## Licence: "Unless otherwise noted, our data sets are available under the Creative Commons
## Attribution 4.0 International License" (fivethirtyeight/data README, checked 2026-09-30).
##
## 538 closed in 2025 and the projects.fivethirtyeight.com URLs now redirect to ABC News,
## so the files are read from the Internet Archive's 2025-03-06 captures (the final
## versions; md5 in `src` below). mlb.R reads the MLB file from the same family.
##
## Tables:
##   fivethirtyeight_nhl_1917_2023     nhl_elo.csv, 1917-18 to 2022-23 incl. playoffs
##   fivethirtyeight_nba_1946_2023     nba_elo.csv, 1946-47 to 2022-23 incl. playoffs
##   fivethirtyeight_nfl_1920_2023     nfl_elo.csv, 1920 to 2022 seasons incl. playoffs
##   fivethirtyeight_soccer_2016_2023  spi_matches.csv, 40 club leagues and cups, 2016-07 to 2023-12
##
## Choices:
## - Only the game record is kept: teams, date, scores, season, playoff flag. 538's own
##   ratings and forecasts (elo*, carm-elo*, raptor*, qbelo*, spi*, prob*, quality,
##   importance) are model output, not data, and are dropped.
## - agent_a is the home team (team1 in the NBA/NFL/soccer files; verified on known games,
##   e.g. the 2016 NBA Finals game 7 at GSW, West Ham v Man City 2019-08-10).
##   homefield is "agent_a", or blank when the game was at a neutral site:
##     NHL/NBA/NFL: 538's `neutral` flag (all 172 games of the 2020 NBA bubble are flagged).
##     Soccer: the file has no flag. Blank for every UEFA final (the last date of each
##     competition-season), the 2020 UCL final eight in Lisbon (2020-08-12 on), the 2020
##     Europa League final eight in Germany (2020-08-10 on), the 2020 NWSL Challenge Cup
##     (Utah) and MLS is Back 2020 (Orlando, 2020-07-08 to 2020-08-11). Other COVID-era
##     relocations of single matches (e.g. 2020-21 UCL ties moved abroad) are not marked.
## - winner follows the score. NHL shootout games carry the shootout goal in the score
##   (538's convention), so they are never draws; `overtime` says OT/2OT.../SO. NHL ties
##   before 2005, NFL ties and soccer draws are "draw". NBA has none.
## - playoff: NHL 0/1; NBA and NFL keep 538's round codes (blank = regular season;
##   NBA q/s/c/f/p/t, NFL w/d/c/s), so "is a playoff game" is playoff != "".
## - Soccer fixtures listed without a score (2,004 unplayed rows, mostly late 2023) are
##   dropped. xg_a/xg_b are kept where 538 had them (top leagues, 2017 on).
## - Agents are 538's labels: NBA and NFL abbreviations, NHL and soccer full names.
##   Relocated or renamed franchises are separate agents, as 538 labels them.

cache <- path.expand("~/.cache/irw-comps/fivethirtyeight")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
src <- list(
    nhl    = c("20250306203344id_/https://projects.fivethirtyeight.com/nhl-api/nhl_elo.csv",       "479bc0273956fe43f55f8dc03b71e7c3"),
    nba    = c("20250306125344id_/https://projects.fivethirtyeight.com/nba-model/nba_elo.csv",     "b11901fb009e1ba393b4a2e653c83aff"),
    nfl    = c("20250306125358id_/https://projects.fivethirtyeight.com/nfl-api/nfl_elo.csv",       "b94bde9587edfa83ef0a08e9c035c1d6"),
    soccer = c("20250306125411id_/https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv", "ff1be88ee170d4a5da3c2625864a027e")
)
read538 <- function(k) {
    f <- file.path(cache, basename(src[[k]][1]))
    if (!file.exists(f)) download.file(paste0("https://web.archive.org/web/", src[[k]][1]), f, mode = "wb")
    stopifnot(unname(tools::md5sum(f)) == src[[k]][2])
    read.csv(f, stringsAsFactors = FALSE, na.strings = "")
}
unix <- function(d) as.numeric(as.POSIXct(d, format = "%Y-%m-%d", tz = "UTC"))
finish <- function(df) {
    df$winner <- ifelse(df$score_a > df$score_b, "agent_a", ifelse(df$score_a < df$score_b, "agent_b", "draw"))
    stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), !anyNA(df$date),
              !anyNA(df$score_a), !anyNA(df$score_b), df$agent_a != df$agent_b)
    df
}

x <- read538("nhl")
nhl <- finish(data.frame(agent_a = x$home_team, agent_b = x$away_team, date = unix(x$date),
                         homefield = ifelse(x$neutral == 1, "", "agent_a"),
                         score_a = x$home_team_score, score_b = x$away_team_score,
                         season = x$season, playoff = x$playoff,
                         overtime = ifelse(is.na(x$ot), "", x$ot)))

x <- read538("nba")
nba <- finish(data.frame(agent_a = x$team1, agent_b = x$team2, date = unix(x$date),
                         homefield = ifelse(x$neutral == 1, "", "agent_a"),
                         score_a = x$score1, score_b = x$score2,
                         season = x$season, playoff = ifelse(is.na(x$playoff), "", x$playoff)))

x <- read538("nfl")
nfl <- finish(data.frame(agent_a = x$team1, agent_b = x$team2, date = unix(x$date),
                         homefield = ifelse(x$neutral == 1, "", "agent_a"),
                         score_a = x$score1, score_b = x$score2,
                         season = x$season, playoff = ifelse(is.na(x$playoff), "", x$playoff)))

x <- read538("soccer")
x <- x[!is.na(x$score1) & !is.na(x$score2), ]
uefa <- grepl("^UEFA", x$league)
final <- uefa & x$date == ave(x$date, x$league, x$season, FUN = max)
neutral <- final |
    (x$league == "UEFA Champions League" & x$date >= "2020-08-12" & x$date <= "2020-08-23") |
    (x$league == "UEFA Europa League" & x$date >= "2020-08-10" & x$date <= "2020-08-21") |
    (x$league == "NWSL Challenge Cup" & x$season == 2020) |
    (x$league == "Major League Soccer" & x$date >= "2020-07-08" & x$date <= "2020-08-11")
stopifnot(sum(final) == 15)  # 7 UCL + 6 UEL + 2 UECL finals
soccer <- finish(data.frame(agent_a = x$team1, agent_b = x$team2, date = unix(x$date),
                            homefield = ifelse(neutral, "", "agent_a"),
                            score_a = x$score1, score_b = x$score2,
                            season = x$season, league = x$league,
                            xg_a = x$xg1, xg_b = x$xg2))

out <- list(fivethirtyeight_nhl_1917_2023 = nhl, fivethirtyeight_nba_1946_2023 = nba,
            fivethirtyeight_nfl_1920_2023 = nfl, fivethirtyeight_soccer_2016_2023 = soccer)
for (n in names(out)) {
    write.csv(out[[n]], file = paste0(n, ".csv"), row.names = FALSE, na = "")
    cat(n, nrow(out[[n]]), "games,", length(unique(c(out[[n]]$agent_a, out[[n]]$agent_b))), "agents,",
        sum(out[[n]]$homefield == ""), "neutral,", sum(out[[n]]$winner == "draw"), "draws\n")
}
