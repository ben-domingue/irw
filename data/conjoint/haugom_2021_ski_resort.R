##Ski day ratings: rating-based conjoint of alpine skiers, Norway (Hafjell, Inland Norway)
##Haugom, E., Malasevska, I., & Lien, G. (2021). The relative importance of ski resort- and weather-related
##characteristics when going alpine skiing: data from a rating-based conjoint survey [Data set]. Mendeley Data, v1.
##Deposit: doi:10.17632/6w4tzrs3yw, CC BY 4.0 (Mendeley data_licence field). The data relate to Haugom, Malasevska & Chen
##(2019) Cogent Social Sciences 10.1080/23311886.2019.1681246 (not stored as the paper DOI of the table: the deposit lists no
##article). File read: DATA.xlsx (sheet Sheet1, converted to CSV in the raw dir; usage:
##Rscript haugom_2021_ski_resort.R <dir holding data.csv> <output dir>).
##
##Active alpine skiers at a large ski area in Inland Norway, February 2018. Ten versions of one questionnaire
##(QUESTIONAIRE_CODE: SLOPES-1/2, WIND-1/2, TP-1, TEMP-1/2, SNOW-1/2, RAIN-1); each respondent rated 18 scenarios
##(two questions of nine scenarios, QUESTION x R8-HELP "q_s_rate"), i.e. 399 respondents x 18 = 7,182 rows. Fixed designs:
##within a version only some of the 8 attributes vary (price, weekday, queue time and the version's focus attribute),
##the rest are held constant across that respondent's 18 cards; all respondents of a version saw the same cards (not
##checked beyond the version code). trial_version records the version. No randomization of level combinations.
##Attributes (8; levels = text of the source columns): weekday (MIDWEEK, WEEKEND), price (250,350,450,550,650; currency
##not documented in the deposit, presumably NOK), period (REGULAR WEEK, VACATION), weather (SUN, CLOUDY, FOG, RAIN, SNOW),
##temperature (-20,-15,-10,-5,0,5; unit not documented, presumably degrees C), wind (NO WIND, GENTLE BREEZE, FRESH BREEZE),
##slopes open (0.5, 0.75, 1 = share of slopes open), queue time (1, 5, 10; unit not documented, presumably minutes).
##Stored as the source text/number rendered as text; the on-screen wording is not in the deposit.
##Outcome: rating (0-100 in the source; observed 0 to 100, integers). Question wording and anchors are NOT in the deposit and
##the direction is not stated (the authors treat higher as more favourable; recorded as unknown). Stored raw. One cell "AN"
##and 691 empty cells are missing ratings: rows with no rating are omitted; 24 respondents with all 18 ratings missing are
##therefore absent (375 respondents remain). task = order of the scenario within the respondent (question then scenario
##number from R8-HELP), profile = 1.
##Covariates kept: cov_gender (MALE/FEMALE flags -> male/female), cov_age (years; NA for 2 respondents).
##Dropped: dummy codings of every attribute, importance indicators (QUE_1/5/10, ...), skiing-days counts, work, family,
##income (coded 0-6 without labels), gear, ancillary services and other derived/unlabelled survey columns. No PII in the file.
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- fread(file.path(raw, "data.csv"), colClasses = "character")
x[, qs := tstrsplit(`R8-HELP`, "_")[[1]]]; x[, sn := as.integer(tstrsplit(`R8-HELP`, "_")[[2]])]
x[, qn := as.integer(QUESTION)]
x[, idn := as.integer(ID)]
setorder(x, idn, qn, sn)
x[, task := seq_len(.N), by = idn]
stopifnot(x[, .N, by = idn][, all(N == 18)])
x[, rating := suppressWarnings(as.integer(RATING))]
x <- x[!is.na(rating)]
stopifnot(all(x$rating >= 0 & x$rating <= 100))
x[, id := match(idn, unique(idn))]
x[, cov_age := suppressWarnings(as.integer(AGE))]
x[, cov_gender := ifelse(MALE == "1", "male", ifelse(FEMALE == "1", "female", NA_character_))]
d <- x[, .(id, task, profile = 1L, rating,
           attr_weekday = WEKKDAY, attr_price = PRICE, attr_period = PERIOD, attr_weather = WEATHER,
           attr_temperature = TEMPERATURE, attr_wind = WIND, attr_slopes_open = SLOPES_OPEN, attr_queue_time = QUE_TIME,
           cov_gender, cov_age, trial_version = QUESTIONAIRE_CODE)]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "haugom_2021_ski_resort.csv"))
