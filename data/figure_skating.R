## figure_skating: individual judges' marks from ISU figure skating protocols,
## 2016-17 and 2017-18 seasons. One row per judge per judged aspect per performance.
##
## Source: https://github.com/BuzzFeedNews/figure-skating-scores (data/tidy/), pinned at
## commit 6aacc688b9847653141a6034feb424723be52d35 (the repo's last commit, 2021-05-14).
## Licence: data files CC BY 4.0 per the repo README; code there is MIT. The underlying
## judging protocols are ISU documents, which that project parsed from the published PDFs.
## Citation: Singer-Vine, J. & Templon, J. (2021). ISU Figure Skating Score Sheets as
## Structured Data. BuzzFeed News.
##
## REBUILD (2026-10-29). The earlier version of this table read judged-aspects.csv and put
## `scores_of_panel` -- the panel's trimmed mean -- in `resp`, so it held one aggregate per
## aspect (23,077 rows) and no rater dimension. This version reads judge-scores.csv and puts
## the individual mark in `resp` with the judge in `rater`, which is what datastandard.md's
## "Rater data" section asks for ("the rater is never placed on `item`"). Two consequences,
## both deliberate:
##   - For components the old resp is recoverable: it was the trimmed mean of these nine
##     marks (checked over all 8,630 component aspects: median absolute difference 0.0029,
##     99.5% within 0.005 -- the rest is rounding in the protocols).
##   - For elements it is NOT. A judge's mark is a grade of execution in {-3..+3}; the old
##     resp was the element's base value plus the era's element-specific conversion of the
##     trimmed grade, so the trimmed mean matches the stored `goe` only 9.6% of the time
##     (median gap 0.43 points). `resp` on element rows therefore changes meaning, from
##     points to the grade the judge actually gave. Base values and panel points stay in the
##     source for anyone who wants to rebuild the points with the ISU conversion table.
##
## Choices:
## - id is the skater (or, in pairs and ice dance, the team), as an integer index. The
##   source names real skaters; the names are not carried into the table.
## - wave orders each id's performances in time: competition in ISU-calendar order, then
##   short segment before free. The competition dates are not in the source, so the order
##   below is the published ISU calendar for those two seasons, written out here. Only the
##   order is used, and `date` is not emitted because the source has no timestamps.
## - item is the judged aspect, prefixed by segment (`sp_` short program / short dance,
##   `fs_` free skating / free dance), because the same five components are marked in both
##   segments and they are separate ratings. An element a skater performed twice in one
##   programme gets `_2` on its second occurrence; the earlier build dropped all 50
##   performances that contained such a repeat, which this one keeps.
## - rater is the judge's seat, scoped to the programme (`<competition>|<program>|J3`),
##   because a panel is appointed per programme: J3 in the men's short at one event is a
##   different person from J3 in the ladies' free at another. The protocols identify judges
##   only by seat number, so a judge cannot be followed across programmes and the design is
##   152 disconnected panels.
## - resp is the mark: a grade of execution in {-3..+3} on element rows, a programme
##   component score in 0.25 steps from 0.25 to 10 on component rows. The two scales live in
##   one table, as they did before.
## - 89 aspects carry no marks in the source and so contribute no rows; 56 aspects were
##   marked by 8 judges rather than 9.

library(dplyr)
library(readr)
library(stringr)

sha <- "6aacc688b9847653141a6034feb424723be52d35"
cache <- path.expand("~/.cache/irw-sports/figure-skating")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
read_pinned <- function(name) {
    f <- file.path(cache, name)
    if (!file.exists(f))
        download.file(sprintf("https://raw.githubusercontent.com/BuzzFeedNews/figure-skating-scores/%s/data/tidy/%s", sha, name), f)
    read_csv(f, show_col_types = FALSE)
}
judge_scores <- read_pinned("judge-scores.csv")
aspects <- read_pinned("judged-aspects.csv")
performances <- read_pinned("performances.csv")

stopifnot(nrow(judge_scores) == 214531, nrow(aspects) == 23932, nrow(performances) == 1726)

## ISU calendar order for the two seasons covered (not in the source; see header).
comp_order <- c(
    "ISU GP 2016 Progressive Skate America",
    "ISU GP 2016 Skate Canada International",
    "ISU GP Rostelecom Cup 2016",
    "ISU GP Trophee de France 2016",
    "ISU GP Audi Cup of China 2016",
    "ISU GP NHK Trophy 2016",
    "ISU Grand Prix of Figure Skating Final 2016",
    "ISU European Figure Skating Championships 2017",
    "ISU Four Continents Championships 2017",
    "ISU World Figure Skating Championships 2017",
    "ISU GP Rostelecom Cup 2017",
    "ISU GP 2017 Skate Canada International",
    "ISU GP Audi Cup of China 2017",
    "ISU GP NHK Trophy 2017",
    "ISU GP Internationaux de France de Patinage 2017",
    "ISU GP 2017 Bridgestone Skate America",
    "Grand Prix Final 2017 Senior and Junior")
stopifnot(setdiff(performances$competition, comp_order) == character(0),
          length(comp_order) == 17)

slug <- function(x) {
    x <- tolower(x)
    x <- str_replace_all(x, "[^a-z0-9]+", "_")
    str_replace_all(x, "^_|_$", "")
}

perf <- performances |>
    mutate(segment = if_else(str_detect(program, "SHORT"), "sp", "fs"),
           level = if_else(str_detect(program, "^JUNIOR"), "junior", "senior"),
           discipline = str_replace(program, "^JUNIOR ", "") |>
               str_replace(" (SHORT|FREE).*$", "") |> tolower(),
           entry_type = if_else(str_detect(name, " / "), "team", "single"),
           comp_rank = match(competition, comp_order),
           seg_rank = if_else(segment == "sp", 1L, 2L)) |>
    select(performance_id, competition, program, name, nation,
           segment, level, discipline, entry_type, comp_rank, seg_rank)

## occurrence: 1 unless the programme contained that aspect more than once. Grouped on the
## item label, not the raw description, because the description also carries the technical
## panel's execution flags (`<` underrotated, `<<` downgraded, `!`, `e`, `*`), which are a
## judged outcome of the attempt rather than part of the element's identity -- they stay in
## the source's info_flag column and out of `item`. 60 performances contain a repeated
## element this way, 8 of them a flagged and an unflagged attempt at the same element.
occ <- aspects |>
    arrange(performance_id, aspect_num, aspect_id) |>
    group_by(performance_id, aspect_slug = slug(aspect_desc)) |>
    mutate(occurrence = row_number()) |>
    ungroup() |>
    select(aspect_id, performance_id, section, aspect_num, aspect_slug, occurrence)

## one row per judge per aspect, with the aspect and performance it belongs to
df <- judge_scores |>
    inner_join(occ, by = "aspect_id") |>
    inner_join(perf, by = "performance_id")
stopifnot(nrow(df) == nrow(judge_scores))

## item: segment-prefixed aspect, with an occurrence suffix when a programme repeats one
df <- df |>
    mutate(item = paste0(segment, "_", aspect_slug,
                         if_else(occurrence > 1, paste0("_", occurrence), "")))

## id = skater/team; wave = that id's performances in time order
ids <- df |> distinct(name) |> arrange(name) |> mutate(id = row_number())
df <- df |> left_join(ids, by = "name")
waves <- df |>
    distinct(id, performance_id, comp_rank, seg_rank) |>
    arrange(id, comp_rank, seg_rank) |>
    group_by(id) |>
    mutate(wave = row_number()) |>
    ungroup() |>
    select(id, performance_id, wave)
df <- df |> left_join(waves, by = c("id", "performance_id"))

out <- df |>
    transmute(id, item, resp = score, wave,
              cov_nation = nation, cov_discipline = discipline, cov_level = level,
              cov_entry_type = entry_type,
              rater = paste(competition, program, judge, sep = "|")) |>
    arrange(id, wave, item, rater)

## checks
stopifnot(nrow(out) == 214531,
          !any(is.na(out$id)), !any(is.na(out$item)), !any(is.na(out$resp)),
          !any(is.na(out$wave)), !any(is.na(out$rater)),
          n_distinct(df$performance_id) == 1726)
dup <- out |> count(id, item, wave, rater) |> filter(n > 1)
stopifnot(nrow(dup) == 0)
cat("rows", nrow(out), "ids", n_distinct(out$id), "items", n_distinct(out$item),
    "raters", n_distinct(out$rater), "\n")
print(range(out$resp))
print(table(cut(out$resp, c(-Inf, -0.001, 3.0001, Inf), labels = c("negative GOE", "0-3", ">3"))))
write.csv(out, file = "figure_skating.csv", row.names = FALSE, quote = TRUE, na = "")
