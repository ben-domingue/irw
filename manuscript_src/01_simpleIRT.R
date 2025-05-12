df<-irw::irw_fetch("gilbert_meta_2") ##fetch data from the IRW
df$item <- paste("item_", df$item, sep = "")
resp <- irwpkg::irw_long2resp(df) ##reformat long data to wide
resp$id <- NULL
psych::alpha(resp) ##compute cronbach's alpha
paran::paran(resp) ##parallel analysis to estimate dimensionality
psych::fa(cov(resp), nfactors = 3) ##exploratory factor analysis
mirt::mirt(resp, 1, "Rasch") ##fitting the Rasch model
