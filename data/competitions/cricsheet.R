## Cricsheet (https://cricsheet.org), ball-by-ball JSON match files, one row per match
## Data: https://cricsheet.org/downloads/all_json.zip (JSON format 1.2.0, downloaded
## 2026-09-30; matches up to 2026-09-17). The zip is refreshed daily, so the script cuts at
## `last_day` to keep the scope fixed; a rerun can still pick up Cricsheet's corrections.
##
## Licence: no statement on cricsheet.org covers the match files (checked 2026-09-30: home,
## /about/, /downloads/, /matches/, /format/json/, /withheld-matches, the README.txt inside
## all_json.zip, and the cricsheet GitHub org, whose repos now point to Sourcehut). The only
## licence on the site is on the people register page (https://cricsheet.org/register/):
##   "This dataset is made available under the Open Data Commons Attribution License:
##    http://opendatacommons.org/licenses/by/1.0/."
## Every page footer reads "Site (c) 2009-2026 Cricsheet. All rights reserved." ODC-BY 1.0 is
## carried forward for the match data on Ben's instruction (2026-09-30).
##
## Withheld matches: Cricsheet withholds every match of the Afghanistan men's team and the
## Afghanistan Premier League (377 matches per the zip README; policy since 2024-11-14,
## https://cricsheet.org/article/explanation-for-withholding-of-afghanistani-matches).
## Afghanistan therefore never appears, and its opponents' records lack those matches.
##
## Tables (output names carry the first and last year present):
##   cricsheet_intl_men_2001_2026      team_type "international", men
##   cricsheet_intl_women_2003_2026    team_type "international", women
##   cricsheet_domestic_men_2008_2026  team_type "club", men (IPL, BBL, PSL, CPL, T20 Blast,
##                                     County Championship, Sheffield Shield, ... 28 competitions)
##   cricsheet_domestic_women_2015_2026 team_type "club", women (WBB, The Hundred, WPL, ...)
##
## Choices:
## - Internationals keep every match type Cricsheet files under team_type "international":
##   Test, ODI, T20 (= T20I), plus IT20 (other international T20s), ODM and MDM (other one-day
##   and multi-day matches between national teams, mostly associates). match_type says which,
##   so a Test/ODI/T20I-only analysis filters on it. Representative sides (ICC World XI, Asia
##   XI, Africa XI) are kept as agents.
## - Domestic: one table per gender with a `competition` column (Cricsheet's code: IPL, BBL,
##   NTB = T20 Blast, CCH = County Championship, RLC = One-Day Cup, SSH = Sheffield Shield,
##   PKS = Plunket Shield, SSM = Super Smash, HND = The Hundred, ...) and the recorded `event`
##   name. One table rather than one per league because the same teams play several
##   competitions (counties in CCH/NTB/RLC, Australian states in SSH/ODC, NZ associations in
##   PKS/SSM, Sri Lankan clubs in MCL/MCT/MLT), and a table per league would give dozens.
##   Leagues are otherwise disconnected; split on `competition` for per-league models.
## - Agents are Cricsheet's team names. Merged only where they are spelling variants or the same
##   franchise rebranded (see `renames`): Swaziland/Eswatini, Kings XI Punjab/Punjab Kings,
##   Delhi Daredevils/Delhi Capitals, Royal Challengers Bangalore/Bengaluru, Rising Pune
##   Supergiant(s), Sharjah Warriors/Warriorz, Kathmandu Gurkhas/Gorkhas, Birmingham Bears/
##   Warwickshire, Plunket Shield names (Auckland Aces etc.) to the associations' Super Smash
##   names, and The Hundred's 2026 rebrands (Oval Invincibles = MI London, Manchester Originals
##   = Manchester Super Giants, Northern Superchargers = Sunrisers Leeds). Franchises that
##   changed owner (CPL, BPL, LPL renamings; Deccan Chargers vs Sunrisers Hyderabad) stay apart.
## - date: first day of the match (Tests and multi-day: start date), UTC midnight.
## - winner: the recorded winner. "draw" for drawn Tests/multi-day matches and for ties; the
##   raw result is in `result` (draw/tie/blank) and the method in `method` (D/L, VJD, Awarded,
##   Lost fewer wickets). A tie settled by a super over (outcome "eliminator") or a bowl-out
##   goes to that team, flagged in `super_over` / `bowl_out`. Matches with result "no result"
##   (abandoned or rained off) are dropped and counted in the summary. Awarded matches (e.g.
##   the 2006 Oval Test) keep the awarded winner.
## - score_a/score_b: total runs per side summed over all its innings (all innings of a Test),
##   including penalty runs, excluding super overs. Blank only if no innings were played. In
##   D/L matches the scores do not decide the winner. Two Botswana/Nigeria/Tanzania T20Is have
##   equal totals with a "by 7 wickets" winner (ball data incomplete at source); kept as recorded.
## - homefield (agent_a is the home side whenever there is one; else the file's first team):
##   Internationals: the venue's host country, from `host_city` (every city in the data,
##   written by hand) and `host_venue` (venues filed without a city); Hamilton is NZ at Seddon
##   Park/Westpac Park, else Bermuda. The Caribbean maps to West Indies, the island of Ireland to
##   Ireland, England and Wales to England. homefield is the team whose country hosts, blank if
##   neither (neutral World Cup games, Pakistan "home" series in the UAE, West Indies in
##   Florida, etc.). The script stops if any international venue is unmapped.
##   Domestic: a ground (venue name before any comma, plus its city) is a team's home ground
##   within one competition and gender when that team played in >= 70% of the competition's
##   matches there over >= 5 matches; the resident team gets homefield. Shared or neutral
##   grounds (BPL, LPL, ILT20, MLC, WPL, the UAE seasons of the IPL and PSL, finals venues)
##   therefore come out blank. Not applied to WCL, SMA, BLZ, SFT (staged at host venues).
## - Covariates: match_type, competition (domestic only), event, season, venue, city,
##   toss_winner (agent_a/agent_b), toss_decision (bat/field), match_id (Cricsheet id).

library(jsonlite)
library(parallel)

cache <- path.expand("~/.cache/irw-comps/cricsheet")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
zip <- file.path(cache, "all_json.zip")
if (!file.exists(zip)) download.file("https://cricsheet.org/downloads/all_json.zip", zip, mode = "wb")
jdir <- file.path(cache, "json")
if (!dir.exists(jdir)) unzip(zip, exdir = jdir)
last_day <- as.Date("2026-09-17")   # last match day in the 2026-09-30 download; later matches are cut

## competition codes (IPL, NTB, ...) are only in the README listing
rd <- readLines(file.path(jdir, "README.txt"), warn = FALSE)
rd <- regmatches(rd, regexec("^([0-9-]{10}) - (club|international) - (\\S+) - (male|female) - (\\S+) - ", rd))
rd <- do.call(rbind, rd[lengths(rd) > 0])
code <- setNames(rd[, 4], rd[, 6])

## ---- parse every match file ------------------------------------------------------------
parse_match <- function(f) {
    d <- fromJSON(f, simplifyVector = FALSE)
    i <- d$info
    o <- i$outcome
    runs <- c(0, 0); names(runs) <- unlist(i$teams)
    for (inn in d$innings) {
        if (isTRUE(inn$super_over)) next
        r <- sum(vapply(inn$overs, function(ov) sum(vapply(ov$deliveries, function(b) b$runs$total, 0)), 0))
        r <- r + sum(unlist(inn$penalty_runs))
        runs[inn$team] <- runs[inn$team] + r
    }
    nz <- function(x) if (is.null(x)) NA_character_ else as.character(x)
    data.frame(
        id = sub("\\.json$", "", basename(f)),
        team1 = i$teams[[1]], team2 = i$teams[[2]],
        runs1 = runs[[1]], runs2 = runs[[2]],
        n_innings = sum(!vapply(d$innings, function(x) isTRUE(x$super_over), TRUE)),
        start = i$dates[[1]], team_type = i$team_type, match_type = i$match_type,
        gender = i$gender, event = nz(i$event$name), season = as.character(i$season),
        venue = nz(i$venue), city = nz(i$city),
        toss_winner = nz(i$toss$winner), toss_decision = nz(i$toss$decision),
        out_winner = nz(o$winner), out_result = nz(o$result), out_method = nz(o$method),
        out_eliminator = nz(o$eliminator), out_bowl_out = nz(o$bowl_out),
        by_runs = nz(o$by$runs), by_wickets = nz(o$by$wickets), by_innings = nz(o$by$innings),
        stringsAsFactors = FALSE)
}
rds <- file.path(cache, "parsed.rds")
if (!file.exists(rds)) {
    fs <- Sys.glob(file.path(jdir, "*.json"))
    m <- do.call(rbind, mclapply(fs, parse_match, mc.cores = max(1, detectCores() - 2)))
    saveRDS(m, rds)
}
m <- readRDS(rds)
cat("parsed", nrow(m), "matches\n")
stopifnot(nrow(m) == nrow(rd), !anyDuplicated(m$id), all(m$id %in% names(code)))
m$competition <- unname(code[m$id])
m$date <- as.Date(m$start)
m <- m[m$date <= last_day, ]
## a ground is the venue's name before any comma plus its city ("County Ground" alone is ambiguous)
m$ground <- paste0(trimws(sub(",.*", "", m$venue)), " | ",
                   ifelse(!is.na(m$city), m$city, ifelse(grepl(",", m$venue), trimws(sub("^[^,]*,\\s*([^,]*).*", "\\1", m$venue)), "")))

## ---- team names: only spelling variants and same-franchise rebrands are merged ---------
renames <- c(
    "Swaziland" = "Eswatini",                                       # international, renamed 2018
    "Kings XI Punjab" = "Punjab Kings",                             # IPL rebrand 2021
    "Delhi Daredevils" = "Delhi Capitals",                          # IPL rebrand 2019
    "Royal Challengers Bangalore" = "Royal Challengers Bengaluru",   # IPL/WPL rebrand 2024
    "Rising Pune Supergiants" = "Rising Pune Supergiant",           # IPL 2016 vs 2017 spelling
    "Sharjah Warriors" = "Sharjah Warriorz",                        # ILT20 spelling
    "Kathmandu Gurkhas" = "Kathmandu Gorkhas",                      # NPL spelling
    "Birmingham Bears" = "Warwickshire",                            # Warwickshire's T20 Blast name
    "Auckland Aces" = "Auckland", "Wellington Firebirds" = "Wellington",   # NZ associations'
    "Otago Volts" = "Otago", "Central Stags" = "Central Districts",        # Plunket Shield names
    "Oval Invincibles" = "MI London",                               # The Hundred rebrands 2026
    "Manchester Originals" = "Manchester Super Giants",
    "Northern Superchargers" = "Sunrisers Leeds")
for (v in c("team1", "team2", "toss_winner", "out_winner", "out_eliminator", "out_bowl_out")) {
    hit <- !is.na(m[[v]]) & m[[v]] %in% names(renames)
    m[[v]][hit] <- renames[m[[v]][hit]]
}

## ---- outcome --------------------------------------------------------------------------
m$tiebreak_winner <- ifelse(!is.na(m$out_eliminator), m$out_eliminator, m$out_bowl_out)
m$win_team <- ifelse(!is.na(m$out_winner), m$out_winner, m$tiebreak_winner)
noresult <- !is.na(m$out_result) & m$out_result == "no result"
stopifnot(is.na(m$out_winner) | is.na(m$out_result),
          !is.na(m$win_team) | m$out_result %in% c("draw", "tie", "no result"),
          is.na(m$win_team) | m$win_team == m$team1 | m$win_team == m$team2,
          is.na(m$tiebreak_winner) | m$out_result == "tie")
dropped <- table(m$team_type[noresult], m$gender[noresult])
m <- m[!noresult, ]
## scores: runs per side summed over all innings (super overs excluded; penalty runs included)
m$score1 <- ifelse(m$n_innings == 0, NA, m$runs1); m$score2 <- ifelse(m$n_innings == 0, NA, m$runs2)
plain <- !is.na(m$out_winner) & is.na(m$out_method) & m$n_innings > 0
wr <- ifelse(m$out_winner == m$team1, m$score1, m$score2); lr <- ifelse(m$out_winner == m$team1, m$score2, m$score1)
bad <- plain & wr <= lr
cat("runs disagree with the recorded winner (no method):", sum(bad), "of", sum(plain), "\n")
if (any(bad)) print(m[bad, c("id", "team1", "team2", "score1", "score2", "out_winner", "by_runs", "by_wickets")])
tie <- !is.na(m$out_result) & m$out_result == "tie" & is.na(m$out_method)
cat("ties with unequal runs:", sum(tie & m$score1 != m$score2), "of", sum(tie), "\n")

## ---- homefield: internationals, by the host country of the venue ------------------------
host_city <- list(
    "Australia" = c("Adelaide", "Bendigo", "Bowral", "Brisbane", "Cairns", "Canberra", "Carrara", "Coffs Harbour",
                    "Darwin", "Geelong", "Gold Coast", "Hobart", "Mackay", "Melbourne", "Perth", "Sydney",
                    "Townsville", "Victoria"),
    "England" = c("Birmingham", "Bishop's Stortford", "Brighton", "Bristol", "Canterbury", "Cardiff", "Chelmsford",
                  "Chester-le-Street", "Coggeshall", "Colchester", "Derby", "Frinton-on-Sea", "Halstead", "Hove",
                  "Leeds", "Leicester", "London", "Loughborough", "Manchester", "Northampton", "Nottingham",
                  "Scarborough", "Southampton", "Southend-on-Sea", "Taunton", "Worcester", "Wormsley"),
    "Scotland" = c("Aberdeen", "Arbroath", "Ayr", "Dundee", "Edinburgh", "Glasgow", "Stirling"),
    "Ireland" = c("Belfast", "Bready", "Derry", "Londonderry", "Dublin"),
    "Netherlands" = c("Amstelveen", "Deventer", "Rotterdam", "Schiedam", "The Hague", "Utrecht", "Voorburg"),
    "Denmark" = c("Brondby", "Copenhagen", "Ishoj", "Koge"),
    "New Zealand" = c("Auckland", "Christchurch", "Dunedin", "Lincoln", "Mount Maunganui", "Napier", "Nelson",
                      "New Plymouth", "Queenstown", "Wellington", "Whangarei"),
    "South Africa" = c("Benoni", "Bloemfontein", "Cape Town", "Centurion", "Durban", "East London", "Gqeberha",
                       "Johannesburg", "Kimberley", "Paarl", "Pietermaritzburg", "Port Elizabeth", "Potchefstroom",
                       "Pretoria"),
    "India" = c("Ahmedabad", "Bangalore", "Bengaluru", "Chandigarh", "Chennai", "Cuttack", "Delhi", "Dharamsala",
                "Dharmasala", "Faridabad", "Guwahati", "Gwalior", "Hyderabad", "Indore", "Jaipur", "Jamshedpur",
                "Kochi", "Kolkata", "Kanpur", "Lucknow", "Margao", "Mohali", "Mumbai", "Nagpur", "Navi Mumbai",
                "New Chandigarh", "Pune", "Raipur", "Rajkot", "Ranchi", "Surat", "Thiruvananthapuram", "Vadodara",
                "Visakhapatnam"),
    "Pakistan" = c("Faisalabad", "Karachi", "Lahore", "Multan", "Peshawar", "Rawalpindi", "Sind"),
    "Sri Lanka" = c("Colombo", "Dambulla", "FTZ Sports Complex", "Galle", "Hambantota", "Kandy", "Katunayake",
                    "Kurunegala", "Pallekele"),
    "Bangladesh" = c("Bogra", "Chattogram", "Chittagong", "Cox's Bazar", "Dhaka", "Fatullah", "Khulna", "Mirpur",
                     "Rajshahi", "Sylhet"),
    "West Indies" = c("Antigua", "Barbados", "Basseterre", "Bridgetown", "Cave Hill", "Coolidge", "Dominica",
                      "Gros Islet", "Grenada", "Guyana", "Jamaica", "Kingston", "Kingstown", "North Sound",
                      "Port of Spain", "Providence", "Roseau", "St George's", "St John's", "St Kitts", "St Lucia",
                      "St Vincent", "Tarouba", "Trinidad"),
    "Zimbabwe" = c("Bulawayo", "Harare", "Kwekwe"),
    "United Arab Emirates" = c("Abu Dhabi", "Ajman", "Dubai", "Sharjah"),
    "Oman" = "Al Amarat",
    "United States of America" = c("Dallas", "Houston", "Lauderhill", "Los Angeles", "Morrisville", "New York", "Pearland"),
    "Canada" = c("King City", "Toronto"),
    "Bermuda" = "Bermuda",
    "Kenya" = "Nairobi", "Uganda" = c("Entebbe", "Jinja", "Kampala"), "Tanzania" = "Dar-es-Salaam",
    "Rwanda" = "Kigali City", "Namibia" = "Windhoek", "Nigeria" = c("Abuja", "Lagos"), "Ghana" = "Accra",
    "Botswana" = "Gaborone", "Malawi" = "Blantyre", "Eswatini" = "Malkerns",
    "Nepal" = c("Kathmandu", "Kirtipur", "Pokhara"), "Bhutan" = "Gelephu",
    "Malaysia" = c("Bandar Kinrara", "Bangi", "Johor", "Kuala Lumpur", "Mantin"),
    "Singapore" = c("Singapore", "Padang"), "Thailand" = c("Bangkok", "Chiang Mai"), "Indonesia" = "Bali",
    "Cambodia" = "Phnom Penh", "Philippines" = "Dasmarinas",
    "Hong Kong" = c("Hong Kong", "Kowloon", "Mong Kok", "Wong Nai Chung Gap"),
    "China" = "Hangzhou", "Japan" = c("Sano", "Nisshin", "Osaka"), "South Korea" = "Incheon",
    "Qatar" = "Doha", "Kuwait" = "Kuwait City",
    "Papua New Guinea" = "Port Moresby", "Vanuatu" = "Port Vila", "Samoa" = "Apia", "Fiji" = "Suva",
    "New Caledonia" = "Noumea",
    "Argentina" = "Buenos Aires", "Brazil" = "Seropedica", "Colombia" = "Bogota",
    "Mexico" = c("Mexico City", "Naucalpan"), "Panama" = "Panama City", "Costa Rica" = "Guacima",
    "Cayman Islands" = "George Town",
    "Gibraltar" = "Gibraltar", "Spain" = c("Almeria", "Murcia"), "Portugal" = "Albergaria", "France" = "Dreux",
    "Belgium" = c("Ghent", "Waterloo", "Zemst"), "Luxembourg" = "Walferdange",
    "Germany" = c("Gelsenkirchen", "Karlsruhe", "Krefeld"), "Austria" = c("Graz", "Latschach", "Lower Austria"),
    "Italy" = c("Medicina", "Navile", "Pianoro", "Rome", "Spinaceto"), "Malta" = "Marsa", "Greece" = "Corfu",
    "Cyprus" = "Episkopi", "Serbia" = "Belgrade", "Croatia" = "Zagreb", "Bulgaria" = "Sofia",
    "Romania" = "Ilfov County", "Hungary" = "Szodliget", "Czech Republic" = "Prague", "Estonia" = "Tallinn",
    "Finland" = c("Kerava", "Vantaa"), "Sweden" = c("Kolsva", "Stockholm"), "Norway" = "Oslo",
    "Guernsey" = c("Castel", "Port  Soif", "St Martin", "St Peter Port"), "Jersey" = c("St Clement", "St Saviour"))
## matches whose file has no city, by venue
host_venue <- c(
    "Adelaide Oval" = "Australia", "Carrara Oval" = "Australia", "Melbourne Cricket Ground" = "Australia",
    "Perth Stadium" = "Australia", "Sydney Cricket Ground" = "Australia",
    "Arundel Castle Cricket Club Ground" = "England", "Louth Cricket Club" = "England",
    "West Mersea Cricket Club" = "England",
    "Al Amerat Cricket Ground Oman Cricket (Ministry Turf 1)" = "Oman",
    "Al Amerat Cricket Ground Oman Cricket (Ministry Turf 2)" = "Oman",
    "Al Dhaid Cricket Village" = "United Arab Emirates", "Dubai International Cricket Stadium" = "United Arab Emirates",
    "Dubai Sports City Cricket Stadium" = "United Arab Emirates", "Sharjah Cricket Stadium" = "United Arab Emirates",
    "Bulawayo Athletic Club" = "Zimbabwe", "Harare Sports Club" = "Zimbabwe",
    "Chittagong Divisional Stadium" = "Bangladesh", "Sylhet International Cricket Stadium" = "Bangladesh",
    "Sylhet Stadium" = "Bangladesh",
    "Colombo Cricket Club Ground" = "Sri Lanka", "Galle International Stadium" = "Sri Lanka",
    "Pallekele International Cricket Stadium" = "Sri Lanka", "Rangiri Dambulla International Stadium" = "Sri Lanka",
    "Entebbe Cricket Oval" = "Uganda", "Gahanga International Cricket Stadium. Rwanda" = "Rwanda",
    "Guanggong International Cricket Stadium" = "China", "Hong Kong Cricket Club" = "Hong Kong",
    "Johor Cricket Academy Oval" = "Malaysia", "Moara Vlasiei Cricket Ground" = "Romania",
    "Mombasa Sports Club Ground" = "Kenya", "Multan Cricket Stadium" = "Pakistan",
    "Rawalpindi Cricket Stadium" = "Pakistan", "Sheikhupura Stadium" = "Pakistan",
    "Queenstown Events Centre" = "New Zealand", "Royal Chiangmai Golf Club" = "Thailand",
    "San Albano" = "Argentina", "St Georges Quilmes" = "Argentina", "Sano International Cricket Ground" = "Japan",
    "Sir Vivian Richards Stadium, North Sound" = "West Indies",
    "Stellenbosch University 1" = "South Africa", "Stellenbosch University 2" = "South Africa",
    "Tafawa Balewa Square (TBS) Cricket Oval" = "Nigeria")
## "Hamilton" is both New Zealand and Bermuda: decided by ground
hamilton_nz <- c("Seddon Park", "Westpac Park")
city2host <- setNames(rep(names(host_city), lengths(host_city)), unlist(host_city))
stopifnot(!anyDuplicated(unlist(host_city)))
intl <- m$team_type == "international"
m$host <- NA_character_
m$host[intl] <- ifelse(is.na(m$city[intl]), host_venue[m$venue[intl]],
                ifelse(m$city[intl] == "Hamilton", ifelse(sub(" \\|.*", "", m$ground[intl]) %in% hamilton_nz, "New Zealand", "Bermuda"),
                       city2host[m$city[intl]]))
unmapped <- intl & is.na(m$host)
if (any(unmapped)) stop("international venue with no host country: ", paste(unique(m$venue[unmapped]), collapse = "; "))
m$home <- NA_character_
m$home[intl] <- ifelse(m$team1[intl] == m$host[intl], m$team1[intl],
                ifelse(m$team2[intl] == m$host[intl], m$team2[intl], NA))

## ---- homefield: domestic, by resident team of the ground ---------------------------------
## A ground is a team's home ground (within one competition and gender) when that team
## played in at least 70% of the competition's matches there, over at least 5 matches.
## Not applied to tournaments staged at one or a few host venues: WCL, SMA (zonal hosts), BLZ, SFT.
club <- which(!intl & !m$competition %in% c("WCL", "SMA", "BLZ", "SFT"))
key <- paste(m$competition, m$gender, m$ground)
gl <- data.frame(key = rep(key[club], 2), team = c(m$team1[club], m$team2[club]))
n_at <- table(key[club])
resident <- do.call(rbind, lapply(split(gl, gl$key), function(x) {
    t <- sort(table(x$team), decreasing = TRUE)
    data.frame(key = x$key[1], team = names(t)[1], n = n_at[[x$key[1]]], share = t[[1]] / n_at[[x$key[1]]])
}))
resident <- resident[resident$n >= 5 & resident$share >= 0.7, ]
res_team <- setNames(resident$team, resident$key)
m$home[club] <- ifelse((m$team1[club] == res_team[key[club]]) %in% TRUE, m$team1[club],
                ifelse((m$team2[club] == res_team[key[club]]) %in% TRUE, m$team2[club], NA))

## ---- assemble ---------------------------------------------------------------------------
## agent_a is the home side when there is one, else the first team listed in the file
swap <- !is.na(m$home) & m$home == m$team2
side <- function(team, a) ifelse(is.na(team), NA, ifelse(team == a, "agent_a", "agent_b"))
m$agent_a <- ifelse(swap, m$team2, m$team1); m$agent_b <- ifelse(swap, m$team1, m$team2)
out <- data.frame(
    agent_a = m$agent_a, agent_b = m$agent_b,
    date = as.numeric(as.POSIXct(format(m$date), tz = "UTC")),
    homefield = ifelse(is.na(m$home), "", "agent_a"),
    score_a = ifelse(swap, m$score2, m$score1), score_b = ifelse(swap, m$score1, m$score2),
    winner = ifelse(is.na(m$win_team), "draw", side(m$win_team, m$agent_a)),
    result = ifelse(is.na(m$out_result), "", m$out_result),
    method = ifelse(is.na(m$out_method), "", m$out_method),
    super_over = as.integer(!is.na(m$out_eliminator)),
    bowl_out = as.integer(!is.na(m$out_bowl_out)),
    match_type = m$match_type, competition = m$competition, event = m$event, season = m$season,
    venue = m$venue, city = ifelse(is.na(m$city), "", m$city),
    toss_winner = ifelse(is.na(m$toss_winner), "", side(m$toss_winner, m$agent_a)),
    toss_decision = ifelse(is.na(m$toss_decision), "", m$toss_decision),
    team_type = m$team_type, gender = m$gender, match_id = m$id,
    stringsAsFactors = FALSE)
out <- out[order(out$date, out$match_id), ]
stopifnot(!anyNA(out$agent_a), !anyNA(out$agent_b), !anyNA(out$date), out$agent_a != out$agent_b,
          out$winner %in% c("agent_a", "agent_b", "draw"), !anyNA(out$toss_winner),
          (out$winner == "draw") == (out$result %in% c("draw", "tie") & out$super_over == 0 & out$bowl_out == 0))

outdir <- path.expand("~/.cache/irw-comps/cricsheet-out")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
write_tab <- function(x, scope) {
    yrs <- format(as.POSIXct(range(x$date), origin = "1970-01-01", tz = "UTC"), "%Y")
    nm <- sprintf("cricsheet_%s_%s_%s", scope, yrs[1], yrs[2])
    x$team_type <- NULL; x$gender <- NULL
    if (grepl("^intl", scope)) x$competition <- NULL
    write.csv(x, file.path(outdir, paste0(nm, ".csv")), row.names = FALSE, na = "")
    ag <- table(c(x$agent_a, x$agent_b))
    cat(sprintf("%s: %d rows, %d agents (%d with >=10 matches), %s to %s, %d draws (%d ties), %d homefield blank, %d super-over/bowl-out\n",
                nm, nrow(x), length(ag), sum(ag >= 10), yrs[1], yrs[2], sum(x$winner == "draw"),
                sum(x$result == "tie" & x$winner == "draw"), sum(x$homefield == ""), sum(x$super_over + x$bowl_out)))
    print(table(x$match_type))
    yr <- format(as.POSIXct(x$date, origin = "1970-01-01", tz = "UTC"), "%Y")
    pr <- paste(pmin(x$agent_a, x$agent_b), pmax(x$agent_a, x$agent_b), yr)
    cat("  median meetings per pair-year (pairs that met):", median(table(pr)), "\n")
    invisible(nm)
}
cat("\ndropped as no result (team_type x gender):\n"); print(dropped)
cat("\n")
for (g in c("male", "female")) {
    s <- if (g == "male") "men" else "women"
    write_tab(out[out$team_type == "international" & out$gender == g, ], paste0("intl_", s))
    write_tab(out[out$team_type == "club" & out$gender == g, ], paste0("domestic_", s))
}
