setwd("/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch")

gt <- readRDS(".gt_sv_maia2_randelovic_2021_maia.rds")
gt_items <- sort(unique(gt$item))   # MAIA2_1 .. MAIA2_37
gt_resp  <- sort(unique(gt$resp))   # 0 1 2 3 4 5
stopifnot(length(gt_items) == 37, length(gt_resp) == 6)

table_name <- "sv-maia2_randelovic_2021_maia"
instrument_name <- "Multidimensional Assessment of Interoceptive Awareness, Version 2 (MAIA-2; Mehling et al., 2018), Serbian translation, REPOPSI record osf.io/tpn6u"

instructions_text <- "U nastavku je niz tvrdnji. Molimo Vas da označite koliko često se svaka od njih uopšteno odnosi na Vas u svakodnevnom životu. Označite po jedan broj u svakom redu."

# Serbian item text, verbatim from maia2_sr_eng_srp.pdf (Instrument in full - Translation block), items 1-37
item_text_srp <- c(
  "1"  = "Kada sam napet/a, primećujem na kojim mestima je napetost locirana u telu.",
  "2"  = "Primećujem kada mi je nelagodno u telu.",
  "3"  = "Primećujem u kom delu tela osećam ugodnost.",
  "4"  = "Primećujem promene u svom disanju, na primer da li se usporava ili ubrzava.",
  "5"  = "Ignorišem fizičke napetosti ili nelagodnosti dok ne postanu ozbiljnije.",
  "6"  = "Skrećem sebi pažnju sa osećaja nelagodnosti.",
  "7"  = "Kada osetim bol ili nelagodnost, pokušavam da izdržim dok ne prođe.",
  "8"  = "Trudim se da ignorišem bol.",
  "9"  = "Guram od sebe osećaj nelagode tako što se fokusiram na nešto.",
  "10" = "Kad osetim neprijatne telesne senzacije, okupiram sebe nečim drugim da ne bih morao/la da ih osećam.",
  "11" = "Uznemirim se kada osetim fizički bol.",
  "12" = "Ako osetim bilo kakvu nelagodnost, počinjem da brinem da nešto nije u redu.",
  "13" = "Mogu da opazim neprijatnu telesnu senzaciju, a da se ne zabrinem zbog toga.",
  "14" = "Mogu da ostanem smiren/a i da ne brinem kada osećam nelagodnost ili bol.",
  "15" = "Kada mi je nelagodno ili me nešto boli, to ne mogu da izbacim iz glave.",
  "16" = "Mogu da obratim pažnju na disanje, a da me ne ometaju stvari koje se događaju oko mene.",
  "17" = "Mogu da zadržim svest o senzacijama u telu čak i kada se mnogo toga dešava oko mene.",
  "18" = "Kada razgovaram s nekim, mogu da obratim pažnju na držanje svog tela.",
  "19" = "Ako sam ometen/a, mogu ponovo da usmerim svest na svoje telo.",
  "20" = "Mogu da preusmerim pažnju sa misli na osećaj svog tela.",
  "21" = "Mogu da zadržim svest o celom telu, čak i kada u nekom delu osećam bol ili nelagodnost.",
  "22" = "U stanju sam da se svesno usredsredim na svoje telo kao celinu.",
  "23" = "Primećujem kako se moje telo menja kada sam ljut/a.",
  "24" = "Kada nešto nije u redu u mom životu, mogu to da osetim u svom telu.",
  "25" = "Primećujem da se moje telo drugačije oseća nakon umirujućeg doživljaja.",
  "26" = "Primećujem da moje disanje postaje slobodno i lagano kada se osećam ugodno.",
  "27" = "Primećujem kako se moje telo menja kada se osećam srećno / radosno.",
  "28" = "Kada se osećam preplavljeno, mogu da nađem mirno mesto u sebi.",
  "29" = "Kada usmerim svest na svoje telo, imam osećaj mira.",
  "30" = "Mogu disanjem da umanjim napetost.",
  "31" = "Kada sam preokupiran/a mislima, mogu da umirim svoj um usmeravanjem pažnje na telo / disanje.",
  "32" = "Osluškujem informacije iz tela o svom emotivnom stanju.",
  "33" = "Kada sam uznemiren/a, bez žurbe istražujem kako se moje telo oseća.",
  "34" = "Osluškujem svoje telo da bi mi reklo šta da radim.",
  "35" = "U svom telu sam „kao kod kuće“.",
  "36" = "Osećam svoje telo kao sigurno mesto.",
  "37" = "Verujem svojim telesnim senzacijama."
)

# Subscale (section) groupings per the instrument's official scoring key
subscale_map <- list(
  Noticing            = 1:4,
  `Not-Distracting`   = 5:10,
  `Not-Worrying`      = 11:15,
  `Attention Regulation` = 16:22,
  `Emotional Awareness`  = 23:27,
  `Self-Regulation`      = 28:31,
  `Body Listening`       = 32:34,
  Trusting               = 35:37
)
num_to_section <- character(37)
for (sub in names(subscale_map)) {
  nums <- subscale_map[[sub]]
  section_label <- paste0(table_name, "_", gsub("[^A-Za-z]", "", sub))
  num_to_section[nums] <- section_label
}

# Response scale: 6-point, only endpoints labeled in the source (0 - nikad ["never"], 5 - uvek ["always"])
option_map <- c(
  "0" = "nikad",
  "1" = NA_character_,
  "2" = NA_character_,
  "3" = NA_character_,
  "4" = NA_character_,
  "5" = "uvek"
)

rows <- list()
for (item_val in gt_items) {
  num <- as.integer(sub("MAIA2_", "", item_val))
  txt <- item_text_srp[[as.character(num)]]
  sec <- num_to_section[num]
  for (r in gt_resp) {
    rows[[length(rows) + 1]] <- data.frame(
      table = table_name,
      section_id = sec,
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
cat("items match:", identical(sort(unique(candidate$item)), gt_items), "\n")
cat("resp match:", identical(sort(unique(candidate$resp)), as.numeric(gt_resp)), "\n")

saveRDS(candidate, file = "candidate_sv-maia2_randelovic_2021_maia.rds")
cat("Saved.\n")
