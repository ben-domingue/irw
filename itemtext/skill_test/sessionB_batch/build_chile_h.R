library(dplyr)

table_id <- "chile_2023_social-welfare-survey_h"
instrument_txt <- "Encuesta de Bienestar Social (EBS) 2023 -- Modulo H: Seguridad (Ministerio de Desarrollo Social y Familia / Instituto Nacional de Estadisticas, Chile)"
instructions_txt <- "Ahora, le hare algunas preguntas respecto a la seguridad publica."

items <- tribble(
  ~section_id, ~item,  ~item_text,
  "h1", "h1",   "En los ultimos 12 meses, ¿cuantas veces ha sido victima de un delito, como asalto o robo al interior o fuera de su hogar?",
  "h2", "h2_a", "Cuando esta en plazas, parques o espacios naturales",
  "h2", "h2_b", "Caminando de dia por calles o caminos",
  "h2", "h2_c", "Caminando de noche por calles o caminos",
  "h2", "h2_d", "Cuando esta dentro de su vivienda o predio",
  "h3", "h3_a", "¿Dejo de salir de dia?",
  "h3", "h3_b", "¿Dejo de salir de noche?",
  "h3", "h3_c", "¿Dejo de llevar dinero en efectivo, joyas, documentos o celular?",
  "h3", "h3_d", "¿Dejo de permitir que ninas, ninos o adolescentes que viven en su hogar salgan por su cuenta?",
  "h3", "h3_e", "¿Dejo de usar transporte publico?",
  "h4", "h4_a", "Vigilancia policial de carabineros como plan cuadrante, fiscalizaciones, rondas, presencia.",
  "h4", "h4_b", "Seguridad ciudadana municipal.",
  "h4", "h4_c", "Instancias de organizacion vecinal como grupos de WhatsApp, alarmas comunitarias."
) %>% mutate(correct_response = "")

sections <- tribble(
  ~section_id, ~section_prompt,
  "h1", "",
  "h2", "En los ultimos 12 meses, en su barrio o localidad me podria decir, ¿que tanta seguridad siente en las siguientes situaciones?",
  "h3", "En los ultimos 12 meses, por temor a ser victima de algun delito; como robo o asalto…",
  "h4", "En su barrio o localidad, ¿cuentan con alguna de estas instancias para abordar los problemas de seguridad?"
)

instrument_tab <- tibble(instrument = instrument_txt, instructions = instructions_txt)

responses <- tribble(
  ~item,  ~resp, ~option_text,
  "h1", 1, "Nunca",
  "h1", 2, "Una vez",
  "h1", 3, "Mas de una vez",
  "h2_a", 1, "Nada", "h2_a", 2, "Poca", "h2_a", 3, "Algo", "h2_a", 4, "Bastante", "h2_a", 5, "Mucha",
  "h2_b", 1, "Nada", "h2_b", 2, "Poca", "h2_b", 3, "Algo", "h2_b", 4, "Bastante", "h2_b", 5, "Mucha",
  "h2_c", 1, "Nada", "h2_c", 2, "Poca", "h2_c", 3, "Algo", "h2_c", 4, "Bastante", "h2_c", 5, "Mucha",
  "h2_d", 1, "Nada", "h2_d", 2, "Poca", "h2_d", 3, "Algo", "h2_d", 4, "Bastante", "h2_d", 5, "Mucha",
  "h3_a", 1, "Si", "h3_a", 2, "No",
  "h3_b", 1, "Si", "h3_b", 2, "No",
  "h3_c", 1, "Si", "h3_c", 2, "No",
  "h3_d", 1, "Si", "h3_d", 2, "No", "h3_d", 3, "No hay ninos, ninas o adolescentes en el hogar",
  "h3_e", 1, "Si", "h3_e", 2, "No", "h3_e", 3, "No usa transporte publico",
  "h4_a", 1, "Si", "h4_a", 2, "No",
  "h4_b", 1, "Si", "h4_b", 2, "No",
  "h4_c", 1, "Si", "h4_c", 2, "No"
)

d <- items %>%
  merge(sections, by = "section_id", all.x = TRUE) %>%
  merge(instrument_tab) %>%
  merge(responses, by = "item", all.x = TRUE)

d$table <- table_id
d <- d[, c("table","section_id","item","instrument","instructions","section_prompt",
           "item_text","correct_response","option_text","resp")]

d <- d[order(match(d$item, items$item), d$resp), ]
rownames(d) <- NULL

saveRDS(d, file = "candidate_chile_2023_social-welfare-survey_h.rds")

# Validation against ground truth
gt <- readRDS(".gt_chile_2023_social_welfare_survey_h.rds")
cat("item match:", identical(sort(unique(d$item)), sort(unique(gt$item))), "\n")
cat("resp set of candidate:", paste(sort(unique(d$resp)), collapse=","), "\n")
cat("resp set of ground truth:", paste(sort(unique(gt$resp)), collapse=","), "\n")
cat("resp match (as sets):", identical(sort(unique(d$resp)), sort(unique(gt$resp))), "\n")

# per-item resp set check
gt_split <- split(gt$resp, gt$item)
d_split  <- split(d$resp, d$item)
for (it in sort(unique(gt$item))) {
  g <- sort(unique(gt_split[[it]]))
  c <- sort(unique(d_split[[it]]))
  ok <- identical(g, c)
  cat(sprintf("%-6s gt=%-12s cand=%-12s match=%s\n", it, paste(g,collapse=","), paste(c,collapse=","), ok))
}

str(d)
print(head(d, 20))
