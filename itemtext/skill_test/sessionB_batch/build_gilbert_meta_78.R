gt <- readRDS(".gt_gilbert_meta_78.rds")
items <- sort(unique(gt$item))
stopifnot(length(items) == 189)
# NB: items are not a contiguous 001-189 block -- live data runs ppvt_001..ppvt_192
# with 3 gaps (ppvt_181, ppvt_182, ppvt_184 absent), all zero-padded to 3 digits.
# Use the actual observed set rather than assuming contiguity.
resp_vals <- sort(unique(gt$resp))
stopifnot(identical(resp_vals, c(0L, 1L)))

instrument_name <- "Peabody Picture Vocabulary Test, Fourth Edition (PPVT-4; Dunn & Dunn, 2007)"

instructions_txt <- paste0(
  "Standardized, individually administered receptive vocabulary test. The examiner ",
  "says a stimulus word aloud and the child selects, from four picture plates shown ",
  "together on a page, the one picture that best represents the word's meaning. Items ",
  "are presented in sets of increasing difficulty following the test's basal/ceiling ",
  "administration rules. Each item was scored dichotomously (1 = correct picture ",
  "selected, 0 = incorrect/no response)."
)

n <- 189
df <- data.frame(
  table = rep("gilbert_meta_78", n * 2),
  section_id = rep(paste0("gilbert_meta_78_", seq_len(n)), each = 2),
  item = rep(items, each = 2),
  instrument = rep(instrument_name, n * 2),
  instructions = rep(instructions_txt, n * 2),
  section_prompt = rep(NA_character_, n * 2),
  item_text = rep(NA_character_, n * 2),
  correct_response = rep(NA_character_, n * 2),
  option_text = rep(c("Incorrect (wrong or no picture selected)", "Correct (target picture selected)"), n),
  resp = rep(c(0, 1), n),
  stringsAsFactors = FALSE
)

stopifnot(nrow(df) == 378)
stopifnot(identical(sort(unique(df$item)), items))
stopifnot(identical(sort(unique(df$resp)), c(0, 1)))

saveRDS(df, "candidate_gilbert_meta_78.rds")
cat("Wrote candidate_gilbert_meta_78.rds with", nrow(df), "rows\n")
str(df)
