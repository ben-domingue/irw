## openfootball (https://github.com/openfootball), Football.TXT match files
## Licence: CC0 1.0 Universal (LICENSE.md in openfootball/world and
## openfootball/champions-league, checked 2026-09-30).
##
## Tables:
##   openfootball_mls_2005_2025   Major League Soccer, world/north-america/major-league-soccer
##   openfootball_uefacl_2011_2026 UEFA Champions League group stage onward, champions-league/*/cl.txt
##
## Choices (as in intlfootball.R):
## - score_a/score_b are the score after 90 minutes, or 120 when there was extra time.
##   winner follows the score, so draws stay "draw". A penalty shootout is kept as
##   shootout_winner (agent_a/agent_b/blank) and does not change winner.
## - The first-listed team is the home side. The files record no venues, so homefield
##   is blank only for stages known to be neutral: every CL final, the CL 2019-20
##   quarter- and semi-finals (Lisbon), the 2020 MLS is Back Tournament (Orlando) and
##   MLS Cup through 2011 (fixed venues; the higher seed has hosted since 2012).
##   COVID-era relocations of single CL matches (2020-21) are not marked.
## - Cancelled matches ("[cancelled]") and fixtures listed without a score are dropped.
## - The year is printed only on a season's first date. It comes from each file's
##   "# Date" range: a month before the start month belongs to the end year. Each date
##   is checked against its printed weekday.
## - Team names are left as the files spell them, with the CL country code kept, e.g.
##   "Manchester City (ENG)". Exception: from 2023-24 the CL files switch many clubs to
##   long official names ("Real Madrid CF", "FC Internazionale Milano"), which would
##   split one club into two agents. `cl_names` maps those back to the 2011-22 spelling.
##   MLS renames (MetroStars, Kansas City Wizards, Impact de Montréal) are left as is.

cache <- path.expand("~/.cache/irw-comps/openfootball")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
for (r in c("world", "champions-league"))
    if (!dir.exists(file.path(cache, r)))
        system2("git", c("clone", "-q", "--depth", "1",
                         paste0("https://github.com/openfootball/", r, ".git"), file.path(cache, r)))

mon <- c(Jan = 1, Feb = 2, Mar = 3, Apr = 4, May = 5, Jun = 6, Jul = 7, Aug = 8, Sep = 9, Oct = 10, Nov = 11, Dec = 12)
wday <- c("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")

parse_file <- function(f, neutral_stage) {
    L <- readLines(f, encoding = "UTF-8", warn = FALSE)
    hdr <- regmatches(L, regexpr("^# Date .*", L))[1]
    yrs <- as.integer(regmatches(hdr, gregexpr("[0-9]{4}", hdr))[[1]])
    y0 <- yrs[1]; y1 <- yrs[length(yrs)]
    m0 <- mon[[regmatches(hdr, regexpr("(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", hdr))]]
    stage <- NA; date <- NA; out <- list(); unplayed <- 0
    for (l in L) {
        if (grepl("^\\s*(#|=|$)", l)) next
        if (grepl("^▪", l)) { stage <- trimws(sub("^▪", "", l)); next }
        d <- regmatches(l, regexec("^\\s+(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ([0-9]+)( [0-9]{4})?\\s*$", l))[[1]]
        if (length(d)) {
            m <- mon[[d[3]]]
            y <- if (nzchar(d[5])) as.integer(d[5]) else if (m >= m0) y0 else y1
            date <- as.Date(sprintf("%d-%02d-%02d", y, m, as.integer(d[4])))
            if (wday[as.POSIXlt(date)$wday + 1] != d[2]) stop("weekday mismatch: ", f, ": ", l)
            next
        }
        if (grepl("\\[cancelled\\]", l)) next
        if (!grepl("[0-9]+-[0-9]+", l)) { unplayed <- unplayed + 1; next }
        x <- regmatches(l, regexec(paste0("^\\s+(?:[0-9]{1,2}:[0-9]{2}\\s+)?(.+?)\\s+v\\s+(.+?)\\s+",
                                          "(?:([0-9]+)-([0-9]+) pen\\.\\s+)?([0-9]+)-([0-9]+)( a\\.e\\.t\\.)?(?:\\s+\\(.*\\))?\\s*$"),
                                   l, perl = TRUE))[[1]]
        if (!length(x)) {
            ## straight to penalties after 90 minutes (MLS 2023-24 round one): "4-2 pen. (0-0)"
            p <- regmatches(l, regexec("^\\s+(?:[0-9]{1,2}:[0-9]{2}\\s+)?(.+?)\\s+v\\s+(.+?)\\s+([0-9]+)-([0-9]+) pen\\.\\s+\\(([0-9]+)-([0-9]+)[,)]",
                                       l, perl = TRUE))[[1]]
            if (!length(p)) stop("unparsed line: ", f, ": ", l)
            x <- c(p[1:7], "")
        }
        out[[length(out) + 1]] <- data.frame(
            agent_a = x[2], agent_b = x[3], date = date, stage = stage,
            score_a = as.integer(x[6]), score_b = as.integer(x[7]),
            extra_time = nzchar(x[8]),
            pen_a = if (nzchar(x[4])) as.integer(x[4]) else NA,
            pen_b = if (nzchar(x[5])) as.integer(x[5]) else NA)
    }
    df <- do.call(rbind, out)
    if (unplayed) message(basename(f), ": skipped ", unplayed, " fixtures with no score")
    stopifnot(!anyNA(df$date))
    df$homefield <- ifelse(neutral_stage(df$stage, y0), "", "agent_a")
    df
}

finish <- function(df) {
    data.frame(
        agent_a = df$agent_a, agent_b = df$agent_b,
        date = as.numeric(as.POSIXct(format(df$date), tz = "UTC")),
        homefield = df$homefield,
        score_a = df$score_a, score_b = df$score_b,
        winner = ifelse(df$score_a > df$score_b, "agent_a", ifelse(df$score_a < df$score_b, "agent_b", "draw")),
        shootout_winner = ifelse(is.na(df$pen_a), "", ifelse(df$pen_a > df$pen_b, "agent_a", "agent_b")),
        extra_time = as.integer(df$extra_time),
        season = df$season, stage = df$stage)
}

## MLS
fs <- sort(Sys.glob(file.path(cache, "world/north-america/major-league-soccer/*_mls.txt")))
mls <- do.call(rbind, lapply(fs, function(f) {
    d <- parse_file(f, function(s, y) grepl("^MLS is Back", s) | (s == "Playoffs, Final" & y <= 2011))
    d$season <- sub("_mls.txt", "", basename(f)); d
}))
write.csv(finish(mls), "openfootball_mls_2005_2025.csv", row.names = FALSE)

## UEFA Champions League
cl_names <- c(
    "FC Red Bull Salzburg (AUT)" = "RB Salzburg (AUT)",
    "Qarabağ Ağdam FK (AZE)" = "Qarabağ FK (AZE)",
    "GNK Dinamo Zagreb (CRO)" = "Dinamo Zagreb (CRO)",
    "SK Slavia Praha (CZE)" = "Slavia Praha (CZE)",
    "Manchester City FC (ENG)" = "Manchester City (ENG)",
    "Manchester United FC (ENG)" = "Manchester United (ENG)",
    "Tottenham Hotspur FC (ENG)" = "Tottenham Hotspur (ENG)",
    "Real Madrid CF (ESP)" = "Real Madrid (ESP)",
    "Real Sociedad de Fútbol (ESP)" = "Real Sociedad (ESP)",
    "Club Atlético de Madrid (ESP)" = "Atlético Madrid (ESP)",
    "Paris Saint-Germain FC (FRA)" = "Paris Saint-Germain (FRA)",
    "Olympique de Marseille (FRA)" = "Olympique Marseille (FRA)",
    "AS Monaco FC (MCO)" = "AS Monaco (FRA)",
    "FC Bayern München (GER)" = "Bayern München (GER)",
    "Bayer 04 Leverkusen (GER)" = "Bayer Leverkusen (GER)",
    "PAE Olympiakos SFP (GRE)" = "Olympiakos Piraeus (GRE)",
    "FC Internazionale Milano (ITA)" = "Inter (ITA)",
    "Juventus FC (ITA)" = "Juventus (ITA)",
    "SS Lazio (ITA)" = "Lazio Roma (ITA)",
    "Atalanta BC (ITA)" = "Atalanta (ITA)",
    "Feyenoord Rotterdam (NED)" = "Feyenoord (NED)",
    "PSV (NED)" = "PSV Eindhoven (NED)",
    "Sporting Clube de Braga (POR)" = "Sporting Braga (POR)",
    "Sport Lisboa e Benfica (POR)" = "SL Benfica (POR)",
    "Sporting Clube de Portugal (POR)" = "Sporting CP (POR)",
    "FK Crvena Zvezda (SRB)" = "Crvena Zvezda (SRB)",
    "Galatasaray SK (TUR)" = "Galatasaray (TUR)",
    "FK Shakhtar Donetsk (UKR)" = "Shakhtar Donetsk (UKR)")
fs <- sort(Sys.glob(file.path(cache, "champions-league/20*/cl.txt")))
cl <- do.call(rbind, lapply(fs, function(f) {
    season <- basename(dirname(f))
    d <- parse_file(f, function(s, y) grepl("(^|, )Final$", s) |
                                      (season == "2019-20" & s %in% c("Quarterfinals", "Semifinals")))
    d$season <- season; d
}))
for (v in c("agent_a", "agent_b")) {
    hit <- cl[[v]] %in% names(cl_names)
    cl[[v]][hit] <- cl_names[cl[[v]][hit]]
}
write.csv(finish(cl), "openfootball_uefacl_2011_2026.csv", row.names = FALSE)
