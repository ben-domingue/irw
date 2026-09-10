# verify_monier_2026_pot.R -- Step 5b re-runnable evidence.
#
# CLAIM: each IRW item code carries its own referent, because the codes ARE the
# S1 Table (10.1371/journal.pone.0352176.s001) column headers verbatim
# (data/monier_2026_pot.py uses ITEM_COLS = the header strings, no rename), and
# each header names its time period: PoTpresent / PoTweek / PoTmonth / PoTyear /
# PoT5yearago / PoT_NowBefore / PoTaging. The paper's Procedure section lists
# exactly those seven periods, split into a 4-item short-period block ("Do you
# think that time passes fast (1) now, (2) this week, (3) this month, (4) this
# year?") and a 3-item long-period block ("Do you think that time passes faster
# (1) now than 5 years ago, (2) now compared to before, and (3) with aging?").
#
# FALSIFIABLE PREDICTION: the paper reports these are "two distinct forms of
# temporal judgment" -- short/recent vs distant-past. If the code->period
# reading were wrong, items would not split into those two blocks. Also checks
# the paper's published Cronbach's alpha of .914 over the seven items.

suppressMessages(library(irw))

TABLE  <- "monier_2026_pot"
SHORT  <- c("PoTpresent_7vite","PoTweek_7vite","PoTmonth_7vite","PoTyear_7vite")
LONG   <- c("PoT5yearago_7vite","PoT_NowBefore_7vite","PoTaging_7vite")
ALPHA_PUBLISHED <- 0.914
ALPHA_TOL <- 0.02

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
m <- as.matrix(w[, c(SHORT, LONG)])
R <- cor(m, use = "pairwise.complete.obs")

cat(sprintf("%-20s %8s %8s %6s\n", "item", "own", "rival", "ok"))
ok <- 0L
for (it in c(SHORT, LONG)) {
    own_g   <- if (it %in% SHORT) SHORT else LONG
    rival_g <- if (it %in% SHORT) LONG  else SHORT
    own   <- mean(R[it, setdiff(own_g, it)])
    rival <- mean(R[it, rival_g])
    good  <- own > rival
    ok <- ok + good
    cat(sprintf("%-20s %8.2f %8.2f %6s\n", it, own, rival,
                if (good) "ok" else "MISS"))
}
cat(sprintf("\n%d/%d items cohere with their hypothesised period block\n",
            ok, length(c(SHORT, LONG))))

# Cronbach's alpha over the seven temporal items (paper: alpha = .914)
cm <- cor(m, use = "pairwise.complete.obs"); k <- ncol(m)
cv <- cov(m, use = "pairwise.complete.obs")
alpha <- (k/(k-1)) * (1 - sum(diag(cv))/sum(cv))
cat(sprintf("Cronbach's alpha: observed %.3f vs published %.3f (diff %.3f, tol %.2f)\n",
            alpha, ALPHA_PUBLISHED, alpha - ALPHA_PUBLISHED, ALPHA_TOL))

cat("Note: the block split confirms the short-vs-long period reading of the codes\n",
    "and alpha confirms the item SET, but neither separates items WITHIN a block\n",
    "(present/week/month/year, or 5yearago/nowbefore/aging). What distinguishes\n",
    "every item from every other is that each code names its own period and the\n",
    "codes are the source spreadsheet's own column headers, unrenamed.\n", sep = "")

pass <- (ok == length(c(SHORT, LONG))) && abs(alpha - ALPHA_PUBLISHED) <= ALPHA_TOL
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
