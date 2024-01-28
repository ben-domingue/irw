library(tidyverse)
library(vroom)

microdata <- vroom('DADOS/MICRODADOS_ENEM_2020.csv', 
                   delim=';', 
                   col_select = list(id = NU_INSCRICAO,
                                     starts_with('CO_PROVA'),
                                     starts_with('TX'))) |>
  drop_na()

set.seed(5150)
enem_subset <- sample(microdata$id, size=1e6, replace=FALSE)

microdata <- microdata |>
  filter(id %in% enem_subset)

items <- vroom('DADOS/ITENS_PROVA_2020.csv', 
               delim=';',
               col_select = list(subj = SG_AREA,
                                 item = CO_ITEM,
                                 position = CO_POSICAO,
                                 booklet = CO_PROVA,
                                 key = TX_GABARITO))

booklets <- microdata |>
  select(id, starts_with('CO_PROVA')) |>
  pivot_longer(starts_with('CO_PROVA'), names_to = 'subj',
               values_to='booklet', names_prefix='CO_PROVA_')

# Language

# there subject + booklet + position combinations that are associated with multiple items
# identify those duplicates to drop from sample
duplicates <- items |>
  filter(subj == 'LC') |>
  select(subj, booklet, position, item, key) |>
  arrange(booklet, position, item) |>
  mutate(count = 1) |>
  group_by(subj, booklet, position) |>
  summarize(count = sum(count)) |>
  filter(count > 1)

df <- microdata |>
  select(id, TX_RESPOSTAS_LC) |>
  separate(TX_RESPOSTAS_LC,
           into=paste0('raw_LC_', 1:45),
           sep=1:44) |>
  pivot_longer(starts_with('raw'), names_to=c('type', 'subj', 'position'), names_sep='_') |>
  pivot_wider(id_cols=c(id, subj, position), names_from='type', values_from='value') |>
  mutate(position = as.numeric(position)) |>
  left_join(booklets, by=c('id', 'subj')) |>
  # next three lines drop the subject + booklet + position duplicates
  left_join(duplicates, by=c('subj', 'booklet', 'position')) |>
  filter(is.na(count)) |>
  select(-count) |>
  left_join(items, by=c('subj', 'booklet', 'position')) |>
  mutate(resp = if_else(raw == key, 1, 0)) |>
  select(id, item, resp, position, booklet)

save(df, file='enem_2020_1mil_lc.Rdata')

# Social Science

df <- microdata |>
  select(id, TX_RESPOSTAS_CH) |>
  separate(TX_RESPOSTAS_CH,
           into=paste0('raw_CH_', 46:90),
           sep=1:44) |>
  pivot_longer(starts_with('raw'), names_to=c('type', 'subj', 'position'), names_sep='_') |>
  pivot_wider(id_cols=c(id, subj, position), names_from='type', values_from='value') |>
  mutate(position = as.numeric(position)) |>
  left_join(booklets, by=c('id', 'subj')) |>
  left_join(items, by=c('subj', 'booklet', 'position')) |>
  mutate(resp = if_else(raw == key, 1, 0)) |>
  select(id, item, resp, position, booklet)

save(df, file='enem_2020_1mil_ch.Rdata')

# Natural Science

df <- microdata |>
  select(id, TX_RESPOSTAS_CN) |>
  separate(TX_RESPOSTAS_CN,
           into=paste0('raw_CN_', 91:135),
           sep=1:44) |>
  pivot_longer(starts_with('raw'), names_to=c('type', 'subj', 'position'), names_sep='_') |>
  pivot_wider(id_cols=c(id, subj, position), names_from='type', values_from='value') |>
  mutate(position = as.numeric(position)) |>
  left_join(booklets, by=c('id', 'subj')) |>
  left_join(items, by=c('subj', 'booklet', 'position')) |>
  mutate(resp = if_else(raw == key, 1, 0)) |>
  select(id, item, resp, position, booklet)

save(df, file='enem_2020_1mil_cn.Rdata')

# Math

df <- microdata |>
  select(id, TX_RESPOSTAS_MT) |>
  separate(TX_RESPOSTAS_MT,
           into=paste0('raw_MT_', 136:180),
           sep=1:44) |>
  pivot_longer(starts_with('raw'), names_to=c('type', 'subj', 'position'), names_sep='_') |>
  pivot_wider(id_cols=c(id, subj, position), names_from='type', values_from='value') |>
  mutate(position = as.numeric(position)) |>
  left_join(booklets, by=c('id', 'subj')) |>
  left_join(items, by=c('subj', 'booklet', 'position')) |>
  mutate(resp = if_else(raw == key, 1, 0)) |>
  select(id, item, resp, position, booklet)

save(df, file='enem_2020_1mil_mt.Rdata')
