# verify_li_2021_cultural_intelligence.R -- Step 5b, route 5 (subscale block
# structure) + route 8 (semantic coherence of the response level).
#
# The claim under test: data columns CQ1..CQ12 correspond, in order, to items
# 1..12 printed under "Cultural Intelligence（CQ）" in S1 Appendix (Questionnaire)
# of Li, Wu & Xiong 2021, PLOS ONE 10.1371/journal.pone.0250878.
#
# That ordering is the canonical CQS facet order retained by Bucker's 12-item
# short form, so the shipped text predicts a four-block structure in the data:
#   metacognitive  items 1-2   (awareness of own cultural knowledge)
#   cognitive      items 3-7   (factual knowledge: legal/economic, language
#                               rules, values/religion, marriage, arts/crafts)
#   motivational   items 8-9   (confidence socialising / coping with a new culture)
#   behavioural    items 10-12 (pause & silence, speaking rate, nonverbal behaviour)
# and predicts that the five knowledge items are the least-endorsed of the twelve
# (rating your factual knowledge of other cultures is harder than rating your own
# awareness, confidence or behavioural flexibility).
#
# What this does NOT establish: order WITHIN a block. Nothing here separates
# CQ3 (legal/economic systems) from CQ6 (marriage systems) or CQ7 (arts and
# crafts), nor CQ1 from CQ2 (r = 0.81). Status is recorded as PARTIAL.

suppressMessages(library(irw))

TABLE  <- "li_2021_cultural_intelligence"
GROUPS <- list(metacognitive = c("CQ1","CQ2"),
               cognitive     = c("CQ3","CQ4","CQ5","CQ6","CQ7"),
               motivational  = c("CQ8","CQ9"),
               behavioural   = c("CQ10","CQ11","CQ12"))

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d)[, c("id","item","resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, paste0("CQ", 1:12)]
R <- cor(w, use = "pairwise.complete.obs")

cat("--- own-block vs best-rival-block mean correlation ---\n")
cat(sprintf("%-6s %-14s %8s %-14s %8s %6s\n",
            "item","own block","own r","best rival","rival r","ok"))
ok_n <- 0
for (g in names(GROUPS)) for (it in GROUPS[[g]]) {
    own <- mean(R[it, setdiff(GROUPS[[g]], it)])
    riv <- sapply(setdiff(names(GROUPS), g),
                  function(h) mean(R[it, GROUPS[[h]]]))
    best <- names(which.max(riv))
    ok <- own > max(riv); ok_n <- ok_n + ok
    cat(sprintf("%-6s %-14s %8.2f %-14s %8.2f %6s\n",
                it, g, own, best, max(riv), ifelse(ok, "ok", "FAIL")))
}
cat(sprintf("\n%d/12 items load strongest on the block their shipped text implies.\n", ok_n))

cat("\n--- per-item means: the five knowledge items should be the lowest ---\n")
m <- sort(tapply(d$resp, d$item, mean))
print(round(m, 2))
lowest5 <- names(m)[1:5]
cog_ok <- setequal(lowest5, GROUPS$cognitive)
cat(sprintf("five lowest means: %s\ncognitive block (items 3-7): %s\nmatch: %s\n",
            paste(lowest5, collapse=","), paste(GROUPS$cognitive, collapse=","), cog_ok))

cat("\nNot established by this script: order within each block (CQ1 vs CQ2, r = 0.81;\n",
    "CQ3/CQ6/CQ7 means 4.16/4.11/4.09). Recorded as PARTIAL.\n", sep = "")

cat(if (ok_n == 12 && cog_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
