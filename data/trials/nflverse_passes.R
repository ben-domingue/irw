## nflverse_passes: NFL pass attempts, 2006-2025, one row per throw
##
## Source: nflverse play-by-play (https://github.com/nflverse/nflverse-data, release "pbp",
## play_by_play_<season>.csv.gz). Licence: the nflverse-data LICENSE is CC BY 4.0 (checked
## 2026-09-30). The play-by-play itself derives from the NFL's GSIS feed.
## nflverse rebuilds these files as corrections come in, so they are not md5-pinned; counts
## at build time (2026-09-30) are checked below. Same source as nflverse_kicks.R.
##
## A real-data counterpart to data/simsyn/nbashots_sim.R: quarterbacks choose where to
## throw, and the defence and game situation shape that choice, so completion rates mix
## passing skill with target selection. The zone (item) and air yards are what an analysis
## adjusts for.
##
## Choices:
## - Starts in 2006, the first season with air yards (pass depth) recorded; before that
##   the zone cannot be built.
## - A pass attempt is a play nflverse codes play_type "pass" with pass_attempt = 1 and no
##   sack: a throw. Sacks, spikes, two-point tries and plays wiped out by penalty are not
##   attempts. Throwaways are attempts and count as incompletions (nflverse does not flag
##   them in every season).
## - id is the passer's GSIS id (passer_player_id), stable across seasons and teams; most
##   passers are quarterbacks, but trick-play throws by others are kept.
## - item is the target zone: depth by air yards (behind = behind the line of scrimmage,
##   short = 0-9, medium = 10-19, deep = 20+) crossed with nflverse's pass_location
##   (left/middle/right), e.g. short_left, deep_middle. Exact air yards are in
##   trial_airyards. Throws missing air yards or location (1,990, 0.5%) are dropped.
##   Air yards are as nflverse records them: 59 throws, nearly all 2006-2010, have air yards
##   below -20 (as low as -93), which are implausible but are kept.
## - resp = 1 for a completion, 0 otherwise. Interceptions are 0 and flagged in
##   trial_interception.
## - trial_receiver is the targeted receiver's GSIS id (blank when none was recorded).
## - Situation: trial_down, trial_togo (yards to a first down), trial_yardline (yards from
##   the opponent's end zone), trial_shotgun, trial_nohuddle, trial_qbhit (passer hit on the
##   play), trial_scorediff (passing team's lead), trial_gameclock (minutes elapsed; overtime
##   continues past 60), trial_home (NA at neutral sites), trial_playoff, trial_roof.
## - date is the game date as Unix time; trial_number orders each passer's throws in time.

library(data.table)

cache <- path.expand("~/.cache/irw-sports/nflpbp")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
seasons <- 2006:2025
cols <- c("play_id", "game_id", "game_date", "season", "season_type", "home_team", "posteam",
          "location", "qtr", "quarter_seconds_remaining", "play_type", "pass_attempt", "sack",
          "two_point_attempt", "passer_player_id", "receiver_player_id", "complete_pass",
          "interception", "air_yards", "pass_location", "down", "ydstogo", "yardline_100",
          "shotgun", "no_huddle", "qb_hit", "roof", "score_differential")
L <- lapply(seasons, function(y) {
    f <- file.path(cache, sprintf("pbp_%d.csv.gz", y))
    if (!file.exists(f))
        download.file(sprintf("https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_%d.csv.gz", y), f, mode = "wb")
    x <- fread(f, select = cols, showProgress = FALSE)
    x[play_type == "pass" & pass_attempt == 1 & sack == 0 & two_point_attempt == 0]
})
x <- rbindlist(L)
n0 <- nrow(x)
x <- x[!is.na(air_yards) & !is.na(pass_location) & pass_location != ""]
cat(n0 - nrow(x), "throws dropped for missing air yards or location\n")
stopifnot(!is.na(x$passer_player_id), x$pass_location %in% c("left", "middle", "right"),
          !(x$complete_pass == 1 & x$interception == 1))

depth <- ifelse(x$air_yards < 0, "behind", ifelse(x$air_yards < 10, "short",
         ifelse(x$air_yards < 20, "medium", "deep")))
x$item <- paste(depth, x$pass_location, sep = "_")
x$date <- as.numeric(as.POSIXct(x$game_date, format = "%Y-%m-%d", tz = "UTC"))
x$gameclock <- 15 * (x$qtr - 1) + (900 - x$quarter_seconds_remaining) / 60
x$home <- ifelse(x$location == "Neutral", NA, as.integer(x$posteam == x$home_team))
setorder(x, passer_player_id, date, game_id, play_id)
x[, trial_number := seq_len(.N), by = passer_player_id]

df <- data.frame(id = x$passer_player_id, item = x$item, resp = x$complete_pass, date = x$date,
                 trial_number = x$trial_number, trial_airyards = x$air_yards,
                 trial_interception = x$interception, trial_receiver = x$receiver_player_id,
                 trial_down = x$down, trial_togo = x$ydstogo, trial_yardline = x$yardline_100,
                 trial_shotgun = x$shotgun, trial_nohuddle = x$no_huddle, trial_qbhit = x$qb_hit,
                 trial_season = x$season, trial_playoff = as.integer(x$season_type == "POST"),
                 trial_game = x$game_id, trial_gameclock = round(x$gameclock, 2),
                 trial_home = x$home, trial_scorediff = x$score_differential,
                 trial_roof = x$roof)
df$trial_roof[df$trial_roof == ""] <- NA
df$trial_receiver[df$trial_receiver == ""] <- NA

## count at build time, 2026-09-30
stopifnot(n0 == 368264, nrow(df) == 366274)
print(table(df$item, df$resp))
print(round(tapply(df$resp, df$item, mean), 2))

write.csv(df, file = "nflverse_passes.csv", quote = FALSE, row.names = FALSE, na = "")
