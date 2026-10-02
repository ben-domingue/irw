##Place Pulse 2.0: crowdsourced pairwise judgements of Google Street View images from 56
##cities, 2013-2019. Salesses, P., & Hidalgo, C. A. (2020). Place Pulse. figshare. Dataset.
##https://doi.org/10.6084/m9.figshare.11859993.v1 (version 1, file votes_clean.csv,
##md5 below); "The data has been cleaned by David Buil-Gil before releasing it to the
##public." Earlier paper: Salesses, P., Schechtner, K., & Hidalgo, C. A. (2013). The
##collaborative image of the city: mapping the inequality of urban perception. PLoS ONE,
##8(7), e68400. https://doi.org/10.1371/journal.pone.0068400
##Licence: figshare API for the article, "license": {"name": "CC BY 4.0",
##"url": "https://creativecommons.org/licenses/by/4.0/"}, checked 2026-10-01.
##
##A voter saw two street images and answered one question: which looks safer, livelier,
##more beautiful, wealthier, more depressing or more boring. Each question is one table:
##  placepulse2_safer, placepulse2_livelier, placepulse2_beautiful, placepulse2_wealthier,
##  placepulse2_depressing, placepulse2_boring
##
##One row per vote, in source order. agent_a = left image, agent_b = right image (the
##source's image ids); choice "left" -> "agent_a", "right" -> "agent_b", "equal" -> "draw".
##rater = voter_uniqueid re-keyed to an integer, one map across all six tables so a voter
##keeps one number; the hashed source ids are not published. date = day + time in Unix
##seconds, read as UTC (the source gives no zone). city_a/city_b (place_name_left/right)
##and study_id are kept. The source's latitude/longitude columns are dropped: their names
##are swapped (long_* holds latitudes), and the image ids identify the images anyway.
##homefield is blank.
##
##Cleaning: votes whose choice is not left/right/equal, whose study_question is missing, or
##whose study_id is not a 24-character hex id are dropped and counted. These are junk rows
##left in the cleaned file by web-vulnerability scanners (probe strings in those fields).

library(data.table)
cache <- path.expand("~/.cache/irw-comps/discovery-1001/placepulse")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "votes_clean.csv")
if (!file.exists(f))
  download.file("https://ndownloader.figshare.com/files/21739137", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "55d2da3bafac0521722bab517fa715c9")
x <- fread(f, colClasses = "character", na.strings = c("", "NA"),
           select = c("left", "right", "study_id", "voter_uniqueid", "choice", "study_question",
                      "place_name_left", "place_name_right", "day", "time"))
n0 <- nrow(x)
bad <- !(x$choice %in% c("left", "right", "equal")) | is.na(x$study_question) |
  !grepl("^[0-9a-f]{24}$", x$study_id)
x <- x[!bad]
cat("dropped", sum(bad), "of", n0, "votes\n")
voters <- sort(unique(x$voter_uniqueid))

q <- c(safer = "safer", livelier = "livelier", beautiful = "more beautiful",
       wealthier = "wealthier", depressing = "more depressing", boring = "more boring")
stopifnot(setequal(unique(x$study_question), q))
for (nm in names(q)) {
  y <- x[study_question == q[[nm]]]
  df <- data.frame(agent_a = y$left, agent_b = y$right,
                   date = as.numeric(as.POSIXct(paste(y$day, y$time), format = "%Y-%m-%d %H:%M:%S", tz = "UTC")),
                   homefield = "",
                   winner = c(left = "agent_a", right = "agent_b", equal = "draw")[y$choice],
                   rater = match(y$voter_uniqueid, voters),
                   city_a = y$place_name_left, city_b = y$place_name_right, study_id = y$study_id,
                   row.names = NULL)
  stopifnot(!anyNA(df$date), !anyNA(df$agent_a), !anyNA(df$agent_b), df$agent_a != df$agent_b)
  out <- paste0("placepulse2_", nm, ".csv")
  fwrite(df, out, na = "")
  cat(out, nrow(df), "votes,", length(unique(c(df$agent_a, df$agent_b))), "images,",
      length(unique(df$rater)), "voters,", sum(df$winner == "draw"), "equal\n")
  rm(y, df); gc()
}
