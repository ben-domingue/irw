library(jsonlite)

setwd("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch")

gt <- readRDS(".gt_sv_maia2_randelovic_2021_hexaco60.rds")
gt_items <- sort(unique(gt$item))
nums <- as.integer(sub("HEXACO_60_", "", gt_items))
stopifnot(length(gt_items) == 60)

items100 <- fromJSON("/home/ben/Dropbox/projects/irw/src/itemtext/.cache/sv-maia2_randelovic_2021_hexaco60/serbian_100_items.json")
# items100 is a named list, names are "1".."100"

table_name <- "sv-maia2_randelovic_2021_hexaco60"
instrument_name <- "HEXACO-PI-R (60-item form / HEXACO-60), Serbian self-report translation (hexaco.org)"

instructions_text <- paste(
  "Molimo Vas, pažljivo pročitajte sve instrukcije pre nego što počnete sa radom.",
  "Ovaj upitnik sadrži 60 tvrdnji. Molimo Vas, pažljivo pročitajte svaku tvrdnju i zaokružite jedan odgovor u meri u kojoj se tvrdnja na Vas odnosi ili ne odnosi.",
  "Ovde nema tačnih i pogrešnih odgovora, pa zato ne treba da budete nekakav stručnjak da biste popunili ovaj upitnik. Opišite sebe što iskrenije i iznesite svoje mišljenje što je moguće tačnije.",
  "ne treba da previše dugo mislite o značenju svake tvrdnje. najbolje ćete učiniti ako izaberete onaj odgovor koji vam, pošto ste razumeli šta tvrdnja znači, prvo padne na pamet."
)

section_id_val <- paste0(table_name, "_1")

option_map <- c(
  "1" = "potpuno netačno",
  "2" = "uglavnom netačno",
  "3" = "nisam siguran",
  "4" = "uglavnom tačno",
  "5" = "potpuno tačno"
)

rows <- list()
for (i in seq_along(gt_items)) {
  item_val <- gt_items[i]
  num <- nums[i]
  txt <- items100[[as.character(num)]]
  if (is.null(txt)) txt <- NA_character_
  for (r in 1:5) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table_name,
      section_id = section_id_val,
      item = item_val,
      instrument = instrument_name,
      instructions = instructions_text,
      section_prompt = "",
      item_text = txt,
      correct_response = "",
      option_text = option_map[[as.character(r)]],
      resp = as.numeric(r),
      stringsAsFactors = FALSE
    )
  }
}

candidate <- do.call(rbind, rows)
candidate <- candidate[order(match(candidate$item, gt_items), candidate$resp), ]
rownames(candidate) <- NULL

str(candidate)
cat("N item text NA:", sum(is.na(candidate$item_text)), "\n")

saveRDS(candidate, file = "candidate_sv-maia2_randelovic_2021_hexaco60.rds")
cat("Saved.\n")
