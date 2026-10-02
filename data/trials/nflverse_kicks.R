## nflverse_kicks: NFL field goal and extra point attempts, 1999-2025, one row per kick
##
## Source: nflverse play-by-play (https://github.com/nflverse/nflverse-data, release "pbp",
## play_by_play_<season>.csv.gz). Licence: the nflverse-data LICENSE is CC BY 4.0 (checked
## 2026-09-30). The play-by-play itself derives from the NFL's GSIS feed.
## nflverse rebuilds these files as corrections come in, so they are not md5-pinned; counts
## at build time (2026-09-30) are checked below.
##
## A real-data counterpart to data/simsyn/nbashots_sim.R: kickers do not choose their
## kicks, but coaches choose whether to try a field goal, and they send stronger kickers out
## for longer ones. Make rates by kicker therefore mix skill with selection, and distance
## (trial_dist) is what an analysis adjusts for.
##
## Choices:
## - id is the kicker's GSIS id (kicker_player_id), stable across seasons and teams.
## - item is the kind of kick: extra_point, or a field goal distance band (fg_18_29,
##   fg_30_39, fg_40_49, fg_50_plus). The exact distance is in trial_dist (yards, measured
##   from where the ball was kicked to the goalposts).
## - resp = 1 for a made field goal or a good extra point; 0 for missed, failed or
##   blocked. Blocked kicks are kept as misses and flagged in trial_blocked. 31 extra points
##   recorded as "aborted" (botched snap or hold, no kick) are dropped.
## - The extra point moved from the 2-yard line to the 15 in 2015 (about 20 yards to 33);
##   trial_dist carries the change.
## - Regular season and playoffs are both kept; trial_playoff = 1 for playoffs.
## - date is the game date as Unix time. trial_gameclock is minutes elapsed in the game
##   (15-minute quarters; overtime continues past 60). trial_home = 1 when the kicking team
##   is the home team; neutral-site games (nflverse location = "Neutral") get NA.
## - Conditions as nflverse records them: trial_roof (outdoors/dome/closed/open),
##   trial_surface, trial_temp (F) and trial_wind (mph); temp and wind are NA indoors and
##   for many games. trial_scorediff is the kicking team's lead before the kick.
## - trial_number orders each kicker's attempts in time (game date, then play order).

library(data.table)

cache <- path.expand("~/.cache/irw-sports/nflpbp")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
seasons <- 1999:2025
cols <- c("play_id", "game_id", "game_date", "season", "season_type", "home_team", "posteam",
          "location", "qtr", "quarter_seconds_remaining", "field_goal_attempt",
          "field_goal_result", "extra_point_attempt", "extra_point_result", "kick_distance",
          "kicker_player_id", "roof", "surface", "temp", "wind", "score_differential")
L <- lapply(seasons, function(y) {
    f <- file.path(cache, sprintf("pbp_%d.csv.gz", y))
    if (!file.exists(f))
        download.file(sprintf("https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_%d.csv.gz", y), f, mode = "wb")
    x <- fread(f, select = cols, showProgress = FALSE)
    x[field_goal_attempt == 1 | extra_point_attempt == 1]
})
x <- rbindlist(L)

fg <- x$field_goal_attempt == 1
x$result <- ifelse(fg, x$field_goal_result, x$extra_point_result)
x <- x[result != "aborted"]
fg <- x$field_goal_attempt == 1
stopifnot(x$result %in% c("made", "missed", "blocked", "good", "failed"),
          !is.na(x$kicker_player_id), !is.na(x$kick_distance))

x$item <- ifelse(!fg, "extra_point",
          ifelse(x$kick_distance < 30, "fg_18_29",
          ifelse(x$kick_distance < 40, "fg_30_39",
          ifelse(x$kick_distance < 50, "fg_40_49", "fg_50_plus"))))
x$resp <- as.integer(x$result %in% c("made", "good"))
x$date <- as.numeric(as.POSIXct(x$game_date, format = "%Y-%m-%d", tz = "UTC"))
x$gameclock <- 15 * (x$qtr - 1) + (900 - x$quarter_seconds_remaining) / 60
x$home <- ifelse(x$location == "Neutral", NA, as.integer(x$posteam == x$home_team))
setorder(x, kicker_player_id, date, game_id, play_id)
x[, trial_number := seq_len(.N), by = kicker_player_id]

df <- data.frame(id = x$kicker_player_id, item = x$item, resp = x$resp, date = x$date,
                 trial_number = x$trial_number, trial_dist = x$kick_distance,
                 trial_blocked = as.integer(x$result == "blocked"),
                 trial_season = x$season, trial_playoff = as.integer(x$season_type == "POST"),
                 trial_game = x$game_id, trial_gameclock = round(x$gameclock, 2),
                 trial_home = x$home, trial_scorediff = x$score_differential,
                 trial_roof = x$roof, trial_surface = x$surface,
                 trial_temp = x$temp, trial_wind = x$wind)
df$trial_surface[df$trial_surface == ""] <- NA
df$trial_roof[df$trial_roof == ""] <- NA

## counts at build time, 2026-09-30
stopifnot(sum(df$item != "extra_point") == 27773, nrow(df) == 27773 + 33525 - 31)
print(table(df$item, df$resp))
print(tapply(df$resp, df$item, mean))

write.csv(df, file = "nflverse_kicks.csv", quote = FALSE, row.names = FALSE, na = "")
