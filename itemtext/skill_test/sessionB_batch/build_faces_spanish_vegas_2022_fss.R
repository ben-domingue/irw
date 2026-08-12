table <- "faces_spanish_vegas_2022_fss"
instrument <- "Family Satisfaction Scale (FSS; Olson, 2000) -- FACES IV package, Spanish adolescent version"

# Item wording NOT recoverable: neither the target paper (Vegas et al., 2022,
# Psicologia: Reflexao e Critica, PMC9209570) nor the Harvard Dataverse record
# (WAF-blocked, could not inspect documentation files) discloses literal FSS
# item text. The paper's Table 4 labels items only as FSS1..FSS10 (factor
# loadings), no wording. FACES IV/FSS is a copyrighted instrument (Life
# Innovations / facesiv.com) requiring permission to use -- items are not
# freely published even where item counts/response scales are described.
# item_text is left NA for all items; see extraction_log for detail.

instructions <- ""  # not disclosed in the accessible source paper

# Confirmed directly from PMC full text (PMC9209570), Measures section:
# "the Family Satisfaction Scale (FSS) (Olson, 2000), with 10 items, with
# responses on a 5-point Likert-type scale: 1 (Very Dissatisfied) to 5 (Very
# Satisfied)." Only the two endpoints are labeled in the source; midpoints
# 2-4 are not given verbal anchors.
opts <- c("1"="Very Dissatisfied","2"="","3"="","4"="","5"="Very Satisfied")

gt <- readRDS(".gt_faces_spanish_vegas_2022_fss.rds")
gt_items <- sort(unique(gt$item))  # "FSS-item 1".."FSS-item 10"
stopifnot(length(gt_items) == 10)

rows <- list()
for (it in gt_items) {
  for (r in 1:5) {
    rows[[length(rows)+1]] <- data.frame(
      table = table,
      section_id = paste0(table, "_1"),
      item = it,
      instrument = instrument,
      instructions = instructions,
      section_prompt = "",
      item_text = NA_character_,
      correct_response = "",
      option_text = opts[[as.character(r)]],
      resp = r,
      stringsAsFactors = FALSE
    )
  }
}
out <- do.call(rbind, rows)
rownames(out) <- NULL
saveRDS(out, file = "candidate_faces_spanish_vegas_2022_fss.rds")

cat("N rows:", nrow(out), "\n")
cat("item match:", setequal(unique(out$item), gt_items), "\n")
cat("resp match:", setequal(sort(unique(out$resp)), sort(unique(gt$resp))), "\n")
str(out)
