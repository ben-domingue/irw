# verify_ren_2019_cpti.R -- batch_312, 2026-09-23
#
# THIS TABLE SHIPPED NO ITEM TEXT. ren_2019_cpti is BLOCKED on a data defect, the same
# one batch_155 found in its duplicate ren2019_cpti (same figshare deposit 11283215,
# same Data_Sheet_1 .xlsx, sha256 0ebf515e...c6e, re-downloaded and re-hashed
# 2026-09-23). The deposit's CPTI column labels do not line up with the CPTI's own
# item numbering, so no instrument wording can be honestly attached to CPTI1..CPTI28.
# mapping_basis = unknown, Step 5b status = NO_ROUTE (no shipped mapping to verify).
#
# (0) THE LIVE TABLE IS THE DEPOSIT'S CPTI COLUMNS, CELL FOR CELL. data/
#     ren_2019_psychopathy_children.py melts the .xlsx columns whose names start with
#     "CPTI" and keeps resp 1..4, so item = source column name. This script re-downloads
#     the .xlsx and checks every live (id, item, resp) triple against it -- which is
#     what makes batch_155's deposit-level finding apply to this table unchanged.
# (A)-(C) are batch_155's three checks, re-run against THIS table:
#  (A) CPTI1 is not a CPTI item (max |r| with the other 27 < .20; they sit ~.30).
#  (B) Ren et al. Table 5 subscale intercorrelations (.773/.643/.681) reproduce only
#      if every instrument item j is read from column CPTI(j+1) (item 28 -> CPTI1).
#  (C) Wang et al. 2019 (PMC6609029) Table 3 per-item means: rho ~ -0.19 as labelled,
#      ~ +0.81 shifted.
#
#   VERDICT: PASS = (0) and (A)-(C) all reproduce; the block stands.
#   VERDICT: FAIL = something did not reproduce; a human should look before relying on
#                   the block or re-queueing the table.

suppressMessages(library(irw))
TABLE <- "ren_2019_cpti"

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

## ------------------------------------------ (0) live table == deposit CPTI columns
cat("== (0) live table vs deposit .xlsx (figshare file 19972844) ==\n")
suppressMessages(library(readxl))
xf <- ".cache/ren_2019_cpti/deposit.xlsx"
if (!file.exists(xf)) { xf <- tempfile(fileext = ".xlsx")
  download.file("https://ndownloader.figshare.com/files/19972844", xf, mode = "wb", quiet = TRUE) }
x <- as.data.frame(read_excel(xf))
dep <- do.call(rbind, lapply(paste0("CPTI", 1:28), function(k)
  data.frame(id = as.integer(x$ID), item = k, resp = suppressWarnings(as.numeric(x[[k]])))))
dep <- dep[!is.na(dep$id) & !is.na(dep$resp) & dep$resp >= 1 & dep$resp <= 4, ]
key <- function(z) paste(z$id, z$item, z$resp)
live_k <- key(d); dep_k <- key(dep)
cat(sprintf("live rows %d | deposit CPTI cells in 1..4 %d | live not in deposit %d | deposit not in live %d\n",
            length(live_k), length(dep_k), sum(!live_k %in% dep_k), sum(!dep_k %in% live_k)))
ok0 <- length(live_k) == length(dep_k) && all(live_k %in% dep_k) && all(dep_k %in% live_k)
cat(sprintf("=> item codes are the deposit's own column names, cells identical: %s\n\n", if (ok0) "YES" else "NO"))

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

cat(if (ok0 && okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
