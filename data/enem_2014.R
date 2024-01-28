library(tidyverse)
setwd('~/projects/irw/enem')

########
# 2014 #
########

microdata <- read_delim('data/2014/DADOS/MICRODADOS_ENEM_2014.csv', delim=';') |>
  select(id = NU_INSCRICAO,
         starts_with('CO_PROVA'),
         starts_with('TX'))

set.seed(5150)
enem_subset <- sample(microdata$id, size=1e6, replace=FALSE)

microdata <- microdata |>
  filter(id %in% enem_subset)

items <- read_delim('data/2014/DADOS/ITENS_PROVA_2014.csv', delim=';') |>
  select(subj = SG_AREA,
         item = CO_ITEM,
         position = CO_POSICAO,
         booklet = CO_PROVA,
         key = TX_GABARITO)

booklets <- microdata |>
  select(id, starts_with('CO_PROVA')) |>
  pivot_longer(starts_with('CO_PROVA'), names_to = 'subj',
               values_to='booklet', names_prefix='CO_PROVA_')

# Social Science

df <- microdata |>
  select(id, TX_RESPOSTAS_CH) |>
  separate(TX_RESPOSTAS_CH,
           into=paste0('raw_CH_', 1:45),
           sep=1:44) |>
  pivot_longer(starts_with('raw'), names_to=c('type', 'subj', 'position'), names_sep='_') |>
  pivot_wider(id_cols=c(id, subj, position), names_from='type', values_from='value') |>
  mutate(position = as.numeric(position)) |>
  left_join(booklets, by=c('id', 'subj')) |>
  left_join(items, by=c('subj', 'booklet', 'position')) |>
  mutate(resp = if_else(raw == key, 1, 0)) |>
  select(id, item, resp, position, booklet)

save(df, file='data/processed/enem_2014_1mil_ch.Rdata')

# Natural Science

df <- microdata |>
  select(id, TX_RESPOSTAS_CN) |>
  separate(TX_RESPOSTAS_CN,
           into=paste0('raw_CN_', 46:90),
           sep=1:44) |>
  pivot_longer(starts_with('raw'), names_to=c('type', 'subj', 'position'), names_sep='_') |>
  pivot_wider(id_cols=c(id, subj, position), names_from='type', values_from='value') |>
  mutate(position = as.numeric(position)) |>
  left_join(booklets, by=c('id', 'subj')) |>
  left_join(items, by=c('subj', 'booklet', 'position')) |>
  mutate(resp = if_else(raw == key, 1, 0)) |>
  select(id, item, resp, position, booklet)

save(df, file='data/processed/enem_2014_1mil_cn.Rdata')


# Language

df <- microdata |>
  select(id, TX_RESPOSTAS_LC) |>
  separate(TX_RESPOSTAS_LC,
           into=paste0('raw_LC_', 91:135),
           sep=1:44) |>
  pivot_longer(starts_with('raw'), names_to=c('type', 'subj', 'position'), names_sep='_') |>
  pivot_wider(id_cols=c(id, subj, position), names_from='type', values_from='value') |>
  mutate(position = as.numeric(position)) |>
  left_join(booklets, by=c('id', 'subj')) |>
  left_join(items, by=c('subj', 'booklet', 'position')) |>
  mutate(resp = if_else(raw == key, 1, 0)) |>
  select(id, item, resp, position, booklet)

save(df, file='data/processed/enem_2014_1mil_lc.Rdata')

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

save(df, file='data/processed/enem_2014_1mil_mt.Rdata')
