##Quizbowl: 2018 ACF Regionals, game results rebuilt from buzz-level detailed stats.
##quizbowl/open-data, https://github.com/quizbowl/open-data, pinned to commit
##5d86399bda90b6d7af514b6d035419016816f378, files detailed-stats/question-sets/2018/
##acf-regionals/tournaments/all/denormalized/tsv/{tossups,bonuses}.tsv.
##Licence: README.md, "This dataset is released under the [Open Database License
##(ODbL)](https://opendatacommons.org/licenses/odbl/summary/). This is a "share-alike"
##license, meaning that if you distribute a work that builds upon this data, you must make
##it available under the same license in order to maintain the same freedoms for others."
##(checked 2026-10-01; GitHub API "license": ODbL-1.0). Attribution requested: "a link to
##this repository (<https://github.com/quizbowl/open-data>) ... and, if applicable, a link
##to the specific version of the data used" (the commit above).
##
##The source has no game table, only one row per buzz (tossups.tsv) and per bonus
##(bonuses.tsv). A game is one (question_set_edition, tournament, room, round). A team's
##score is the sum of its tossup buzz_value (10 correct, -5 neg, 0 incorrect without
##penalty) plus all points it earned on bonuses (value1 + value2 + value3).
##
##One row per game. Teams are unique across the 12 regional sites (`tournament`), so all
##games form one table; teams only play within their own site. agent_a/agent_b = the two
##teams in alphabetical order (the source has no home side); winner from the score,
##"draw" on a tie. Games in which only one team appears (its opponent never buzzed or
##took a bonus, so it cannot be named) are dropped and counted. score_a/score_b,
##tu_a/tu_b (tossups answered correctly), neg_a/neg_b (negs), tournament (site), room,
##round and edition (question_set_edition) are kept. There is no date: the edition date
##labels the question-set edition, which the source does not tie to the day of play.
##Player names are not kept. homefield is blank.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/quizbowl")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
base <- paste0("https://raw.githubusercontent.com/quizbowl/open-data/5d86399bda90b6d7af514b6d035419016816f378/",
               "detailed-stats/question-sets/2018/acf-regionals/tournaments/all/denormalized/tsv/")
md5 <- c(tossups.tsv = "2e550b9a8267d3238c99582122ae815b", bonuses.tsv = "992640755468e9b7fedd281d32e050ac")
for (fn in names(md5)) {
  f <- file.path(cache, fn)
  if (!file.exists(f)) download.file(paste0(base, fn), f, mode = "wb")
  stopifnot(unname(tools::md5sum(f)) == md5[[fn]])
}
rd <- function(fn) read.delim(file.path(cache, fn), stringsAsFactors = FALSE, quote = "", na.strings = "")
tu <- rd("tossups.tsv")
bo <- rd("bonuses.tsv")
stopifnot(all(tu$buzz_value %in% c(10, -5, 0)))

key <- c("question_set_edition", "tournament", "room", "round")
tu$pts <- tu$buzz_value
bo$pts <- rowSums(bo[, c("value1", "value2", "value3")], na.rm = TRUE)
tu$tu <- as.integer(tu$buzz_value == 10)
tu$neg <- as.integer(tu$buzz_value == -5)
bo$tu <- 0L
bo$neg <- 0L
all <- rbind(tu[, c(key, "team", "pts", "tu", "neg")], bo[, c(key, "team", "pts", "tu", "neg")])
s <- aggregate(cbind(pts, tu, neg) ~ question_set_edition + tournament + room + round + team, data = all, FUN = sum)
s <- s[order(s$question_set_edition, s$tournament, s$room, s$round, s$team), ]
g <- paste(s$question_set_edition, s$tournament, s$room, s$round)
k <- table(g)
stopifnot(all(k %in% 1:2))
nd <- sum(k == 1)
s <- s[g %in% names(k)[k == 2], ]
a <- s[seq(1, nrow(s), 2), ]
b <- s[seq(2, nrow(s), 2), ]
stopifnot(a$tournament == b$tournament, a$room == b$room, a$round == b$round,
          a$question_set_edition == b$question_set_edition, a$team < b$team)

df <- data.frame(agent_a = a$team, agent_b = b$team, homefield = "",
                 winner = ifelse(a$pts > b$pts, "agent_a", ifelse(a$pts < b$pts, "agent_b", "draw")),
                 score_a = a$pts, score_b = b$pts, tu_a = a$tu, tu_b = b$tu, neg_a = a$neg, neg_b = b$neg,
                 tournament = a$tournament, room = a$room, round = a$round, edition = a$question_set_edition)
df <- df[order(df$edition, df$tournament, df$round, df$room), ]
out <- "quizbowl_acf_regionals_2018.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "games,", length(unique(c(df$agent_a, df$agent_b))), "teams,",
    length(unique(df$tournament)), "sites,", sum(df$winner == "draw"), "ties; dropped", nd, "one-team games\n")
