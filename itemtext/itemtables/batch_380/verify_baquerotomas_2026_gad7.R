# verify_baquerotomas_2026_gad7.R -- Step 5b mapping check (batch_380).
#
# Claim: GAD7_1..GAD7_7 (the deposit's own unlabelled .sav column names) are the
# GAD-7 items in the instrument's fixed published order, 1..7. The .sav carries
# no variable labels, so the order is inferred, not read. This script tests the
# parts of that claim the data can speak to:
#
#   P1 (item 5, content twin): GAD-7 item 5 "restless, hard to sit still" is the
#      only GAD item sharing content with PHQ-9 item 8 (psychomotor "fidgety or
#      restless"), administered to the same 566 students. Predict GAD7_5 is the
#      GAD item most correlated with PHQ9_8, AND PHQ9_8 is GAD7_5's strongest
#      PHQ-9 correlate (reciprocal).
#   P2 (PHQ-9 anchor for P1): PHQ9_9 (self-harm) is the least endorsed PHQ item
#      -- checks the PHQ numbering P1 leans on is itself in canonical order at
#      the end.
#   P3 (item 7, marker): "afraid something awful might happen" is the most
#      severe GAD-7 symptom; predict GAD7_7 has the lowest mean of the seven.
#
# What this does NOT establish: the relative order of items 1, 2, 3, 4 and 6.
# Those share one response scale and have no distinguishing statistic here, so
# the verification is PARTIAL, not VERIFIED.

suppressMessages(library(irw))

g <- irw::irw_fetch("baquerotomas_2026_gad7")
p <- irw::irw_fetch("baquerotomas_2026_phq9")
gw <- reshape(as.data.frame(g[, c("id", "item", "resp")]), idvar = "id",
              timevar = "item", direction = "wide")
pw <- reshape(as.data.frame(p[, c("id", "item", "resp")]), idvar = "id",
              timevar = "item", direction = "wide")
names(gw) <- sub("^resp\\.", "", names(gw)); names(pw) <- sub("^resp\\.", "", names(pw))
w <- merge(gw, pw, by = "id")
cat("respondents joined on id:", nrow(w), "\n\n")

G <- paste0("GAD7_", 1:7); P <- paste0("PHQ9_", 1:9)
cg <- sapply(G, function(x) cor(w[[x]], w[["PHQ9_8"]], use = "pair"))
cat("corr(GAD_i, PHQ9_8):\n"); print(round(cg, 3))
c5 <- sapply(P, function(x) cor(w[["GAD7_5"]], w[[x]], use = "pair"))
cat("\ncorr(GAD7_5, PHQ_j):\n"); print(round(c5, 3))
p1 <- names(which.max(cg)) == "GAD7_5" && names(which.max(c5)) == "PHQ9_8"
cat(sprintf("\nP1 GAD7_5 <-> PHQ9_8 reciprocal max: %s (margin over next GAD item %.3f)\n",
            p1, sort(cg, decreasing = TRUE)[1] - sort(cg, decreasing = TRUE)[2]))

pm <- tapply(p$resp, p$item, mean)[P]
cat("\nPHQ-9 item means:\n"); print(round(pm, 2))
p2 <- names(which.min(pm)) == "PHQ9_9"
cat("P2 PHQ9_9 least endorsed:", p2, "\n")

gm <- tapply(g$resp, g$item, mean)[G]
cat("\nGAD-7 item means:\n"); print(round(gm, 2))
p3 <- names(which.min(gm)) == "GAD7_7"
cat("P3 GAD7_7 lowest mean:", p3, "\n\n")

cat("Not established: order among GAD7_1, _2, _3, _4, _6.\n")
cat(if (p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
