# verify_jeon_2019_cbi.R -- Step 5b evidence, re-runnable.
#
# Claim being tested (the two things that could be wrong and that
# validate_items.R cannot see):
#
#  (a) SUBSCALE MEMBERSHIP -- BT_I_* = personal burnout, BT_W_* = work-related,
#      BT_C_* = client-related, exactly as the shipped section_prompt/item_text
#      assign them.
#  (b) THE DIRECTION OF `resp` ON BT_W_4 -- the shipped option_text runs the
#      normal way (0 = "never/0%" ... 4 = "always/100%") for 18 of the 19 items
#      but is INVERTED for BT_W_4, on the claim that the deposited .sav already
#      holds that item reverse-scored.
#
# Falsifiable prediction: Jeon et al. (2019) PLOS ONE 14(8):e0221323 report
# subscale means on the CBI's 0-100 metric (resp * 25), N = 464:
#     PB 38.59 (SD 18.52), WRB 33.94 (SD 17.81), CRB 34.88 (SD 18.36).
# The WRB figure is the discriminating one: it reproduces ONLY if BT_W_4 is
# averaged as stored. Reversing BT_W_4 first gives ~36.12, off by 2.2 points.
#
# The table is 8,816 rows, so irw_fetch() here is a trivial export.

suppressMessages(library(irw))

TABLE <- "jeon_2019_cbi"
PUB <- c(PB = 38.59, WRB = 33.94, CRB = 34.88)
PUB_SD <- c(PB = 18.52, WRB = 17.81, CRB = 18.36)
TOL <- 0.05

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
d$score100 <- d$resp * 25

grp <- function(pfx) d[grepl(pfx, d$item), ]
per_person <- function(sub) {
    m <- tapply(sub$score100, sub$id, mean)
    c(mean = mean(m), sd = sd(m))
}

obs <- rbind(PB  = per_person(grp("^BT_I_")),
             WRB = per_person(grp("^BT_W_")),
             CRB = per_person(grp("^BT_C_")))

cat(sprintf("N respondents: %d | rows: %d\n\n", length(unique(d$id)), nrow(d)))
cat(sprintf("%-5s %10s %10s %8s | %10s %10s\n",
            "sub", "pub.mean", "obs.mean", "diff", "pub.sd", "obs.sd"))
for (s in rownames(obs))
    cat(sprintf("%-5s %10.2f %10.2f %8.3f | %10.2f %10.2f\n",
                s, PUB[s], obs[s, "mean"], obs[s, "mean"] - PUB[s],
                PUB_SD[s], obs[s, "sd"]))

# --- the BT_W_4 direction, stated as the counterfactual -------------------
w <- grp("^BT_W_")
wide <- reshape(w[, c("id", "item", "score100")], idvar = "id",
                timevar = "item", direction = "wide")
rownames(wide) <- wide$id; wide$id <- NULL
colnames(wide) <- sub("^score100\\.", "", colnames(wide))
as_stored <- mean(rowMeans(wide))
flipped   <- wide; flipped[["BT_W_4"]] <- 100 - flipped[["BT_W_4"]]
as_flipped <- mean(rowMeans(flipped))
cat(sprintf("\nWRB mean with BT_W_4 as stored : %.2f  (published %.2f)\n", as_stored, PUB["WRB"]))
cat(sprintf("WRB mean with BT_W_4 reversed  : %.2f\n", as_flipped))

# Item-rest correlation of BT_W_4 against the other 18 items, as stored.
allw <- reshape(d[, c("id", "item", "resp")], idvar = "id",
                timevar = "item", direction = "wide")
rownames(allw) <- allw$id; allw$id <- NULL
colnames(allw) <- sub("^resp\\.", "", colnames(allw))
rest <- rowSums(allw[, setdiff(colnames(allw), "BT_W_4")])
r <- cor(allw[["BT_W_4"]], rest)
cat(sprintf("BT_W_4 item-rest r (as stored)  : %+.3f   (paper's loading for this item: +0.16 / +0.19)\n", r))
cat("A raw, positively-worded 'do you have enough energy' item would correlate NEGATIVELY here.\n")

worst <- max(abs(obs[, "mean"] - PUB[rownames(obs)]))
cat(sprintf("\nlargest subscale-mean deviation: %.3f (tolerance %.2f)\n", worst, TOL))

cat("Note: this route establishes subscale MEMBERSHIP and the resp direction of\n",
    "BT_W_4; it does not order items WITHIN a subscale. That is settled instead by\n",
    "the .sav's own variable labels, which sit on the very columns the IRW `item`\n",
    "codes are copied from (19/19), cross-read against S1 Fig's 6/7/6 questionnaire.\n", sep = "")

ok <- worst <= TOL && r > 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
