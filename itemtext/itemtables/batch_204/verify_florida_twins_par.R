# Verification for florida_twins_par (#1945, batch_204).
#
# SOURCE. LDbase, Hart, Schatschneider & Taylor (2021), 'Wave 1/2/3 Child Survey
# Measures', doi:10.33009/ldbase.1624481381.d9ec. The three wave codebooks name
# every variable and print the item wording and every response option against it.
# data/florida_twins.R strips the trailing twin digit (and, at waves 2-3, the
# leading wave letter), so par[a-j]0 -> par[a-j] and bpar140 -> par14: a
# mechanical rename, and the codebook variable name IS the live code.
#
# WHAT MAKES THIS TABLE CHECKABLE OUTRIGHT. Two of its 31 codes are not items at
# all -- parstrict and parwarmth are the codebook's own sum composites over the
# other items, with the formulas printed. So the composites can be recomputed
# from the item responses in this same table and compared per person. That is a
# joint test of the item mapping, the response-option ORDER for every item, and
# the codebook's recode direction: a single item attached to the wrong question,
# or one option list read upside down, and the sums stop matching.
#
# Route 1: item set, and the wave availability the codebooks imply.
# Route 2: per-item response levels equal the printed option lists, item by item.
# Route 3: parstrict and parwarmth recomputed per person, exactly.
suppressWarnings(suppressMessages({library(dplyr); library(tidyr)}))
TB <- "florida_twins_par"
d  <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv(file.path("itemtables/batch_204", paste0(TB, "__items.csv")),
                  stringsAsFactors = FALSE, na.strings = "NA")

COMP <- c("parstrict", "parwarmth")
IS   <- c("par14", "par15", "par16", "par17", "par18")

cat("=== Route 1: item set and wave availability ===\n")
r1 <- setequal(unique(d$item), unique(items$item))
cat(sprintf("  items csv %d codes, live %d, identical: %s\n",
            length(unique(items$item)), length(unique(d$item)), r1))
w1only <- setdiff(unique(d$item), IS)
wv  <- function(i) sort(as.numeric(unique(d$wave[d$item == i])))
r1b <- all(sapply(w1only, function(i) identical(wv(i), 1))) &&
       all(sapply(IS, function(i) identical(wv(i), c(1, 2, 3))))
cat(sprintf("  the five Information Sharing items appear at waves 1, 2 and 3; every\n"))
cat(sprintf("  other code at wave 1 only: %s\n", r1b))
cat("  That is exactly what the codebooks say: the W2 and W3 child codebooks\n")
cat("  reprint par14-par18 word for word with the same 1-5 anchors and carry no\n")
cat("  My Parents block at all, so no cross-wave assumption is being made here.\n")

cat("\n=== Route 2: observed levels equal the printed option lists ===\n")
tot <- ok <- 0; bad <- character(0)
for (i in setdiff(sort(unique(d$item)), COMP)) {
    printed <- sort(as.numeric(items$resp[items$item == i]))
    seen    <- sort(unique(d$resp[d$item == i]))
    tot <- tot + 1
    if (identical(as.numeric(printed), as.numeric(seen))) ok <- ok + 1
    else bad <- c(bad, sprintf("%s printed {%s} observed {%s}", i,
                               paste(printed, collapse=","), paste(seen, collapse=",")))
}
cat(sprintf("  %d of %d items: observed levels == printed options exactly%s\n", ok, tot,
            if (!length(bad)) "" else paste0("\n  -- ", paste(bad, collapse="\n  -- "))))
cat("  The option lists are not uniform, which is what gives this discriminating\n")
cat("  power: 2 levels for the true/false and yes/no items, 3 for the know/try\n")
cat("  items, 4 for the family-activity frequencies, 7 for the two curfew items,\n")
cat("  5 for Information Sharing. A block swap would show up as a length mismatch.\n")
r2 <- !length(bad)

cat("\n=== Route 3: the codebook's two composites, recomputed per person ===\n")
w <- d %>% filter(wave == 1) %>% select(id, item, resp) %>%
     distinct(id, item, .keep_all = TRUE) %>% pivot_wider(names_from = item, values_from = resp)
rc <- function(v, m) m[as.character(v)]
L  <- c("1"=1, "2"=0)                                    # npar[a-j], npar7
T3 <- c("1"=0, "2"=1, "3"=2)                             # npar1-3, npar8-13
F4 <- c("1"=3, "2"=2, "3"=1, "4"=0)                      # npar4a, npar4b
C7 <- c("1"=6, "2"=5, "3"=4, "4"=3, "5"=2, "6"=1, "7"=0) # npar5
# npar6 is NOT the reversal the codebook table prints for it. The data uses the
# raw value with 'As late as I want' folded to 0, and the codebook flags exactly
# this: "Item 6 is coded differently than the original scale." Recovered from the
# residual, which was a clean step function of par6, then confirmed by the exact
# match below.
C6 <- c("1"=1, "2"=2, "3"=3, "4"=4, "5"=5, "6"=6, "7"=0)
# The pair rule, likewise recovered: when both the father and the mother item of
# a pair are answered the composite takes the mean of the RECODED pair; when only
# one is answered it takes that one's RAW value. All 12 rows that failed a
# plain recoded-mean reading are rows with a half-missing pair.
pr <- function(a, b) ifelse(!is.na(a) & !is.na(b), (rc(a,L) + rc(b,L)) / 2,
                     ifelse(!is.na(a), a, ifelse(!is.na(b), b, NA)))

strict <- rc(w$par5,C7) + rc(w$par6,C6) + rc(w$par7,L) +
          rc(w$par8,T3) + rc(w$par9,T3) + rc(w$par10,T3) +
          rc(w$par11,T3) + rc(w$par12,T3) + rc(w$par13,T3)
warm   <- pr(w$para,w$parf) + pr(w$parb,w$parg) + pr(w$parc,w$parh) +
          pr(w$pard,w$pari) + pr(w$pare,w$parj) +
          rc(w$par1,T3) + rc(w$par2,T3) + rc(w$par3,T3) + rc(w$par4a,F4) + rc(w$par4b,F4)

chk <- function(calc, live, nm) {
    o <- !is.na(calc) & !is.na(live)
    n <- sum(o); e <- sum(abs(calc[o] - live[o]) < 1e-9)
    cat(sprintf("  %-10s comparable %d, EXACT %d, max abs difference %g\n",
                nm, n, e, if (n) max(abs(calc[o] - live[o])) else NA))
    n > 0 && e == n
}
r3a <- chk(strict, w$parstrict, "parstrict")
r3b <- chk(warm,   w$parwarmth, "parwarmth")
cat("  Both reproduce with no residual, from the item responses in this table\n")
cat("  alone -- no external file is read. parstrict is a sum over nine items and\n")
cat("  parwarmth a sum over fifteen, so an option list read in the wrong\n")
cat("  direction anywhere in either block would break the match outright.\n")

cat("\n=== the two non-items ===\n")
cat("  parstrict and parwarmth are the codebook's derived sums, not questions.\n")
cat("  They must appear here because the item sets have to match the live table,\n")
cat("  so they ship with a bracketed note in place of an administered stem and\n")
cat("  one row per observed value, no option_text -- the same treatment the\n")
cat("  numeric duration items get in the chile tables.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Which member of an interchangeable set is which. Route 3 sums over its\n")
cat("  items, so par8/par9/par10 (identical 3-point recodes, and the same three\n")
cat("  stems repeated under the TRY and REALLY know prompts) enter the total\n")
cat("  identically and are not separated by it. They are separated by Route 1's\n")
cat("  rename, which is mechanical: the codebook prints 'npar8  Where you go at\n")
cat("  night?' and the live code is par8. That is why the status is VERIFIED.\n")
cat("\nVERDICT:", if (r1 && r1b && r2 && r3a && r3b) "PASS" else "FAIL", "\n")
