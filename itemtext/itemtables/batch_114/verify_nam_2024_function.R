# verify_nam_2024_function.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST
#   (a) option_text <-> resp: 1 = "No difficulty", 2 = "Some difficulty",
#       3 = "A lot of difficulty", 4 = "Cannot do at all" (WG-SS canonical coding).
#   (b) item_text <-> item: FL1..FL6 are the WG-SS domains in the canonical order the
#       paper itself lists them -- seeing, hearing, walking/climbing steps,
#       remembering or concentrating, self-care (washing/dressing), communicating.
#
# The mapping, not the plumbing: every number below would move if the option
# direction were flipped, or if the mobility/self-care items sat elsewhere.

suppressMessages(library(irw))
TABLE <- "nam_2024_function"

# --- Published values, Nam & Yoon (2024) PLOS ONE 19(3):e0299971 ------------------
# Table 1, "Functional limitation": No 79 (36.9), Yes 135 (63.1).
# Footnote b: "Respondents reporting 'some difficulty', 'a lot of difficulty', or
# 'cannot do at all' in at least one of the six core domains in the Washington Group
# Short Set on Functioning".
PUB_YES <- 135L
PUB_NO  <-  79L

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
m <- as.matrix(w[, paste0("FL", 1:6)])
ok <- logical(0)

# --- CHECK 1 (route 3 / route 9, OPTION AXIS): the paper's own dichotomisation -----
# Only true if resp 1 is the no-difficulty category and 2/3/4 are the three
# difficulty categories. A flipped scale (4 = No difficulty) gives 214 and 0 here.
obs_yes <- sum(apply(m, 1, function(r) any(r >= 2)))
obs_no  <- sum(apply(m, 1, function(r) all(r == 1)))
cat("CHECK 1 -- Table 1 'Functional limitation' (option direction)\n")
cat(sprintf("  Yes (any domain >= 2): published %d (%.1f%%)  observed %d (%.1f%%)\n",
            PUB_YES, 100 * PUB_YES / nrow(m), obs_yes, 100 * obs_yes / nrow(m)))
cat(sprintf("  No  (all domains = 1): published %d (%.1f%%)  observed %d (%.1f%%)\n",
            PUB_NO, 100 * PUB_NO / nrow(m), obs_no, 100 * obs_no / nrow(m)))
flip_yes <- sum(apply(m, 1, function(r) any(r <= 3)))
cat(sprintf("  (reversed reading, 4 = No difficulty, would give Yes = %d)\n", flip_yes))
ok <- c(ok, obs_yes == PUB_YES && obs_no == PUB_NO)

# --- CHECK 2 (route 8, ITEM AXIS): sample is diabetic patients with PHYSICAL --------
# disabilities (84.1% severe per the paper's text), so the mobility item and the
# self-care item must carry the most difficulty of the six.
mu <- colMeans(m)
cat("\nCHECK 2 -- per-item means; mobility (FL3) and self-care (FL5) should lead\n")
lbl <- c(FL1 = "seeing", FL2 = "hearing", FL3 = "walking/steps",
         FL4 = "remembering", FL5 = "self-care", FL6 = "communicating")
for (i in names(mu)) cat(sprintf("  %-4s %-14s mean %.3f  %%>=2 %.1f\n",
                                 i, lbl[i], mu[i], 100 * mean(m[, i] >= 2)))
top2 <- names(sort(mu, decreasing = TRUE))[1:2]
cat(sprintf("  two highest: %s (expected FL3, FL5 in some order)\n",
            paste(top2, collapse = ", ")))
ok <- c(ok, setequal(top2, c("FL3", "FL5")))

# --- CHECK 3 (route 5, ITEM AXIS): correlation block structure ---------------------
# Seeing and hearing are the sensory pair and should be the tightest pair in the
# matrix; walking and communicating are the most distant domains.
r <- cor(m)
diag(r) <- NA
cat("\nCHECK 3 -- correlation structure\n")
print(round(cor(m), 3))
pairs <- which(upper.tri(r), arr.ind = TRUE)
vals  <- r[upper.tri(r)]
nm    <- apply(pairs, 1, function(p) paste0(rownames(r)[p[1]], "-", colnames(r)[p[2]]))
cat(sprintf("  strongest pair: %s r = %.3f (expected FL1-FL2, seeing/hearing)\n",
            nm[which.max(vals)], max(vals)))
cat(sprintf("  weakest pair:   %s r = %.3f (expected FL3-FL6, walking/communicating)\n",
            nm[which.min(vals)], min(vals)))
ok <- c(ok, nm[which.max(vals)] == "FL1-FL2", nm[which.min(vals)] == "FL3-FL6")

# --- What this does NOT establish -------------------------------------------------
cat("\nNOT ESTABLISHED: nothing here separates FL1 from FL2 (both checks that touch\n",
    "them are symmetric in the pair), and FL4 vs FL6 rests only on check 3's\n",
    "a-priori expectation that walking is furthest from communicating. Their means\n",
    "are 1.66/1.62 and 1.64/1.67 -- indistinguishable. Hence PARTIAL, not VERIFIED.\n",
    sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
