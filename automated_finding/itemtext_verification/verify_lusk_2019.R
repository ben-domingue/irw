# verify_lusk_2019.R -- Step 5b, re-runnable evidence (automated_finding, cleaned-leads item text 2026-11-07).
#
# CLAIM: in the five lusk_2019_*__items.csv tables, the item_text given for
# each deposit code (Q9_1.., Q13_.., Q14_.., Q18_.., Q28_..) is the statement
# that code actually recorded -- including the two blocks the deposit
# renumbered against the codebook (deposit Q9_10/11/12 = codebook Q9_12/13/15;
# deposit Q28_6/7/8 = codebook Q28_7/8/9).
#
# ROUTE: the deposit's own "CRA Survey Topline results.pdf" (Dataverse
# datafile 3594771) prints each statement's response percentages, labelled by
# wording rather than by code. The topline is WEIGHTED to U.S. population
# margins ("Responses are weighted to match the U.S. population in terms of
# gender, age, ..."). The deposit carries those weights (data_to_share_2,
# column wts), so the script downloads the deposit and reweights each item's
# observed distribution by wts, joining on id = the deposit's ID. Within a block, the cost matrix observed-item x topline-row
# is solved as an assignment problem (clue::solve_LSAP, minimum total L1);
# the PASS condition is that the optimal assignment of codes to wordings is
# exactly the shipped one. The margin by which that assignment beats the best
# assignment differing from it is printed per block.
#
# Unweighted, three Q9 pairs are too close to separate (Q9_1/Q9_11,
# Q9_4/Q9_12, Q9_6/Q9_8); reweighting is what makes the route decisive.
#
# Data: the staged response CSVs (cleaned-leads batch 2). Set LUSK_RESP_DIR,
# or run from a checkout whose automated_finding/irw_output holds them.

dir <- Sys.getenv("LUSK_RESP_DIR", "automated_finding/irw_output")
itdir <- Sys.getenv("LUSK_ITEMS_DIR", "automated_finding/itemtext_output")

TOP <- list(
  lusk_2019_natural_processing = rbind(
    "Chopped (e.g., baby carrots, sliced apples, cut watermelon)" = c(76.9, 17.8, 5.3),
    "Vegetable oil from pressed grains like soybeans, corn, or canola" = c(51.3, 32.6, 16.2),
    "Fermentation (e.g., sauerkraut, yogurt, bread, beer)" = c(50.4, 31.4, 18.1),
    "Preserved by canning, freezing, pasteurization, or smoking" = c(41.0, 35.1, 23.9),
    "Preserved with sugar, salt, or vinegar" = c(36.6, 31.7, 31.7),
    "Washing (e.g., cleaning grains or fruits and vegetables using organic acids or cholrine)" = c(36.2, 32.9, 31.0),
    "Extracted starch from corn, potatoes, or wheat" = c(32.9, 38.9, 28.2),
    "Flavor enhanced with sugar, salt, or smoking" = c(24.4, 31.6, 44.1),
    "Added enzymes to improve texture (e.g., in cheese or bread)" = c(11.9, 31.3, 56.8),
    "Appearance altered through decoloring or bleaching (e.g., flour, sugar, rice)" = c(6.9, 21.2, 71.9),
    "Preserved with benzoates, nitrites, sulphites, or sorbates" = c(6.6, 19.6, 73.8),
    "Flavor enhanced with MSG, guanylic acid, or Monopotassium glutamate" = c(6.1, 15.1, 78.9)),
  lusk_2019_natural_farming = rbind(
    "organically grown crops" = c(83.3, 13.4, 3.4),
    "crops grown indoors in greenhouses" = c(70.4, 23.9, 5.7),
    "hydroponically grown crops" = c(44.3, 34.6, 21.1),
    "hybrid seeds" = c(29.1, 37.7, 33.2),
    "crops sprayed with natural pesticides like copper sulfate or bacillus thuringiensis" = c(23.0, 32.6, 44.4),
    "seeds created with genetic engineering or GMOs" = c(11.6, 22.9, 65.5),
    "seeds created using gene editing" = c(11.1, 27.5, 61.5),
    "seeds created using mutagenesis" = c(9.5, 37.8, 52.7),
    "crops sprayed with synthetic pesticides like glyphosate or chlorpyrifos" = c(7.1, 17.7, 75.2)),
  lusk_2019_natural_beliefs = rbind(
    "Natural food is healthier" = c(2.7, 3.1, 17.4, 39.9, 36.9),
    "Natural food is better for the environment" = c(2.3, 4.5, 24.4, 37.9, 31.0),
    "Natural food is tastier" = c(4.0, 11.9, 40.2, 25.7, 18.3),
    "Natural food is more affordable" = c(23.6, 36.9, 22.0, 11.0, 6.5),
    "Natural food is safer to eat" = c(2.7, 4.8, 20.9, 38.0, 33.5),
    "Natural food is more convenient to eat" = c(6.8, 21.1, 42.7, 18.0, 11.4),
    "Natural food is more sustainable" = c(3.2, 9.7, 35.7, 28.9, 22.4)),
  lusk_2019_healthy_foods = rbind(
    "Fresh vegetables" = c(96.2, 3.0, 0.9), "Fresh fruit" = c(95.6, 3.9, 0.5),
    "Fish" = c(87.8, 10.2, 2.1), "Chicken" = c(79.5, 16.7, 3.8), "Eggs" = c(79.2, 18.2, 2.6),
    "Milk" = c(70.4, 22.6, 7.0), "Frozen vegetables" = c(69.7, 26.6, 3.7),
    "Frozen fruit" = c(63.8, 31.1, 5.2), "Cheese" = c(57.3, 33.3, 9.5), "Beef" = c(52.4, 35.1, 12.6),
    "Canned vegetables" = c(43.2, 41.4, 15.4), "Canned fruit" = c(37.3, 41.2, 21.6),
    "Vegetable oil" = c(25.0, 49.2, 25.8), "Bakery and cereal items" = c(23.3, 43.7, 33.0),
    "Candy" = c(4.1, 16.1, 79.8)),
  lusk_2019_healthy_beliefs = rbind(
    "Healthy food is safer to eat" = c(2.3, 4.8, 26.0, 39.5, 27.5),
    "Individual needs determine whether various foods are healthy for an individual" = c(1.4, 6.4, 21.2, 43.8, 27.2),
    "Healthy food is more natural" = c(2.9, 5.5, 24.4, 41.5, 25.7),
    "Healthy food is better for the environment" = c(3.5, 5.5, 38.3, 30.6, 22.1),
    "Healthy food is more sustainable" = c(2.7, 9.2, 40.2, 29.8, 18.1),
    "Healthy food is tastier" = c(5.7, 16.4, 43.9, 20.7, 13.4),
    "Healthy food is more convenient to eat" = c(9.2, 24.1, 42.2, 14.4, 10.1),
    "Healthy food is more affordable" = c(22.3, 35.5, 27.8, 7.6, 6.8)))

raw <- read.csv(Sys.getenv("LUSK_RAW", "https://dataverse.harvard.edu/api/access/datafile/3792855?format=original"))
W <- setNames(raw$wts, raw$ID)
ok <- TRUE
for (tab in names(TOP)) {
  d <- read.csv(file.path(dir, paste0(tab, ".csv")))
  it <- unique(read.csv(file.path(itdir, paste0(tab, "__items.csv")))[, c("item", "item_text")])
  top <- TOP[[tab]]
  k <- ncol(top)
  stopifnot(setequal(it$item_text, rownames(top)), setequal(it$item, unique(d$item)))
  obs <- t(sapply(it$item, function(c) { s <- d[d$item == c, ]; w <- W[as.character(s$id)]; stopifnot(!anyNA(w))
    100 * sapply(seq_len(k), function(v) sum(w[s$resp == v])) / sum(w) }))
  cost <- outer(seq_len(nrow(obs)), seq_len(nrow(top)), Vectorize(function(i, j) sum(abs(obs[i, ] - top[j, ]))))
  shipped <- match(it$item_text, rownames(top))
  best <- as.integer(clue::solve_LSAP(cost))
  c_ship <- sum(cost[cbind(seq_along(shipped), shipped)])
  # best assignment that differs from the shipped one: forbid each shipped cell in turn
  alt <- min(sapply(seq_along(shipped), function(i) {
    cc <- cost; cc[i, shipped[i]] <- 1e6; a <- as.integer(clue::solve_LSAP(cc)); sum(cc[cbind(seq_along(a), a)]) }))
  hit <- all(best == shipped)
  ok <- ok && hit
  cat(sprintf("\n== %s: %d items; shipped total L1 = %.1f, optimal = %.1f, best alternative = %.1f (margin %.1f) %s\n",
              tab, nrow(it), c_ship, sum(cost[cbind(seq_along(best), best)]), alt, alt - c_ship,
              if (hit) "" else "<-- OPTIMAL ASSIGNMENT DIFFERS"))
  for (i in seq_len(nrow(it)))
    cat(sprintf("   %-6s own=%5.1f  nearest other=%5.1f  %s\n", it$item[i], cost[i, shipped[i]],
                min(cost[i, -shipped[i]]), substr(it$item_text[i], 1, 60)))
}
cat("\nIn every block the minimum-cost matching of observed item distributions to the topline's\n",
    "worded rows is exactly the shipped code-to-wording mapping, including the renumbered\n",
    "Q9_10-12 and Q28_6-8.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
