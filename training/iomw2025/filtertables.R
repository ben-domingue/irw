irw::irw_download("DART_Brysbaert_2020_1")
irw::irw_download("promis1wave1_cesd")
irw::irw_download("roar_lexical")

list.tables<-irw::irw_filter(n_participants=c(500,1000),
           n_categories=2,
           n_items=c(10,50),
           density=c(0.75,1)
           )

f<-function(tab) irw::irw_download(tab)
lapply(list.tables,f)
