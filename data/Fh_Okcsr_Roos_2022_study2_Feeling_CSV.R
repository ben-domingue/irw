# Paper: https://pubmed.ncbi.nlm.nih.gov/38032901/
# Data: https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/IHNKUN
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

study1_df <- read_sav("Feeling heard - Questionnaire data Study 1.sav") 
study2_df <- read_sav("Feeling heard - Questionnaire data Study 2.sav") 

study1_df[] <- lapply(study1_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

# Exclude participants that gave nonsensical responses to Q3.1
exclude_rows <- c(9, 30, 32, 40, 56, 66, 72, 81, 84, 90, 101, 106, 110, 114, 131, 150, 162, 167, 170, 177, 189, 197, 203)

# Exclude the rows from study1 dataframe using slice
study1_df <- study1_df %>%
  slice(-exclude_rows)

study2_df[] <- lapply(study2_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

study1_df <- study1_df %>%
  mutate(id = row_number() )

study2_df <- study2_df %>%
  mutate(id = row_number() )

# ------ Process Study 1 Data ------
heard_df <- study1_df |>
  select(ends_with("11"), ends_with("12"),id, -FL_13_DO_FL_11)
heard_df <- remove_na(heard_df)
heard_df[] <- lapply(heard_df, function(x) if (is.labelled(x)) as.numeric(x) else x)
heard_df <- pivot_longer(heard_df, cols=-c(id), names_to="item", values_to="resp")

Voice_df <- study1_df |>
  select(ends_with("_1"), ends_with("_2"),ends_with("_3"),id)
Voice_df <- remove_na(Voice_df)
Voice_df[] <- lapply(Voice_df, function(x) if (is.labelled(x)) as.numeric(x) else x)
Voice_df <- pivot_longer(Voice_df, cols=-c(id), names_to="item", values_to="resp")

Attention_df <- study1_df |>
  select(ends_with("_4"), ends_with("_5"),ends_with("_6"),id)
Attention_df  <- remove_na(Attention_df )
Attention_df[] <- lapply(Attention_df, function(x) if (is.labelled(x)) as.numeric(x) else x)
Attention_df  <- pivot_longer(Attention_df, cols=-c(id), names_to="item", values_to="resp")


Empathy_df <- study1_df |>
  select(ends_with("_7"), ends_with("_8"),ends_with("_9"),id)
Empathy_df <- remove_na(Empathy_df)
Empathy_df[] <- lapply(Empathy_df, function(x) if (is.labelled(x)) as.numeric(x) else x)
Empathy_df <- pivot_longer(Empathy_df, cols=-c(id), names_to="item", values_to="resp")


Respect_df <- study1_df |>
  select(ends_with("_10"), ends_with("_11"),ends_with("_12"),id,-FL_13_DO_FL_11)
Respect_df <- remove_na(Respect_df)
Respect_df[] <- lapply(Respect_df, function(x) if (is.labelled(x)) as.numeric(x) else x)
Respect_df <- pivot_longer(Respect_df, cols=-c(id), names_to="item", values_to="resp")


Common_ground_df <- study1_df |>
  select(ends_with("_13"), ends_with("_14"),ends_with("_15"),id)
Common_ground_df <- remove_na(Common_ground_df)
Common_ground_df[] <- lapply(Common_ground_df, function(x) if (is.labelled(x)) as.numeric(x) else x)
Common_ground_df <- pivot_longer(Common_ground_df, cols=-c(id), names_to="item", values_to="resp")

Disagree_df <- study1_df |>
  select(ends_with("_16"),id)
Disagree_df <- remove_na(Disagree_df)
Disagree_df[] <- lapply(Disagree_df, function(x) if (is.labelled(x)) as.numeric(x) else x)
Disagree_df <- pivot_longer(Disagree_df, cols=-c(id), names_to="item", values_to="resp")

heard_df$group <- "Feeling Heard Group"
Voice_df$group <- "Voice Group"
Attention_df$group <- "Attention Group"
Empathy_df$group <- "Empathy Group"
Respect_df$group <- "Respect Group"
Common_ground_df$group <- "Common ground Group"
Disagree_df$group <- "Disagree Group"


study1_Feeling_Heard_df <- rbind(heard_df, 
                                 Voice_df,
                                 Attention_df, 
                                 Empathy_df,
                                 Respect_df,
                                 Common_ground_df,
                                 Disagree_df)

save(study1_Feeling_Heard_df, file="Fh_Okcsr_Roos_2022_study1_Feeling_Heard.Rdata")
write.csv(study1_Feeling_Heard_df, "Fh_Okcsr_Roos_2022_study1_Feeling_Heard.csv", row.names=FALSE)

# ------ Process Study 2 Feeling Heard Data ------
Reliability_df <- study2_df |>
  select(starts_with("Q5.1"),id)
Reliability_df   <- remove_na(Reliability_df)
Reliability_df  <- pivot_longer(Reliability_df , cols=-c(id), names_to="item", values_to="resp")

Convergent_Validity_conversational_intimacy_df <- study2_df |>
  select(starts_with("Q6.1"),id)
Convergent_Validity_conversational_intimacy_df  <- remove_na(Convergent_Validity_conversational_intimacy_df)
Convergent_Validity_conversational_intimacy_df <- pivot_longer(Convergent_Validity_conversational_intimacy_df , cols=-c(id), names_to="item", values_to="resp")

Convergent_Validity_conversational_dominance_df<- study2_df |>
  select(starts_with("Q75"),id)
Convergent_Validity_conversational_dominance_df  <- remove_na(Convergent_Validity_conversational_dominance_df)
Convergent_Validity_conversational_dominance_df <- pivot_longer(Convergent_Validity_conversational_dominance_df, cols=-c(id), names_to="item", values_to="resp")

Individualized_Trust_df <- study2_df |>
  select(starts_with("Q8.1"),id)
Individualized_Trust_df  <- remove_na(Individualized_Trust_df)
Individualized_Trust_df <- pivot_longer(Individualized_Trust_df , cols=-c(id), names_to="item", values_to="resp")

Affective_Attraction_df <- study2_df |>
  select(starts_with("Q9"),id)
Affective_Attraction_df  <- remove_na(Affective_Attraction_df)
Affective_Attraction_df <- pivot_longer(Affective_Attraction_df , cols=-c(id), names_to="item", values_to="resp")

Perceived_partner_responsiveness_df <- study2_df |>
  select(starts_with("Q10.1"),id)
Perceived_partner_responsiveness_df <- remove_na(Perceived_partner_responsiveness_df )
Perceived_partner_responsiveness_df  <- pivot_longer(Perceived_partner_responsiveness_df, cols=-c(id), names_to="item", values_to="resp")

Perceived_goal_accomplishment_df <- study2_df |>
  select(starts_with("Q11.1"),id)
Perceived_goal_accomplishment_df <- remove_na(Perceived_goal_accomplishment_df)
Perceived_goal_accomplishment_df  <- pivot_longer(Perceived_goal_accomplishment_df, cols=-c(id), names_to="item", values_to="resp")

Communication_Apprehension_df <- study2_df |>
  select(starts_with("Q12.1"),id)
Communication_Apprehension_df <- remove_na(Communication_Apprehension_df)
Communication_Apprehension_df <- pivot_longer(Communication_Apprehension_df, cols=-c(id), names_to="item", values_to="resp")

Reliability_df$group <- "Reliability Group"
Convergent_Validity_conversational_intimacy_df $group <- "Convergent Validity Conversational Intimacy Group"
Convergent_Validity_conversational_dominance_df $group <- "Convergent Validity Conversational Dominance Group"
Individualized_Trust_df$group <- "Individualized Trust Group"
Affective_Attraction_df$group <- "Affective Attraction Group"
Perceived_partner_responsiveness_df$group  <- "Perceived Partner Responsiveness Group"
Perceived_goal_accomplishment_df$group  <- "Perceived Goal Accomplishment Group"
Communication_Apprehension_df$group <- "Communication Apprehension Group"

convert_labelled_to_numeric <- function(df) {
  df[] <- lapply(df, function(x) {
    if (is.labelled(x)) {
      # If it's a labelled column, convert it to numeric (which removes labels)
      as.numeric(x)
    } else {
      x
    }
  })
  return(df)
}

# Apply this conversion to all data frames
Reliability_df <- convert_labelled_to_numeric(Reliability_df)
Convergent_Validity_conversational_intimacy_df <- convert_labelled_to_numeric(Convergent_Validity_conversational_intimacy_df )
Convergent_Validity_conversational_dominance_df <- convert_labelled_to_numeric(Convergent_Validity_conversational_dominance_df)
Individualized_Trust_df <- convert_labelled_to_numeric(Individualized_Trust_df)
Affective_Attraction_df <- convert_labelled_to_numeric(Affective_Attraction_df)
Perceived_partner_responsiveness_df <- convert_labelled_to_numeric(Perceived_partner_responsiveness_df)
Perceived_goal_accomplishment_df <- convert_labelled_to_numeric(Perceived_goal_accomplishment_df)
Communication_Apprehension_df <- convert_labelled_to_numeric(Communication_Apprehension_df)

study2_Feeling_Heard_df <- rbind(Reliability_df, 
                                 Convergent_Validity_conversational_intimacy_df,
                                 Convergent_Validity_conversational_dominance_df,
                                 Individualized_Trust_df, 
                                 Affective_Attraction_df,
                                 Perceived_partner_responsiveness_df,
                                 Perceived_goal_accomplishment_df,
                                 Communication_Apprehension_df)
study2_Feeling_Heard_df$resp <- ifelse(study2_Feeling_Heard_df$resp >= 10 & study2_Feeling_Heard_df$resp <= 18, study2_Feeling_Heard_df$resp - 9, study2_Feeling_Heard_df$resp)
# ------ Process Negative Avoidance Study 2 Data ------
negative_avoidance_df <- study2_df %>%
  select(Q13.1_1, Q23.1_1, Q13.1_2, Q23.1_2,id)
negative_avoidance_df  <- remove_na(negative_avoidance_df )
negative_avoidance_df <- pivot_longer(negative_avoidance_df , cols=-c(id), names_to="item", values_to="resp")

# Positive Avoidance
positive_avoidance_df <- study2_df  %>%
  select(Q13.1_3, Q23.1_3, Q13.1_4, Q23.1_4, id)
positive_avoidance_df <- remove_na(positive_avoidance_df )
positive_avoidance_df <- pivot_longer(positive_avoidance_df, cols=-c(id), names_to="item", values_to="resp")

# Negative Approach
negative_approach_df <- study2_df  %>%
  select(Q13.1_5, Q23.1_5, Q13.1_6, Q23.1_6, id)
negative_approach_df <- remove_na(negative_approach_df)
negative_approach_df<- pivot_longer(negative_approach_df , cols=-c(id), names_to="item", values_to="resp")

# Positive Approach
positive_approach_df <- study2_df  %>%
  select(Q13.1_7, Q23.1_7, Q13.1_8, Q23.1_8, id)
positive_approach_df <- remove_na(positive_approach_df)
positive_approach_df <- pivot_longer(positive_approach_df, cols=-c(id), names_to="item", values_to="resp")

negative_avoidance_df <- convert_labelled_to_numeric(negative_avoidance_df)
positive_avoidance_df <- convert_labelled_to_numeric(positive_avoidance_df)
negative_approach_df <- convert_labelled_to_numeric(negative_approach_df)
positive_approach_df <- convert_labelled_to_numeric(positive_approach_df)

study2_not_feeling_heard_df <- rbind(negative_avoidance_df, 
                                     positive_avoidance_df,
                                     negative_approach_df, 
                                     positive_approach_df)

study2_not_feeling_heard_df$group <- "negative"
study2_Feeling_Heard_df$group <- "positive"
study2_df <- rbind(study2_Feeling_Heard_df, study2_not_feeling_heard_df)

save(study2_df, file="Fh_Okcsr_Roos_2022_study2_Feeling_Heard.Rdata")
write.csv(study2_df, "Fh_Okcsr_Roos_2022_study2_Feeling_Heard.csv", row.names=FALSE)

