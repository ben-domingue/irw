##Northern elephant seal male-male dominance interactions, Año Nuevo State Reserve
##(breeding seasons 2009-10 to 2012-13) and Piedras Blancas (2011-12). Casey, C.,
##Charrier, I., Mathevon, N., & Reichmuth, C. (2015). Rival assessment among northern
##elephant seals: evidence of associative learning during male-male contests. Royal
##Society Open Science, 2(8), 150228. https://doi.org/10.1098/rsos.150228
##Data: Dryad doi:10.5061/dryad.6g06h, read from its Zenodo mirror, record 4963387
##(https://zenodo.org/records/4963387), file "raw dominance interaction data 2009_2013.xlsx".
##Licence: Zenodo API for the record, "license": {"id": "cc-zero"} (CC0 1.0), checked
##2026-10-01.
##
##The workbook's METHODS sheet: interactions "were observed and scored each day in the
##field"; "Winner and loser were established based on the turning away or retreat by the
##subordinate animal, the loser"; "Interactions occuring within 5 minutes of one another
##were treated as one interaction."
##
##Males are identified by marks and tags applied each season (e.g. 1R, GL, 8RS/G5479), so
##ids are not comparable across seasons or sites: each season sheet is its own table.
##  elephant_seals_anonuevo_2009_2010       sheet "2009-2010 SEASON"
##  elephant_seals_anonuevo_2010_2011       sheet "2010-2011 SEASON"
##  elephant_seals_anonuevo_2011_2012       sheet "2011-2012 SEASON"
##  elephant_seals_anonuevo_2012_2013       sheet "2012-2013 SEASON"
##  elephant_seals_piedrasblancas_2012      sheet "2010-2012 SEASON PIEDRAS BLANCA" (all of
##                                          its dates fall in Jan-Feb 2012)
##
##One row per interaction, in source order. agent_a = WINNER, agent_b = LOSER (ids
##upper-cased and trimmed), so winner is always "agent_a". Rows with a missing id, or the
##same id on both sides (e.g. one marked "NO APPARENT WINNNER"), are dropped and counted.
##date = DATE in Unix seconds, UTC midnight (the sheets store it as text like DEC_18_2010
##or as an Excel serial). time = TIME as HH:MM where it can be read (Excel day fractions,
##hhmm or h:mm), else the source text (e.g. "PM", "UK", "UNKNOWN"). rater = OBSERVER, the observer's
##initials upper-cased ("CC/SF" = two observers), blank where missing or unknown; the
##Piedras Blancas sheet has no observer column. Other columns kept where the sheet has them:
##interaction_number, area, vocal_a/vocal_b, intensity_a/intensity_b (physical intensity
##1-3 per METHODS), contact, contact_intensity, distance, description, comments.
##homefield is blank.

library(readxl)
cache <- path.expand("~/.cache/irw-comps/discovery-1001/4963387")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "raw dominance interaction data 2009_2013.xlsx")
if (!file.exists(f))
  download.file("https://zenodo.org/api/records/4963387/files/raw%20dominance%20interaction%20data%202009_2013.xlsx/content", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "3090bf435dce2d904305cac04269954b")

rd <- function(sheet, skip, cols) {
  x <- as.data.frame(read_excel(f, sheet = sheet, col_names = FALSE, col_types = "text", skip = skip,
                                 .name_repair = "minimal"))
  stopifnot(ncol(x) == length(cols))
  names(x) <- cols
  x[!is.na(x$interaction_number) | !is.na(x$winner), ]
}
s <- list(
  anonuevo_2009_2010 = rd("2009-2010 SEASON", 3, c("interaction_number", "date", "winner", "loser",
                          "vocal_a", "vocal_b", "description", "rater")),
  anonuevo_2010_2011 = rd("2010-2011 SEASON", 1, c("interaction_number", "date", "time", "area",
                          "winner", "vocal_a", "intensity_a", "loser", "vocal_b", "intensity_b",
                          "vocal_interaction", "contact", "contact_intensity", "rater", "comments")),
  anonuevo_2011_2012 = rd("2011-2012 SEASON", 2, c("interaction_number", "date", "time", "area",
                          "winner", "vocal_a", "intensity_a", "loser", "vocal_b", "intensity_b",
                          "contact", "contact_intensity", "distance", "rater", "comments")),
  anonuevo_2012_2013 = rd("2012-2013 SEASON", 2, c("interaction_number", "date", "time", "area",
                          "winner", "vocal_a", "intensity_a", "loser", "vocal_b", "intensity_b",
                          "contact", "contact_intensity", "distance", "rater", "comments")),
  piedrasblancas_2012 = rd("2010-2012 SEASON PIEDRAS BLANCA", 2, c("interaction_number", "date", "time",
                          "area", "winner", "vocal_a", "intensity_a", "loser", "vocal_b", "intensity_b",
                          "contact", "contact_intensity", "distance", "comments")))

todate <- function(d) {
  serial <- grepl("^[0-9]+(\\.0+)?$", d)
  out <- rep(NA_real_, length(d))
  out[serial] <- as.numeric(as.POSIXct(as.Date(as.numeric(d[serial]), origin = "1899-12-30"), tz = "UTC"))
  out[!serial] <- as.numeric(as.POSIXct(d[!serial], format = "%b_%d_%Y", tz = "UTC"))
  out
}
totime <- function(t) {
  t <- trimws(t)
  out <- t
  fr <- !is.na(t) & grepl("^[0-9]*\\.[0-9]+$", t)  # Excel day fraction (a few carry a day part too)
  m <- round((as.numeric(t[fr]) %% 1) * 1440)
  out[fr] <- sprintf("%02d:%02d", m %/% 60, m %% 60)
  hm <- !is.na(t) & grepl("^[0-9]{3,4}$", t)           # hhmm
  v <- as.integer(t[hm])
  out[hm] <- sprintf("%02d:%02d", v %/% 100, v %% 100)
  cl <- !is.na(t) & grepl("^[0-9]{1,2}:[0-9]{2}$", t)  # h:mm or hh:mm
  p <- strsplit(t[cl], ":")
  out[cl] <- sprintf("%02d:%s", as.integer(sapply(p, `[`, 1)), sapply(p, `[`, 2))
  out[is.na(t)] <- ""
  out
}

for (nm in names(s)) {
  x <- s[[nm]]
  x$winner <- toupper(trimws(x$winner))
  x$loser <- toupper(trimws(x$loser))
  keep <- !is.na(x$winner) & !is.na(x$loser) & x$winner != x$loser
  nd <- sum(!keep)
  x <- x[keep, ]
  df <- data.frame(agent_a = x$winner, agent_b = x$loser, date = todate(x$date),
                   homefield = "", winner = "agent_a")
  if ("rater" %in% names(x)) {
    r <- toupper(trimws(x$rater))
    df$rater <- ifelse(is.na(r) | r %in% c("UK", "UNKNOWN"), "", r)
  }
  df$interaction_number <- x$interaction_number
  if ("time" %in% names(x)) df$time <- totime(x$time)
  for (k in c("area", "vocal_a", "vocal_b", "intensity_a", "intensity_b", "vocal_interaction",
              "contact", "contact_intensity", "distance", "description", "comments"))
    if (k %in% names(x)) df[[k]] <- x[[k]]
  stopifnot(!anyNA(df$date))
  out <- paste0("elephant_seals_", nm, ".csv")
  write.csv(df, out, row.names = FALSE, na = "")
  cat(out, nrow(df), "interactions,", length(unique(c(df$agent_a, df$agent_b))), "males,",
      if (!is.null(df$rater)) length(unique(df$rater[df$rater != ""])) else 0, "observer codes;",
      format(as.POSIXct(range(df$date), origin = "1970-01-01", tz = "UTC"), "%Y-%m-%d"),
      "; dropped", nd, "\n")
}
