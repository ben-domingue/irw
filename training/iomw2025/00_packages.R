install.packages(c("splines",
                   "lme4",
                   "mirt",
                   "WrightMap",
                   "difR",
                   "TAM",
                   "eRm"
                   ),dep=TRUE
                 )


##if you want to use irwpkg
install.packages("devtools",dep=TRUE)
devtools::install_github("redivis/redivis-r", ref="main")
devtools::install_github("hansorlee/irwpkg")


