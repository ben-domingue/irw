# verify_ren2019_cpti.R -- batch_155, 2026-09-10
#
# THIS TABLE SHIPPED NO ITEM TEXT. ren2019_cpti is BLOCKED on a data defect: the
# deposit's CPTI column labels do not line up with the Child Problematic Traits
# Inventory's own item numbering, so no instrument wording can be honestly attached
# to the published item codes CPTI1..CPTI28. mapping_basis = unknown, Step 5b
# status = NO_ROUTE (no shipped mapping exists to verify).
#
# What this script re-runs is the three claims the round actually made, all from the
# live IRW table plus published numbers hard-coded below.
#
#  (A) CPTI1 IS NOT A CPTI ITEM. In the live table it correlates ~0 with every one of
#      the other 27 CPTI columns (max |r| = 0.14), while those 27 correlate ~0.3 with
#      each other. In the source .xlsx its strongest partner anywhere in the file is
#      YPIC10 (+0.38) -- a child SELF-report item from a different instrument, whereas
#      the CPTI here is PARENT-rated.
#
#  (B) THE LABELS ARE OFF BY ONE. Ren et al.'s own Table 5 prints the three CPTI
#      subscale intercorrelations (GD-CU .773, GD-INS .643, CU-INS .681). Scoring the
#      subscales from the columns AS LABELLED (identity: GD = CPTI5,7,9,15,18,21,24,26)
#      misses those by up to .121. Scoring them one column to the right
#      (instrument item j -> column CPTI(j+1), item 28 -> CPTI1) reproduces all three
#      to within .003.
#
#  (C) AN INDEPENDENT SAMPLE AGREES WITH (B). Wang et al. (PLOS ONE 2019,
#      doi:10.1371/journal.pone.0219136, PMC6609029) print per-item M for all 28 CPTI
#      items rated by mothers of 585 Chinese children aged 8-12 -- the same instrument,
#      informant and population as Ren et al. Against the labels as published the two
#      item-mean profiles correlate rho = -0.19; one column to the right, rho = +0.81.
#
#   VERDICT: PASS = all three reproduce; the block stands and no item text should be
#                   attached to these codes as labelled.
#   VERDICT: FAIL = something did not reproduce; a human should look before this table
#                   is re-queued or the block is relied on again.

suppressMessages(library(irw))
TABLE <- "ren2019_cpti"

## published values, hard-coded (they came from papers and will not change)
REN_T5 <- c(GD_CU = .773, GD_INS = .643, CU_INS = .681)   # Ren et al. 2019, Table 5
PLOS_N <- c(5,7,9,15,18,21,24,26, 2,4,8,11,13,17,20,22,25,27, 1,3,6,10,12,14,16,19,23,28)
PLOS_M <- c(1.93,2.23,1.68,1.51,1.48,1.49,2.00,1.37, 1.71,1.80,1.88,1.57,1.60,1.90,1.80,
            1.81,1.85,1.64, 2.26,2.41,2.27,1.91,2.05,1.93,2.05,2.28,2.03,1.89)  # Wang 2019 Table 3, Time 1

## CPTI key (Andershed, CPTI v2.0 KEY, oru.se): instrument item numbers per dimension
GDi  <- c(5,7,9,15,18,21,24,26)
CUi  <- c(2,4,8,11,13,17,20,22,25,27)
INSi <- c(1,3,6,10,12,14,16,19,23,28)

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
its <- paste0("CPTI", 1:28)
stopifnot(all(its %in% names(w)))

## ------------------------------------------------------------------ (A) CPTI1
cat("== (A) is CPTI1 a CPTI item? ==\n")
R <- cor(w[, its], use = "pairwise.complete.obs")
r1 <- R["CPTI1", setdiff(its, "CPTI1")]
Roth <- R[setdiff(its,"CPTI1"), setdiff(its,"CPTI1")]
cat(sprintf("CPTI1 vs the other 27 : max|r| = %.3f (at %s), median r = %+.3f\n",
            max(abs(r1)), names(r1)[which.max(abs(r1))], median(r1)))
cat(sprintf("the other 27 among themselves: median r = %+.3f\n", median(Roth[upper.tri(Roth)])))
okA <- max(abs(r1)) < 0.20 && median(Roth[upper.tri(Roth)]) > 0.20
cat(sprintf("=> CPTI1 unrelated to the CPTI block: %s\n", if (okA) "YES" else "NO"))

## --------------------------------------------------- (B) identity vs off-by-one
cat("\n== (B) subscale intercorrelations vs Ren et al. Table 5 ==\n")
f <- function(cols) rowMeans(w[, cols], na.rm = TRUE)
idc <- function(j) paste0("CPTI", j)                              # labels as published
shc <- function(j) paste0("CPTI", ifelse(j == 28, 1, j + 1))      # one column to the right
trio <- function(g) c(GD_CU  = cor(f(g(GDi)), f(g(CUi)),  use = "pairwise"),
                      GD_INS = cor(f(g(GDi)), f(g(INSi)), use = "pairwise"),
                      CU_INS = cor(f(g(CUi)), f(g(INSi)), use = "pairwise"))
ti <- trio(idc); ts <- trio(shc)
cat(sprintf("%-8s %9s %9s %9s %9s %9s\n","", "published","identity","err","shifted","err"))
for (k in names(REN_T5))
  cat(sprintf("%-8s %9.3f %9.3f %9.3f %9.3f %9.3f\n", k, REN_T5[k], ti[k], ti[k]-REN_T5[k], ts[k], ts[k]-REN_T5[k]))
cat(sprintf("max abs error: identity %.3f | shifted %.3f\n", max(abs(ti-REN_T5)), max(abs(ts-REN_T5))))
okB <- max(abs(ts - REN_T5)) < 0.02 && max(abs(ti - REN_T5)) > 0.05

## ---------------------------------------- (C) independent per-item mean profile
cat("\n== (C) per-item means vs Wang et al. 2019 (585 Chinese children, mother-rated) ==\n")
m   <- tapply(d$resp, d$item, mean, na.rm = TRUE)
pl  <- setNames(PLOS_M, PLOS_N)[as.character(1:28)]
obs_id <- as.numeric(m[idc(1:28)]); obs_sh <- as.numeric(m[shc(1:28)])
cat(sprintf("%-5s %9s %9s %9s\n", "item", "Wang M", "as-labelled", "shifted"))
for (j in 1:28) cat(sprintf("%-5d %9.2f %9.2f %9.2f\n", j, pl[j], obs_id[j], obs_sh[j]))
rid <- cor(obs_id, pl, method = "spearman"); rsh <- cor(obs_sh, pl, method = "spearman")
cat(sprintf("Spearman rho: as-labelled %+.3f | shifted %+.3f\n", rid, rsh))
cat(sprintf("Pearson  r  : as-labelled %+.3f | shifted %+.3f\n",
            cor(obs_id, pl), cor(obs_sh, pl)))
okC <- rsh > 0.6 && rid < 0.2

cat("\nWhat this does NOT establish: which variable CPTI1 actually holds, whether CPTI\n",
    "item 28 is present anywhere in the deposit, or that every one of the remaining 27\n",
    "codes is individually pinned -- (B) is a subscale-level statistic and (C) is a\n",
    "cross-sample profile, neither of which separates two items with similar means.\n",
    "It is enough to refute the labels as published, which is why the table is blocked;\n",
    "it is not enough to ship the shifted mapping as if it were transcribed. Note in (C)\n",
    "that items 25-28 actually fit the Wang profile BETTER as-labelled (|diff| .04-.22)\n",
    "than shifted (.29-.49), so even the off-by-one reading is not clean at the tail.\n", sep = "")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
