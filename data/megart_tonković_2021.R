library(dplyr)

data_1 <- read.csv("cda1012_dat_c_reaction-times_1.csv")
data_1 <- data_1%>%
  transmute(id,
            # stimulus_rt is in milliseconds (cda1012_doc_variable-metadata:
            # "Reaction time to stimulus expressed in milliseconds"); IRW wants
            # seconds (irw#2401). stimulus_acc is TRUE/FALSE; written as 1/0,
            # which is how the live table already holds it.
            rt = stimulus_rt / 1000,
            resp = as.integer(stimulus_acc),
            date =session_start_date_time_utc,
            item = string,
            itemcov_type = string_type)


data_1$date <- as.numeric(as.POSIXct(data_1$date,
                                   format = "%d.%m.%Y. %H:%M:%S",
                                   tz = "UTC"))

data_2 <- read.csv("cda1012_dat_c_reaction-times_2.csv")
data_2 <- data_2%>%
  transmute(id,
            # stimulus_rt is in milliseconds (cda1012_doc_variable-metadata:
            # "Reaction time to stimulus expressed in milliseconds"); IRW wants
            # seconds (irw#2401). stimulus_acc is TRUE/FALSE; written as 1/0,
            # which is how the live table already holds it.
            rt = stimulus_rt / 1000,
            resp = as.integer(stimulus_acc),
            date =session_start_date_time_utc,
            item = string,
            itemcov_type = string_type)


data_2$date <- as.numeric(as.POSIXct(data_2$date,
                                     format = "%d.%m.%Y. %H:%M:%S",
                                     tz = "UTC"))

combined_data <- bind_rows(data_1, data_2)

write.csv(combined_data, "megart_tonković_2021.csv", row.names = FALSE)

