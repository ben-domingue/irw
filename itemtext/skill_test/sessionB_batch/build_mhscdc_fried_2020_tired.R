table_id <- "mhscdc_fried_2020_tired"
instrument <- "Chalder Fatigue Scale"

item_text_map <- c(
  item_1  = "Do you have problems with tiredness?",
  item_2  = "Do you need to rest more?",
  item_3  = "Do you feel sleepy or drowsy?",
  item_4  = "Do you have problems starting things?",
  item_5  = "Do you lack energy?",
  item_6  = "Do you have less strength in your muscles?",
  item_7  = "Do you feel weak?",
  item_8  = "Do you have difficulties concentrating?",
  item_9  = "Do you start things without difficulty but get weak as you go on?",
  item_10 = "Do you think as clearly as usual?"
)

items <- paste0("item_", 1:10)

option_map <- c(
  `1` = "Less than usual",
  `2` = "No more than usual",
  `3` = "More than usual",
  `4` = "Much more than usual"
)

rows <- list()
i <- 1
for (it in items) {
  for (r in 1:4) {
    rows[[i]] <- data.frame(
      table = table_id,
      section_id = paste0(table_id, "_1"),
      item = it,
      instrument = instrument,
      instructions = "",
      section_prompt = "",
      item_text = item_text_map[[it]],
      correct_response = "",
      option_text = option_map[[as.character(r)]],
      resp = as.integer(r),
      stringsAsFactors = FALSE
    )
    i <- i + 1
  }
}
out <- do.call(rbind, rows)
rownames(out) <- NULL
str(out)
saveRDS(out, file = "candidate_mhscdc_fried_2020_tired.rds")

# Validation against cached ground truth
gt <- readRDS(".gt_mhscdc_fried_2020_tired.rds")
cat("item match:", setequal(unique(out$item), unique(gt$item)), "\n")
cat("resp match:", setequal(unique(out$resp), unique(gt$resp)), "\n")
print(sort(unique(gt$item)))
print(sort(unique(out$item)))
print(sort(unique(gt$resp)))
print(sort(unique(out$resp)))
