library(tidyr)
library(dplyr)

df <- read.csv("tmcs_professores_es.csv")

df <- df %>%
  rename(cov_gen = gen, cov_idade = idade, cov_raca = raca, cov_estado_civil = estado_civil,
         cov_escolaridade = escolaridade, cov_renda_familiar = renda_familiar,
         cov_depend_renda = depend_renda, cov_renda_pos_pandemia = renda_pos_pandemia, 
         cov_vinculo = vinculo, cov_grupo_de_risco = grupo_de_risco,
         cov_diagnostico_de_covid = diagnostico_de_covid, cov_perdas_p_covid = perdas_p_covid)

ct <- df %>%
  select(-c(starts_with("srq"))) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp")

srq <- df %>%
  select(-c(starts_with("ct"))) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp")

write.csv(ct, "pinheiro_2023_trwcas.csv", row.names = FALSE)
write.csv(srq, "pinheiro_2023_srq.csv", row.names = FALSE)
