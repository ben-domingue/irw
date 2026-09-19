# verify_matarboumosleh_2017_gad2.R
#
# What is being verified: the option_text <-> resp mapping (the DIRECTION of the
# GAD-2 frequency anchors). The item_text <-> item axis is exempt: the live item
# codes ARE the source spreadsheet's own column headers
# (S1 Dataset, journal.pone.0182239.s001, columns "Feel_anxious" and
# "NotAble_Stpworry"), data/matarboumosleh_2017_smartphone_depr_anx.py melts them
# by name, and the two codes are self-describing and mutually exclusive in content
# ("feel anxious" vs "not able to stop worrying") -- a swap would be self-evident.
#
# The falsifiable claim: 0 = "Not at all" ... 3 = "Nearly every day" (the printed
# coding on the GAD-7 form), stored UNREVERSED. Under the flipped assignment every
# observed value v would mean 3 - v.
#
# Two hard-coded facts from the deposit S1 Dataset (fetched 2026-09-08), which the
# live table cannot supply because the processing script drops the total column:
#   - Anxiety_score == Feel_anxious + NotAble_Stpworry exactly, over all 407
#     complete cases (max abs difference 0.0). So the study's own total is the RAW
#     unreversed sum; nothing was reverse-scored on the way in.
#   - Under the shipped anchors the sample mean GAD-2 total is 1.97 (SD 1.39) and
#     26.5% score >= 3, the standard GAD-2 positive-screen cut-point. Under the
#     flipped anchors it would be 4.03 and 85.7% -- i.e. six in seven of an
#     unselected undergraduate sample screening positive for generalized anxiety.

suppressMessages(library(irw))

TABLE <- "matarboumosleh_2017_gad2"
DEPOSIT_TOTAL_MEAN <- 1.97   # S1 Dataset, shipped-anchor reading
DEPOSIT_POSRATE    <- 0.265  # share with total >= 3, shipped-anchor reading

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)

cat("--- response distribution, live table ---\n")
tb <- table(d$item, d$resp)
lab <- c("0 Not at all", "1 Several days", "2 More than half the days", "3 Nearly every day")
cat(sprintf("%-18s %s\n", "item", paste(sprintf("%26s", lab), collapse = "")))
for (i in rownames(tb))
    cat(sprintf("%-18s %s\n", i, paste(sprintf("%26d", as.integer(tb[i, ])), collapse = "")))

m_ship <- mean(d$resp)
m_flip <- mean(3 - d$resp)
cat(sprintf("\nmean response, anchors AS SHIPPED (0=Not at all): %.3f\n", m_ship))
cat(sprintf("mean response, anchors FLIPPED  (0=Nearly every day): %.3f\n", m_flip))

# per-respondent GAD-2 total, both readings
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
w <- w[complete.cases(w), ]
tot_ship <- rowSums(w[, -1])
tot_flip <- rowSums(3 - w[, -1])
cat(sprintf("\ncomplete respondents: %d\n", nrow(w)))
cat(sprintf("GAD-2 total AS SHIPPED : mean %.2f, SD %.2f, %% >= 3 = %.1f%%  (deposit: %.2f, %.1f%%)\n",
            mean(tot_ship), sd(tot_ship), 100 * mean(tot_ship >= 3),
            DEPOSIT_TOTAL_MEAN, 100 * DEPOSIT_POSRATE))
cat(sprintf("GAD-2 total FLIPPED    : mean %.2f, SD %.2f, %% >= 3 = %.1f%%\n",
            mean(tot_flip), sd(tot_flip), 100 * mean(tot_flip >= 3)))

ok_total  <- abs(mean(tot_ship) - DEPOSIT_TOTAL_MEAN) < 0.15
ok_posrate <- abs(mean(tot_ship >= 3) - DEPOSIT_POSRATE) < 0.03
ok_dir    <- mean(tot_ship) < 3   # below the 0-6 midpoint; the flipped reading is above it

cat("\nWhat this does NOT establish: it fixes the DIRECTION of the anchors only.\n")
cat("It cannot separate the two interior anchors ('Several days' vs 'More than half\n")
cat("the days') from each other by data alone -- those come from the printed 0/1/2/3\n")
cat("coding on the official GAD-7 form, not from this check. It also says nothing\n")
cat("about the item axis, which is exempt (item codes are the source column names).\n")

cat(if (ok_total && ok_posrate && ok_dir) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
