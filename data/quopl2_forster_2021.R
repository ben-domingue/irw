library(dplyr)
library(haven)
library(tidyr)

data <- read_sav("02_data_prepared.sav", encoding = "latin1")

data <- data %>%
  rename(id = code,
         cov_teacher = teacher,
         cov_class = class,
         cov_school = school,
         cov_grade = grade,
         cov_state = state,
         cov_sex = s_sex,
         cov_migration = s_migr,
         )

scales <- c("dmat", "cft", "elfe")

scale_patterns <- list(
  dmat = c("MZ", "ZR", "AD","SU", "ZZ", "TG", "KA", "UG"),
  cft = c("labyr","Ã¤hnl","reihe","klass","matrix"),
  elfe = c("WortKorrekt", "SatzKorrekt","TextKorrekt"))

pivot_scale <- function(data, scale_name) {
  patterns <- scale_patterns[[scale_name]]
  regex <- paste0("^(", paste(patterns, collapse="|"), ")")
  data %>%
    zap_labels() %>%
    select(id, starts_with("cov_"), matches(regex),-matches("^substi")) %>%
    pivot_longer(
      cols =matches(regex),
      names_to = "item",
      values_to = "resp"
    )
}

for (scale in scales) {
  data_sub <- pivot_scale(data, scale)
  write.csv(data_sub, paste0("quopl2_forster_2021_", scale, ".csv"), row.names = FALSE)
}


#Now for the L2 test
tests <- 1:8

pivot_test <- function(data, test) {
  
  prefix <- paste0("t", test, "_")
  
  # Accuracy (r) columns
  r_cols <- grep(paste0("^", prefix, "r[0-9]+$"), names(data), value = TRUE)
  
  # RT (g) columns
  g_cols <- grep(paste0("^", prefix, "g[0-9]+$"), names(data), value = TRUE)
  
  # Date and time
  date_col <- paste0("t", test, "_date")
  test_name <- paste0("test",test)
  
  all_cols <- c(test_name,date_col, r_cols, g_cols)
  all_cols <- all_cols[all_cols %in% names(data)]
  
  # Remove the prefix (t1_, t2_, etc.)
  cleaned_names <- sub(prefix, "", all_cols)
  cleaned_names[1] <- "test_label"
  
  data %>%
    select(id, starts_with("cov_"), all_of(all_cols)) %>%
    rename_with(~ cleaned_names, all_of(all_cols)) %>%
    mutate(test = test)  #the order in which the test is performed
}

final <- bind_rows(lapply(tests, \(t) pivot_test(data, t)))

final$date <- as.numeric(as.POSIXct(final$date, format = "%Y-%m-%d %H:%M:%S", tz = "UTC"))

final <- final %>%
  rename(item_family = test_label,
         wave = test)


final_long <- final %>%
  pivot_longer(
    cols = starts_with("r"),
    names_to = "item",
    values_to = "resp"
  ) 

item_num <- as.integer(sub("r", "", final_long$item))
gmat <- as.matrix(final_long[paste0("g", 1:46)])
final_long$rt <- gmat[cbind(seq_len(nrow(final_long)), item_num)]


final_long <- final_long %>%
  select(
    id, cov_teacher, cov_class, cov_grade, cov_school, cov_state,
    cov_sex, cov_migration, item_family, date, wave,
    item, resp, rt
  )

write.csv(final_long, "quopl2_forster_2021_quop.csv", row.names = FALSE)
