library(dplyr)

table_id <- "wang_onlineriskexp_2025"

instrument_txt <- "Online Risk Exposure Scale (Wisniewski et al., 2015, English original; adapted for Chinese college students by Zhang et al., 2023, Chinese Journal of Clinical Psychology, 31(2), 392-395; as administered in Wang et al., 2025)"

instructions_txt <- "Participants rate each item on a 5-point Likert scale ranging from 1 (none) to 5 (a lot), indicating the extent of their exposure to online risks."

subscales <- list(
  FXXL = list(n = 3, section_prompt = "Information breaches"),
  FXQF = list(n = 4, section_prompt = "Cyberbullying"),
  FXXY = list(n = 4, section_prompt = "Online sexual solicitations"),
  FXJC = list(n = 5, section_prompt = "Exposure to explicit content")
)

rows <- list()
for (prefix in names(subscales)) {
  info <- subscales[[prefix]]
  section_id <- paste0(table_id, "_", tolower(prefix))
  for (i in seq_len(info$n)) {
    item_code <- paste0(prefix, i)
    for (resp in 1:5) {
      option_text <- switch(as.character(resp),
        "1" = "none",
        "5" = "a lot",
        "")
      rows[[length(rows) + 1]] <- data.frame(
        table = table_id,
        section_id = section_id,
        item = item_code,
        instrument = instrument_txt,
        instructions = instructions_txt,
        section_prompt = info$section_prompt,
        item_text = "",
        correct_response = "",
        option_text = option_text,
        resp = resp,
        stringsAsFactors = FALSE
      )
    }
  }
}

d <- bind_rows(rows)
str(d)

gt <- readRDS(".gt_wang_onlineriskexp_2025.rds")
stopifnot(identical(sort(unique(d$item)), sort(unique(gt$item))))
stopifnot(identical(sort(unique(d$resp)), sort(unique(gt$resp))))
cat("VALIDATION OK: item and resp sets match ground truth exactly.\n")

saveRDS(d, "candidate_wang_onlineriskexp_2025.rds")
