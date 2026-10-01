## Meta Kaggle (https://www.kaggle.com/datasets/kaggle/meta-kaggle), Kaggle's own daily dump of
## its platform records. Simulation competitions: one row per episode (game) between two
## submitted bots.
## Licence: "Apache 2.0" (licenseName in the Kaggle API record for kaggle/meta-kaggle, dataset
## version 2332, last updated 2026-09-30T06:07:34Z, checked 2026-09-30). The dataset description
## says: "We also updated the license on Meta Kaggle from CC-BY-NC-SA to Apache 2.0."
## The files are re-dumped daily, so a rerun picks up later episodes of any competition
## still running (kaggriculture, connectx).
##
## Inputs (anonymous download, no API key needed): Episodes.csv (8.2 GB), EpisodeAgents.csv
## (27.6 GB), Submissions.csv (2.6 GB), Competitions.csv. Each is converted once to parquet
## (only the columns used) with arrow, so nothing is held in memory whole.
##
## Tables (metakaggle_<competition>_<firstyear>_<lastyear>), one per simulation competition
## whose episodes are 1v1:
##   metakaggle_connectx_2020_2026              connectx (Getting Started, open since 2020)
##   metakaggle_google_football_2020_2020       google-football
##   metakaggle_halite_iv_playground_2020_2021  halite-iv-playground-edition (1v1 Halite)
##   metakaggle_rock_paper_scissors_2020_2021   rock-paper-scissors
##   metakaggle_santa_2020_2021                 santa-2020 (two-player bandit game)
##   metakaggle_lux_ai_s1_2021_2021             lux-ai-2021
##   metakaggle_kore_2022_2022                  kore-2022
##   metakaggle_kore_beta_2022_2022             kore-2022-beta (1v1 episodes only)
##   metakaggle_lux_ai_s2_beta_2022_2022        lux-ai-2022-beta
##   metakaggle_lux_ai_s2_2023_2023             lux-ai-season-2
##   metakaggle_connect_4_2023_2024             connect-4 (community competition)
##   metakaggle_lux_ai_s2_neurips_stage1_2023_2023, ..._stage2_2023_2023  lux-ai-season-2-neurips-*
##   metakaggle_lux_ai_s3_2024_2025             lux-ai-season-3
##   metakaggle_fide_chess_2024_2025            fide-google-efficiency-chess-ai-challenge
##   metakaggle_pokemon_tcg_2026_2026           pokemon-tcg-ai-battle
##   metakaggle_orbit_wars_2026_2026            orbit-wars (1v1 episodes only)
##   metakaggle_maze_crawler_2026_2026          maze-crawler
##   metakaggle_kaggriculture_2026_2026         kaggriculture
## Not built: halite (2020), hungry-geese and llm-20-questions (every episode has 4 agents);
## copy22-of-connectx (4 submissions), connect-4clone1 (10 submissions) and
## the-pokemon-company-ptcg-ai-battle-challenge-playground (1,766 episodes, opened 2026-09-29).
##
## Choices:
## - agent = SubmissionId. A submission is a fixed bot, so one agent is one unchanging program;
##   a team's successive bots are separate agents. team_a/team_b give the submitting team
##   (Submissions.TeamId) so users can group them; blank where the submission is missing from
##   Submissions.csv (counted in the summary line). Meta Kaggle omits every connectx and
##   kaggriculture submission from Submissions.csv, so team_a/team_b are blank throughout
##   those two tables.
## - agent_a is seat 0 (EpisodeAgents.Index 0), agent_b seat 1. homefield is "agent_a" only
##   where seat 0 moves first: connectx and connect_4 (seat 0 starts ACTIVE in the
##   kaggle-environments connectx interpreter) and fide_chess (seat 0 starts ACTIVE and all
##   2,000 opening FENs in the chess env have White to move, so seat 0 is White; games were
##   scheduled in colour-swapped pairs). Blank for the rest: their environments move both
##   players simultaneously (no ACTIVE/INACTIVE alternation), and in pokemon_tcg the engine
##   decides who starts and alternates it between the games of a match.
## - Only Type == "Public" episodes; Validation episodes (a new submission against copies
##   of itself) are excluded. Only episodes with exactly two agents are kept: orbit_wars and
##   kore_2022_beta also ran 4-player free-for-alls, which are dropped and counted.
## - score_a/score_b are EpisodeAgents.Reward, whose meaning is game-specific: +1/-1/0 (connectx,
##   pokemon_tcg, orbit_wars), 1/0.5/0 (chess), goal difference (football), round-win margin
##   with |margin| < 20 clipped to 0 (rock-paper-scissors), candy collected (santa_2020),
##   city tiles*10000+units (lux 2021), lichen or -1000 if eliminated (lux S2), match wins
##   out of 5 (lux S3), kore/halite held or a negative elimination step (kore, halite IV),
##   money at the end (kaggriculture), energy or a negative elimination step (maze_crawler).
##   winner compares the two rewards; equal rewards are a draw.
## - Agent failures are kept as forfeits. When an agent times out, crashes (ErrorEvaluation)
##   or makes an invalid action, its Reward is missing; Kaggle's rating update counted the
##   episode as a loss for it and a win for the opponent (checked in chess, rps and
##   pokemon_tcg: the failing agent's UpdatedScore fell, and the opponent's rose, in over
##   99.7% of such episodes). So
##   winner is the agent that did not fail, the failed side's score is blank, and
##   error = "agent_a"/"agent_b" with error_type = timeout/evaluation/invalid_action says which
##   side failed and how. Filter on error == "" for played-out games only. Chess timeouts are
##   ~9% of fide_chess episodes and are losses on time under the competition's time control.
##   Episodes where both agents failed have no result and are dropped (counted).
## - date: Episodes.EndTime (CreateTime if blank), as UNIX seconds; Meta Kaggle times are UTC.
## - episode_id is kept so rows can be traced back to Kaggle's replay viewer.
## - Kaggle's ratings (InitialScore/UpdatedScore, the Confidence columns) are model output and
##   are not carried.
## Run time: ~1 h for the downloads at ~16 MB/s, then ~30 min to build; fits in 30 GB RAM.
## kaggriculture was still running on 2026-09-30 (games until ~2026-10-15), so that table is a
## snapshot of its episodes to 2026-09-30.
suppressMessages({library(arrow); library(dplyr); library(data.table)})
cache <- path.expand("~/.cache/irw-comps/metakaggle")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
options(timeout = 24 * 3600)
base <- "https://www.kaggle.com/api/v1/datasets/download/kaggle/meta-kaggle/"
for (f in c("Competitions.csv", "Episodes.csv", "EpisodeAgents.csv", "Submissions.csv")) {
    d <- file.path(cache, f)
    if (!file.exists(d)) {  # anonymous download works; EpisodeAgents.csv is ~27.5 GB
        download.file(paste0(base, f), paste0(d, ".part"), mode = "wb")
        file.rename(paste0(d, ".part"), d)
    }
}

## One streamed pass per big CSV into parquet (only the columns used), cached.
to_pq <- function(f, schema, cols) {
    out <- file.path(cache, sub("\\.csv$", "_pq", f))
    if (!dir.exists(out)) {
        open_dataset(file.path(cache, f), format = "csv", schema = schema, skip = 1) |>
            select(all_of(cols)) |>
            write_dataset(paste0(out, ".tmp"), format = "parquet", max_rows_per_file = 5e7)
        file.rename(paste0(out, ".tmp"), out)
    }
    open_dataset(out)
}
ep <- to_pq("Episodes.csv",
            schema(Id = int64(), Type = utf8(), CompetitionId = int64(), CreateTime = utf8(), EndTime = utf8()),
            c("Id", "Type", "CompetitionId", "CreateTime", "EndTime"))
ea <- to_pq("EpisodeAgents.csv",
            schema(Id = int64(), EpisodeId = int64(), Index = int32(), Reward = float64(), State = utf8(),
                   SubmissionId = int64(), InitialConfidence = float64(), InitialScore = float64(),
                   UpdatedConfidence = float64(), UpdatedScore = float64()),
            c("EpisodeId", "Index", "Reward", "State", "SubmissionId"))
sub <- to_pq("Submissions.csv",
             schema(Id = int64(), SubmittedUserId = int64(), TeamId = int64(), SourceKernelVersionId = int64(),
                    SubmissionDate = utf8(), ScoreDate = utf8(), IsAfterDeadline = utf8(), IsSelected = utf8(),
                    PublicScoreLeaderboardDisplay = utf8(), PublicScoreFullPrecision = utf8(),
                    PrivateScoreLeaderboardDisplay = utf8(), PrivateScoreFullPrecision = utf8()),
             c("Id", "TeamId"))

## ---- competitions kept (2-player episodes only) ----
## first = TRUE where seat 0 (agent_a) moves first.
keep <- data.table(
    id   = c(17592, 21723, 22806, 22838, 24539, 30067, 34419, 35272, 40898, 45040,
             54014, 54859, 60243, 86411, 86524, 116727, 138420, 140389, 147734),
    name = c("connectx", "google_football", "halite_iv_playground", "rock_paper_scissors", "santa",
             "lux_ai_s1", "kore", "kore_beta", "lux_ai_s2_beta", "lux_ai_s2",
             "connect_4", "lux_ai_s2_neurips_stage1", "lux_ai_s2_neurips_stage2", "lux_ai_s3",
             "fide_chess", "pokemon_tcg", "orbit_wars", "maze_crawler", "kaggriculture"),
    first = c(TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE,
              TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE))
comp <- fread(file.path(cache, "Competitions.csv"), select = c("Id", "Slug"))
keep <- merge(keep, comp, by.x = "id", by.y = "Id", sort = FALSE)
stopifnot(nrow(keep) == 19)
only <- commandArgs(TRUE)   # optional: build only the named tables, e.g. Rscript metakaggle.R connect_4
if (length(only)) keep <- keep[name %in% only]
team <- sub |> rename(SubmissionId = Id) |> compute()
out_dir <- path.expand("~/.cache/irw-comps/metakaggle-out")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

## State codes: 0 = Complete, 1 = timeout, 2 = evaluation error, 3 = invalid action.
err_code <- c("", "timeout", "evaluation", "invalid_action")
for (k in seq_len(nrow(keep))) {
    cid <- keep$id[k]
    ## Everything up to the collect runs in arrow; R only sees numeric columns.
    e <- ep |> filter(CompetitionId == cid, Type == "Public") |>
        mutate(t = if_else(is.na(EndTime) | EndTime == "", CreateTime, EndTime),
               date = cast(strptime(t, format = "%m/%d/%Y %H:%M:%S", tz = "UTC", unit = "s"), int64())) |>
        select(Id, date) |> compute()
    n_ep <- nrow(e)
    a <- ea |> inner_join(e, by = c("EpisodeId" = "Id")) |>
        mutate(st = case_when(State == "Complete" ~ 0L, State == "ErrorTimeout" ~ 1L,
                              State == "ErrorEvaluation" ~ 2L, State == "ErrorInvalidAction" ~ 3L, TRUE ~ 9L)) |>
        select(EpisodeId, Index, SubmissionId, Reward, st, date) |> compute()
    na <- a |> count(EpisodeId) |> compute()
    n_multi <- na |> filter(n != 2) |> nrow()    # 4-player episodes (orbit_wars, kore_2022_beta)
    n_empty <- n_ep - nrow(na)                     # public episodes with no agent rows
    two <- na |> filter(n == 2) |> select(EpisodeId) |> compute()
    a <- a |> semi_join(two, by = "EpisodeId") |> left_join(team, by = "SubmissionId") |> compute()
    s0 <- a |> filter(Index == 0) |> select(EpisodeId, agent_a = SubmissionId, score_a = Reward, st_a = st,
                                            team_a = TeamId, date)
    s1 <- a |> filter(Index == 1) |> select(EpisodeId, agent_b = SubmissionId, score_b = Reward, st_b = st,
                                            team_b = TeamId)
    x <- inner_join(s0, s1, by = "EpisodeId") |> collect() |> as.data.table()
    stopifnot(nrow(x) == nrow(two), nrow(a) == 2 * nrow(two),   # exactly one agent per seat
              x$st_a != 9L, x$st_b != 9L)
    rm(a, na, two, e); gc()
    ok_a <- x$st_a == 0L; ok_b <- x$st_b == 0L
    ## A failed agent forfeits: Kaggle scored these as a loss for it and a win for the opponent.
    x[, winner := fifelse(ok_a & ok_b,
                          fifelse(score_a > score_b, "agent_a", fifelse(score_a < score_b, "agent_b", "draw")),
                          fifelse(ok_a, "agent_a", fifelse(ok_b, "agent_b", NA_character_)))]
    x[!ok_a, score_a := NA]; x[!ok_b, score_b := NA]
    x[, error := fifelse(!ok_a, "agent_a", fifelse(!ok_b, "agent_b", ""))]
    x[, error_type := err_code[fifelse(!ok_a, st_a, st_b) + 1L]]
    n_both <- sum(!ok_a & !ok_b)
    n_nores <- sum(is.na(x$winner)) - n_both   # both completed but a reward missing
    n_self <- sum(x$agent_a == x$agent_b)
    x <- x[!is.na(winner) & agent_a != agent_b]
    x[, homefield := if (keep$first[k]) "agent_a" else ""]
    x <- x[, .(agent_a, agent_b, date, homefield, score_a, score_b, winner, team_a, team_b,
               episode_id = EpisodeId, error, error_type)]
    setorder(x, date, episode_id)
    stopifnot(!anyNA(x$date), !anyNA(x$agent_a), !anyNA(x$agent_b), x$winner %in% c("agent_a", "agent_b", "draw"),
              !anyNA(x$error_type), all(is.na(x$score_a) == (x$error == "agent_a")),
              all(is.na(x$score_b) == (x$error == "agent_b")))
    yr <- format(as.POSIXct(range(x$date), origin = "1970-01-01", tz = "UTC"), "%Y")
    nm <- paste("metakaggle", keep$name[k], yr[1], yr[2], sep = "_")
    fwrite(x, file.path(out_dir, paste0(nm, ".csv")), na = "")
    cat(sprintf("%s (%s): %d rows, %d agents, %d teams, %s to %s, %d draws, homefield %s, %d forfeits, %d agents without a team; dropped %d both-failed, %d no-reward, %d self-play, %d non-2-agent, %d empty episodes (of %d public)\n",
                nm, keep$Slug[k], nrow(x), uniqueN(c(x$agent_a, x$agent_b)), uniqueN(c(x$team_a, x$team_b)),
                format(as.POSIXct(min(x$date), origin = "1970-01-01", tz = "UTC")),
                format(as.POSIXct(max(x$date), origin = "1970-01-01", tz = "UTC")),
                sum(x$winner == "draw"), if (keep$first[k]) "agent_a" else "blank",
                sum(x$error != ""), uniqueN(c(x[is.na(team_a), agent_a], x[is.na(team_b), agent_b])), n_both, n_nores, n_self, n_multi, n_empty, n_ep))
    rm(x); gc()
}
