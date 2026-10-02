## TCEC (Top Chess Engine Championship) engine-vs-engine games, one row per game.
## Source: https://github.com/TCEC-Chess/tcecgames, release S29-final (published 2026-06-07),
## asset TCEC-everything-compact.zip (md5 in `asset_md5` below). Games played at tcec-chess.com.
## Licence: "The PGN game files are released under the [Creative Commons BY-SA 3.0
## license](https://creativecommons.org/licenses/by-sa/3.0/legalcode)." (tcecgames README.md,
## "License" section, checked 2026-09-30; the scripts in that repo are Apache 2.0.)
##
## Tables:
##   tcec_engines_2010_2026   TCEC-everything-compet-traditional.pgn: every competition game of
##                            standard chess, Season 00 (2010) to Season 29 (2026), all stages
##                            (leagues, divisions, cups, superfinals, Swiss, etc.).
##
## Not built: the same zip holds TCEC-everything-bonus-test.pgn (bonus, test and side events,
## 29,596 games) and the Fischer-random competition files (compet-frc 1,754, compet-dfrc 3,516).
##
## Choices:
## - agent_a = White, agent_b = Black, homefield = "agent_a" on every row (White moves first).
##   TCEC plays each book opening twice with colours reversed, so within an opening pair the
##   first-move edge is balanced by design; across the table White still has the edge.
## - Agents are the PGN White/Black tags verbatim, e.g. "Stockfish (16.1)", "Rybka (4)". Each
##   version string is its own agent (versions are distinct engines); nothing is merged. A check
##   for pure formatting duplicates (case, whitespace) finds none (stopifnot below).
## - score_a/score_b from Result: 1-0 -> 1/0, 1/2-1/2 -> 0.5/0.5, 0-1 -> 0/1; winner follows.
##   Games with Result "*" would be dropped and counted (there are none in S29-final). Results
##   decided by adjudication, time forfeit, disconnection, crash or "abandoned" are kept as TCEC
##   recorded them; `termination` and `termination_details` say how each game ended.
## - date: UNIX seconds UTC. GameStartTime when present (2018 on) converted from its zone label:
##   UTC; "W. Europe Standard Time" = Europe/Berlin; EDT = UTC-4; CST = UTC-6 (assumed US
##   Central; it appears Jan-Apr 2020 before the server switched to EDT). Earlier games have
##   only a Date tag (their Time tag has no zone), so they get midnight UTC of that day.
## - Covariates: season (number from Event), event (full Event tag: season, stage/division),
##   round (Round tag, e.g. "12.3"), eco, opening, variation (compact-format reclassification),
##   ply_count, time_control, termination, termination_details.
##   Dropped as model output / ratings: WhiteElo, BlackElo, Annotator (engine evals).

cache <- path.expand("~/.cache/irw-comps/tcec")
outdir <- path.expand("~/.cache/irw-comps/tcec-out")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
release <- "S29-final"
asset <- "TCEC-everything-compact.zip"
asset_md5 <- "f11257edcc7a94ff5fc16aeab9498332"
pgn_name <- "TCEC-everything-compet-traditional.pgn"
pgn_md5 <- "e73ca11eb85263a5db3195039ccb7133"  # matches the release's MD5SUM file

zip <- file.path(cache, asset)
if (!file.exists(zip)) {
    rel <- jsonlite::fromJSON(paste0("https://api.github.com/repos/TCEC-Chess/tcecgames/releases/tags/", release))
    url <- rel$assets$browser_download_url[rel$assets$name == asset]
    stopifnot(length(url) == 1)
    options(timeout = 600)
    download.file(url, zip, mode = "wb")
}
stopifnot(unname(tools::md5sum(zip)) == asset_md5)
pgn <- file.path(cache, pgn_name)
if (!file.exists(pgn)) unzip(zip, files = pgn_name, exdir = cache)
stopifnot(unname(tools::md5sum(pgn)) == pgn_md5)

## line-based tag parser: each game starts with an [Event "..."] tag; moves are ignored
x <- readLines(pgn, encoding = "UTF-8", warn = FALSE)
x <- x[startsWith(x, "[")]
game <- cumsum(startsWith(x, "[Event "))
key <- sub("^\\[([A-Za-z]+) .*$", "\\1", x)
val <- sub("^\\[[A-Za-z]+ \"(.*)\"\\]\\s*$", "\\1", x)
ng <- max(game)
tag <- function(k) { v <- rep(NA_character_, ng); i <- key == k; v[game[i]] <- val[i]; v }
g <- data.frame(event = tag("Event"), round = tag("Round"), date_tag = tag("Date"),
                start = tag("GameStartTime"), white = tag("White"), black = tag("Black"),
                result = tag("Result"), eco = tag("ECO"), opening = tag("Opening"),
                variation = tag("Variation"), ply_count = as.integer(tag("PlyCount")),
                time_control = tag("TimeControl"), termination = tag("Termination"),
                termination_details = tag("TerminationDetails"), stringsAsFactors = FALSE)
stopifnot(ng == 32770, !anyNA(g$white), !anyNA(g$black), !anyNA(g$result), !anyNA(g$date_tag))

unfinished <- g$result == "*"
stopifnot(all(g$result %in% c("1-0", "0-1", "1/2-1/2", "*")))
g <- g[!unfinished, ]

## dates
day <- as.numeric(as.POSIXct(g$date_tag, format = "%Y.%m.%d", tz = "UTC"))
stopifnot(!anyNA(day))
stamp <- sub("^(\\S+T[0-9:]+)(\\.[0-9]+)? (.*)$", "\\1", g$start)
zone <- sub("^\\S+ ", "", g$start)
stopifnot(all(is.na(g$start) | zone %in% c("UTC", "W. Europe Standard Time", "EDT", "CST")))
t_utc <- as.numeric(as.POSIXct(stamp, format = "%Y-%m-%dT%H:%M:%S", tz = "UTC"))
t_ber <- as.numeric(as.POSIXct(stamp, format = "%Y-%m-%dT%H:%M:%S", tz = "Europe/Berlin"))
start <- ifelse(zone == "UTC", t_utc, ifelse(zone == "W. Europe Standard Time", t_ber,
         ifelse(zone == "EDT", t_utc + 4 * 3600, t_utc + 6 * 3600)))
stopifnot(all(is.na(g$start) | !is.na(start)))
date <- ifelse(is.na(start), day, start)
stopifnot(all(abs(date - day) < 2 * 86400))  # start time agrees with the Date tag

## agents: verbatim, but refuse formatting-only duplicates
nm <- unique(c(g$white, g$black))
stopifnot(!anyDuplicated(tolower(gsub("\\s+", "", nm))), all(nm == trimws(nm)))

sa <- c("1-0" = 1, "0-1" = 0, "1/2-1/2" = 0.5)[g$result]
tcec <- data.frame(agent_a = g$white, agent_b = g$black, date = date, homefield = "agent_a",
                   score_a = unname(sa), score_b = unname(1 - sa),
                   winner = c("1-0" = "agent_a", "0-1" = "agent_b", "1/2-1/2" = "draw")[g$result],
                   season = as.integer(sub("^TCEC Season ([0-9]+).*$", "\\1", g$event)),
                   event = g$event, round = g$round, eco = g$eco, opening = g$opening,
                   variation = g$variation, ply_count = g$ply_count, time_control = g$time_control,
                   termination = g$termination, termination_details = g$termination_details,
                   stringsAsFactors = FALSE, row.names = NULL)
tcec <- tcec[order(tcec$date, seq_len(nrow(tcec))), ]
stopifnot(!anyNA(tcec$agent_a), !anyNA(tcec$agent_b), !anyNA(tcec$date), !anyNA(tcec$season),
          !anyNA(tcec$winner), tcec$agent_a != tcec$agent_b)

yr <- format(as.POSIXct(range(tcec$date), origin = "1970-01-01", tz = "UTC"), "%Y")
n <- paste0("tcec_engines_", yr[1], "_", yr[2])
stopifnot(n == "tcec_engines_2010_2026")
write.csv(tcec, file = file.path(outdir, paste0(n, ".csv")), row.names = FALSE, na = "")
cat(n, nrow(tcec), "games,", length(unique(c(tcec$agent_a, tcec$agent_b))), "agents,",
    sum(tcec$winner == "draw"), "draws,", sum(tcec$homefield == ""), "homefield blank,",
    sum(unfinished), "unfinished (*) dropped\n")
