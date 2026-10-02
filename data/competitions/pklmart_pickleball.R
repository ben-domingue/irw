## pklmart doubles pickleball game results, 2021-2025 -> irw_competitions (irw#2714).
##
## Source: "pklmart's Competitive Pickleball Extracts", Kaggle dataset
## cakesofspan/pklmarts-competitive-pickleball-extracts, version 6 (2025-04-20), published by
## the pklmart's own maintainer (Kaggle owner aspancake, the author of the pklmart data-entry
## tool, https://pklmart.com). Shot-by-shot data entered by players through the pklmart tool,
## doubles only, skill levels 2.5 to Pro.
##
## Licence: the Kaggle dataset page's licence field reads "CC BY-NC-SA 4.0" (Kaggle API
## `licenseName`, checked 2026-10-01). Non-commercial share-alike, so Derived License is
## CC BY-NC-SA 4.0 (ruling on #2714, 2026-10-01: NC licences can be hosted, NC carries into
## Derived License). The older NolanSmyth/pklshop repo (Apache-2.0) repackages a 2022 subset
## of the same database; it is not the publisher and is not used.
##
## Unit: one row per GAME, team vs team. The extract also holds 40,702 rallies and 304,649
## shots; rallies are points nested inside these games and are not used here (a possible
## follow-up). Choices:
## - agent_a is the winning team, agent_b the losing team (game.csv records only w_team_id /
##   l_team_id, not a side or serving order), so winner is always "agent_a"; score_a/score_b
##   are score_w/score_l. homefield is blank.
## - Agents are doubles teams, labelled by their two player ids sorted and joined with "_"
##   (e.g. "P27_P28"). team.csv gives two team ids (T15, T31) to the same pair; keying on the
##   pair merges them. Player ids are pklmart's pseudonymous ids; no names are published.
## - Dropped: 6 games whose recorded score is level (5-5, 12-12, 11-11, 8-8, 10-10, 21-21).
##   Pickleball has no drawn games, so these are unfinished entries and the recorded winner
##   cannot be checked. Dropped: 1 game (G253) whose winning team T212 is missing from
##   team.csv, so its players are unknown.
## - date = dt_played as Unix seconds (UTC midnight). Two games carry the placeholder
##   0001-01-01; their date is blank.
## - Kept: match_id, game_id, game_nbr (game within the match), skill_lvl (self-reported
##   level or "Pro"/"Senior Pro"), scoring_type (standard or MLP rally-scoring variants, which
##   run to higher scores), ball_type (pklmart's ball code), n_rallies (rallies entered for
##   the game; 0 where none were entered).

cache <- path.expand("~/.cache/irw-comps/pklmart")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
zf <- file.path(cache, "kaggle_v6.zip")
if (!file.exists(zf))
    download.file(paste0("https://www.kaggle.com/api/v1/datasets/download/cakesofspan/",
                         "pklmarts-competitive-pickleball-extracts?datasetVersionNumber=6"),
                  zf, mode = "wb")
stopifnot(unname(tools::md5sum(zf)) == "a9903c840f8a0429ef0600217b863c85")
rd <- function(n) read.csv(unz(zf, n), colClasses = "character", na.strings = character(0))
game <- rd("game.csv"); team <- rd("team.csv"); rally <- rd("rally.csv")
stopifnot(nrow(game) == 935, !anyDuplicated(game$game_id))

stopifnot(all(table(team$team_id) == 2))
team <- team[order(team$player_id), ]
pair <- tapply(team$player_id, team$team_id, paste, collapse = "_")

sw <- as.integer(game$score_w); sl <- as.integer(game$score_l)
level <- sw == sl
stopifnot(sum(level) == 6, all(sw >= sl))
unknown <- !(game$w_team_id %in% names(pair)) | !(game$l_team_id %in% names(pair))
stopifnot(identical(game$game_id[unknown], "G253"))
keep <- !level & !unknown
g <- game[keep, ]

nr <- table(rally$game_id)
dt <- ifelse(g$dt_played == "0001-01-01", NA, g$dt_played)
stopifnot(sum(is.na(dt)) == 2)
nrl <- as.integer(nr[g$game_id]); nrl[is.na(nrl)] <- 0L

df <- data.frame(agent_a = unname(pair[g$w_team_id]), agent_b = unname(pair[g$l_team_id]),
                 winner = "agent_a",
                 ## integer, so write.csv never prints 1.674e+09 (fits int32 until 2038)
                 date = as.integer(as.POSIXct(dt, format = "%Y-%m-%d", tz = "UTC")),
                 homefield = "", score_a = sw[keep], score_b = sl[keep],
                 match_id = g$match_id, game_id = g$game_id,
                 game_nbr = as.integer(g$game_nbr), skill_lvl = g$skill_lvl,
                 scoring_type = g$scoring_type, ball_type = g$ball_type, n_rallies = nrl,
                 stringsAsFactors = FALSE)
stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), df$agent_a != df$agent_b,
          df$score_a > df$score_b, nrow(df) == 928)
## same order as before: date (blanks first), then match, then game number
df <- df[order(!is.na(df$date), df$date, df$match_id, df$game_nbr, method = "radix"), ]
n <- "pklmart_pickleball_2021_2025"
write.csv(df, file = paste0(n, ".csv"), row.names = FALSE, na = "")
cat(n, nrow(df), "games,", length(unique(c(df$agent_a, df$agent_b))), "teams,",
    length(unique(df$match_id)), "matches\n")
