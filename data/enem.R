library(tidyverse)
library(haven)
library(mirt)
library(beepr)


#setwd('~/projects/blue-books/')

# Working with 2014 math test
#data_path <- 'data/MICRODADOS_ENEM_2014_mt_equated.dta'
#d <- read_dta(data_path)
d<-read.csv("MICRODADOS_ENEM_2014.csv",sep=";",nrows=100000)
names(d)<-tolower(names(d))
beep(1)

df <- d %>%
    select(nu_inscricao,
           tp_st_conclusao, #edited from st_conclusao
           booklet, starts_with('v')) %>%
  pivot_longer(starts_with('v'), names_to='item', names_prefix='v', values_to='resp') %>%
  mutate(item = as.numeric(item))

i <- read_dta('data/ITENS_ENEM_2014.dta')%>%
  filter(id_prova %in% c(207:210)) %>%
  transmute(
    booklet = case_when(
      id_prova == 207 ~ 'yellow',
      id_prova == 208 ~ 'grey',
      id_prova == 209 ~ 'blue',
      id_prova == 210 ~ 'pink'),
    item = as.numeric(id_posicao) - 135,
    seq = seq)

df <- left_join(df, i, by=c('booklet', 'item'))

df <- df %>%
  filter(st_conclusao == 2)  %>%
  select(id = nu_inscricao,
         itemkey = item,
         sequence_number = seq,
         resp = resp,
         booklet = booklet)


yellow <- unique(df$id[df$booklet=='yellow'])
grey <- unique(df$id[df$booklet=='grey'])
blue <- unique(df$id[df$booklet=='blue'])
pink <- unique(df$id[df$booklet=='pink'])

small_samp <- c(sample(yellow, 2500, replace=FALSE),
                sample(grey, 2500, replace=FALSE),
                sample(blue, 2500, replace=FALSE),
                sample(pink, 2500, replace=FALSE))

calibration_samp <- c(sample(yellow, 125000, replace=FALSE),
                      sample(grey, 125000, replace=FALSE),
                      sample(blue, 125000, replace=FALSE),
                      sample(pink, 125000, replace=FALSE))

big_cal_samp <- c(sample(yellow, 200000, replace=FALSE),
                  sample(grey, 200000, replace=FALSE),
                  sample(blue, 200000, replace=FALSE),
                  sample(pink, 200000, replace=FALSE))

saveRDS(df, '~/projects/blue-books/data/enem_math_2014_full.rds')
df %>%
  filter(id %in% small_samp) %>%
  saveRDS('~/projects/blue-books/data/enem_math_2014_10k.rds')

df %>%
  select(-booklet) %>%
  filter(id %in% small_samp) %>%
  write_csv('~/projects/mmirt/data/enem_test_little.csv')

df %>%
  select(-booklet) %>%
  filter(id %in% calibration_samp) %>%
  write_csv('~/projects/mmirt/data/enem_item_calibration.csv')

df %>%
  select(-booklet) %>%
  filter(id %in% big_cal_samp) %>%
  write_csv('~/projects/mmirt/data/enem_big_item_cal.csv')

