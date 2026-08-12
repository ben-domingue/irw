# Build candidate_oxfordcovid_xue_2024_mfq.rds
# Source: OSF 4b85w "data paper/codebooks/raw_data_codebook.pdf" (REDCap raw data
# codebook for the Oxford ARC study), section "Instrument: MFQ-26 (mfq26)",
# cached at .cache/oxfordcovid_xue_2024_mfq/raw_data_codebook.pdf (+ .txt via pdftotext).
# OCR ligature artifacts ("di erent" -> "different", "con dent" -> "confident",
# "nd" -> "find", "di culties" -> "difficulties") corrected by hand against context.

item_ids <- sprintf("mfq_26_%d", 1:20)

item_text <- c(
  "I'm optimistic about the future",
  "I am much more open to change than my friends.",
  "I'm good at getting used to different situations",
  "I sometimes do unusual things",
  "I am confident that I can adapt to new situations.",
  "I know that things will always change - it's just the way life is",
  "Once I start something I find it fairly easy to stop if I have to",
  "When I encounter difficulties, I try lots of different ways to find a solution",
  "I am good at switching quickly from one thought to another.",
  "I am good at coping with the unexpected",
  "I find it exciting when things are changing rather than getting stressed",
  "I sometimes think in ways that are very different from other people",
  "I am keen to learn from other people",
  "I am good at juggling different ideas at the same time.",
  "I find it easy to balance my long-term goals with what I want to do in the short-term.",
  "I have learned that some things I do work well in some situations but not in others.",
  "Most things in life are not black and white - they are much more complicated.",
  "I am very good at noticing when people's mood changes",
  "I am able to learn from my mistakes.",
  "I am good at changing my mind when I can see that it works for others"
)

stopifnot(length(item_ids) == length(item_text))

instructions_txt <- "Please rate the degree to which you agree or disagree with each of the questions on the scale below. Think carefully about each question and answer them honestly."

instrument_txt <- "Mental Flexibility Questionnaire (MFQ) - trait version; REDCap instrument name \"MFQ-26\"; developed by the study team for the Oxford Achieving Resilience during COVID-19 (ARC) study"

resp_levels <- 1:6
option_levels <- c(
  "Strongly Disagree",
  "Disagree",
  "Slightly Disagree",
  "Slightly Agree",
  "Agree",
  "Strongly Agree"
)

table_name <- "oxfordcovid_xue_2024_mfq"
section_id_val <- paste0(table_name, "_1")

rows <- do.call(rbind, lapply(seq_along(item_ids), function(i) {
  data.frame(
    table = table_name,
    section_id = section_id_val,
    item = item_ids[i],
    instrument = instrument_txt,
    instructions = instructions_txt,
    section_prompt = "",
    item_text = item_text[i],
    correct_response = "",
    option_text = option_levels,
    resp = resp_levels,
    stringsAsFactors = FALSE
  )
}))

rownames(rows) <- NULL

saveRDS(rows, file = "candidate_oxfordcovid_xue_2024_mfq.rds")
cat("Wrote", nrow(rows), "rows\n")
