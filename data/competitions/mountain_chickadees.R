##Wild mountain chickadee displacements at RFID feeders, high- and low-elevation sites,
##two winters (2019-20, 2020-21; the file ends in December 2020). Heinen, V., Benedict, L., Pitera, A.,
##Sonnenberg, B., Bridge, E., & Pravosudov, V. (2021). Social dominance has
##limited effects on spatial cognition in a wild food-caching bird. Proceedings of the Royal
##Society B, 288, 20211784. https://doi.org/10.1098/rspb.2021.1784 (the deposit carries the
##submitted title, "Social dominance status is associated with differences in spatial
##cognitive flexibility in wild mountain chickadees").
##Data: Dryad doi:10.5061/dryad.kh189326b, read from its Zenodo mirror, record 5576298
##(https://zenodo.org/records/5576298), file DisplacementEvents.csv.
##Licence: Zenodo API for the record, "license": {"id": "cc-zero"} (CC0 1.0), checked
##2026-10-01.
##
##These contests are inferred, not observed: README.docx says the file is "Partial output
##from the first half of 01_DetectDisplacement.R", which detects displacements from the
##RFID visit stream with the method of Evans et al. (2018, Ethology 124:188-195), and
##"Contains only within-group displacement events". There is no rater.
##
##Agents are PIT-tag codes. Tags are unique birds and are stable across both seasons, so
##the whole file is one table; contests only occur within a community (group), so the
##contest graph splits into several disconnected parts (by area and elevation).
##
##One row per displacement, in source order. agent_a = win, agent_b = loss, so winner is
##always "agent_a". date = dt (POSIX seconds, as recorded). 68 rows carry a 2002-02-05
##logger timestamp inside the 2019-20 season (presumably a logger clock fault); their date is blank
##and the raw value is kept in dt_source for every row. site (feeder), group (community
##and season), season and elevation (H/L, the first letter of group) are kept.
##homefield is blank.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/5576298")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "DisplacementEvents.csv")
if (!file.exists(f))
  download.file("https://zenodo.org/api/records/5576298/files/DisplacementEvents.csv/content", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "98081be4550b5de16c93a7533fe4e853")
x <- read.csv(f, stringsAsFactors = FALSE, colClasses = c(win = "character", loss = "character"))

bad <- x$dt < as.numeric(as.POSIXct("2019-01-01", tz = "UTC"))
stopifnot(sum(bad) == 68)
df <- data.frame(agent_a = x$win, agent_b = x$loss, date = ifelse(bad, NA, x$dt),
                 homefield = "", winner = "agent_a",
                 site = x$Site, group = x$group, season = x$season,
                 elevation = substr(x$group, 1, 1), dt_source = x$dt)
stopifnot(!anyNA(df$agent_a), !anyNA(df$agent_b), df$agent_a != df$agent_b,
          all(df$elevation %in% c("H", "L")))
out <- "mountain_chickadees_2019_2020.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "displacements,", length(unique(c(df$agent_a, df$agent_b))), "birds,",
    length(unique(df$group)), "communities\n")
