table_id <- "gilbert_meta_59"

gt <- readRDS(".gt_gilbert_meta_59.rds")
items_gt <- sort(unique(gt$item))
resp_gt  <- sort(unique(gt$resp))
stopifnot(identical(items_gt, c("pss1","pss10","pss2","pss3","pss4rev","pss5rev",
                                 "pss6","pss7rev","pss8rev","pss9")))
stopifnot(identical(resp_gt, c(0L,1L,2L,3L,4L)))

# Standard Cohen (1983) PSS-10, presentation order pss1..pss10, cross-validated
# against reverse-scored item positions (4,5,7,8) matching the "rev" suffixes in
# the live data exactly. See .cache/gilbert_meta_59/sources.md for source detail.
item_order <- c("pss1","pss2","pss3","pss4rev","pss5rev","pss6","pss7rev","pss8rev","pss9","pss10")

# Verbatim from cached PDF (.cache/gilbert_meta_59/pss10_wovenwomenvets.pdf), a
# direct reproduction of Cohen, Kamarck & Mermelstein (1983)'s PSS-10 instrument
# (citation printed on the source page itself). The "In the last month, how
# often:" stem is the shared column header/instructions; each item below is the
# literal numbered clause.
item_text <- c(
  pss1     = "Have you been upset because of something that happened unexpectedly?",
  pss2     = "Have you felt that you were unable to control important things in your life?",
  pss3     = "Have you felt nervous and stressed?",
  pss4rev  = "Have you felt confident about your ability to handle your personal problems?",
  pss5rev  = "Have you felt that things were going your way?",
  pss6     = "Have you found that you could not cope with all the things that you do?",
  pss7rev  = "Have you been able to control irritations in your life?",
  pss8rev  = "Have you felt that you were on top of things?",
  pss9     = "Have you been angered because of things that happened that were outside of your control?",
  pss10    = "Have you felt difficulties were piling up so high you could not overcome them?"
)

# Standard PSS-10 response anchors, 0=Never .. 4=Very often, printed identically
# under every item on the source page (see PDF table: columns Never/Almost
# Never/Sometimes/Fairly Often/Very Often = 0/1/2/3/4). The "rev" in item names
# like pss4rev signals that reverse-scoring is applied when computing a total
# scale score (per the source's "Reverse your scores for questions 4, 5, 7, 8"
# instructions) -- it does not change the raw response anchor wording itself, and
# the live `resp` column holds the raw (pre-reversal) 0-4 codes.
option_text <- c(`0` = "Never", `1` = "Almost never", `2` = "Sometimes",
                  `3` = "Fairly often", `4` = "Very often")

instrument_name <- "Perceived Stress Scale (PSS-10; Cohen, Kamarck, & Mermelstein, 1983)"
instructions_text <- "In the last month, how often:"

rows <- list()
for (it in item_order) {
  for (r in 0:4) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table_id,
      section_id = paste0(table_id, "_1"),
      item = it,
      instrument = instrument_name,
      instructions = instructions_text,
      section_prompt = "",
      item_text = item_text[[it]],
      correct_response = "",
      option_text = option_text[[as.character(r)]],
      resp = r,
      stringsAsFactors = FALSE
    )
  }
}
out <- do.call(rbind, rows)

# Validate against ground truth
stopifnot(identical(sort(unique(out$item)), items_gt))
stopifnot(identical(sort(unique(out$resp)), resp_gt))

saveRDS(out, "candidate_gilbert_meta_59.rds")
str(out)
cat("Rows:", nrow(out), "\n")
