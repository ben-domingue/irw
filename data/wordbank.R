#https://github.com/langcog/wordbankr
# install.packages("devtools")
#devtools::install_github("langcog/wordbankr")

library(wordbankr)

english_ws_admins <- get_administration_data("English (American)", "WS")
all_admins <- get_administration_data()

english_ws_data <- get_instrument_data("English (American)", "WS")

