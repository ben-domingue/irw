## openpowerlifting: individual attempts at the three powerlifting lifts, one row per
## attempt. The lifter chooses the weight on every attempt, so this is a test whose item
## difficulties are set by the test-taker.
##
## Source: the OpenPowerlifting bulk CSV export,
## https://openpowerlifting.gitlab.io/opl-csv/files/openpowerlifting-latest.zip
## (project repository https://gitlab.com/openpowerlifting/opl-data).
## Licence: public domain. LICENSE.txt in the export: "OpenPowerlifting data is contributed
## to the public domain ... To the extent possible under law, all CSV data is waived of all
## copyright and related or neighboring rights." Attribution is requested, not required.
## The export is rebuilt continuously and is not versioned, so it cannot be md5-pinned; the
## counts printed below are what the 2026-10-24 export gave, and they are reported rather
## than asserted.
##
## A real-data counterpart to data/trials/nflverse_kicks.R and data/simsyn/nbashots_sim.R,
## with the selection on the other side of the table: a kicker is sent out by his coach and
## a shooter is shaped by the defence, but a lifter announces the weight himself, knowing
## the standings and what he has already made. Attempts two and three are chosen after
## seeing attempt one, so the nine responses are not locally independent by construction.
## `resp` is therefore about attempt selection under risk; the weight attempted, which is
## where the strength actually shows, is `trial_load`.
##
## Choices:
## - Full-power meets only (Event == "SBD") with all nine attempts recorded. Not every
##   federation reports attempts; many report best lifts only, and those entries are dropped.
## - resp = 1 if the attempt was made, 0 if missed. OpenPowerlifting records a missed
##   attempt as a negative weight, so the sign carries the outcome and the magnitude the
##   load. No cell in the kept entries is 0, so a kept entry is nine real attempts.
## - Fourth attempts (Squat4Kg etc.) are excluded: they are record attempts outside the
##   nine-attempt design, taken only by lifters who have already won their class.
## - id is an integer per lifter, in order of first appearance. OpenPowerlifting's `Name` is
##   a real name (disambiguated with a '#' suffix when two lifters share one), so per
##   datastandard.md it is neither carried into the table nor used as the id; the integer
##   index preserves the linkage across meets that makes the table longitudinal.
## - wave orders each lifter's meets in time and `date` is the meet date in Unix seconds. A
##   lifter entered twice in one meet under different divisions appears once: entries with
##   the same lifter, meet, date and identical nine attempts are collapsed.
## - item is the lift and attempt number (squat_1 ... deadlift_3), in the order taken.
## - trial_load is the weight attempted in kg, always positive. trial_bodyweight is the
##   weigh-in weight at that meet, trial_equipment the squat/bench equipment class (Raw,
##   Wraps, Single-ply, Multi-ply, Unlimited), trial_federation the sanctioning body, and
##   trial_age the lifter's age at the meet where the source records it.
## - cov_sex is taken from the lifter's first meet (the source records it per entry).

library(data.table)

cache <- path.expand("~/.cache/irw-sports/opl")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
zipf <- file.path(cache, "openpowerlifting-latest.zip")
if (!file.exists(zipf))
    download.file("https://openpowerlifting.gitlab.io/opl-csv/files/openpowerlifting-latest.zip",
                  zipf, mode = "wb")
inner <- grep("\\.csv$", unzip(zipf, list = TRUE)$Name, value = TRUE)
stopifnot(length(inner) == 1)
cat("export:", inner, "\n")
unzip(zipf, files = inner, exdir = cache, overwrite = TRUE, junkpaths = TRUE)
csvf <- file.path(cache, basename(inner))

acols <- c("Squat1Kg", "Squat2Kg", "Squat3Kg", "Bench1Kg", "Bench2Kg", "Bench3Kg",
           "Deadlift1Kg", "Deadlift2Kg", "Deadlift3Kg")
x <- fread(csvf, select = c("Name", "Sex", "Event", "Equipment", "Age", "BodyweightKg",
                            acols, "Federation", "Date", "MeetName"),
           showProgress = FALSE)
cat("export rows:", nrow(x), "\n")

x <- x[Event == "SBD"]
x <- x[rowSums(is.na(x[, ..acols])) == 0]
cat("full-power entries with all nine attempts:", nrow(x), "\n")
stopifnot(!any(as.matrix(x[, ..acols]) == 0))

## a lifter entered twice in one meet with the same nine attempts is one performance
setorder(x, Name, Date, MeetName)
before <- nrow(x)
x <- unique(x, by = c("Name", "Date", "MeetName", acols))
cat("duplicate division entries collapsed:", before - nrow(x), "\n")
rep_keys <- nrow(x) - nrow(unique(x, by = c("Name", "Date", "MeetName")))
cat("lifter-meet keys left with a second, different set of attempts:", rep_keys, "\n")

x[, date := as.integer(as.POSIXct(Date, format = "%Y-%m-%d", tz = "UTC"))]
setorder(x, Name, date, MeetName)
x[, id := .GRP, by = Name]
x[, wave := seq_len(.N), by = id]
x[, cov_sex := Sex[1], by = id]

long <- melt(x, id.vars = c("id", "wave", "date", "cov_sex", "BodyweightKg", "Equipment",
                            "Federation", "Age"),
             measure.vars = acols, variable.name = "item", value.name = "kg")
long[, item := tolower(sub("Kg$", "", as.character(item)))]
long[, item := sub("([a-z]+)([0-9])$", "\\1_\\2", item)]
long[, resp := as.integer(kg > 0)]
long[, trial_load := abs(kg)]

out <- long[, .(id, item, resp, wave, date, trial_load,
                trial_bodyweight = BodyweightKg, trial_equipment = Equipment,
                trial_federation = Federation, trial_age = Age, cov_sex)]
out[, item := factor(item, levels = c("squat_1", "squat_2", "squat_3", "bench_1", "bench_2",
                                      "bench_3", "deadlift_1", "deadlift_2", "deadlift_3"))]
setorder(out, id, wave, item)

stopifnot(nrow(out) == 9 * nrow(x), !any(is.na(out$id)), !any(is.na(out$item)),
          !any(is.na(out$resp)), !any(is.na(out$wave)), !any(is.na(out$trial_load)),
          out$resp %in% c(0L, 1L), out$trial_load > 0,
          uniqueN(out, by = c("id", "item", "wave")) == nrow(out))

cat("rows", nrow(out), "lifters", uniqueN(out$id), "items", uniqueN(out$item),
    "meets", nrow(x), "\n")
print(out[, .(n = .N, made = round(mean(resp), 3), load_med = median(trial_load)), by = item])
print(as.POSIXct(range(out$date, na.rm = TRUE), origin = "1970-01-01", tz = "UTC"))
out[, item := as.character(item)]
fwrite(out, "openpowerlifting.csv", na = "", quote = TRUE)
