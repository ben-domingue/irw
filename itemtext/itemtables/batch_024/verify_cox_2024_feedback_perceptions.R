# verify_cox_2024_feedback_perceptions.R
#
# Claim: each IRW item code (confidence/interest/effort/importance/frequency)
# carries the wording of the S1 Dataset column it was renamed from.
# Falsifiable prediction: Cox, Arthur & Burtson (2024) PLOS ONE 19(4):e0300205
# report per-question pre- and post-workshop mean+-SD in the Results text
# (Table 1). Those 10 numbers must reproduce from the live table's
# item x wave means. All five items have distinct mean profiles, so a swap of
# any pair breaks the comparison.

suppressMessages(library(irw))

TABLE <- "cox_2024_feedback_perceptions"

# Published mean (SD), Results section / Table 1. wave 1 = pre, wave 2 = post.
PUB <- data.frame(
  item = c("confidence", "effort",  "frequency", "interest", "importance"),
  pre  = c(3.52,          4.14,      4.34,        4.83,       4.79),
  pre_sd = c(0.57,        0.74,      0.55,        0.38,       0.49),
  post = c(4.37,          4.50,      4.75,        4.83,       4.87),
  post_sd = c(0.58,       0.59,      0.53,        0.48,       0.45),
  stringsAsFactors = FALSE
)
TOL <- 0.02

d <- irw::irw_fetch(TABLE)
m <- function(it, w) mean(d$resp[d$item == it & d$wave == w])
s <- function(it, w) sd(d$resp[d$item == it & d$wave == w])

cat(sprintf("%-11s %9s %9s %8s | %9s %9s %8s\n",
            "item", "pub.pre", "obs.pre", "diff", "pub.post", "obs.post", "diff"))
worst <- 0
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]
  op <- m(it, 1); oq <- m(it, 2)
  cat(sprintf("%-11s %9.2f %9.2f %8.3f | %9.2f %9.2f %8.3f\n",
              it, PUB$pre[i], op, op - PUB$pre[i], PUB$post[i], oq, oq - PUB$post[i]))
  worst <- max(worst, abs(op - PUB$pre[i]), abs(oq - PUB$post[i]))
}

cat("\nSDs (published vs observed):\n")
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]
  cat(sprintf("%-11s pre %.2f/%.2f  post %.2f/%.2f\n",
              it, PUB$pre_sd[i], s(it, 1), PUB$post_sd[i], s(it, 2)))
}

cat(sprintf("\nlargest mean deviation: %.3f (tolerance %.2f)\n", worst, TOL))
cat("This distinguishes every item from every other: the five pre-means\n",
    "(3.52/4.14/4.34/4.79/4.83) and post-means (4.37/4.50/4.75/4.83/4.87) are\n",
    "mutually distinct except interest-vs-importance at post (4.83 vs 4.87,\n",
    "separated at pre by 4.83 vs 4.79 and by their SDs).\n",
    "It does NOT independently check the option_text->resp anchor mapping,\n",
    "which is taken verbatim from the paper's stated 1=never..5=almost always.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
