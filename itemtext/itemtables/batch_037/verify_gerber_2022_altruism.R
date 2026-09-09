# verify_gerber_2022_altruism.R -- Step 5b mapping check.
#
# CLAIM UNDER TEST: alt1..alt14 are the 14 items of the Witt & Boleman child
# adaptation of Rushton's Self-Report Altruism Scale, in the adaptation's own
# order (= Rushton's 1981 order with items 1,5,7,8,12,15 dropped):
#   1 directions, 2 make change, 3 money to charity, 4 clothes/goods,
#   5 carry belongings, 6 hold door, 7 go ahead in line, 8 cashier's error,
#   9 neighbour borrows a valuable, 10 classmate's homework, 11 neighbour's
#   pet/children, 12 elderly person across the street, 13 seat on bus/train,
#   14 help a neighbour move house.
# Nothing in the deposit labels the columns, so this is what stands in for a
# label match. Two routes, neither of which separates every item.

suppressMessages(library(irw))
TABLE <- "gerber_2022_altruism"

d <- as.data.frame(irw::irw_fetch(TABLE))
d$key <- paste(d$id, d$wave, sep = "_")
codes <- paste0("alt", 1:14)
W <- reshape(d[, c("key", "item", "resp")], idvar = "key", timevar = "item",
             direction = "wide")
colnames(W) <- sub("^resp\\.", "", colnames(W))
W <- W[, codes]

means <- sapply(W, mean, na.rm = TRUE)
tot <- rowSums(W)
itc <- sapply(codes, function(k) suppressWarnings(cor(W[[k]], tot - W[[k]],
                                                      use = "complete.obs")))

# ---- Route 7, marker item -------------------------------------------------
# Published single-factor (principal axis) loadings for the SAME 14-item
# instrument in the SAME canonical order, from the Urdu translation/validation
# of Witt & Boleman (2009): Pakistan Journal of Humanities and Social Sciences
# 10(3), 2022, Table 2, N = 400 adults.
URDU <- c(0.576, 0.754, 0.696, 0.698, 0.483, 0.725, 0.613, 0.363,
          0.417, 0.502, 0.692, 0.671, 0.655, 0.576)
names(URDU) <- codes

cat(sprintf("%-6s %8s %8s %14s\n", "item", "mean", "item-tot", "urdu loading"))
for (k in codes)
  cat(sprintf("%-6s %8.2f %8.3f %14.3f\n", k, means[k], itc[k], URDU[k]))

cat(sprintf("\nlowest item-total in live data : %s (%.3f); next lowest %s (%.3f)\n",
            names(which.min(itc)), min(itc),
            names(sort(itc)[2]), sort(itc)[2]))
cat(sprintf("lowest published loading       : %s (%.3f); next lowest %s (%.3f)\n",
            names(which.min(URDU)), min(URDU),
            names(sort(URDU)[2]), sort(URDU)[2]))

ok_marker <- names(which.min(itc)) == "alt8" && names(which.min(URDU)) == "alt8"

# ---- Route 8, semantic coherence of the response distribution -------------
# Frequency-of-intention responses from 6-16 year olds: the acts a child is
# least able to perform must sit at the bottom, the taught courtesies at the top.
low3  <- names(sort(means))[1:3]          # expect make change / lend valuable / cede place in line
high2 <- names(sort(means, decreasing = TRUE))[1:2]  # expect elderly crossing / give up seat
cat(sprintf("\nthree lowest means : %s (%.2f, %.2f, %.2f)  [expected alt2, alt9, alt7]\n",
            paste(low3, collapse = ", "), means[low3[1]], means[low3[2]], means[low3[3]]))
cat(sprintf("two highest means  : %s (%.2f, %.2f)  [expected alt12, alt13]\n",
            paste(high2, collapse = ", "), means[high2[1]], means[high2[2]]))
ok_sem <- setequal(low3, c("alt2", "alt9", "alt7")) && setequal(high2, c("alt12", "alt13"))

cat("\nWhat this does NOT establish: the mid-range items are not separated from\n",
    "one another -- alt4 and alt11 (2.49), alt10 (2.47), alt3 and alt8 (2.22) sit\n",
    "inside sampling noise of each other, so a swap within that block would not\n",
    "show up here. Position 8 and the three floor / two ceiling items are pinned;\n",
    "the rest rests on the instrument's published item order. Status PARTIAL.\n",
    sep = "")

cat(if (ok_marker && ok_sem) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
