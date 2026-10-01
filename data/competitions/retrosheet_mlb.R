## Retrosheet MLB game logs, 1871-2025 (https://www.retrosheet.org/gamelogs/index.html), one row per game.
## Field definitions: https://www.retrosheet.org/gamelogs/glfields.txt
##
## Licence: https://www.retrosheet.org/notice.txt (checked 2026-10-01): "Recipients of Retrosheet
## data are free to make any desired use of the information, including (but not limited to)
## selling it, giving it away, or producing a commercial product based upon the data. Retrosheet
## has one requirement for any such transfer of data or product development, which is that the
## following statement must appear prominently: The information used here was obtained free of
## charge from and is copyrighted by Retrosheet. Interested parties may contact Retrosheet at
## "www.retrosheet.org"." Accepted as a permissive custom licence (Ben, irw#2702, 2026-10-01).
##
## The information used here was obtained free of charge from and is copyrighted by Retrosheet.
## Interested parties may contact Retrosheet at www.retrosheet.org.
##
## Table: retrosheet_mlb_1871_2025
##
## Source: gl1871_2025.zip (all regular-season logs gl1871.txt ... gl2025.txt, plus the
## postseason and All-Star logs), md5 pinned below. Retrosheet corrects its files over time,
## so a re-download may change the md5; update it deliberately.
##
## Choices:
## - Regular season (game_type "regular") plus the four postseason logs, flagged in game_type:
##   "wildcard" (glwc), "division" (gldv), "lcs" (gllc), "worldseries" (glws; includes the
##   19th-century championship series Retrosheet files there). The All-Star log (glas) is
##   dropped: its "teams" are the leagues, not clubs.
## - agent_a is the home team, agent_b the visitor (fields 7 and 4), as Retrosheet team codes.
##   homefield is always "agent_a": Retrosheet always names a home team (the one batting last,
##   save the early games flagged HTBF in its additional-info field). Neutral-site games
##   (e.g. Tokyo, London, Mexico City series) are not marked; `park` (Retrosheet park id) lets a
##   user find them.
## - date = game date (field 1) as Unix seconds UTC. For suspended games completed later,
##   the date is the start date and `completed` holds Retrosheet's completion string
##   ("yyyymmdd,park,vs,hs,len"); scores are the final scores.
## - winner follows the score, except forfeits: forfeit "V" (forfeited to the visitor) gives
##   agent_b, "H" gives agent_a. Forfeit "T" (ruled a no-decision) is "draw". Ties are "draw".
##   `forfeit` and `protest` keep Retrosheet's codes.
## - Kept: season, league_a/league_b, game_num (0 single, 1/2/3 double- or triple-header,
##   A/B three-team double-header), day_night, park, attendance, length_outs, minutes.
##   league "NA" (Retrosheet's code for the National Association, 1871-75) is written "NAssn".
##   Box-score statistics, line scores, umpires, managers, pitchers and lineups are dropped.
## - Event files (plate appearances, pitches) are not included here.

cache <- path.expand("~/.cache/irw-comps/retrosheet")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "gl1871_2025.zip")
if (!file.exists(f)) download.file("https://www.retrosheet.org/gamelogs/gl1871_2025.zip", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "bb08286ea787f173a1b5b5c30a35d041")

members <- unzip(f, list = TRUE)$Name
reg <- sort(grep("^gl[0-9]{4}\\.txt$", members, value = TRUE))
stopifnot(length(reg) == 155, reg[1] == "gl1871.txt", reg[155] == "gl2025.txt")
post <- c(glwc = "wildcard", gldv = "division", gllc = "lcs", glws = "worldseries")
stopifnot(paste0(names(post), ".txt") %in% members)

readgl <- function(m) {
    x <- read.csv(unz(f, m), header = FALSE, stringsAsFactors = FALSE, na.strings = "",
                  colClasses = "character")
    stopifnot(ncol(x) == 161)
    x
}
x <- do.call(rbind, c(lapply(reg, function(m) cbind(readgl(m), game_type = "regular")),
                      lapply(names(post), function(k) cbind(readgl(paste0(k, ".txt")), game_type = post[[k]]))))

num <- function(v) as.numeric(v)
na2 <- function(v) ifelse(is.na(v), "", v)
## Retrosheet's league code for the National Association (1871-75) is "NA", which reads as a
## missing value downstream; it is written as "NAssn".
lg <- function(v) ifelse(!is.na(v) & v == "NA", "NAssn", na2(v))
df <- data.frame(agent_a = x$V7, agent_b = x$V4,
                 date = as.numeric(as.POSIXct(x$V1, format = "%Y%m%d", tz = "UTC")),
                 homefield = "agent_a",
                 score_a = num(x$V11), score_b = num(x$V10),
                 season = as.integer(substr(x$V1, 1, 4)),
                 game_type = x$game_type,
                 league_a = lg(x$V8), league_b = lg(x$V5),
                 game_num = x$V2, day_night = na2(x$V13),
                 park = na2(x$V17), attendance = num(x$V18),
                 length_outs = num(x$V12), minutes = num(x$V19),
                 forfeit = na2(x$V15), protest = na2(x$V16), completed = na2(x$V14),
                 stringsAsFactors = FALSE)
df$winner <- ifelse(df$score_a > df$score_b, "agent_a", ifelse(df$score_a < df$score_b, "agent_b", "draw"))
df$winner[df$forfeit == "V"] <- "agent_b"
df$winner[df$forfeit == "H"] <- "agent_a"
df$winner[df$forfeit == "T"] <- "draw"
df <- df[, c("agent_a", "agent_b", "winner", setdiff(names(df), c("agent_a", "agent_b", "winner")))]

stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), !anyNA(df$date), !anyNA(df$score_a),
          !anyNA(df$score_b), df$agent_a != df$agent_b, df$forfeit %in% c("", "V", "H", "T"),
          !any(as.matrix(df) == "NA", na.rm = TRUE), df$season >= 1871, df$season <= 2025,
          !anyDuplicated(df[, c("date", "agent_a", "agent_b", "game_num")]))

n <- "retrosheet_mlb_1871_2025"
write.csv(df, file = paste0(n, ".csv"), row.names = FALSE, na = "")
cat(n, nrow(df), "games,", length(unique(c(df$agent_a, df$agent_b))), "agents,",
    sum(df$winner == "draw"), "draws,", sum(df$forfeit != ""), "forfeits\n")
print(table(df$game_type))
print(table(df$forfeit))
