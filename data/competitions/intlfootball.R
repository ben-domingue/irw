##International football results, men (1872-) and women (1956-), Mart Jürisoo
##(martj42). CC0 1.0: LICENSE in github.com/martj42/international_results, and
##"CC0: Public Domain" on both Kaggle pages
##(kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017,
## kaggle.com/datasets/martj42/womens-international-football-results).
##Built from the GitHub copies, pinned to the commits fetched 2026-09-30. Issue #1169.
##
##agent_a = home_team, agent_b = away_team; score_a/score_b = full-time score
##(including extra time, per the source); winner from the score, "draw" on a tie.
##homefield = "agent_a" unless the match was at a neutral venue (neutral = TRUE),
##where it is blank. A drawn match decided on penalties keeps winner = "draw";
##the shootout result is carried separately in shootout_winner (agent_a/agent_b),
##from shootouts.csv. Most shootouts follow a draw, but some (38 men's, 6 women's)
##follow the second leg of a two-legged tie that one side won on the day while the
##aggregate was level, so shootout_winner describes the tie, not that match's score.
##Rows with no score (fixtures not yet played) are dropped.
##tournament, city and country are kept as extra columns.

build <- function(repo, sha, out) {
  base <- paste0("https://raw.githubusercontent.com/martj42/", repo, "/", sha, "/")
  x <- read.csv(paste0(base, "results.csv"), stringsAsFactors = FALSE)
  so <- read.csv(paste0(base, "shootouts.csv"), stringsAsFactors = FALSE)
  x <- x[!is.na(x$home_score) & !is.na(x$away_score), ]

  df <- data.frame(agent_a = x$home_team, agent_b = x$away_team)
  df$date <- as.numeric(as.POSIXct(x$date, format = "%Y-%m-%d", tz = "UTC"))
  df$score_a <- x$home_score
  df$score_b <- x$away_score
  df$homefield <- ifelse(toupper(x$neutral) == "TRUE", "", "agent_a")
  df$winner <- ifelse(df$score_a > df$score_b, "agent_a",
               ifelse(df$score_a < df$score_b, "agent_b", "draw"))

  key <- paste(x$date, x$home_team, x$away_team)
  sw <- so$winner[match(key, paste(so$date, so$home_team, so$away_team))]
  df$shootout_winner <- ifelse(is.na(sw), "",
                        ifelse(sw == x$home_team, "agent_a",
                        ifelse(sw == x$away_team, "agent_b", NA)))
  stopifnot(!anyNA(df$shootout_winner), !anyNA(df$date))

  df$tournament <- x$tournament
  df$city <- x$city
  df$country <- x$country
  write.csv(df, file = out, row.names = FALSE, na = "")
  cat(out, nrow(df), "matches,", length(unique(c(df$agent_a, df$agent_b))), "teams,",
      sum(df$shootout_winner != ""), "shootouts\n")
}

build("international_results", "394fe81893b062fbc2cf6257e988ac7cc4c039a1",
      "intlfootball_men_1872-2026.csv")
build("womens-international-results", "1855e313ae8bcd0330426e62c8e4cf15ce45077c",
      "intlfootball_women_1956-2026.csv")
