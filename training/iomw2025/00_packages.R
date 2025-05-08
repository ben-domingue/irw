##You will need the following packages during the training session. The below command will install all of them (along with needed dependencies).

install.packages(c("splines",
                   "lme4",
                   "mirt",
                   "WrightMap",
                   "difR",
                   "TAM",
                   "eRm"
                   ),dep=TRUE
                 )


##If you want to use the irw R package, you will also need to install the following:
install.packages("devtools",dep=TRUE)
devtools::install_github("redivis/redivis-r", ref="main")
devtools::install_github("hansorlee/irw")


