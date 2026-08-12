table <- "ffm_agr"
instrument <- "IPIP Big-Five Factor Markers (IPIP-50): Agreeableness subscale"

# AGR1..AGR10 item text, verbatim from codebook.txt (IPIP-FFM-data-8Nov2018),
# in the codebook's stated presentation order for the Agreeableness block.
agr <- c(
"I feel little concern for others.",
"I am interested in people.",
"I insult people.",
"I sympathize with others' feelings.",
"I am not interested in other people's problems.",
"I have a soft heart.",
"I am not really interested in others.",
"I take time out for others.",
"I feel others' emotions.",
"I make people feel at ease."
)
stopifnot(length(agr) == 10)

instructions <- "The following items were presented on one page and each was rated on a five point scale using radio buttons. The order on page was EXT1, AGR1, CSN1, EST1, OPN1, EXT2, etc. The scale was labeled 1=Disagree, 3=Neutral, 5=Agree."

opts <- c("1"="Disagree","2"="","3"="Neutral","4"="","5"="Agree")

gt <- readRDS(".gt_ffm_agr.rds")
gt_items <- sort(unique(gt$item))  # "item_1".."item_10"

rows <- list()
for (i in 1:10) {
  it <- paste0("item_", i)
  if (!(it %in% gt_items)) next
  for (r in 1:5) {
    rows[[length(rows)+1]] <- data.frame(
      table = table,
      section_id = paste0(table, "_1"),
      item = it,
      instrument = instrument,
      instructions = instructions,
      section_prompt = "",
      item_text = agr[i],
      correct_response = "",
      option_text = opts[[as.character(r)]],
      resp = r,
      stringsAsFactors = FALSE
    )
  }
}
out <- do.call(rbind, rows)
rownames(out) <- NULL
saveRDS(out, file = "candidate_ffm_agr.rds")

cat("N rows:", nrow(out), "\n")
cat("item match:", setequal(unique(out$item), gt_items), "\n")
cat("resp match:", setequal(sort(unique(out$resp)), sort(unique(gt$resp))), "\n")
cat("missing items:", paste(setdiff(gt_items, unique(out$item)), collapse=", "), "\n")
cat("extra items:", paste(setdiff(unique(out$item), gt_items), collapse=", "), "\n")
str(out)
