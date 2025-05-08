df<-irw::irw_fetch("gilbert_meta_2")
df$item <- paste("item_", df$item, sep = "")
resp <- irwpkg::irw_long2resp(df)
resp$id <- NULL
psych::alpha(resp)
paran::paran(resp)
psych::fa(cov(resp), nfactors = 3)
mirt::mirt(resp, 1, "Rasch")
