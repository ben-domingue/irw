## International rugby union: men's test matches between the ten tier-one nations (irw#2708).
##
## Source: English Wikipedia, the 45 head-to-head pages "History of rugby union matches
## between X and Y", one for every pair of Argentina, Australia, England, France, Ireland,
## Italy, New Zealand, Scotland, South Africa and Wales. Each page is pinned to the revision
## fetched on 2026-10-01 (`revs` below) and read with
## https://en.wikipedia.org/w/index.php?oldid=<id>&action=raw.
## Licence: Wikipedia page footer, "Text is available under the Creative Commons
## Attribution-ShareAlike 4.0 License" (CC BY-SA 4.0), checked 2026-10-01. Attribution: the
## Wikipedia contributors to those pages (see each revision's history). Ruled 2026-10-01
## (Ben, #2708): build from Wikipedia's own tables, not the Kaggle relabel of them.
##
## Scope and choices:
## - Rows come from every results table (a header with No., Date, Score and Winner) under the
##   page's test-results section. Tables under "XV results" / "Non-test results" headings
##   (uncapped matches, e.g. Australia v New Zealand 1920-28 when New South Wales stood in)
##   are skipped. Fixtures not yet played (score TBD/TBC/blank) and one abandoned match
##   (Ireland v Scotland, 1885) are dropped. The British & Irish Lions and tier-two nations
##   are out of scope: Wikipedia has no head-to-head page for most such pairs.
## - winner is the page's own Winner column ("agent_a", "agent_b" or "draw").
## - score_a / score_b: the page prints one score "x-y" without saying whose is first, so
##   the larger number goes to the winner (equal for a draw). Early matches decided on goals
##   (e.g. "2G-0G") have no points score: score_a / score_b are blank there and score_raw
##   keeps the printed score (order as printed on the page, not normalised). Before about
##   1890 the points values in the tables are the pages' own (scoring systems varied).
## - Home side: the venue's country, from its city or country name (mapping in `host_map`).
##   Ireland's home includes Belfast. agent_a is the home team and homefield = "agent_a";
##   where the venue is in neither team's country (World Cups, Hong Kong, the US, ...)
##   homefield is blank and agent_a / agent_b are in alphabetical order. host_country keeps
##   the venue's country.
## - date: match day as Unix seconds, UTC midnight. competition: the page's Competition (or
##   Comments) cell as plain text. venue: the Venue (and City) cell as plain text.
##
## Checked 2026-10-01 against Wikipedia's per-nation result lists (Wales, New Zealand,
## Australia, Argentina; South Africa's 2026 match boxes): 2,156 tier-one matches agree on
## pair, date (17 off by one day) and score; 6 scores differ, and in each case the list page
## is the one in error (e.g. Wales v England 1995 is 9-23). List-page matches not here are
## ones the head-to-head pages file as XV / uncapped (Australia v New South Wales-era New
## Zealand and South Africa 1920-28; Argentina v uncapped touring XVs 1952-79; New Zealand
## Army 1919) or carry on a different date (5 matches, e.g. Australia v South Africa 1992:
## 22 August on the list, 29 August on the head-to-head page).

invisible(Sys.setlocale("LC_TIME", "C"))
options(scipen = 100)  # write dates as whole seconds, never 8.1e+08
out_file <- "rugby_union_tier1_1871_2026.csv"
cache <- path.expand("~/.cache/irw-comps/rugby_union")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
T1 <- c("Argentina", "Australia", "England", "France", "Ireland", "Italy", "New Zealand",
        "Scotland", "South Africa", "Wales")
revs <- c(
  `Argentina and Australia` = 1373429561,
  `Argentina and England` = 1365022558,
  `Argentina and France` = 1365847561,
  `Argentina and Ireland` = 1335471789,
  `Argentina and Italy` = 1364778501,
  `Argentina and New Zealand` = 1310449946,
  `Argentina and Scotland` = 1364260103,
  `Argentina and South Africa` = 1368419884,
  `Argentina and Wales` = 1367473861,
  `Australia and England` = 1354768877,
  `Australia and France` = 1363653811,
  `Australia and Ireland` = 1362521881,
  `Australia and Italy` = 1364769512,
  `Australia and New Zealand` = 1369969084,
  `Australia and Scotland` = 1321058698,
  `Australia and South Africa` = 1377212891,
  `Australia and Wales` = 1377640460,
  `England and France` = 1366961214,
  `England and Ireland` = 1364140778,
  `England and Italy` = 1346558551,
  `England and New Zealand` = 1344533164,
  `England and Scotland` = 1344177435,
  `England and South Africa` = 1362721735,
  `England and Wales` = 1345274022,
  `France and Ireland` = 1355427763,
  `France and Italy` = 1365854801,
  `France and New Zealand` = 1376342892,
  `France and Scotland` = 1343577578,
  `France and South Africa` = 1322318767,
  `France and Wales` = 1338518351,
  `Ireland and Italy` = 1338365913,
  `Ireland and New Zealand` = 1372561972,
  `Ireland and Scotland` = 1344290986,
  `Ireland and South Africa` = 1328960196,
  `Ireland and Wales` = 1347347955,
  `Italy and New Zealand` = 1363661502,
  `Italy and Scotland` = 1341401624,
  `Italy and South Africa` = 1322319055,
  `Italy and Wales` = 1343633695,
  `New Zealand and Scotland` = 1324405456,
  `New Zealand and South Africa` = 1375906227,
  `New Zealand and Wales` = 1367966496,
  `Scotland and South Africa` = 1363766090,
  `Scotland and Wales` = 1376342913,
  `South Africa and Wales` = 1364815416)

code <- c(ARG = "Argentina", AUS = "Australia", ENG = "England", FRA = "France",
          IRE = "Ireland", IRL = "Ireland", ITA = "Italy", NZL = "New Zealand",
          SCO = "Scotland", RSA = "South Africa", WAL = "Wales")
host_map <- c(
  `Argentina` = "Argentina", `Buenos Aires` = "Argentina", `Córdoba` = "Argentina", `Cordoba` = "Argentina", `Jujuy` = "Argentina", `La Plata` = "Argentina", `Mar del Plata` = "Argentina", `Mendoza` = "Argentina", `Puerto Madryn` = "Argentina", `Resistencia` = "Argentina", `Rosario` = "Argentina", `Salta` = "Argentina", `San Juan` = "Argentina", `San Miguel de Tucumán` = "Argentina", `San Salvador de Jujuy` = "Argentina", `Santa Fe` = "Argentina", `Santiago del Estero` = "Argentina", `Tucumán` = "Argentina",
  `Australia` = "Australia", `Adelaide` = "Australia", `Brisbane` = "Australia", `Canberra` = "Australia", `Gold Coast` = "Australia", `Melbourne` = "Australia", `Newcastle` = "Australia", `Perth` = "Australia", `Sydney` = "Australia", `Townsville` = "Australia", `SCG` = "Australia", `Ballymore Stadium Brisbane` = "Australia",
  `England` = "England", `Birkenhead` = "England", `Blackheath` = "England", `Bristol` = "England", `Dewsbury` = "England", `Gloucester` = "England", `Huddersfield` = "England", `Leeds` = "England", `Leicester` = "England", `London` = "England", `Manchester` = "England", `Newcastle upon Tyne` = "England", `Richmond` = "England", `Twickenham` = "England", `The Oval` = "England",
  `France` = "France", `Agen` = "France", `Auch` = "France", `Bordeaux` = "France", `Chambéry` = "France", `Clermont-Ferrand` = "France", `Colombes` = "France", `Décines-Charpieu` = "France", `Grenoble` = "France", `Lens` = "France", `Lille` = "France", `Lourdes` = "France", `Lyon` = "France", `Marseille` = "France", `Montpellier` = "France", `Nantes` = "France", `Nice` = "France", `Paris` = "France", `Parc des Princes Paris` = "France", `Pau` = "France", `Saint-Denis` = "France", `Saint-Étienne` = "France", `Strasbourg` = "France", `Tarbes` = "France", `Toulon` = "France", `Toulouse` = "France", `Villeneuve-d'Ascq` = "France", `Vincennes` = "France",
  `Ireland` = "Ireland", `Belfast` = "Ireland", `Balmoral` = "Ireland", `Cork` = "Ireland", `Dublin` = "Ireland", `Limerick` = "Ireland",
  `Italy` = "Italy", `Bologna` = "Italy", `Brescia` = "Italy", `Florence` = "Italy", `Genoa` = "Italy", `Genova` = "Italy", `Milan` = "Italy", `Naples` = "Italy", `Padova` = "Italy", `Padua` = "Italy", `Parma` = "Italy", `Piacenza` = "Italy", `Rome` = "Italy", `Rovigo` = "Italy", `Treviso` = "Italy", `Turin` = "Italy", `Udine` = "Italy", `Verona` = "Italy",
  `New Zealand` = "New Zealand", `Albany` = "New Zealand", `Auckland` = "New Zealand", `Christchurch` = "New Zealand", `Dunedin` = "New Zealand", `Hamilton` = "New Zealand", `Napier` = "New Zealand", `Nelson` = "New Zealand", `New Plymouth` = "New Zealand", `Rotorua` = "New Zealand", `Wellington` = "New Zealand",
  `Scotland` = "Scotland", `Edinburgh` = "Scotland", `Glasgow` = "Scotland",
  `South Africa` = "South Africa", `Bloemfentein` = "South Africa", `Bloemfontein` = "South Africa", `Cape Town` = "South Africa", `Durban` = "South Africa", `East London` = "South Africa", `Gqeberha` = "South Africa", `Johannesburg` = "South Africa", `Mbombela` = "South Africa", `Nelspruit` = "South Africa", `Port Elizabeth` = "South Africa", `Pretoria` = "South Africa", `Rustenburg` = "South Africa", `Springs` = "South Africa", `Witbank` = "South Africa",
  `Wales` = "Wales", `Cardiff` = "Wales", `Llanelli` = "Wales", `Newport` = "Wales", `Swansea` = "Wales",
  `Japan` = "Japan", `Chōfu` = "Japan", `Fukuroi` = "Japan", `Tokyo` = "Japan", `Toyota` = "Japan", `Yokohama` = "Japan", `Ōita` = "Japan",
  `United States` = "United States", `US` = "United States", `Baltimore` = "United States", `Chicago` = "United States", `D.C.` = "United States", `Washington` = "United States",
  `Hong Kong` = "Hong Kong",
  `Singapore` = "Singapore")

countries <- c("Argentina", "Australia", "England", "France", "Ireland", "Italy", "New Zealand",
               "Scotland", "South Africa", "Wales", "Japan", "United States", "US", "Hong Kong",
               "Singapore")

fetch <- function(rev) {
  f <- file.path(cache, paste0(rev, ".wiki"))
  if (!file.exists(f)) {
    download.file(paste0("https://en.wikipedia.org/w/index.php?oldid=", rev, "&action=raw"), f,
                  mode = "wb", headers = c(`User-Agent` = "irw-competitions/1.0 (research; https://itemresponsewarehouse.org)"))
    stopifnot(!startsWith(trimws(readLines(f, n = 1, warn = FALSE)), "<"))
    Sys.sleep(3)
  }
  paste(readLines(f, encoding = "UTF-8", warn = FALSE), collapse = "\n")
}
P <- function(pat, rep, s) gsub(pat, rep, s, perl = TRUE)
ustrip <- function(s) P("(*UCP)^\\s+|\\s+$", "", s)
strip_refs <- function(s) {
  s <- P("<ref[^>]*/>", "", s)
  s <- P("(?s)<ref[^>]*>.*?</ref>", "", s)
  P("(?s)<!--.*?-->", "", s)
}
plain <- function(s) {
  s <- P("\\{\\{(?:efn|ref|refn)[^}]*\\}\\}", "", s)
  s <- P("\\[\\[(?:[^\\]|]*\\|)?([^\\]]*)\\]\\]", "\\1", s)
  s <- P("\\{\\{(?:flagicon|flag)[^}]*\\}\\}", "", s)
  s <- P("\\{\\{(?:sort|nowrap|small)\\|(?:[^|{}]*\\|)?", "", s)
  s <- P("<[^>]+>", "", s)
  s <- gsub("{{", "", gsub("}}", "", s, fixed = TRUE), fixed = TRUE)
  s <- gsub("&ndash;", "\u2013", gsub("&nbsp;", " ", s, fixed = TRUE), fixed = TRUE)
  s <- P("''+", "", s)
  s <- P("(*UCP)\\s+", " ", s)
  P("^[ |]+|[ |]+$", "", s)
}
## split keeping trailing empty fields (as Python's re.split does)
split_keep <- function(x, pat) {
  s <- strsplit(paste0(x, "\001"), pat, perl = TRUE)[[1]]
  s[length(s)] <- sub("\001$", "", s[length(s)])
  s
}
## cell "attrs | value" -> list(attrs, value), ignoring pipes inside [[ ]] / {{ }}
split_attr <- function(cell) {
  ch <- strsplit(cell, "")[[1]]
  n <- length(ch); depth <- 0; i <- 1
  while (i <= n) {
    two <- if (i < n) paste0(ch[i], ch[i + 1]) else ch[i]
    if (two %in% c("[[", "{{")) { depth <- depth + 1; i <- i + 2; next }
    if (two %in% c("]]", "}}")) { depth <- depth - 1; i <- i + 2; next }
    if (ch[i] == "|" && depth == 0) {
      a <- paste(ch[seq_len(i - 1)], collapse = "")
      if (grepl("(style|align|rowspan|colspan|scope|class|bgcolor|width)\\s*=", a, perl = TRUE))
        return(list(a, paste(ch[-seq_len(i)], collapse = "")))
      return(list("", cell))
    }
    i <- i + 1
  }
  list("", cell)
}
span <- function(a, what) {
  m <- regmatches(a, regexec(paste0(what, "\\s*=\\s*\"?(\\d+)"), a, perl = TRUE))[[1]]
  if (length(m)) as.integer(m[2]) else NA_integer_
}
table_rows <- function(body) {
  rows <- list(); cur <- character(0)
  for (l in body) {
    if (startsWith(l, "|-")) {
      if (length(cur)) rows[[length(rows) + 1]] <- cur
      cur <- character(0)
    } else if (startsWith(l, "|") || startsWith(l, "!")) {
      cur <- c(cur, split_keep(substring(l, 2), if (startsWith(l, "|")) "\\|\\|" else "\\|\\||!!"))
    } else if (length(cur)) cur[length(cur)] <- paste0(cur[length(cur)], "\n", l)
  }
  if (length(cur)) rows[[length(rows) + 1]] <- cur
  ## expand rowspan / colspan
  pending <- list(); out <- list()
  for (r in rows) {
    res <- character(0); ci <- 0; k <- 1
    while (k <= length(r) || !is.null(pending[[as.character(ci)]])) {
      key <- as.character(ci)
      if (!is.null(pending[[key]])) {
        p <- pending[[key]]
        res <- c(res, p$v)
        if (p$left <= 1) pending[[key]] <- NULL else pending[[key]]$left <- p$left - 1
        ci <- ci + 1
        next
      }
      sa <- split_attr(r[k]); k <- k + 1
      rs <- span(sa[[1]], "rowspan"); cs <- span(sa[[1]], "colspan")
      v <- ustrip(sa[[2]])
      for (z in seq_len(if (is.na(cs)) 1 else cs)) {
        res <- c(res, v)
        if (!is.na(rs) && rs > 1) pending[[as.character(ci)]] <- list(left = rs - 1, v = v)
        ci <- ci + 1
      }
    }
    out[[length(out) + 1]] <- res
  }
  out
}
winner_of <- function(s) {
  m <- regmatches(s, regexec("\\{\\{ruA?\\|([^|}]+)", s, perl = TRUE))[[1]]
  if (length(m)) {
    t <- ustrip(m[2])
    return(if (t %in% names(code)) unname(code[t]) else t)
  }
  if (grepl("(?i)\\bdraw", s, perl = TRUE)) return("draw")
  NA_character_
}
host_of <- function(venue) {
  v <- gsub(")", ",", gsub("(", ",", plain(venue), fixed = TRUE), fixed = TRUE)
  toks <- ustrip(strsplit(paste0(v, ","), ",", fixed = TRUE)[[1]])
  toks <- toks[nzchar(toks)]
  cs <- unique(unname(host_map[toks[toks %in% countries]]))
  if (length(cs) == 1) return(cs)
  hs <- unique(unname(host_map[toks[toks %in% names(host_map)]]))
  if (length(hs) == 1) hs else NA_character_
}

fields <- c("Date", "Venue", "City", "Score", "Winner", "Competition", "Comments")
recs <- list()
for (pair in names(revs)) {
  ab <- strsplit(pair, " and ", fixed = TRUE)[[1]]
  rev <- revs[[pair]]
  lines <- strsplit(strip_refs(fetch(rev)), "\n", fixed = TRUE)[[1]]
  heads <- character(0); i <- 1
  while (i <= length(lines)) {
    if (grepl("^=+.*=+\\s*$", lines[i], perl = TRUE)) heads <- c(heads, P("^[= ]+|[= ]+$", "", lines[i]))
    if (startsWith(lines[i], "{|")) {
      j <- i + 1; depth <- 1
      while (depth > 0) {
        depth <- depth + startsWith(lines[j], "{|") - startsWith(lines[j], "|}")
        j <- j + 1
      }
      g <- table_rows(lines[(i + 1):(j - 2)])
      i <- j
      if (!length(g)) next
      hdr <- ustrip(P(".*\\|", "", P("\\{\\{tooltip\\|[^}]*\\}\\}", "Ref", g[[1]])))
      if (!all(c("No.", "Date", "Score", "Winner") %in% hdr)) next
      if (length(heads) && grepl("(?i)XV|non-test|series", heads[length(heads)], perl = TRUE)) next
      for (row in g[-1]) {
        n <- min(length(hdr), length(row))
        rec <- vapply(fields, function(f) {
          w <- which(hdr[seq_len(n)] == f)
          if (length(w)) row[max(w)] else ""
        }, "")
        recs[[length(recs) + 1]] <- c(pair = pair, a = ab[1], b = ab[2], rev = rev, rec)
      }
      next
    }
    i <- i + 1
  }
}
raw <- as.data.frame(do.call(rbind, recs), stringsAsFactors = FALSE)
n_raw <- nrow(raw)

dropped <- c(unplayed = 0, abandoned = 0, note_row = 0)
out <- vector("list", n_raw)
for (k in seq_len(n_raw)) {
  r <- raw[k, ]
  score <- plain(r$Score)
  if (startsWith(sub("^[|& ]+", "", r$Date), "<sup>") || grepl("Denotes", r$Date, fixed = TRUE)) {
    dropped["note_row"] <- dropped["note_row"] + 1; next }
  if (score %in% c("", "TBD", "TBC") || grepl("cancelled", r$Score, fixed = TRUE)) {
    dropped["unplayed"] <- dropped["unplayed"] + 1; next }
  if (grepl("Abandoned", r$Winner, fixed = TRUE)) {
    dropped["abandoned"] <- dropped["abandoned"] + 1; next }
  w <- winner_of(r$Winner)
  stopifnot(w %in% c(r$a, r$b, "draw"))
  day <- as.Date(plain(r$Date), format = "%d %B %Y")
  stopifnot(!is.na(day))
  m <- regmatches(score, regexec("^(\\d+)\\s*[\u2013-]\\s*(\\d+)$", score, perl = TRUE))[[1]]
  hi <- lo <- NA_integer_
  if (length(m)) {
    x <- as.integer(m[2]); y <- as.integer(m[3])
    hi <- max(x, y); lo <- min(x, y)
    stopifnot((w == "draw") == (x == y))
  } else stopifnot(grepl("\\d+G", score, perl = TRUE))
  venue <- plain(paste0(r$Venue, if (nzchar(r$City)) paste0(", ", r$City) else ""))
  host <- host_of(paste0(r$Venue, ",", r$City))
  stopifnot(!is.na(host))
  if (host %in% c(r$a, r$b)) {
    home <- host; away <- setdiff(c(r$a, r$b), host); hf <- "agent_a"
  } else { home <- r$a; away <- r$b; hf <- "" }
  if (w == "draw") { wn <- "draw"; sa <- hi; sb <- lo }
  else if (w == home) { wn <- "agent_a"; sa <- hi; sb <- lo }
  else { wn <- "agent_b"; sa <- lo; sb <- hi }
  out[[k]] <- data.frame(agent_a = home, agent_b = away, winner = wn,
                         date = as.numeric(as.POSIXct(day, tz = "UTC")),
                         homefield = hf, score_a = sa, score_b = sb,
                         score_raw = if (is.na(sa)) score else "",
                         competition = plain(if (nzchar(r$Competition)) r$Competition else r$Comments),
                         venue = venue, host_country = host,
                         source_page = paste0("History of rugby union matches between ", r$pair,
                                              " (oldid ", r$rev, ")"),
                         stringsAsFactors = FALSE)
}
df <- do.call(rbind, out)
df <- df[order(df$date, df$agent_a, method = "radix"), ]

## shape checks (the validator does not apply to comps tables)
num <- !is.na(df$score_a)
pair_key <- ifelse(df$agent_a < df$agent_b, paste(df$agent_a, df$agent_b, sep = "|"),
                   paste(df$agent_b, df$agent_a, sep = "|"))
stopifnot(all(c(df$agent_a, df$agent_b) %in% T1), df$agent_a != df$agent_b,
          df$winner %in% c("agent_a", "agent_b", "draw"), df$homefield %in% c("agent_a", ""),
          !anyNA(df$date),
          with(df[num & df$winner == "agent_a", ], score_a > score_b),
          with(df[num & df$winner == "agent_b", ], score_a < score_b),
          with(df[num & df$winner == "draw", ], score_a == score_b),
          !anyDuplicated(paste(pair_key, df$date)),
          length(unique(pair_key)) == 45)

write.csv(df, out_file, row.names = FALSE, na = "", fileEncoding = "UTF-8")
cat(n_raw, "table rows;", paste(names(dropped), dropped, collapse = " "), ";", nrow(df), "matches,",
    length(unique(c(df$agent_a, df$agent_b))), "agents,", sum(df$homefield == ""), "neutral,",
    sum(df$winner == "draw"), "draws,", sum(!num), "goal-era scores;",
    format(as.Date(as.POSIXct(min(df$date), origin = "1970-01-01", tz = "UTC"))), "to",
    format(as.Date(as.POSIXct(max(df$date), origin = "1970-01-01", tz = "UTC"))), "\n")
