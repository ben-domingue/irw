## International football results (men's and women's), Mart Jürisoo (martj42)
## https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017
## https://www.kaggle.com/datasets/martj42/womens-international-football-results
## Licence: CC0 Public Domain (Kaggle API licenseName, checked 2026-09-30). Refs #1169.
##
## Choices:
## - winner is decided by the score after 90/120 minutes; draws stay "draw".
## - shootouts.csv is joined on (date, home, away) and kept as `shootout_winner`
##   (agent_a/agent_b/blank). It is not folded into winner: some shootouts follow a
##   match that was not drawn (second legs of two-legged ties), so a shootout
##   settles a tie rather than the match.
## - neutral == TRUE means neither side was at home, so homefield is blank.
## - Teams keep the names the source uses at the time of the match (former_names.csv
##   is not applied), so e.g. Dahomey and Benin are separate agents.

cache <- path.expand("~/.cache/irw-comps")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)

get <- function(slug) {
    out <- file.path(cache, basename(slug))
    if (!file.exists(file.path(out, "results.csv"))) {
        zip <- paste0(out, ".zip")
        download.file(paste0("https://www.kaggle.com/api/v1/datasets/download/", slug), zip, mode = "wb")
        unzip(zip, exdir = out)
    }
    out
}

build <- function(dir) {
    r <- read.csv(file.path(dir, "results.csv"), stringsAsFactors = FALSE)
    s <- read.csv(file.path(dir, "shootouts.csv"), stringsAsFactors = FALSE)
    df <- data.frame(agent_a = r$home_team, agent_b = r$away_team)
    df$date <- as.numeric(as.POSIXct(r$date, format = "%Y-%m-%d", tz = "UTC"))
    df$homefield <- ifelse(r$neutral %in% c(TRUE, "TRUE"), "", "agent_a")
    df$score_a <- r$home_score
    df$score_b <- r$away_score
    df$winner <- ifelse(df$score_a > df$score_b, "agent_a",
                 ifelse(df$score_a < df$score_b, "agent_b", "draw"))
    k <- paste(r$date, r$home_team, r$away_team)
    so <- s$winner[match(k, paste(s$date, s$home_team, s$away_team))]
    df$shootout_winner <- ifelse(is.na(so), "",
                          ifelse(so == df$agent_a, "agent_a", "agent_b"))
    df$tournament <- r$tournament
    df$city <- r$city
    df$country <- r$country
    stopifnot(!anyNA(df$date), !anyNA(df$score_a), !anyNA(df$score_b))
    df
}

men <- build(get("martj42/international-football-results-from-1872-to-2017"))
women <- build(get("martj42/womens-international-football-results"))

write.csv(men, "intlfootball_men_1872_2026.csv", row.names = FALSE)
write.csv(women, "intlfootball_women_1956_2026.csv", row.names = FALSE)
