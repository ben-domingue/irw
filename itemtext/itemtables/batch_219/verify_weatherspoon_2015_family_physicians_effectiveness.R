# Mapping verification for weatherspoon_2015_family_physicians_effectiveness.
#
# Claim under test: Q12_Nb carries the perceived-effectiveness answer for
# technique N of Question 12 of the Maryland Survey of Dental Caries Prevention
# (Physicians), and resp 1 = "Yes", 2 = "No" (9 = "Do not know", dropped by the
# IRW processing script).
#
# Falsifiable prediction: Weatherspoon, Horowitz & Kleinman (2015) PLoS ONE
# 10.1371/journal.pone.0119855, Table 4, prints per-technique n, %Yes and %No
# for the 79 family physicians. n counts Yes + No + Unsure, so the predicted
# live counts are Yes = round(n * %Yes/100) and No = round(n * %No/100) -- the
# Unsure (9) rows never reach the IRW table. If any two items' item_text were
# swapped, these counts would move, because all 17 (Yes, No) count pairs are
# distinct.
#
# The route says nothing about resp 3/4/5, which are out-of-instrument values
# (25 rows) and are shipped with blank option_text.

suppressMessages(library(irw))
TABLE <- "weatherspoon_2015_family_physicians_effectiveness"

# Table 4, Family Physicians columns, in questionnaire item order 1..17.
pub <- data.frame(
  item = paste0("Q12_", 1:17, "b"),
  technique = c("Ask patients to repeat back information or instructions",
                "Speak slowly", "Limit the number of concepts presented at a time (2 to 3)",
                "Ask patients to tell you what they will do at home to follow instructions",
                "Use simple language", "Read instructions out loud",
                "Hand out printed materials", "Underline key points on print material",
                "Write or printout instructions", "Draw pictures or use printed illustrations",
                "Use models or x-rays to explain",
                "Refer patients to the Internet or other sources of information",
                "Ask other office staff to follow up with patients for post-care instructions",
                "Use video or DVD",
                "Follow-up with patients by telephone to check understanding and adherence",
                "Ask patients whether they would like a family member or friend",
                "Use a translator or interpreter when needed"),
  n    = c(56, 58, 58, 55, 59, 58, 59, 58, 59, 58, 55, 58, 57, 53, 59, 55, 57),
  pyes = c(73.21, 60.34, 74.14, 61.82, 81.36, 67.24, 57.63, 48.28, 69.49,
           58.62, 41.82, 43.10, 49.12, 15.09, 59.32, 58.18, 73.68),
  pno  = c(3.57, 5.17, 0.00, 0.00, 0.00, 0.00, 3.39, 3.45, 0.00,
           1.72, 3.64, 5.17, 1.75, 7.55, 1.69, 0.00, 0.00),
  stringsAsFactors = FALSE)

pub$exp_yes <- round(pub$n * pub$pyes / 100)
pub$exp_no  <- round(pub$n * pub$pno  / 100)

d <- irw::irw_fetch(TABLE)          # 616 rows -- a negligible export
tab <- table(d$item, d$resp)
obs_yes <- as.integer(tab[pub$item, "1"])
obs_no  <- as.integer(tab[pub$item, "2"])

cat(sprintf("%-8s %5s %7s %7s | %7s %7s | %s\n",
            "item", "n", "expYes", "obsYes", "expNo", "obsNo", "technique"))
for (i in seq_len(nrow(pub)))
  cat(sprintf("%-8s %5d %7d %7d | %7d %7d | %s\n", pub$item[i], pub$n[i],
              pub$exp_yes[i], obs_yes[i], pub$exp_no[i], obs_no[i],
              substr(pub$technique[i], 1, 52)))

ok <- all(obs_yes == pub$exp_yes) && all(obs_no == pub$exp_no)
cat(sprintf("\nitems reconciling on BOTH Yes and No counts: %d/17\n",
            sum(obs_yes == pub$exp_yes & obs_no == pub$exp_no)))

pairs <- paste(pub$exp_yes, pub$exp_no)
cat(sprintf("distinct published (Yes,No) count pairs: %d/17 -- %s\n",
            length(unique(pairs)),
            if (length(unique(pairs)) == 17)
              "every item is separated from every other" else
              "some items are NOT separated by this route"))
cat("Does NOT establish: the meaning of resp 3/4/5 (25 out-of-instrument rows,\n",
    "shipped with blank option_text).\n", sep = "")

cat(if (ok && length(unique(pairs)) == 17) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
