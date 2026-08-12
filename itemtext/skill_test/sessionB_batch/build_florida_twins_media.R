library(dplyr)

table_name <- "florida_twins_media"
instrument <- "Homework and Free Time (Florida Twin Project on Reading, Behavior, and Environment, Wave 3 Child Codebook) -- Parental Monitoring of Media Use"

# No single overarching instructions sentence applies to both sub-blocks (they have
# distinct stems: "Have your parents ever talked to you..." vs "How much do your
# parents know about..."). Leaving table-level `instructions` blank and putting each
# stem in `section_prompt`, scoped to its own section_id, per the boundary rule.

items_text <- list(
  media1t = "When you can use media (such as only on weekends, only after homework or chores)",
  media2t = "How long you can use media for (such as no more than an hour a day)",
  media3t = "What types of media you can use (such as no watching certain types of shows or playing certain games)",
  media4t = "Staying safe online (such as not giving out personal information)",
  media5t = "Being responsible, respectful, and kind online (such as not bullying or copying other people's work)",
  media6t = "What you do and see online",
  media7t = "The types of video or computer games you play",
  media8t = "Which TV shows you watch",
  media9t = "The songs you listen to",
  media10t = "What you do on social media (such as Facebook, Twitter, or Instagram)",
  media11t = "Which apps you use"
)

section_of <- function(item) {
  if (item %in% c("media1t","media2t","media3t","media4t","media5t")) "florida_twins_media_talked"
  else "florida_twins_media_know"
}

section_prompt_of <- function(sec) {
  if (sec == "florida_twins_media_talked") {
    "Have your parents ever talked to you about any of the following (Please circle Yes or No):"
  } else {
    "How much do your parents know about..."
  }
}

# response options per section
opts_talked <- data.frame(resp = c(0L,1L), option_text = c("No","Yes"), stringsAsFactors = FALSE)
opts_know   <- data.frame(resp = c(0L,1L,2L,3L),
                           option_text = c("Nothing","Only a little","Some","A lot"),
                           stringsAsFactors = FALSE)

rows <- list()
for (item in names(items_text)) {
  sec <- section_of(item)
  opts <- if (sec == "florida_twins_media_talked") opts_talked else opts_know
  df <- data.frame(
    table = table_name,
    section_id = sec,
    item = item,
    instrument = instrument,
    instructions = "",
    section_prompt = section_prompt_of(sec),
    item_text = items_text[[item]],
    correct_response = "",
    option_text = opts$option_text,
    resp = opts$resp,
    stringsAsFactors = FALSE
  )
  rows[[item]] <- df
}

out <- do.call(rbind, rows)
rownames(out) <- NULL

# order columns per model
out <- out[, c("table","section_id","item","instrument","instructions",
               "section_prompt","item_text","correct_response","option_text","resp")]

str(out)
print(out)

saveRDS(out, "candidate_florida_twins_media.rds")

# validation against ground truth
gt <- readRDS(".gt_florida_twins_media.rds")
cat("item match:", identical(sort(unique(out$item)), sort(unique(gt$item))), "\n")
cat("resp match:", identical(sort(unique(out$resp)), sort(unique(gt$resp))), "\n")
print(sort(unique(out$item)))
print(sort(unique(gt$item)))
print(sort(unique(out$resp)))
print(sort(unique(gt$resp)))
