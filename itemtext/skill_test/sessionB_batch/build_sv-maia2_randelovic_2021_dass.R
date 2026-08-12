setwd("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch")

gt <- readRDS(".gt_sv_maia2_randelovic_2021_dass.rds")
gt_items <- sort(unique(gt$item))   # DASS_1 .. DASS_21
gt_resp  <- sort(unique(gt$resp))   # 0 1 2 3
stopifnot(length(gt_items) == 21, length(gt_resp) == 4)

table_name <- "sv-maia2_randelovic_2021_dass"
instrument_name <- "Depression Anxiety Stress Scales - 21 Item (DASS-21; Lovibond & Lovibond, 1995), Serbian translation by Zoran Protulipac (official DASS site, maic.qut.edu.au mirror at www2.psy.unsw.edu.au/dass/Serbian/DASS21-SER.pdf)"

# NOTE ON SOURCE: this study's own OSF Method component (osf.io/vrhdu materials
# list, maia2_materials.txt) lists DASS-21 as "to be added" -- i.e. the study's
# own materials page does NOT contain a linked Serbian DASS-21 file. Per the
# task instructions, fell back to the official DASS instrument site's Serbian
# translation (Dr. Zoran Protulipac, published on www2.psy.unsw.edu.au/dass --
# the official home of DASS/DASS-21, mirrored under the maic.qut.edu.au domain
# historically). This is a general/official translation, not confirmed as the
# literal file used by this specific study, though it is THE standard Serbian
# DASS-21 translation and item count/order/response-scale (21 items, 0-3)
# match the live IRW data exactly. See extraction log.

# Literal Serbian item text transcribed from DASS21-SER.pdf (cached at
# itemtext/.cache/sv-maia2_randelovic_2021_dass/DASS21-SER.pdf), items 1-21,
# in the instrument's own printed order/numbering.
item_text_srp <- c(
  "1"  = "Bilo mi je teško da se smirim.",
  "2"  = "Primetio/la sam da mi se suše usta",
  "3"  = "Nisam imao/la nikakvo lepo osećanje",
  "4"  = "Imao/la sam poteškoća sa disanjem (recimo, osetio/la sam ubrzano disanje a nisam se fizički zamorio/la).",
  "5"  = "Primetio sam da mi je teško da ostvarim inicijativu i započnem bilo šta.",
  "6"  = "Preterano reagujem u nekim situacijama.",
  "7"  = "Osetio/la sam da se tresem (napr. tresle su mi se ruke).",
  "8"  = "Primetio/la sam da koristim dosta “nervozne energije” .",
  "9"  = "Bojao/la sam se situacija u kojima bih mogao/la da se uspanicim i napravim budalu od sebe",
  "10" = "Osećao/la sam da nemam čemu da se nadam.",
  "11" = "Primetio sam da se nerviram.",
  "12" = "Teško mi je da se opustim.",
  "13" = "Osećao/la sam se tužno i jadno.",
  "14" = "Nerviralo me je kada me nešto prekida u onome što radim",
  "15" = "Osećao/la sam da sam blizu panike.",
  "16" = "Ništa nije moglo da me zainteresuje",
  "17" = "Osećao/la sam se da kao osoba ne vredim mnogo.",
  "18" = "Bio/la sam jako osetljiv.",
  "19" = "Osetio/la sam rad srca iako se nisam fizički zamorio/la (napr. lupanje srca, ili osećaj da srce \"preskače\").",
  "20" = "Osećao/la sam se uplašeno bez razloga.",
  "21" = "Osećao sam da je život besmislen."
)
stopifnot(length(item_text_srp) == 21)

# Instructions: literal, from the top of DASS21-SER.pdf
instructions_text <- paste(
  "Pročitajte svaku od navedenih rečenica i zaokružite broj sa desne strane koji najbolje opisuje kako ste se",
  "osećali u zadnjih nedelju dana. Ne postoji tačan ili netačan odgovor. Nemojte se predugo zadržavati na",
  "pojedinim rečenicama."
)

# Response scale, literal from PDF: 0 Ni malo / 1 Pomalo ili ponekad /
# 2 U priličnoj meri ili često / 3 Uglavnom ili skoro uvek
option_text_srp <- c(
  "0" = "Ni malo",
  "1" = "Pomalo ili ponekad",
  "2" = "U priličnoj meri ili često",
  "3" = "Uglavnom ili skoro uvek"
)

# Subscale letter codes printed at right margin of the PDF (S=Stress,
# A=Anxiety, D=Depression) -- items are interleaved, not presented in blocks,
# so one section_id per item per SKILL.md guidance (no shared passage/testlet).
subscale_code <- c(
  "1"="S","2"="A","3"="D","4"="A","5"="D","6"="S","7"="A","8"="S","9"="A",
  "10"="D","11"="S","12"="S","13"="D","14"="S","15"="A","16"="D","17"="D",
  "18"="S","19"="A","20"="A","21"="D"
)

rows <- list()
for (item_val in gt_items) {
  num <- sub("DASS_", "", item_val)
  txt <- item_text_srp[[num]]
  for (r in gt_resp) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table_name,
      section_id = paste0(table_name, "_", num),
      item = item_val,
      instrument = instrument_name,
      instructions = instructions_text,
      section_prompt = "",
      item_text = txt,
      correct_response = "",
      option_text = option_text_srp[[as.character(r)]],
      resp = as.numeric(r),
      stringsAsFactors = FALSE
    )
  }
}

candidate <- do.call(rbind, rows)
# order by numeric item index, then resp
item_num <- as.integer(sub("DASS_", "", candidate$item))
candidate <- candidate[order(item_num, candidate$resp), ]
rownames(candidate) <- NULL

str(candidate)
cat("N item text NA:", sum(is.na(candidate$item_text)), "\n")
cat("items match:", identical(sort(unique(candidate$item)), gt_items), "\n")
cat("resp match:", identical(sort(unique(candidate$resp)), as.numeric(gt_resp)), "\n")

saveRDS(candidate, file = "candidate_sv-maia2_randelovic_2021_dass.rds")
cat("Saved.\n")
