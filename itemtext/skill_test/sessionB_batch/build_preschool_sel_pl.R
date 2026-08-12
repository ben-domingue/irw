library(dplyr)

table_id <- "preschool_sel_pl"
sec <- "preschool_sel_pl_1"
instrument_name <- "PreLAS 2000 (Duncan & De Avila, 1998) -- Simon Says and Art Show subtests, English and Spanish forms"
instructions_txt <- "The preLAS tests receptive language, listening comprehension, and expressive language. Two subtests were used: Simon Says and Art Show."

# item, item_text, correct_response (text of the "1" anchor), option_text_1 (label for resp=1), option_text_0 (label for resp=0)
items <- tribble(
  ~item,           ~item_text,                                              ~opt1,                              ~opt0,
  # English Simon Says
  "pl_ss1_t1",  "Simon says touch your ear",                                "correct",                          "incorrect",
  "pl_ss2_t1",  "Simon says point to the door",                             "correct",                          "incorrect",
  "pl_ss3_t1",  "Simon says lift one foot",                                 "correct",                          "incorrect",
  "pl_ss4_t1",  "Simon says open your hand",                                "correct",                          "incorrect",
  "pl_ss5_t1",  "Simon says pick up the paper",                             "correct",                          "incorrect",
  "pl_ss6_t1",  "Simon says turn the paper over",                          "correct",                          "incorrect",
  "pl_ss7_t1",  "Simon says put one hand on top of the other",             "correct",                          "incorrect",
  "pl_ss8_t1",  "Simon says knock on the table",                            "correct",                          "incorrect",
  "pl_ss9_t1",  "Simon says point to the middle of the paper",             "correct",                          "incorrect",
  "pl_ss10_t1", "Simon says put your feet together",                       "correct",                          "incorrect",
  # English Art Show
  "pl_as1_t1",  "What is this? (Apple)",                                   "apple",                            "other",
  "pl_as2_t1",  "What is this? (Frog/toad)",                               "frog, toad",                       "other",
  "pl_as3_t1",  "What is this? (Pig)",                                     "pig",                              "other",
  "pl_as4_t1",  "What is this? (Bee)",                                     "bee",                              "other",
  "pl_as5_t1",  "What is this? (Book)",                                    "book",                             "other",
  "pl_as6_t1",  "What can you do with it? (Book)",                         "read, look at it",                 "other",
  "pl_as7_t1",  "What is this? (Cup)",                                     "cup",                              "other",
  "pl_as8_t1",  "What can you do with it? (Drink)",                        "drink",                            "other",
  "pl_as9_t1",  "What is this? (Knife)",                                   "knife",                            "other",
  "pl_as10_t1", "What can you do with it? (Knife)",                        "cut, eat",                         "other",
  # Spanish Simon Says (Simon Dice)
  "plsp_ss1_t1",  "Simón dice tócate la cara",                    "toca la cara",                     "otro",
  "plsp_ss2_t1",  "Simón dice baja la mano",                           "baja la mano",                     "otro",
  "plsp_ss3_t1",  "Simón dice dame el lápiz",                     "dale el lápiz",               "otro",
  "plsp_ss4_t1",  "Simón dice esconde el lápiz debajo del papel", "esconde el lápiz debajo del papel", "otro",
  "plsp_ss5_t1",  "Simón dice levanta la mano",                        "levanta la mano",                  "otro",
  "plsp_ss6_t1",  "Simón dice mueve la mano",                          "mueve la mano",                    "otro",
  "plsp_ss7_t1",  "Simón dice muéstrame una cara alegre",         "te muestra una cara alegre",       "otro",
  "plsp_ss8_t1",  "Simón dice muéstrame una cara triste",         "te muestra una cara triste",       "otro",
  "plsp_ss9_t1",  "Simón dice levántate",                         "él/ella se levanta",          "otro",
  # NOTE: codebook also lists plsp_ss10_t1 "Simón dice siéntate" (correct="él/ella se sienta")
  # but that item is NOT present in ground truth (irw_fetch) for this table -- omitted per
  # "don't force a match"; see extraction log discrepancy note.
  # Spanish Art Show (Muestra de Arte)
  "plsp_as1_t1",  "¿Qué es esto? (mariposa)",                     "mariposa",                         "otro",
  "plsp_as2_t1",  "¿Qué es esto? (rana, sapo, coquí)",       "rana",                             "otro",
  "plsp_as3_t1",  "¿Qué es esto? (libro)",                        "libro",                            "otro",
  "plsp_as4_t1",  "¿Qué puedes hacer con esto? (leer, mirar)",    "leer, mirar",                      "otro",
  "plsp_as5_t1",  "¿Qué es esto? (lápiz)",                   "lapíz",                       "otro",
  "plsp_as6_t1",  "¿Qué puedes hacer con esto? (escribir, dibujar)", "escribir, dibujar",             "otro",
  "plsp_as7_t1",  "¿Qué es esto? (mesa)",                         "mesa",                             "otro",
  "plsp_as8_t1",  "¿Qué puedes hacer con esto? (poner(la), comer, escribir, sentar(me), etc.)", "poner(la), comer, escribir, sentar(me), etc.", "otro",
  "plsp_as9_t1",  "¿Qué es esto? (taza, vaso, pocilla)",          "taza, vaso, pocillo",              "otro",
  "plsp_as10_t1", "¿Qué puedes hacer con esto? (tomar, beber)",   "tomar, beber",                     "otro"
)

stopifnot(nrow(items) == 39)
stopifnot(!"plsp_ss10_t1" %in% items$item)

long <- items %>%
  rowwise() %>%
  do({
    it <- .
    data.frame(
      table = table_id,
      section_id = sec,
      item = it$item,
      instrument = instrument_name,
      instructions = instructions_txt,
      section_prompt = "",
      item_text = it$item_text,
      correct_response = "1",
      option_text = c(it$opt1, it$opt0),
      resp = c(1L, 0L),
      stringsAsFactors = FALSE
    )
  }) %>%
  ungroup() %>%
  as.data.frame()

cand <- long[, c("table","section_id","item","instrument","instructions",
                  "section_prompt","item_text","correct_response","option_text","resp")]

# Validate against ground truth
gt <- readRDS("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/.gt_preschool_sel_pl.rds")
gt_items <- sort(unique(gt$item))
gt_resp  <- sort(unique(gt$resp))

cand_items <- sort(unique(cand$item))
cand_resp  <- sort(unique(cand$resp))

cat("items match:", identical(gt_items, cand_items), "\n")
cat("resp match:", identical(as.numeric(gt_resp), as.numeric(cand_resp)), "\n")

saveRDS(cand, "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_preschool_sel_pl.rds")
str(cand)
