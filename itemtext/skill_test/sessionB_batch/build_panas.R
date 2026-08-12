table <- "florida_twins_behavior_panas"
instrument <- "Positive and Negative Affect Schedule (PANAS; Watson, Clark, & Tellegen, 1988) -- self-report and parent-report forms, Florida Twin Project on Behavior and Environment (FTP-BE)"

self_instructions <- "Below are a number of words that describe different feelings and emotions. Read each word and then circle the appropriate number under the correct column next to that word. Mark each word for the degree you feel this way, that is, for how you feel in general."
parent_instructions <- "Below are a number of words that describe different feelings and emotions. Read each word and then circle the appropriate number under the correct column next to that word. Mark each word for the degree your child feels this way, that is, for how your child feels in general. Please fill this out for each child."

# Literal 20-item PANAS word list and order as printed in the codebook (Youth Booklet
# "PANAS" section and Parent Booklet "PANAS - Parent" section use the identical word
# list/order; only the framing sentence in the instructions differs self vs. parent).
words <- c(
"1"="Interested",
"2"="Distressed",
"3"="Excited",
"4"="Upset",
"5"="Strong",
"6"="Guilty",
"7"="Scared",
"8"="Hostile",
"9"="Enthusiastic",
"10"="Proud",
"11"="Irritable",
"12"="Alert",
"13"="Ashamed",
"14"="Inspired",
"15"="Nervous",
"16"="Determined",
"17"="Attentive",
"18"="Jittery",
"19"="Active",
"20"="Afraid"
)

# Response scale printed as the literal column headers above the 1-5 circled numbers.
opts <- c(
"1"="Very Slightly or Not at All",
"2"="A Little",
"3"="Moderately",
"4"="Quite a Bit",
"5"="Extremely"
)

gt <- readRDS(".gt_florida_twins_behavior_panas.rds")
gt_items <- sort(unique(gt$item))

rows <- list()
for (n in names(words)) {
  it <- paste0("panas", n)
  if (!(it %in% gt_items)) next
  sec <- paste0(table, "_self")
  for (r in 1:5) {
    rows[[length(rows)+1]] <- data.frame(
      table=table, section_id=sec, item=it, instrument=instrument,
      instructions=self_instructions, section_prompt="",
      item_text=words[[n]], correct_response="", option_text=opts[[as.character(r)]], resp=r,
      stringsAsFactors=FALSE)
  }
}
for (n in names(words)) {
  it <- paste0("panas_", n)
  if (!(it %in% gt_items)) next
  sec <- paste0(table, "_parent")
  for (r in 1:5) {
    rows[[length(rows)+1]] <- data.frame(
      table=table, section_id=sec, item=it, instrument=instrument,
      instructions=parent_instructions, section_prompt="",
      item_text=words[[n]], correct_response="", option_text=opts[[as.character(r)]], resp=r,
      stringsAsFactors=FALSE)
  }
}
out <- do.call(rbind, rows)
rownames(out) <- NULL
saveRDS(out, file="candidate_florida_twins_behavior_panas.rds")
cat("N rows:", nrow(out), "\n")
cat("item match:", setequal(unique(out$item), gt_items), "\n")
cat("resp match:", setequal(unique(out$resp), sort(unique(gt$resp))), "\n")
cat("missing:", paste(setdiff(gt_items, unique(out$item)), collapse=", "), "\n")
