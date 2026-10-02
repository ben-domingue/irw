##Tonkean macaque conflicts at automated testing machines (MALT), Strasbourg
##Primatology Centre, 2016-10 to 2024-08. Ballesta, S., & Guerillon, A. (2025).
##"MALT Macaque hierarchy of dominance and economic decisions". Zenodo record 15090088,
##version 1.0.0, doi:10.5281/zenodo.15090088 (https://zenodo.org/records/15090088).
##Licence: Zenodo API for the record, "license": {"id": "cc-by-4.0"} (CC BY 4.0),
##checked 2026-10-01.
##
##Source file: eloconf_modules.txt, which the record describes as "the raw data used for
##the computation of the hierarchy of dominance"; readme.pdf: "This dataset contains all
##conflict results, including the winner, loser, and the date/time of the conflict."
##Conflicts were recorded automatically at the MALT testing booths, not by an observer,
##so there is no rater.
##
##One row per conflict, in source order. agent_a = winner, agent_b = loser, so winner is
##always "agent_a" (the source records no draws). Agents are the source's three-letter
##animal codes (infos.csv maps them to names). date = Date + time in Unix seconds, read
##as UTC (the source gives local clock time with no zone). homefield is blank.
##timesincetouch and timetonextconf are kept as in the source; the readme does not
##define them.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/15090088")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "eloconf_modules.txt")
if (!file.exists(f))
  download.file("https://zenodo.org/api/records/15090088/files/eloconf_modules.txt/content", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "3240fee684778e432be2c46eb88a31fc")
x <- read.csv(f, stringsAsFactors = FALSE)

df <- data.frame(agent_a = x$winner, agent_b = x$loser,
                 date = as.numeric(as.POSIXct(paste(x$Date, x$time), format = "%Y-%m-%d %H:%M:%S", tz = "UTC")),
                 homefield = "", winner = "agent_a",
                 timesincetouch = x$timesincetouch, timetonextconf = x$timetonextconf)
stopifnot(!anyNA(df$date), !anyNA(df$agent_a), !anyNA(df$agent_b), df$agent_a != df$agent_b)
out <- "tonkean_macaques_2016_2024.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "conflicts,", length(unique(c(df$agent_a, df$agent_b))), "animals\n")
