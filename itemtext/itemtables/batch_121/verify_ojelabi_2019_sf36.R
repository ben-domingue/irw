# verify_ojelabi_2019_sf36.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the IRW item codes sf1..sf36 denote SF-36 (RAND 36-Item
# Health Survey 1.0) questionnaire items 1..36 in canonical order, so the item
# text shipped for sfN is the RAND page's item N.
#
# The processing script (data/ojelabi_2019_sf36_sickle_cell.py) melts the PLOS
# S1 workbook's columns sf1..sf36 unchanged, so the source workbook IS the live
# table's items. This script fetches that workbook (no Redivis export) and runs
# two falsifiable checks.
#
#   ROUTE 2 (per-item response ranges). The SF-36 is not a single-scale
#   instrument: item 1 has 5 options, item 2 has 5, items 3-12 have 3, items
#   13-19 have 2, item 20 has 5, item 21 has 6, item 22 has 5, items 23-31 have
#   6, item 32 has 5, items 33-36 have 5. That block pattern is a structural
#   signature; any mapping that moves an item across a block boundary produces
#   responses outside the option list we shipped for it.
#
#   ROUTE 4 (a parameter the item text implies). The workbook carries the
#   authors' own SF-6D scoring columns -- 'Health State', a 6-digit code, one
#   digit per SF-6D dimension. Brazier's SF-6D reads each dimension off named
#   SF-36 items: PF from items 3/4/12, role limitation from 15/18, social
#   functioning from 32, pain from 21/22, mental health from 24/28, vitality
#   from 27. If our numbering is right, each digit is a FUNCTION of exactly
#   those items. This is arithmetic on the authors' own derived column, and it
#   pins 11 of the 36 items individually.
#
# WHAT THIS DOES NOT ESTABLISH: order WITHIN a block for the 25 items that are
# not SF-6D inputs (e.g. sf5 vs sf8 inside the physical-functioning block, or
# sf13 vs sf14 inside role-physical). Both routes are blind to a swap of two
# same-block non-SF-6D items. Status is therefore PARTIAL, not VERIFIED.

SRC <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0223043.s001")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(SRC, tmp, quiet = TRUE, mode = "wb",
                     headers = c("User-Agent" = "IRW-itemtext/1.0"))
d <- as.data.frame(readxl::read_excel(tmp))

items <- paste0("sf", 1:36)
num <- sapply(items, function(c) suppressWarnings(as.numeric(d[[c]])))

# Number of response options the shipped item text gives each SF-36 item.
NOPT <- c(5, 5, rep(3, 10), rep(2, 7), 5, 6, 5, rep(6, 9), 5, rep(5, 4))
names(NOPT) <- items
stopifnot(length(NOPT) == 36)

obs_max <- apply(num, 2, function(x) max(x, na.rm = TRUE))

cat("== ROUTE 2: per-item observed max vs options in the shipped text ==\n")
cat(sprintf("%-6s %8s %8s  %s\n", "item", "n_opts", "obs_max", "flag"))
for (it in items)
    cat(sprintf("%-6s %8d %8d  %s\n", it, NOPT[[it]], obs_max[[it]],
                if (obs_max[[it]] > NOPT[[it]]) "OUT OF RANGE" else ""))
viol_id <- sum(obs_max > NOPT)

# Discriminating power: how badly does a wrong alignment fail this test?
shift_viol <- sapply(1:35, function(k) sum(obs_max > NOPT[c((k + 1):36, 1:k)]))
cat(sprintf("\nviolations under the shipped mapping: %d of 36\n", viol_id))
cat(sprintf("violations under the 35 non-identity cyclic shifts: min %d, median %d, max %d\n",
            min(shift_viol), as.integer(median(shift_viol)), max(shift_viol)))

cat("\n== ROUTE 4: SF-6D 'Health State' digits vs the SF-36 items that define them ==\n")
hs <- sprintf("%06d", as.integer(d[["Health State"]]))
dig <- sapply(1:6, function(k) as.integer(substr(hs, k, k)))
colnames(dig) <- paste0("d", 1:6)

# violations = rows whose digit differs from the modal digit for their cell
viol <- function(cols, dcol) {
    key <- apply(num[, cols, drop = FALSE], 1, paste, collapse = "|")
    y <- dig[, dcol]
    ok <- !is.na(key) & !is.na(y)
    m <- ave(y[ok], key[ok], FUN = function(s) as.integer(names(sort(table(s), decreasing = TRUE))[1]))
    sum(y[ok] != m)
}

claim <- list(d1 = c("sf3", "sf4", "sf12"), d2 = c("sf15", "sf18"), d3 = "sf32",
              d4 = c("sf21", "sf22"),      d5 = c("sf24", "sf28"),  d6 = "sf27")
dimnm <- c(d1 = "physical functioning", d2 = "role limitation", d3 = "social functioning",
           d4 = "pain", d5 = "mental health", d6 = "vitality")

# best rival of the same arity, drawn from all other items
rival <- function(dcol, arity) {
    combs <- combn(items, arity, simplify = FALSE)
    combs <- Filter(function(z) !identical(sort(z), sort(claim[[dcol]])), combs)
    v <- sapply(combs, viol, dcol = dcol)
    list(v = min(v), set = combs[[which.min(v)]])
}

n <- nrow(d)
fails <- 0
for (dcol in names(claim)) {
    cv <- viol(claim[[dcol]], dcol)
    rv <- rival(dcol, length(claim[[dcol]]))
    cat(sprintf("%s (%-20s) claimed %-22s misfits %3d/%d | best rival %-22s misfits %3d/%d\n",
                dcol, dimnm[[dcol]], paste(claim[[dcol]], collapse = "+"), cv, n,
                paste(rv$set, collapse = "+"), rv$v, n))
    if (!(cv < rv$v)) fails <- fails + 1
}

cat("\nNote: this pins sf3, sf4, sf12, sf15, sf18, sf21, sf22, sf24, sf27, sf28 and sf32\n",
    "individually, and pins every item's block membership; it does NOT separate two\n",
    "same-block items that are both outside the SF-6D (e.g. sf5 vs sf8, sf13 vs sf14).\n", sep = "")

cat(if (viol_id == 0 && min(shift_viol) > 0 && fails == 0)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
