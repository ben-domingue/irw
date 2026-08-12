items_pl <- c(
"1"="Jeśli dziewczyna zostanie zgwałcona kiedy jest pijana, to jest ona przynajmniej trochę odpowiedzialna za to, co się stało.",
"2"="Kiedy dziewczyny idą na przyjęcia ubrane w wyzywające ubrania, same proszą się o problemy.",
"3"="Jeśli dziewczyna idzie do pokoju sama z chłopakiem, kiedy są na przyjęciu, to jest to jej wina, jeśli zostanie zgwałcona.",
"4"="Jeśli dziewczyna zachowuje się jak zdzira, w końcu wpakuje się w kłopoty.",
"5"="Kiedy faceci gwałcą, to zazwyczaj jest to spowodowane ich silną żądzą seksu.",
"6"="Faceci zazwyczaj nie zamierzają zmuszać dziewczyny do seksu, ale czasami nie mogą się pohamować seksualnie.",
"7"="Gwałt ma miejsce, kiedy popęd seksualny mężczyzny wymyka się spod kontroli.",
"8"="Kiedy facet jest pijany, może kogoś zgwałcić nieumyślnie.",
"9"="Jeśli dwie osoby są pijane - to nie może być gwałt.",
"10"="Nie powinno uznawać się za gwałt zbliżenia, do którego doszło kiedy facet był pijany i nie zdawał sobie sprawy z tego, co robił.",
"11"="Jeśli dziewczyna nie stawia fizycznego oporu – nawet jeśli protestuje werbalnie – to nie powinno się tego uznawać za gwałt.",
"12"="Jeśli dziewczyna nie odpowiada na atak siłą fizyczną, nie można tak naprawdę mówić o gwałcie.",
"13"="Często dziewczyny, które twierdzą, że zostały zgwałcone, zgodziły się na seks, ale później tego żałowały.",
"14"="Oskarżenia o gwałt są często używane jako sposób na odegranie się na facetach.",
"15"="Dziewczyny, które twierdzą, że zostały zgwałcone, często prowokowały faceta, a potem miały wyrzuty sumienia.",
"16"="Często dziewczyny, które twierdzą, że zostały zgwałcone, po prostu mają problemy emocjonalne.",
"17"="Jeśli oskarżony gwałciciel nie ma broni, tak naprawdę nie można nazwać tego gwałtem.",
"18"="Dziewczyny, które zostaną przyłapane na zdradzie, czasem twierdzą, że zostały zgwałcone.",
"19"="Jeśli dziewczyna nie powie nie, to nie może twierdzić, że została zgwałcona."
)

table <- "lys_2020_rape_2_rma_pre"
item_ids <- paste0("rma_pre", 1:19)
item_text_map <- setNames(unname(items_pl[as.character(1:19)]), item_ids)

instrument <- "Polish Updated Illinois Rape Myth Acceptance Scale (Debowska et al. 2015 Polish translation of McMahon & Farmer 2011)"
instructions <- "19 items scored on a 5-point Likert scale from 1 = \"strongly disagree\" to 5 = \"strongly agree\"; higher score = higher rape myth acceptance."
section_id <- paste0(table, "_1")
section_prompt <- ""

resp_vals <- 1:5
option_text_map <- c("1"="zdecydowanie się nie zgadzam (strongly disagree)","2"="","3"="","4"="","5"="zdecydowanie się zgadzam (strongly agree)")

rows <- list()
for (it in item_ids) {
  for (r in resp_vals) {
    rows[[length(rows)+1]] <- data.frame(
      table = table,
      section_id = section_id,
      item = it,
      instrument = instrument,
      instructions = instructions,
      section_prompt = section_prompt,
      item_text = item_text_map[[it]],
      correct_response = "",
      option_text = option_text_map[[as.character(r)]],
      resp = r,
      stringsAsFactors = FALSE
    )
  }
}
d <- do.call(rbind, rows)
str(d)
saveRDS(d, "candidate_lys_2020_rape_2_rma_pre.rds")
cat("N rows:", nrow(d), "\n")
