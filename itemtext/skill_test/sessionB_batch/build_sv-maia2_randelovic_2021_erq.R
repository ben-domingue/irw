setwd("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch")

gt <- readRDS(".gt_sv_maia2_randelovic_2021_erq.rds")
gt_items <- sort(unique(gt$item))   # ERQ_1 ... ERQ_10 (lexicographic order fine, sourced from doc by number)
gt_resp  <- sort(unique(gt$resp))   # 1 2 3 4 5
stopifnot(length(gt_items) == 10, length(gt_resp) == 5)

table_name <- "sv-maia2_randelovic_2021_erq"
instrument_name <- "Emotion Regulation Questionnaire (ERQ; Gross & John, 2003), Serbian translation (Knezevic, 2021), REPOPSI record osf.io/fdpc2"

instructions_text <- paste(
  "Želimo da vam postavimo neka pitanja o vašem emotivnom životu, konkretno o tome kako",
  "kontrolišete svoje emocije (to jest, regulišete ih i upravljate njima). Pitanja u nastavku",
  "uključuju dva odvojena aspekta vašeg emotivnog života. Jedan je vaše emotivno iskustvo,",
  "odnosno kako se vi osećate \"iznutra\". Drugi je vaša emotivna izražajnost, odnosno kako",
  "pokazujete svoje emocije kada pričate, gestikulirate i ponašate se na različite načine.",
  "Iako vam neka od narednih pitanja mogu delovati slično jedna drugim, ona se razlikuju na",
  "važne načine."
)

# Serbian item text, verbatim from erq_eng_srp.odt (Translation/Adaptation block), items 1-10
item_text_srp <- c(
  "1" = "Kada želim da osećam pozitivnije emocije (kao što se uživanje ili zabava), promenim ono o čemu razmišljam.",
  "2" = "Svoje emocije držim za sebe.",
  "3" = "Kada želim da loše emocije (kao što su tuga ili bes) osećam u manjoj meri, promenim ono o čemu razmišljam.",
  "4" = "Kada osećam pozitivne emocije, pazim da ih ne ispoljim.",
  "5" = "Kada sam suočen/a sa stresnom situacijom, trudim se da o njoj razmišljam na način koji će mi pomoći da ostanem smiren/a.",
  "6" = "Kontrolišem svoje emocije tako što ih ne ispoljavam.",
  "7" = "Kada želim da se osećam pozitivnije, menjam način razmišljanja o datoj situaciji.",
  "8" = "Kontrolišem svoje emocije tako što promenim način na koji mislim o situaciji u kojoj sam.",
  "9" = "Kada osećam negativne emocije, postaram se da ih ne ispoljim.",
  "10" = "Kada želim da se osećam manje loše, menjam način na koji mislim o situaciji u kojoj sam."
)

section_id_val <- paste0(table_name, "_1")

rows <- list()
for (item_val in gt_items) {
  num <- sub("ERQ_", "", item_val)
  txt <- item_text_srp[[num]]
  for (r in gt_resp) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table_name,
      section_id = section_id_val,
      item = item_val,
      instrument = instrument_name,
      instructions = instructions_text,
      section_prompt = "",
      item_text = txt,
      correct_response = "",
      option_text = NA_character_,   # response-scale wording NOT recovered for this 5-pt variant; see log
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
cat("items match:", identical(sort(unique(candidate$item)), gt_items), "\n")
cat("resp match:", identical(sort(unique(candidate$resp)), as.numeric(gt_resp)), "\n")

saveRDS(candidate, file = "candidate_sv-maia2_randelovic_2021_erq.rds")
cat("Saved.\n")
