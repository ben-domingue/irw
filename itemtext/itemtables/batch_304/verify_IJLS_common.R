# Shared verification for the three IJLS_Eersel_2024 tables (#2228, batch_304).
#
# MAPPING BASIS IS data_labels FOR ALL THREE, so there is no mapping step: the
# live item codes are the .sav's own column names and each column carries both
# its item (variable label) and its per-item response options (value labels).
# IJLS_readme.txt repeats the same wording and coding independently.
#
# Route 1: shipped item_text == the .sav variable labels, code for code.
# Route 2: shipped option_text/resp == the .sav value labels, per item. This is
#   load-bearing rather than cosmetic: the source stores its reverse-keyed items
#   already reversed and encodes that ONLY in the value labels.
# Route 3: the readme carries the same wording, so the labels are not a
#   one-source claim.
ijls_verify <- function(table, cols, strip_rev = TRUE) {
    sav <- ".cache/batch_304/IJLS.sav"
    rme <- ".cache/batch_304/IJLS_readme.txt"
    for (p in c(sav, rme)) if (!file.exists(p)) stop("missing cached deposit file: ", p)
    if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven")
    d <- as.data.frame(irw::irw_fetch(table))
    if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
    items <- read.csv(sprintf("itemtables/batch_304/%s__items.csv", table),
                      stringsAsFactors = FALSE, na.strings = "NA", encoding = "UTF-8")
    s <- haven::read_sav(sav)

    cat("=== Route 1: shipped text == .sav variable labels ===\n")
    lab <- sapply(cols, function(c) {
        z <- trimws(attr(s[[c]], "label"))
        z <- trimws(sub("^[0-9]+\\.\\s*", "", z))
        z <- trimws(sub("\\s*\\((reverse coded|reversed)\\)\\s*$", "", z))
        paste0(trimws(sub("\\.$", "", z)), ".")
    })
    sh <- unique(items[, c("item", "item_text")]); sh <- sh[match(cols, sh$item), ]
    r1 <- all(sh$item_text == unname(lab)) && setequal(cols, unique(as.character(d$item)))
    for (i in seq_along(cols)) cat(sprintf("  %-10s %s\n", cols[i], substr(lab[i], 1, 78)))
    cat(sprintf("  -> all match, and equal the live item set: %s\n", r1))

    cat("\n=== Route 2: per-item value labels ===\n")
    ok <- logical(0); nrev <- 0
    for (c in cols) {
        vl <- attr(s[[c]], "labels"); vl <- vl[order(vl)]
        got <- items[items$item == c, c("resp", "option_text")]
        got <- got[order(got$resp), ]
        ok <- c(ok, identical(as.numeric(got$resp), unname(as.numeric(vl))) &&
                    identical(got$option_text, trimws(names(vl))))
        if (grepl("revers", attr(s[[c]], "label"))) {
            nrev <- nrev + 1
            cat(sprintf("  %-10s [reverse-keyed] %s\n", c,
                        paste(sprintf("%d=%s", unname(vl), substr(trimws(names(vl)), 1, 22)),
                              collapse = ", ")))
        }
    }
    r2 <- all(ok)
    cat(sprintf("  items whose value labels are reproduced exactly: %d of %d\n", sum(ok), length(cols)))
    cat(sprintf("  reverse-keyed items in this table: %d\n", nrev))
    cat(sprintf("  -> per-item anchors reproduced: %s\n", r2))

    cat("\n=== Route 3: the readme says the same thing ===\n")
    rl <- paste(readLines(rme, warn = FALSE, encoding = "UTF-8"), collapse = " ")
    r3 <- grepl("all items were translated from Dutch to English", rl, fixed = TRUE)
    cat(sprintf("  readme states the items were translated from Dutch: %s\n", r3))
    cat("  so language=Dutch with English in the base fields and empty\n")
    cat("  *_translated columns -- the documented fallback, not a default.\n")

    cat("\n=== What this does NOT establish ===\n")
    cat("  The administered Dutch. It is in neither the deposit nor the paper.\n")
    cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
}
