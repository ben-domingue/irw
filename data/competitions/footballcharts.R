## Football Charts match results, 92 leagues (https://www.football-charts.com), one row per match
## Licence: CC BY 4.0 (Zenodo record metadata), sole creator Damir Devetak. The file's own
## DATA_DICTIONARY.md says "free to use for research and modelling with attribution to
## football-charts.com". Offered to the IRW by Devetak by email, 2026-10-19.
##
## Tables:
##   footballcharts_2023_2026   76,988 matches, 92 league competitions in 42 countries,
##                              2023-02-17 to 2026-07-05
##
## The deposit continues where FiveThirtyEight's spi_matches.csv stops: 538 closed and its
## file ends in 2023-12, so fivethirtyeight_soccer_2016_2023 is the corpus's most recent
## club-football table. The two overlap from 2023-02-17 to 2023-12 on the leagues 538 also
## covered, which is the window to check a splice on.
##
## The deposit is a ROLLING window -- it holds the three most recent completed seasons of
## each league, so next year's version will drop 2023 rather than add to it. The record DOI
## below is pinned for that reason; it is not the concept DOI (10.5281/zenodo.22295583),
## which always resolves to the newest version.
##
## Choices:
## - agent_a is the home team; homefield is "agent_a" on every row. The file has no neutral
##   -site flag and holds league matches only (no cups, no play-off finals), so the small
##   number of relocated or neutral fixtures cannot be identified and are not marked.
## - winner follows the full-time score, and agrees with the file's own `result` on all rows.
## - Half-time scores are split into ht_score_a/ht_score_b (85 rows have none).
## - goal_times is the file's all_goal_times: the minute of every goal, home and away
##   together, in order, and not attributed to a side. It is kept only where it is complete
##   and is actually minutes, so two kinds of row are blanked: 7 (all italy19) read the
##   literal string "Not found", and 78 list fewer minutes than the match had goals. Those
##   85 keep their result -- only the timing is unusable. After that, timing is present on
##   71,061 of 76,988 rows (92.3%); of the rest 5,785 are goalless and 142 scored but
##   untimed. (The deposit's first_goal_time column is dropped as redundant. It is also
##   wrong on two italy19 rows in 2026-05, where it reads "33.50", which is not a minute.)
## - Two bad rows in 77k, both 2026: an exact duplicate (france3 2026-02-06, Bourg en Bresse
##   v Le Puy-en-Velay) is de-duplicated, and a genuine conflict (germany-north 2026-04-26,
##   Werder Bremen II v Hamburger SV II, recorded both 1:1 with two goal minutes and 2:1 with
##   three) is dropped entirely, since there is no way to tell which row is right.
## - Agents are the deposit's team names, which are stable within a league; 347 teams appear
##   in two leagues of the same country through promotion and relegation, and that is the
##   same club. Five names are used by clubs in two different countries (Bohemians, Al
##   Ittihad, Al Qadisiya, Al Arabi, Al Shabab); only those five get " (country)" appended,
##   so that an agent is one club throughout.
## - Columns kept beyond the standard: season, league (short code), league_name, country,
##   ht_score_a, ht_score_b, goal_times. The deposit's ft_result, home_goals, away_goals,
##   total_goals and result are the standard columns under other names and are not repeated;
##   time and kickoff_utc are dropped (date carries the match date, and the 2026.09 version
##   of the deposit had the clock wrong). Note that date is the UTC date of the kickoff, so
##   a late local kickoff in the Americas or Asia sits one day after the date another
##   source would give it.
##
## Checked against fivethirtyeight_soccer_2016_2023 (2026-10-19). 538's played matches stop
## 2023-06-13, and in that window this deposit holds only summer-season leagues -- its
## European winter leagues begin with 2023-24 -- so the two sources share just three
## competitions there: Brasileiro Serie A (100 matches), Swedish Allsvenskan (98) and
## Norwegian Tippeligaen (83). Scores agree on all 281. 11 of the Brazilian matches sit one
## day later here, which is the UTC-date convention above, and the rest agree on the date
## too.

cache <- path.expand("~/.cache/irw-comps/footballcharts")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
## Zenodo record 23348754 = version 2026.10 of concept 22295583.
src <- c("https://zenodo.org/api/records/23348754/files/football_charts_matches.csv/content",
         "0b0a72c2c316e6b7a3f522d2e3fb258f")
f <- file.path(cache, "football_charts_matches.csv")
if (!file.exists(f)) download.file(src[1], f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == src[2])

x <- read.csv(f, stringsAsFactors = FALSE, na.strings = "", colClasses = "character")
stopifnot(nrow(x) == 76991, length(unique(x$league)) == 92, length(unique(x$country)) == 42)

key <- paste(x$league, x$season, x$match_date, x$home_team, x$away_team, sep = "\r")
## the france3 pair is identical in every column, so unique() keeps one of the two
dup <- duplicated(key) & duplicated(x)
stopifnot(sum(dup) == 1)
x <- x[!dup, ]
## what is left under a repeated key is the germany-north conflict: both rows go
key <- paste(x$league, x$season, x$match_date, x$home_team, x$away_team, sep = "\r")
conflict <- key %in% key[duplicated(key)]
stopifnot(sum(conflict) == 2, all(x$league[conflict] == "germany-north"))
x <- x[!conflict, ]
stopifnot(nrow(x) == 76988, !anyDuplicated(paste(x$league, x$season, x$match_date,
                                                 x$home_team, x$away_team, sep = "\r")))

num <- function(v) { n <- suppressWarnings(as.integer(v)); stopifnot(!anyNA(n[!is.na(v)])); n }
score_a <- num(x$home_goals); score_b <- num(x$away_goals)
stopifnot(!anyNA(score_a), !anyNA(score_b), score_a >= 0, score_b >= 0,
          x$ft_result == paste0(score_a, ":", score_b))

ht <- do.call(rbind, strsplit(ifelse(is.na(x$ht_result), ":", x$ht_result), ":", fixed = TRUE))
ht_a <- num(ifelse(ht[, 1] == "", NA, ht[, 1])); ht_b <- num(ifelse(ht[, 2] == "", NA, ht[, 2]))
stopifnot(sum(is.na(ht_a)) == 85, ht_a[!is.na(ht_a)] <= score_a[!is.na(ht_a)],
          ht_b[!is.na(ht_b)] <= score_b[!is.na(ht_b)])

## keep the goal minutes only where they are complete and are minutes
goals <- ifelse(is.na(x$all_goal_times), "", x$all_goal_times)
not_found <- grepl("[^0-9,]", goals)                   # 7 rows read "Not found"
stopifnot(sum(not_found) == 7, unique(goals[not_found]) == "Not found")
goals[not_found] <- ""
n_times <- ifelse(goals == "", 0L, lengths(strsplit(goals, ",", fixed = TRUE)))
incomplete <- goals != "" & n_times != score_a + score_b
stopifnot(sum(incomplete) == 78)
goals[incomplete] <- ""
timed <- goals != ""
stopifnot(sum(timed) == 71061, sum(!timed & score_a + score_b == 0) == 5785)

## five team names are used in two countries; those five are qualified, the rest are not
teams <- data.frame(team = c(x$home_team, x$away_team), country = c(x$country, x$country))
shared <- names(which(tapply(teams$country, teams$team, function(z) length(unique(z))) > 1))
stopifnot(length(shared) == 5)
qualify <- function(team, country) ifelse(team %in% shared, paste0(team, " (", country, ")"), team)

## integer, so that write.csv does not render round values as 1.728e+09
unix <- function(d) as.integer(as.POSIXct(d, format = "%Y-%m-%d", tz = "UTC"))
out <- data.frame(
    agent_a = qualify(x$home_team, x$country), agent_b = qualify(x$away_team, x$country),
    date = unix(x$match_date), homefield = "agent_a",
    score_a = score_a, score_b = score_b,
    winner = ifelse(score_a > score_b, "agent_a", ifelse(score_a < score_b, "agent_b", "draw")),
    season = x$season, league = x$league, league_name = x$league_name, country = x$country,
    ht_score_a = ht_a, ht_score_b = ht_b, goal_times = goals)
stopifnot(!anyNA(out$agent_a), !anyNA(out$agent_b), !anyNA(out$date), out$agent_a != out$agent_b,
          out$winner == c(H = "agent_a", A = "agent_b", D = "draw")[x$result],
          range(out$date) == unix(c("2023-02-17", "2026-07-05")))

write.csv(out, "footballcharts_2023_2026.csv", row.names = FALSE, na = "")
cat("footballcharts_2023_2026", nrow(out), "matches,",
    length(unique(c(out$agent_a, out$agent_b))), "agents,",
    length(unique(out$league)), "leagues,", length(unique(out$country)), "countries,",
    sum(out$winner == "agent_a"), "home wins,", sum(out$winner == "draw"), "draws,",
    sum(out$goal_times != ""), "timed\n")
