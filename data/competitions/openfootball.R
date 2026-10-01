## openfootball (https://github.com/openfootball), Football.TXT match files
## Licence: CC0 1.0 Universal (LICENSE.md in openfootball/world,
## openfootball/champions-league and openfootball/south-america, each beginning
## "CC0 1.0 Universal", checked 2026-09-30).
##
## Tables:
##   openfootball_mls_2005_2025   Major League Soccer, world/north-america/major-league-soccer
##   openfootball_uefacl_2011_2026 UEFA Champions League group stage onward, champions-league/*/cl.txt
##   openfootball_libertadores_2012_2026 Copa Libertadores, south-america/copa-libertadores/*_copal.txt
##   openfootball_sudamericana_2012_2025 Copa Sudamericana, south-america/copa-libertadores/*_copas.txt
##   openfootball_concacafcl_2010_2025 CONCACAF Champions League / Champions Cup,
##                                world/north-america/champions-league/*_concacafcl.txt
## The first two are written to the working directory; the three added 2026-09-30 to
## ~/.cache/irw-comps/nflverse-openfootball-out. Their specific choices are with their code
## below; the general choices here apply to all five. Two-legged ties: each leg is a row.
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
## - Cancelled matches ("[cancelled]"), forfeits ("[awarded]") and fixtures listed
##   without a score are dropped.
## - The year is printed only on a season's first date. It comes from each file's
##   "# Date" range: a month before the start month belongs to the end year (and a date in
##   the start month whose weekday fits only the end year, for Libertadores 2020, which
##   ended in Jan 2021). Each date is checked against its printed weekday.
## - Team names are left as the files spell them, with the CL country code kept, e.g.
##   "Manchester City (ENG)". Exception: from 2023-24 the CL files switch many clubs to
##   long official names ("Real Madrid CF", "FC Internazionale Milano"), which would
##   split one club into two agents. `cl_names` maps those back to the 2011-22 spelling.
##   MLS renames (MetroStars, Kansas City Wizards, Impact de Montréal) are left as is.

cache <- path.expand("~/.cache/irw-comps/openfootball")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
for (r in c("world", "champions-league", "south-america"))
    if (!dir.exists(file.path(cache, r)))
        system2("git", c("clone", "-q", "--depth", "1",
                         paste0("https://github.com/openfootball/", r, ".git"), file.path(cache, r)))

mon <- c(Jan = 1, Feb = 2, Mar = 3, Apr = 4, May = 5, Jun = 6, Jul = 7, Aug = 8, Sep = 9, Oct = 10, Nov = 11, Dec = 12)
wday <- c("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
dropped <- NULL

parse_file <- function(f, neutral_stage) {
    L <- readLines(f, encoding = "UTF-8", warn = FALSE)
    hdr <- regmatches(L, regexpr("^# Date .*", L))[1]
    yrs <- as.integer(regmatches(hdr, gregexpr("[0-9]{4}", hdr))[[1]])
    y0 <- yrs[1]; y1 <- yrs[length(yrs)]
    m0 <- mon[[regmatches(hdr, regexpr("(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", hdr))]]
    stage <- NA; date <- NA; out <- list(); unplayed <- 0; awarded <- 0
    for (l in L) {
        if (grepl("^\\s*(#|=|$)", l)) next
        if (grepl("^▪", l)) { stage <- trimws(sub("^▪", "", l)); next }
        d <- regmatches(l, regexec("^\\s+(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ([0-9]+)( [0-9]{4})?\\s*$", l))[[1]]
        if (length(d)) {
            m <- mon[[d[3]]]
            y <- if (nzchar(d[5])) as.integer(d[5]) else if (m >= m0) y0 else y1
            date <- as.Date(sprintf("%d-%02d-%02d", y, m, as.integer(d[4])))
            ## a season that ends in its start month a year later (Libertadores 2020 ran
            ## Jan 2020 - Jan 2021): if the weekday rules out the start year, try the end year
            if (wday[as.POSIXlt(date)$wday + 1] != d[2] && !nzchar(d[5]) && y0 != y1 && m == m0)
                date <- as.Date(sprintf("%d-%02d-%02d", y1, m, as.integer(d[4])))
            if (wday[as.POSIXlt(date)$wday + 1] != d[2]) stop("weekday mismatch: ", f, ": ", l)
            next
        }
        if (grepl("\\[cancelled\\]", l)) next
        if (grepl("\\[awarded\\]", l)) { awarded <- awarded + 1; next }
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
    if (awarded) message(basename(f), ": skipped ", awarded, " matches awarded by forfeit")
    dropped <<- rbind(dropped, data.frame(file = basename(f), unplayed = unplayed, awarded = awarded))
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

## ---- Added 2026-09-30: CONMEBOL Libertadores / Sudamericana, CONCACAF Champions Cup ----
## Same parser and conventions as above; new tables are written to `out`.
out <- path.expand("~/.cache/irw-comps/nflverse-openfootball-out")
dir.create(out, showWarnings = FALSE, recursive = TRUE)
tidy_stage <- function(s) sub("^(Finals|Qualifying), ", "", sub("^Gruppe ", "Group ", s))
rename <- function(df, map) {
    for (v in c("agent_a", "agent_b")) {
        hit <- df[[v]] %in% names(map)
        df[[v]][hit] <- map[df[[v]][hit]]
    }
    df
}
build <- function(glob, neutral, season, map = NULL) {
    fs <- sort(Sys.glob(file.path(cache, glob)))
    d <- do.call(rbind, lapply(fs, function(f) {
        x <- parse_file(f, neutral); x$season <- season(f); x
    }))
    d$stage <- tidy_stage(d$stage)
    if (!is.null(map)) d <- rename(d, map)
    d
}
summarise <- function(name, t) {
    stopifnot(!anyNA(t$date), !anyNA(t$score_a), !anyNA(t$score_b),
              t$winner %in% c("agent_a", "agent_b", "draw"),
              t$homefield %in% c("agent_a", ""), t$agent_a != t$agent_b,
              !duplicated(t[c("agent_a", "agent_b", "date")]))
    write.csv(t, file.path(out, paste0(name, ".csv")), row.names = FALSE)
    cat(sprintf("%s: %d rows, %d agents, %s to %s, %d draws, %d neutral\n", name, nrow(t),
                length(unique(c(t$agent_a, t$agent_b))),
                format(as.POSIXct(min(t$date), origin = "1970-01-01", tz = "UTC"), "%Y-%m-%d"),
                format(as.POSIXct(max(t$date), origin = "1970-01-01", tz = "UTC"), "%Y-%m-%d"),
                sum(t$winner == "draw"), sum(t$homefield == "")))
}

## Copa Libertadores (copal) and Copa Sudamericana (copas): openfootball/south-america,
## copa-libertadores/<year>_copal.txt and <year>_copas.txt. Both finals have been single
## matches at a pre-chosen venue since 2019 (blank homefield); before that they were two
## legs, home and away, except the 2018 Libertadores final second leg (River Plate v Boca
## Juniors), moved to Madrid after the attack on Boca's bus, also blank. COVID-era
## relocations of single matches (2020-21) are not marked, as in the CL table.
## From 2023 the files switch many clubs to long official names ("CA Boca Juniors",
## "CR Flamengo"); `conmebol_names` maps those back to the 2012-22 spelling. Genuine
## renames (e.g. Club San José -> GV San José) are left as is. Matches decided by forfeit
## ("[awarded]") are dropped: 2015 Boca v River (abandoned at half-time), 2017 Lanús v
## Chapecoense (not played), 2018 San Lorenzo v Temuco (ineligible player).
## 2025 Sudamericana: the file has scores for only 64 of 121 fixtures (most group
## matches and the knockout rounds unscored); the scored ones are kept. The 2026
## Libertadores is in progress; unplayed fixtures are dropped.
conmebol_names <- c(
    "AA Argentinos Juniors (ARG)" = "Argentinos Juniors (ARG)",
    "CA Boca Juniors (ARG)" = "Boca Juniors (ARG)",
    "CA Huracán (ARG)" = "Huracán (ARG)",
    "CA Lanús (ARG)" = "Lanús (ARG)",
    "CA River Plate (ARG)" = "River Plate (ARG)",
    "CA Rosario Central (ARG)" = "Rosario Central (ARG)",
    "CA San Lorenzo de Almagro (ARG)" = "San Lorenzo (ARG)",
    "CA Talleres (ARG)" = "Talleres de Córdoba (ARG)",
    "CA Vélez Sarsfield (ARG)" = "Vélez Sarsfield (ARG)",
    "CD Godoy Cruz Antonio Tomba (ARG)" = "Godoy Cruz (ARG)",
    "Estudiantes de La Plata (ARG)" = "Estudiantes (ARG)",
    "Club Always Ready (BOL)" = "Always Ready (BOL)",
    "Club Bolívar (BOL)" = "Bolívar (BOL)",
    "Club The Strongest (BOL)" = "The Strongest (BOL)",
    "Botafogo FR (BRA)" = "Botafogo RJ (BRA)",
    "CA Mineiro (BRA)" = "Atlético Mineiro (BRA)",
    "CA Paranaense (BRA)" = "Athletico Paranaense (BRA)",
    "CR Flamengo (BRA)" = "Flamengo RJ (BRA)",
    "Cruzeiro EC (BRA)" = "Cruzeiro (BRA)",
    "Fluminense FC (BRA)" = "Fluminense RJ (BRA)",
    "Fortaleza EC (BRA)" = "Fortaleza CE (BRA)",
    "Grêmio FBPA (BRA)" = "Grêmio Porto Alegre (BRA)",
    "RB Bragantino (BRA)" = "Red Bull Bragantino (BRA)",
    "SC Corinthians Paulista (BRA)" = "Corinthians SP (BRA)",
    "SC Internacional (BRA)" = "Internacional (BRA)",
    "SE Palmeiras (BRA)" = "Palmeiras (BRA)",
    "CD Cobresal (CHI)" = "Cobresal (CHI)",
    "CD Huachipato (CHI)" = "Huachipato (CHI)",
    "CD Iquique (CHI)" = "Deportes Iquique (CHI)",
    "CD Palestino (CHI)" = "Palestino (CHI)",
    "CD Universidad Católica (CHI)" = "Universidad Católica (CHI)",
    "CF Universidad de Chile (CHI)" = "Universidad de Chile (CHI)",
    "CSD Colo-Colo (CHI)" = "Colo-Colo (CHI)",
    "O'Higgins FC (CHI)" = "O'Higgins (CHI)",
    "CDC Atlético Nacional (COL)" = "Atlético Nacional (COL)",
    "CD Independiente Medellín (COL)" = "Independiente Medellín (COL)",
    "CD Tolima (COL)" = "Deportes Tolima (COL)",
    "CDP Junior FC (COL)" = "Atlético Junior (COL)",
    "Independiente Santa Fe (COL)" = "Santa Fe (COL)",
    "Millonarios FC (COL)" = "Millonarios (COL)",
    "Barcelona SC (ECU)" = "Barcelona (ECU)",
    "CAR Independiente del Valle (ECU)" = "Independiente del Valle (ECU)",
    "CSCyD El Nacional (ECU)" = "El Nacional (ECU)",
    "LDU de Quito (ECU)" = "LDU Quito (ECU)",
    "Club Cerro Porteño (PAR)" = "Cerro Porteño (PAR)",
    "Club Guaraní (PAR)" = "Guaraní (PAR)",
    "Club Libertad Asuncion (PAR)" = "Libertad (PAR)",
    "Olimpia Asuncion (PAR)" = "Club Olimpia (PAR)",
    "Club Alianza Lima (PER)" = "Alianza Lima (PER)",
    "Club Universitario de Deportes (PER)" = "Universitario de Deportes (PER)",
    "CS Cristal (PER)" = "Sporting Cristal (PER)",
    "CSD Sport Huancayo (PER)" = "Sport Huancayo (PER)",
    "CA Peñarol (URU)" = "Peñarol (URU)",
    "Club Nacional de Football (URU)" = "Nacional (URU)",
    "Defensor SC (URU)" = "Defensor Sporting (URU)",
    "Liverpool FC (URU)" = "Liverpool (URU)",
    "Deportivo La Guaira FC (VEN)" = "Deportivo La Guaira (VEN)",
    "Deportivo Táchira FC (VEN)" = "Deportivo Táchira (VEN)",
    "Monagas SC (VEN)" = "Monagas (VEN)",
    "CD Magallanes (CHI)" = "Magallanes (CHI)",
    "CD Nublense (CHI)" = "Ñublense (CHI)")
year_of <- function(f) substr(basename(f), 1, 4)
conmebol_final <- function(s, y) s %in% c("Final", "Finals, Final") & y >= 2019

lib <- build("south-america/copa-libertadores/*_copal.txt", conmebol_final, year_of, conmebol_names)
lib$homefield[lib$season == "2018" & lib$stage == "Final" & lib$date == as.Date("2018-12-09")] <- ""
stopifnot(sum(lib$season == "2018" & lib$homefield == "") == 1)
summarise("openfootball_libertadores_2012_2026", finish(lib))

sud <- build("south-america/copa-libertadores/*_copas.txt", conmebol_final, year_of, conmebol_names)
summarise("openfootball_sudamericana_2012_2025", finish(sud))

## CONCACAF Champions League / Champions Cup (2024-): world/north-america/champions-league.
## Seasons 2010-11 to 2016-17, then calendar years 2018-2025 (no 2017-18 file: the
## competition switched calendars). Finals were two legs except 2021, 2024 and 2025,
## single matches at the better-placed finalist's ground (first listed; homefield kept).
## The 2020 tournament resumed in December in a bubble in Orlando: every match from
## December 2020 is neutral. The 2025 final (Cruz Azul v Vancouver) has no score in the
## file and is dropped. Two 2022 round-of-16 forfeits ("[awarded]") are dropped.
## "CSD Comunicaciones (GUA)" (2011-14) is mapped to "Comunicaciones (GUA)"; the
## Impact de Montréal -> CF Montréal rebrand is left as is, as in the MLS table.
concacaf <- build("world/north-america/champions-league/*_concacafcl.txt",
                  function(s, y) rep(FALSE, length(s)),
                  function(f) sub("_concacafcl.txt", "", basename(f)),
                  c("CSD Comunicaciones (GUA)" = "Comunicaciones (GUA)"))
concacaf$homefield[concacaf$date >= as.Date("2020-12-01") & concacaf$date < as.Date("2021-01-01")] <- ""
summarise("openfootball_concacafcl_2010_2025", finish(concacaf))

## Nigeria NPFL (world/africa/nigeria/*_ng1.txt) is not built: its dates are "dd.mm."
## with no year or weekday, so nothing can be checked, and the "# Date" headers that
## would supply the year are wrong for several seasons (2020-21 says 2020 but starts
## 27.12.; 2009-10 says Jan 2009 but starts 14.10.); 2018-19 and 2022-23 have no
## header; 2017-18 has 240 of 380 matches.
dropped$competition <- sub("^[0-9-]+_(.*)\\.txt$", "\\1", dropped$file)
cat("Dropped (no score / awarded) per competition:\n")
print(aggregate(cbind(unplayed, awarded) ~ competition, dropped, sum))
