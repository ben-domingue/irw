# verify_perfectionismlit_2021_engagement.R -- Step 5b mapping check (batch_454).
#
# Claim: EQ1 = "I found the lesson useful", EQ2 = "... interesting",
# EQ3 = "... informative" (the last three rows of Table 1 of Hill, Fenwick &
# Lightfoot (2021), NACE "Evaluation Report: Perfectionism Literacy Lesson", in
# that order). The report's Results (key finding 6) publishes, per question, the
# percentage who agreed or strongly agreed -- useful 75.4%, interesting 72.3%,
# informative 80.0% -- and the percentage who disagreed/strongly disagreed for
# interesting (6.1%) and informative (6.1%) only, i.e. none disagreed that it was
# useful. The three agree percentages are all distinct, so they separate every
# item from every other; any permutation of item_text breaks the match.

suppressMessages(library(irw))

TABLE <- "perfectionismlit_2021_engagement"
TOL   <- 0.1   # published figures are rounded to one decimal

pub <- data.frame(
  item      = c("EQ1", "EQ2", "EQ3"),
  text      = c("useful", "interesting", "informative"),
  agree     = c(75.4, 72.3, 80.0),
  disagree  = c(0,    6.1,  6.1)    # useful: no disagreement reported
)

d <- irw::irw_fetch(TABLE)
obs_agree    <- sapply(pub$item, function(i) 100 * mean(d$resp[d$item == i] >= 4))
obs_disagree <- sapply(pub$item, function(i) 100 * mean(d$resp[d$item == i] <= 2))
n            <- sapply(pub$item, function(i) sum(d$item == i))

cat(sprintf("%-4s %-12s %4s %9s %9s %11s %11s\n",
            "item", "shipped", "n", "pub_agr%", "obs_agr%", "pub_disagr%", "obs_disagr%"))
for (k in seq_len(nrow(pub)))
  cat(sprintf("%-4s %-12s %4d %9.1f %9.2f %11.1f %11.2f\n", pub$item[k], pub$text[k], n[k],
              pub$agree[k], obs_agree[k], pub$disagree[k], obs_disagree[k]))

ok_agree <- all(abs(obs_agree - pub$agree) <= TOL)
ok_dis   <- all(abs(obs_disagree - pub$disagree) <= TOL)

# Every alternative permutation of the three texts must fail the agree match.
perms <- list(c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
alt_ok <- sapply(perms, function(p) all(abs(obs_agree - pub$agree[p]) <= TOL))
cat(sprintf("\nidentity mapping matches agree%%: %s; disagree%%: %s\n", ok_agree, ok_dis))
cat(sprintf("alternative permutations that also match agree%%: %d of 5\n", sum(alt_ok)))
cat("Note: the rounding tolerance absorbs 4/65 = 6.15% published as 6.1.\n")

cat(if (ok_agree && ok_dis && !any(alt_ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
