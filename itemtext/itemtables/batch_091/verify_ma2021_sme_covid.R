# verify_ma2021_sme_covid.R
#
# mapping_basis = data_labels: the IRW `item` codes ARE the source workbook's own
# column headers, slugified verbatim by data/ma2021_sme_covid.py
# (str.lower() + non-alphanumeric -> "_"), so the code-to-header tie is mechanical.
# Each header names its item's content ("Tax relief", "Loan discount", ...), which
# is what pins it to a numbered item of the study's questionnaire (S1/S2 File of
# PLOS ONE 10.1371/journal.pone.0257036).
#
# This script is the corroborating data-side check (Step 5b route 3): the paper
# publishes a Cronbach alpha for each of the five factor blocks, and the block
# membership follows directly from the item_text assignment shipped here. A
# permuted item_text that moved an item across a block boundary would change
# these alphas.
#
# What this does NOT establish: alpha is invariant to permutations WITHIN a
# block, so this route pins block membership and boundaries, not order inside a
# block. Order inside a block is settled by the header names themselves, which
# are not an inference.

suppressMessages(library(irw))

TABLE <- "ma2021_sme_covid"

# Published Cronbach alphas, Ma, Liu & Gao (2021) PLOS ONE 16(12):e0257036,
# section 3.2.2 ("the value for finance's Cronbach alpha is 0.946, ...").
PUBLISHED <- c(finance = 0.946, market = 0.930, employee = 0.936,
               cost = 0.947, policy = 0.944)
TOL <- 0.01

BLOCKS <- list(
  finance  = c("operating_income", "sales_profit", "solvency_capacity",
               "liquidity_stock", "financing_requirements"),
  market   = c("raw_material_supply", "market_demand", "product_price",
               "inventory", "export"),
  employee = c("recruitment", "employee_reduction", "employee_loyalty",
               "working_hours", "online_office"),
  cost     = c("raw_material_cost", "labor_cost",
               "online_office_and_transportation_costs", "training_cost",
               "time_cost"),
  policy   = c("tax_relief", "employment_subsidies", "operating_subsidies",
               "rent_reduction_for_commercial_property", "loan_discount")
)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

alpha <- function(m) {
  m <- m[complete.cases(m), , drop = FALSE]
  k <- ncol(m)
  (k / (k - 1)) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
}

cat(sprintf("%-10s %5s %10s %10s %8s\n", "block", "k", "published", "observed", "diff"))
obs <- numeric(length(BLOCKS))
for (i in seq_along(BLOCKS)) {
  b <- names(BLOCKS)[i]
  obs[i] <- alpha(w[, BLOCKS[[b]], drop = FALSE])
  cat(sprintf("%-10s %5d %10.3f %10.3f %8.3f\n",
              b, length(BLOCKS[[b]]), PUBLISHED[b], obs[i], obs[i] - PUBLISHED[b]))
}

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation: %.4f (tolerance %.2f)\n", worst, TOL))
cat("Note: alpha is permutation-invariant within a block, so this pins the five\n",
    "block memberships (25 of 28 items; the 3 outcome items are not covered by a\n",
    "published alpha) and not the order inside a block. The item codes are the\n",
    "source workbook headers verbatim, which is what fixes order.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
