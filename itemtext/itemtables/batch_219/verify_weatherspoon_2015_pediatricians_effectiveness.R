# Step 5b verification -- weatherspoon_2015_pediatricians_effectiveness
#
# CLAIM: each item code Q12_Nb carries the communication technique shipped as its
# item_text, and resp 1 = "Yes", 2 = "No" (the survey's 9 = "Don't Know" was
# dropped by the processing script).
#
# FALSIFIABLE PREDICTION: PLOS ONE 10.1371/journal.pone.0119855 Table 4 publishes,
# per technique (named in words, in domain order, NOT questionnaire order), the
# pediatricians' n and the Yes/No/Unsure percentages. Pairing each published row
# with the item code we shipped its wording to gives, for every item, an expected
# count of resp==1 and resp==2 in the live table (the live n excludes the Unsure
# responses, which were filtered as code 9). A permutation of item_text across
# codes breaks these pairings immediately.
#
# Table is tiny (~2.6k rows), so a full fetch is cheap here.

suppressMessages(library(irw))
TABLE <- "weatherspoon_2015_pediatricians_effectiveness"

# Published Table 4, pediatrician columns: technique wording -> n, Yes%, No%, Unsure%
# keyed by the item code this extraction assigned that wording to.
PUB <- list(
  Q12_1b  = list(txt="Ask patients to repeat back information or instructions",                 n=157, yes=68.79, no=3.82),
  Q12_2b  = list(txt="Speak slowly",                                                            n=164, yes=71.95, no=1.83),
  Q12_3b  = list(txt="Limit the number of concepts presented at a time (2 to 3)",               n=160, yes=75.63, no=1.88),
  Q12_4b  = list(txt="Ask patients to tell you what they will do at home to follow instructions",n=152, yes=59.21, no=1.97),
  Q12_5b  = list(txt="Use simple language",                                                     n=160, yes=85.63, no=0.63),
  Q12_6b  = list(txt="Read instructions out loud",                                              n=157, yes=52.23, no=5.73),
  Q12_7b  = list(txt="Hand out printed materials",                                              n=160, yes=59.38, no=6.88),
  Q12_8b  = list(txt="Underline key points on print material",                                  n=153, yes=53.59, no=3.92),
  Q12_9b  = list(txt="Write or printout instructions",                                          n=160, yes=77.50, no=1.25),
  Q12_10b = list(txt="Draw pictures or use printed illustrations",                              n=154, yes=71.43, no=0.65),
  Q12_11b = list(txt="Use models or x-rays to explain",                                         n=148, yes=52.70, no=2.03),
  Q12_12b = list(txt="Refer patients to the Internet or other sources of information",          n=156, yes=40.38, no=5.77),
  Q12_13b = list(txt="Ask other office staff to follow up with patients for post-care instructions", n=149, yes=49.66, no=4.70),
  Q12_14b = list(txt="Use video or DVD",                                                        n=136, yes=22.79, no=2.21),
  Q12_15b = list(txt="Follow-up with patients by telephone to check understanding and adherence",n=150, yes=68.67, no=2.00),
  Q12_16b = list(txt="Ask patients whether they would like a family member or friend",          n=141, yes=41.84, no=5.67),
  Q12_17b = list(txt="Use a translator or interpreter when needed",                             n=148, yes=77.03, no=0.68)
)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

cat(sprintf("%-9s %28s %13s %13s\n", "item", "published(n,yes,no)", "expected 1/2", "observed 1/2"))
bad <- 0
for (it in names(PUB)) {
  p <- PUB[[it]]
  exp_yes <- round(p$n * p$yes / 100)
  exp_no  <- round(p$n * p$no  / 100)
  v <- d$resp[d$item == it]
  obs_yes <- sum(v == 1); obs_no <- sum(v == 2)
  ok <- (exp_yes == obs_yes) && (exp_no == obs_no)
  if (!ok) bad <- bad + 1
  cat(sprintf("%-9s %10d %6.2f %6.2f %6d/%-6d %6d/%-6d %s\n",
              it, p$n, p$yes, p$no, exp_yes, exp_no, obs_yes, obs_no,
              if (ok) "ok" else "MISMATCH"))
}

cat(sprintf("\n%d of %d items reproduce their published Yes/No counts exactly.\n",
            length(PUB) - bad, length(PUB)))
cat("Every (n, Yes%, No%) triple in Table 4 is unique across the 17 techniques, so this\n",
    "pairing distinguishes each item from every other item, not merely a block or a\n",
    "subscale. It also fixes resp 1 = Yes and 2 = No (swapping them would invert every\n",
    "row). It does NOT independently establish the wording of the option 'Don't Know',\n",
    "which is code 9 and absent from the live table.\n", sep = "")

cat(if (bad == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
