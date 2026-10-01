## wyscout_shots: soccer shots from Wyscout match event logs, one row per shot
##
## Source: Pappalardo, L., Cintia, P., Rossi, A., Massucco, E., Ferragina, P., Pedreschi, D.,
## & Giannotti, F. (2019). A public data set of spatio-temporal match events in soccer
## competitions. Scientific Data, 6, 236. https://doi.org/10.1038/s41597-019-0247-7
## Data: figshare collection 4415000 (https://doi.org/10.6084/m9.figshare.c.4415000).
## Events, Matches and the tag map are each "CC BY 4.0" on figshare (checked 2026-09-30);
## md5 below.
##
## Coverage: every match of the 2017-18 seasons of the English, French, German, Italian and
## Spanish first divisions, the 2018 World Cup and Euro 2016 (1,941 matches).
##
## A real-data counterpart to data/simsyn/nbashots_sim.R: players choose when and from
## where to shoot, so conversion rates mix finishing skill with shot selection; shot
## location (trial_dist, trial_angle) is what an analysis adjusts for.
##
## Choices:
## - id is the Wyscout player id (playerId). 3 shots with no player recorded (playerId 0)
##   are dropped.
## - item is the kind of shot: penalty, free_kick (direct free-kick shots), or, for shots in
##   open play and from corners and crosses, the body part Wyscout tags: foot or head (head
##   covers head/body). Every open-play shot carries one of the two tags.
## - resp = 1 if Wyscout tags the shot as a goal (tag 101), else 0. Saved, blocked, wide and
##   woodwork shots are all 0.
## - Shoot-out penalties (matchPeriod "P", World Cup and Euro only) are kept and flagged
##   by trial_shootout.
## - Location: Wyscout gives the shot origin as percentages of the pitch, with x toward the
##   goal being attacked (goal centre at x = 100, y = 50). These are kept as trial_locx and
##   trial_locy. trial_dist is metres to the goal centre and trial_angle is the angle (degrees)
##   the goal mouth subtends from the shot, both on a 105 x 68 m pitch, which is an
##   approximation: pitch sizes vary.
## - date is the match date as Unix time; trial_gameclock is minutes into the match (second
##   half starts at 45; extra time at 90 and 105). trial_home = 1 for the home side,
##   NA at the World Cup and Euro (the first-named team is not playing at home, except
##   hosts Russia 2018 and France 2016, which are not flagged either).
## - trial_counter = 1 if Wyscout tags the shot as part of a counter-attack (tag 1901).
## - trial_number orders each player's shots in time.

library(jsonlite)

cache <- path.expand("~/.cache/irw-sports/wyscout")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
src <- list(events.zip = c(14464685, "7c20e8647e7eda58d7838a0c7b1ec6ab"),
            matches.zip = c(14464622, "51d80beb17480919f69a53a0152c2d71"))
for (f in names(src)) {
    p <- file.path(cache, f)
    if (!file.exists(p)) download.file(paste0("https://ndownloader.figshare.com/files/", src[[f]][1]), p, mode = "wb")
    stopifnot(unname(tools::md5sum(p)) == src[[f]][2])
    unzip(p, exdir = file.path(cache, sub(".zip", "", f)))
}

comps <- c(England = "england", France = "france", Germany = "germany", Italy = "italy",
           Spain = "spain", European_Championship = "euro2016", World_Cup = "worldcup2018")
hastag <- function(tags, id) vapply(tags, function(t) id %in% t$id, logical(1))
L <- list()
for (cc in names(comps)) {
    print(cc)
    m <- fromJSON(file.path(cache, "matches", paste0("matches_", cc, ".json")), simplifyVector = FALSE)
    home <- do.call(rbind, lapply(m, function(g) {
        s <- vapply(g$teamsData, function(t) t$side, "")
        data.frame(matchId = g$wyId, home = as.integer(names(s)[s == "home"]),
                   date = as.numeric(as.POSIXct(substr(g$dateutc, 1, 10), format = "%Y-%m-%d", tz = "UTC")))
    }))
    e <- fromJSON(file.path(cache, "events", paste0("events_", cc, ".json")), simplifyVector = FALSE)
    e <- Filter(function(z) z$eventName == "Shot" || z$subEventName %in% c("Free kick shot", "Penalty"), e)
    tags <- lapply(e, function(z) vapply(z$tags, function(t) t$id, numeric(1)))
    tags <- lapply(tags, function(t) list(id = t))
    x <- data.frame(
        playerId = vapply(e, function(z) z$playerId, numeric(1)),
        matchId = vapply(e, function(z) z$matchId, numeric(1)),
        teamId = vapply(e, function(z) z$teamId, numeric(1)),
        period = vapply(e, function(z) z$matchPeriod, ""),
        sec = vapply(e, function(z) z$eventSec, numeric(1)),
        eventId = vapply(e, function(z) z$id, numeric(1)),
        sub = vapply(e, function(z) z$subEventName, ""),
        locx = vapply(e, function(z) z$positions[[1]]$x, numeric(1)),
        locy = vapply(e, function(z) z$positions[[1]]$y, numeric(1)),
        goal = hastag(tags, 101), head = hastag(tags, 403),
        foot = hastag(tags, 401) | hastag(tags, 402), counter = hastag(tags, 1901))
    x <- merge(x, home, by = "matchId")
    x$competition <- comps[[cc]]
    x$home <- if (cc %in% c("European_Championship", "World_Cup")) NA else as.integer(x$teamId == x$home)
    L[[cc]] <- x
}
x <- do.call(rbind, L)
stopifnot(nrow(x) == 45945, sum(x$playerId == 0) == 3)
x <- x[x$playerId > 0, ]

x$item <- ifelse(x$sub == "Penalty", "penalty",
          ifelse(x$sub == "Free kick shot", "free_kick",
          ifelse(x$head, "head", ifelse(x$foot, "foot", NA))))
stopifnot(!anyNA(x$item))

start <- c("1H" = 0, "2H" = 45, "E1" = 90, "E2" = 105, "P" = 120)
x$gameclock <- start[x$period] + x$sec / 60
dx <- (100 - x$locx) * 1.05
dy <- (50 - x$locy) * 0.68
x$dist <- sqrt(dx^2 + dy^2)
## angle between the lines to the two posts (goal 7.32 m wide)
x$angle <- abs(atan2(dy + 3.66, dx) - atan2(dy - 3.66, dx)) * 180 / pi
x <- x[order(x$playerId, x$date, x$matchId, x$gameclock, x$eventId), ]
x$trial_number <- ave(seq_len(nrow(x)), x$playerId, FUN = seq_along)

df <- data.frame(id = x$playerId, item = x$item, resp = as.integer(x$goal), date = x$date,
                 trial_number = x$trial_number, trial_competition = x$competition,
                 trial_match = x$matchId, trial_gameclock = round(x$gameclock, 2),
                 trial_shootout = as.integer(x$period == "P"), trial_home = x$home,
                 trial_locx = x$locx, trial_locy = x$locy, trial_dist = round(x$dist, 1),
                 trial_angle = round(x$angle, 1), trial_counter = as.integer(x$counter))
print(table(df$item, df$resp))
print(tapply(df$resp, df$item, mean))

write.csv(df, file = "wyscout_shots.csv", quote = FALSE, row.names = FALSE, na = "")
