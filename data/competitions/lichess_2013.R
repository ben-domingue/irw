## Lichess rated standard-chess games, January-December 2013, one row per game, split into one
## table per time control. Source: the Lichess open database, https://database.lichess.org/
## (standard/lichess_db_standard_rated_2013-MM.pgn.zst), pinned by the sha256 sums Lichess
## publishes (standard/sha256sums.txt) and checked against its published game counts
## (standard/counts.txt). Licence: "Database exports are released under the Creative Commons CC0
## license. Use them for research, commercial purpose, publication, anything you like."
## (database.lichess.org, checked 2026-09-30). irw#2634.
##
## Why 2013: early Lichess was small, so its regulars played each other constantly; a month holds
## a core of hundreds of players with many repeated pairings, which is what pairwise models (and
## tests of transitivity) need. Later years are far larger and far sparser per pair.
##
## Tables (Event tag "Rated <X> game", or "Rated <X> tournament <url>" for arena games):
##   lichess_2013_bullet      Bullet
##   lichess_2013_blitz       Blitz
##   lichess_2013_classical   Classical (in 2013 Lichess called every game over ~8 minutes
##                            "Classical"; there was no Rapid category yet)
## Not built: Correspondence (about 0.3% of games).
##
## Choices:
## - agent_a = White, agent_b = Black, homefield = "agent_a" on every row (White moves first).
## - Agents are Lichess usernames verbatim (public handles in a CC0 release).
## - score_a/score_b from Result: 1-0 -> 1/0, 1/2-1/2 -> 0.5/0.5, 0-1 -> 0/1; winner follows.
##   Result "*" (unfinished) is dropped and counted. Games ending by time forfeit, abandonment
##   or rules infraction are kept as Lichess scored them; `termination` says how each ended.
##   Self-play games (White and Black the same account, a few per month in 2013) are dropped
##   and counted.
## - date: UNIX seconds, UTC, from UTCDate + UTCTime (game start). Lichess files games by
##   month, so the January file opens with games started on the evening of 2012-12-31 (UTC);
##   they are kept, as Lichess filed them.
## - Covariates: white_elo, black_elo (each player's Lichess rating before the game; Glicko-2 on
##   the Elo 400-point scale, so a 400-point gap is odds of 10:1), time_control (base+increment
##   in seconds, e.g. "180+0"), termination, tournament (the arena tournament id for games
##   played in a Lichess tournament, https://lichess.org/tournament/<id>; blank otherwise), game_id (the Lichess game id; the game is at
##   https://lichess.org/<game_id>). Ratings are kept because a player's strength moves within
##   the year and the rating is the record of that. Rating diffs and moves are dropped.

cache <- path.expand("~/.cache/irw-comps/lichess")
outdir <- path.expand("~/.cache/irw-comps/lichess-out")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
base <- "https://database.lichess.org/standard/"
months <- sprintf("2013-%02d", 1:12)
files <- paste0("lichess_db_standard_rated_", months, ".pgn.zst")

sums <- read.table(url(paste0(base, "sha256sums.txt")), col.names = c("sha", "file"))
counts <- read.table(url(paste0(base, "counts.txt")), col.names = c("file", "n"))
stopifnot(all(files %in% sums$file), all(files %in% counts$file))
stopifnot(nzchar(Sys.which("zstd")), nzchar(Sys.which("sha256sum")))

parse_month <- function(f) {
    path <- file.path(cache, f)
    if (!file.exists(path)) {  # one at a time: Lichess answers parallel fetches with 429
        options(timeout = 1800)
        download.file(paste0(base, f), path, mode = "wb")
    }
    sha <- sub(" .*", "", system2("sha256sum", shQuote(path), stdout = TRUE))
    stopifnot(sha == sums$sha[sums$file == f])
    ## tag lines only; each game starts with an [Event "..."] tag
    x <- readLines(pipe(paste("zstd -dc", shQuote(path), "| grep '^\\['")), warn = FALSE)
    game <- cumsum(startsWith(x, "[Event "))
    key <- sub("^\\[([A-Za-z]+) .*$", "\\1", x)
    val <- sub("^\\[[A-Za-z]+ \"(.*)\"\\]\\s*$", "\\1", x)
    ng <- max(game)
    stopifnot(ng == counts$n[counts$file == f])  # every game Lichess counts, no more
    tag <- function(k) { v <- rep(NA_character_, ng); i <- key == k; v[game[i]] <- val[i]; v }
    data.frame(event = tag("Event"), site = tag("Site"), white = tag("White"),
               black = tag("Black"), result = tag("Result"), utc_date = tag("UTCDate"),
               utc_time = tag("UTCTime"), white_elo = tag("WhiteElo"),
               black_elo = tag("BlackElo"), time_control = tag("TimeControl"),
               termination = tag("Termination"), stringsAsFactors = FALSE)
}

g <- do.call(rbind, lapply(files, function(f) {
    rds <- file.path(cache, sub("\\.pgn\\.zst$", ".tags.rds", f))  # parsed tags, so reruns are quick
    if (file.exists(rds)) return(readRDS(rds))
    cat(f, "\n"); x <- parse_month(f); saveRDS(x, rds); x }))
stopifnot(nrow(g) == sum(counts$n[counts$file %in% files]), !anyNA(g$white), !anyNA(g$black),
          !anyNA(g$result), !anyNA(g$event), !anyNA(g$site))

tc <- sub("^Rated (\\w+) (game|tournament).*$", "\\1", g$event)
tournament <- ifelse(grepl("^Rated \\w+ tournament ", g$event), sub("^.*/tournament/", "", g$event), "")
stopifnot(all(tournament == "" | grepl("^[A-Za-z0-9]+$", tournament)))
stopifnot(all(tc %in% c("Bullet", "Blitz", "Classical", "Correspondence")))
stopifnot(all(g$result %in% c("1-0", "0-1", "1/2-1/2", "*")))
unfinished <- g$result == "*"

date <- as.numeric(as.POSIXct(paste(g$utc_date, g$utc_time), format = "%Y.%m.%d %H:%M:%S", tz = "UTC"))
stopifnot(!anyNA(date))
elo <- function(v) { v[v %in% c("?", "")] <- NA; as.integer(v) }
game_id <- sub("^https://lichess.org/", "", g$site)
stopifnot(!anyDuplicated(game_id), all(nchar(game_id) == 8))

sa <- c("1-0" = 1, "0-1" = 0, "1/2-1/2" = 0.5, "*" = NA)[g$result]
all_games <- data.frame(agent_a = g$white, agent_b = g$black, date = date, homefield = "agent_a",
                        score_a = unname(sa), score_b = unname(1 - sa),
                        winner = c("1-0" = "agent_a", "0-1" = "agent_b", "1/2-1/2" = "draw", "*" = NA)[g$result],
                        white_elo = elo(g$white_elo), black_elo = elo(g$black_elo),
                        time_control = g$time_control, termination = g$termination,
                        tournament = tournament, game_id = game_id, stringsAsFactors = FALSE, row.names = NULL)
self_play <- all_games$agent_a == all_games$agent_b  # a few per month on 2013 Lichess

for (k in c("Bullet", "Blitz", "Classical")) {
    d <- all_games[tc == k & !unfinished & !self_play, ]
    d <- d[order(d$date, d$game_id), ]
    stopifnot(!anyNA(d$winner), !anyNA(d$date))
    n <- paste0("lichess_2013_", tolower(k))
    write.csv(d, file = file.path(outdir, paste0(n, ".csv")), row.names = FALSE, na = "")
    cat(n, nrow(d), "games,", length(unique(c(d$agent_a, d$agent_b))), "players,",
        sum(d$winner == "draw"), "draws,", sum(is.na(d$white_elo) | is.na(d$black_elo)), "missing a rating,",
        sum(unfinished & tc == k), "unfinished (*) dropped,", sum(self_play & tc == k), "self-play dropped\n")
}
cat("Correspondence not built:", sum(tc == "Correspondence"), "games\n")
