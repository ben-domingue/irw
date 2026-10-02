##University Challenge (BBC quiz), match results of the main series 1994-95 to 2026-27,
##parsed from the English Wikipedia series pages "University Challenge YYYY-YY", each
##pinned to the revision fetched 2026-10-01 (revision ids in `revs` below; read via
##https://en.wikipedia.org/w/index.php?oldid=<id>&action=raw).
##Licence: Wikipedia page footer, "Text is available under the Creative Commons
##Attribution-ShareAlike 4.0 License" (CC BY-SA 4.0), checked 2026-10-01. Attribution:
##the Wikipedia contributors to those pages (see each revision's history).
##
##Scope: every results table whose header names "Team 1" and "Score" (first round,
##highest-scoring-losers play-offs, second round, quarter-final group matches,
##semi-finals, final). Tables under the "Spin-off: Christmas Special" sections are skipped
##(alumni teams, a different competition), as are standings tables. The 2026-27 series
##is in progress, so its page holds only the matches broadcast so far.
##
##One row per match, in page order. agent_a = Team 1, agent_b = Team 2, as Wikipedia
##lists them; an agent is the institution's Wikipedia link target, or the plain cell text
##where there is no link. Link targets that are redirects are mapped to the article they
##redirect to (`redirect` below, resolved with the Wikipedia API on 2026-10-01, e.g.
##"The Open University" -> "Open University", "University of Durham" -> "Durham
##University"), so an institution keeps one name across series. Renamed or merged
##institutions follow Wikipedia (e.g. City University London -> City St George's,
##University of London); predecessor bodies with their own article (e.g. Victoria
##University of Manchester) stay separate. score_a/score_b are the final scores;
##winner from the score. Where the scores are level the match was decided by a tie-break
##question: winner is the team the page marks in bold and tiebreak = 1; if neither is
##bold, winner = "draw". date = broadcast date in Unix seconds, UTC midnight (blank where
##the cell has no readable date). series (e.g. "2016-17") and stage (the section heading)
##are kept. homefield is blank. Results are as played and broadcast: e.g. the 2008-09 final
##is Corpus Christi, Oxford's win, although the team was later disqualified and the title
##given to Manchester. Rows lacking either score (7 at these revisions) are
##dropped.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/uc")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
revs <- c(`1994-95` = 1373844442, `1995-96` = 1311537624, `1996-97` = 1358978587,
          `1997-98` = 1373844500, `1998-99` = 1373844091, `1999-00` = 1361017928,
          `2000-01` = 1311752532, `2001-02` = 1325939026, `2002-03` = 1311537629,
          `2003-04` = 1371861406, `2004-05` = 1361017690, `2005-06` = 1361017793,
          `2006-07` = 1361017590, `2007-08` = 1361017515, `2008-09` = 1373844311,
          `2009-10` = 1377367432, `2010-11` = 1357804537, `2011-12` = 1311752539,
          `2012-13` = 1361017354, `2013-14` = 1311537636, `2014-15` = 1361017212,
          `2015-16` = 1311752541, `2016-17` = 1353995663, `2017-18` = 1325526004,
          `2018-19` = 1361016992, `2019-20` = 1361016846, `2020-21` = 1311522172,
          `2021-22` = 1311537641, `2022-23` = 1311752547, `2023-24` = 1344740355,
          `2024-25` = 1351925386, `2025-26` = 1364165073, `2026-27` = 1377701230)

redirect <- c(
  "City University London" = "City St George's, University of London",
  "City University, London" = "City St George's, University of London",
  "Imperial College, London" = "Imperial College London",
  "King's College London School of Medicine" = "King's College London GKT School of Medical Education",
  "King's College London School of Medicine and Dentistry" = "King's College London GKT School of Medical Education",
  "King's College, London" = "King's College London",
  "London School of Hygiene & Tropical Medicine" = "London School of Hygiene and Tropical Medicine",
  "Queen Mary, University of London" = "Queen Mary University of London",
  "Queen's College, Oxford" = "The Queen's College, Oxford",
  "Queen's University, Belfast" = "Queen's University Belfast",
  "SOAS, University of London" = "SOAS University of London",
  "School of Oriental and African Studies" = "SOAS University of London",
  "South Bank University" = "London South Bank University",
  "The Courtauld Institute of Art" = "Courtauld Institute of Art",
  "The Open University" = "Open University",
  "University of Aberystwyth" = "Aberystwyth University",
  "University of Central Lancashire" = "University of Lancashire",
  "University of Durham" = "Durham University",
  "University of Lancaster" = "Lancaster University",
  "University of Middlesex" = "Middlesex University",
  "University of Wales, Cardiff" = "Cardiff University",
  "University of Wales, Swansea" = "Swansea University")

wiki <- function(rev) {
  f <- file.path(cache, paste0(rev, ".wiki"))
  if (!file.exists(f)) {
    download.file(paste0("https://en.wikipedia.org/w/index.php?oldid=", rev, "&action=raw"), f,
                  mode = "wb", headers = c(`User-Agent` = "irw-competitions/1.0 (research)"))
    Sys.sleep(3)
  }
  readLines(f, encoding = "UTF-8", warn = FALSE)
}
## strip cell attributes (style="..."|), refs, comments and templates such as {{fontcolor|white|130}}
clean <- function(s) {
  s <- gsub("<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", "", s, perl = TRUE)
  s <- gsub("\\{\\{[^{}|]*\\|[^{}|]*\\|([^{}]*)\\}\\}", "\\1", s, perl = TRUE)
  s <- gsub("^\\s*(?:[a-z-]+\\s*=\\s*(?:\"[^\"]*\"|'[^']*'|[^\\s|\\[]+)\\s*)+\\|(?!\\|)", "", s, perl = TRUE)
  trimws(s)
}
team <- function(s) {
  m <- regmatches(s, regexpr("\\[\\[[^]|]+", s))
  if (length(m)) return(trimws(sub("^\\[\\[", "", m)))
  trimws(gsub("'''|''|\\[|\\]", "", s))
}
score <- function(s) {
  n <- regmatches(s, gregexpr("[0-9]+", s))[[1]]
  if (length(n)) as.integer(n[length(n)]) else NA_integer_
}

rows <- list()
for (se in names(revs)) {
  w <- wiki(revs[[se]])
  h2 <- ""; h3 <- ""; i <- 1
  while (i <= length(w)) {
    l <- w[i]
    if (grepl("^==[^=].*==\\s*$", l)) { h2 <- trimws(gsub("=", "", l)); h3 <- "" }
    else if (grepl("^===+.*===+\\s*$", l)) h3 <- trimws(gsub("=", "", l))
    if (grepl("^\\{\\|", l)) {
      j <- i
      while (!grepl("^\\|\\}", w[j])) j <- j + 1
      tab <- w[(i + 1):(j - 1)]
      hdr <- paste(tab[grepl("^!", tab)], collapse = " ")
      if (grepl("Team 1", hdr) && grepl("Score", hdr) && !grepl("Spin-off|Christmas", h2)) {
        brk <- c(which(grepl("^\\|-", tab)), length(tab) + 1)
        for (k in seq_len(length(brk) - 1)) {
          seg <- tab[(brk[k] + 1):(brk[k + 1] - 1)]
          seg <- seg[grepl("^\\|", seg) & !grepl("^\\|-|^\\|\\}", seg)]
          if (!length(seg)) next
          cells <- unlist(strsplit(sub("^\\|", "", seg), "||", fixed = TRUE))
          cells <- vapply(cells, clean, "", USE.NAMES = FALSE)
          if (length(cells) < 5) next
          rows[[length(rows) + 1]] <- data.frame(
            series = se, stage = if (nzchar(h3)) h3 else h2,
            a = team(cells[1]), b = team(cells[4]),
            bold_a = grepl("'''", cells[1]), bold_b = grepl("'''", cells[4]),
            score_a = score(cells[2]), score_b = score(cells[3]),
            date = cells[length(cells)], stringsAsFactors = FALSE)
        }
      }
      i <- j
    }
    i <- i + 1
  }
}
x <- do.call(rbind, rows)
for (s in c("a", "b")) x[[s]] <- ifelse(x[[s]] %in% names(redirect), redirect[x[[s]]], x[[s]])
## rows without both scores (e.g. a match listed before broadcast) cannot be scored
nd <- sum(is.na(x$score_a) | is.na(x$score_b))
x <- x[!is.na(x$score_a) & !is.na(x$score_b), ]

d <- gsub("'''|''|\\[|\\]", "", x$date)
dt <- as.numeric(as.POSIXct(d, format = "%d %B %Y", tz = "UTC"))
tie <- x$score_a == x$score_b
df <- data.frame(agent_a = x$a, agent_b = x$b, date = dt, homefield = "",
                 winner = ifelse(x$score_a > x$score_b, "agent_a", ifelse(x$score_a < x$score_b, "agent_b",
                          ifelse(x$bold_a & !x$bold_b, "agent_a", ifelse(x$bold_b & !x$bold_a, "agent_b", "draw")))),
                 score_a = x$score_a, score_b = x$score_b, tiebreak = as.integer(tie),
                 series = x$series, stage = x$stage)
stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), nzchar(df$agent_a), nzchar(df$agent_b),
          df$agent_a != df$agent_b)
out <- "university_challenge_1994_2026.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "matches,", length(unique(c(df$agent_a, df$agent_b))), "institutions,",
    sum(tie), "tie-breaks,", sum(df$winner == "draw"), "draws,", sum(is.na(df$date)),
    "without a date; dropped", nd, "rows without both scores\n")
