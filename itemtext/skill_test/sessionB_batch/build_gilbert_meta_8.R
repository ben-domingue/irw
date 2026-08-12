## Build candidate_gilbert_meta_8.rds

gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_gilbert_meta_8.rds")

items <- sort(unique(gt$item))
resps <- sort(unique(gt$resp))
stopifnot(length(items) == 29, setequal(resps, c(0,1)))

instrument_str <- paste0(
  "Grade 3 domain-specific (science) reading comprehension \"transfer\" assessment ",
  "(researcher-designed, MORE study) -- 29 multiple-choice items across three ",
  "reading passages (near-, mid-, and far-transfer) measuring students' ability to ",
  "read and understand main ideas and scientific concepts; Kim, Gilbert, Relyea, ",
  "Rich, Scherer, Burkhauser, & Tvedt (2024), Developmental Psychology, ",
  "'Time to Transfer: Long-Term Effects of a Sustained and Spiraled Content ",
  "Literacy Intervention in the Elementary Grades.'"
)

rows <- list()
for (it in items) {
  for (r in resps) {
    rows[[length(rows) + 1]] <- data.frame(
      table            = "gilbert_meta_8",
      section_id       = paste0("gilbert_meta_8_", it),
      item             = it,
      instrument       = instrument_str,
      instructions     = "",
      section_prompt   = "",
      item_text        = "",
      correct_response = "",
      option_text      = "",
      resp             = r,
      stringsAsFactors = FALSE
    )
  }
}
out <- do.call(rbind, rows)

## type check vs ground truth
stopifnot(identical(sort(unique(out$item)), sort(unique(gt$item))))
stopifnot(setequal(unique(out$resp), unique(gt$resp)))

saveRDS(out, "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_gilbert_meta_8.rds")
cat("Wrote candidate_gilbert_meta_8.rds:", nrow(out), "rows,", length(items), "items x", length(resps), "resp values\n")
