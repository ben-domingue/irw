# verify_shinohara_2021_testimony.R -- Step 5b check for batch_174.
#
# Claim being verified (both mapping axes):
#   item axis: allo_* = reward-allocation task, anti_* = reward-anticipation task,
#     eva_* = explicit evaluation; *_observation = puppet A (first-hand observation),
#     *_valence testimony = puppet B (positive/negative testimony),
#     *_neutral testimony = puppet C (neutral testimony).
#   resp axis: allo/anti 1 = high reward / first choice, 2 = medium, 3 = low reward /
#     least desired (NOT "higher = larger reward", as data/shinohara_2021_testimony.py's
#     header comment says); eva -2..2 = very bad..very good.
#
# Published values hard-coded from Shinohara et al. (2021) PLOS ONE 16(12):e0261075:
#   Results text (reward-allocation / reward-anticipation counts) and Table 1
#   (t001 image, mean rating scores by condition x age x puppet).
# Only the live IRW table is fetched (1,152 rows; carries cov_condition and cov_age).

suppressMessages(library(irw))
TABLE <- "shinohara_2021_testimony"
d <- as.data.frame(irw::irw_fetch(TABLE))
d$item <- as.character(d$item)
w <- reshape(d[, c("id", "item", "resp", "cov_condition", "cov_age")],
             idvar = c("id", "cov_condition", "cov_age"), timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cat("children:", nrow(w), "\n")
P <- c("observation", "valence testimony", "neutral testimony")
ok <- TRUE

## ---- Route 1a: reward-task counts (Results text) -------------------------------
# stat(task_data, spec) -> vector of counts for puppets A,B,C, or medium B,A
counts <- function(get, cond, age, val) {
  s <- w$cov_condition == cond & (is.na(age) | w$cov_age == age)
  sapply(P, function(p) sum(get(p)[s] == val))
}
medium_given_C_high <- function(get) {
  s <- w$cov_condition == "negative" & w$cov_age == "7y" & get("neutral testimony") == 1
  c(B = sum(get("valence testimony")[s] == 2), A = sum(get("observation")[s] == 2))
}
pub <- list(
  allo = list(pos_low = c(15, 20, 29), neg5_high = c(10, 7, 15), neg7_high = c(2, 2, 28), med7 = c(20, 8)),
  anti = list(pos_low = c(17, 19, 28), neg5_high = c(9, 9, 14), neg7_high = c(2, 3, 27), med7 = c(15, 12)))
stats_for <- function(cols, low = 3, high = 1) {
  get <- function(p) w[[cols[match(p, P)]]]
  list(pos_low = counts(get, "positive", NA, low),
       neg5_high = counts(get, "negative", "5y", high),
       neg7_high = counts(get, "negative", "7y", high),
       med7 = unname(medium_given_C_high(get)))
}
match_pub <- function(st, pb) all(mapply(function(a, b) all(a == b), st, pb))

cat("\n== Reward tasks: live counts under the shipped mapping vs published ==\n")
for (task in c("allo", "anti")) {
  st <- stats_for(paste0(task, "_", P))
  for (k in names(st))
    cat(sprintf("%-4s %-9s live %-12s published %-12s %s\n", task, k,
                paste(st[[k]], collapse = "/"), paste(pub[[task]][[k]], collapse = "/"),
                if (all(st[[k]] == pub[[task]][[k]])) "ok" else "MISMATCH"))
  if (!match_pub(st, pub[[task]])) ok <- FALSE
}

# Direction: under the reverse reading (3 = high reward) the published counts must fail.
cat("\n== Direction test: reverse reading (3 = high, 1 = low) ==\n")
for (task in c("allo", "anti")) {
  st <- stats_for(paste0(task, "_", P), low = 1, high = 3)
  cat(sprintf("%-4s pos_low %s (pub %s)  neg7_high %s (pub %s) -> %s\n", task,
              paste(st$pos_low, collapse = "/"), paste(pub[[task]]$pos_low, collapse = "/"),
              paste(st$neg7_high, collapse = "/"), paste(pub[[task]]$neg7_high, collapse = "/"),
              if (match_pub(st, pub[[task]])) "MATCHES (bad)" else "fails, as it should"))
  if (match_pub(st, pub[[task]])) ok <- FALSE
}

# Exhaustive: all 720 assignments of the 6 reward-task codes to the 6 (task, puppet) slots.
cat("\n== Exhaustive permutation test over the 6 reward-task codes ==\n")
codes <- c(paste0("allo_", P), paste0("anti_", P))
perms <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
hits <- 0; hit_ids <- character(0)
for (pm in perms(codes)) {
  if (match_pub(stats_for(pm[1:3]), pub$allo) && match_pub(stats_for(pm[4:6]), pub$anti)) {
    hits <- hits + 1; hit_ids <- c(hit_ids, paste(pm, collapse = ","))
  }
}
cat("assignments reproducing every published count:", hits, "of 720\n")
cat(" ", hit_ids, sep = "\n  ")
if (hits != 1 || hit_ids[1] != paste(codes, collapse = ",")) ok <- FALSE

## ---- Route 1b: explicit evaluation, Table 1 means (SD) ---------------------------
cat("\n== Explicit evaluation: live M (SD) vs Table 1 ==\n")
T1 <- rbind(  # rows: cond x age; cols: observation, valence testimony, neutral testimony
  "positive.5y" = c(1.31, 1.28, 1.03), "positive.7y" = c(1.81, 1.59, 0.78),
  "negative.5y" = c(-0.59, -0.38, 1.22), "negative.7y" = c(-1.25, -1.06, 1.25))
T1sd <- rbind(
  "positive.5y" = c(0.97, 1.05, 1.09), "positive.7y" = c(0.40, 0.61, 0.71),
  "negative.5y" = c(1.36, 1.39, 0.79), "negative.7y" = c(0.62, 0.88, 0.80))
eva_tab <- function(cols) {
  m <- s <- T1 * NA
  for (r in rownames(T1)) {
    cc <- strsplit(r, ".", fixed = TRUE)[[1]]
    sel <- w$cov_condition == cc[1] & w$cov_age == cc[2]
    m[r, ] <- sapply(cols, function(x) mean(w[[x]][sel]))
    s[r, ] <- sapply(cols, function(x) sd(w[[x]][sel]))
  }
  list(m = m, s = s)
}
e <- eva_tab(paste0("eva_", P))
for (r in rownames(T1)) for (j in 1:3)
  cat(sprintf("%-12s %-18s live %5.2f (%.2f)  pub %5.2f (%.2f)\n", r, P[j],
              e$m[r, j], e$s[r, j], T1[r, j], T1sd[r, j]))
dev <- max(abs(round(e$m, 2) - T1), abs(round(e$s, 2) - T1sd))
cat(sprintf("largest |live - published| after rounding to 2dp: %.3f\n", dev))
if (dev > 0.011) ok <- FALSE
cat("\nOther eva assignments (6 permutations x sign flip), max abs mean deviation:\n")
for (pm in perms(paste0("eva_", P))) for (sg in c(1, -1)) {
  ee <- eva_tab(pm); dv <- max(abs(sg * ee$m - T1))
  cat(sprintf("  %-60s sign %+d  %.3f\n", paste(pm, collapse = ", "), sg, dv))
  if (!(identical(pm, paste0("eva_", P)) && sg == 1) && dv < 0.02) ok <- FALSE
}

cat("\nNOT established by this script: the literal wording children heard. The paper\n",
    "reports the task prompts as Methods narration in English for a Japanese\n",
    "administration; this checks which code is which task/puppet and the resp direction only.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
