# verify_dpt_noncog__intolerance_of_uncertainty.R
#
# WHAT IS BEING VERIFIED
#   The item_text shipped for this table comes from the Harvard Dataverse deposit's own
#   header block (doi:10.7910/DVN/Y75CP2, "Jeehp_15_19_raw data.xlsx": row 1 = survey code
#   Q16_1..Q16_16, row 4 = the question wording). The IRW codes iu_* are assigned in
#   data/dpt_noncognitive_traits.py by an explicit Q16_k -> iu_N dictionary. The mapping
#   that could break is therefore Q16_k -> iu_N: if that dictionary were shifted or
#   permuted, every item_text would be attached to the wrong item and no set-level gate
#   would notice.
#
# HOW
#   Route 9 style, on the item axis: for each of the 16 source columns compute the full
#   response-level count vector (how many 1s, 2s, ... 5s), and compare it cell for cell
#   with the live IRW table's per-item count vector for the iu_* code the script claims it
#   became. The 16 source vectors are mutually distinct, so a correct match distinguishes
#   EVERY item from every other item, not merely a block or a direction.
#
# NOT checked here: item/resp set membership (validate_items.R does that), and the
# response-option anchors for resp 2/3/4, which come from the canonical IUS-27 rather
# than from this study's materials.

suppressMessages({library(irw); library(readxl)})

URL <- "https://dataverse.harvard.edu/api/access/datafile/3234209"
xlsx <- file.path(tempdir(), "y75cp2.xlsx")
utils::download.file(URL, xlsx, mode = "wb", quiet = TRUE)

raw <- suppressMessages(readxl::read_excel(xlsx, col_names = FALSE))
raw <- as.data.frame(raw)
codes <- as.character(unlist(raw[1, ]))      # Q16_1 ...
dat   <- raw[-(1:4), , drop = FALSE]         # rows 1-4 are code / scale num / domain / question

MAP <- c(Q16_1="iu_2",  Q16_2="iu_3",  Q16_3="iu_4",  Q16_4="iu_5",
         Q16_5="iu_8",  Q16_6="iu_10", Q16_7="iu_11", Q16_8="iu_14",
         Q16_9="iu_15", Q16_10="iu_16",Q16_11="iu_18",Q16_12="iu_21a",
         Q16_13="iu_21b",Q16_14="iu_23",Q16_15="iu_26",Q16_16="iu_27")

live <- as.data.frame(irw::irw_fetch("dpt_noncog__intolerance_of_uncertainty"))
live_tab <- table(live$item, as.integer(live$resp))

levs <- as.character(1:5)
ok <- TRUE
cat(sprintf("%-8s %-8s %-22s %-22s %s\n", "src", "item", "source counts 1..5",
            "live counts 1..5", "match"))
for (q in names(MAP)) {
    j <- which(codes == q)
    v <- as.integer(dat[[j]])
    v <- v[!is.na(v)]
    src <- as.integer(table(factor(as.character(v), levels = levs)))
    it  <- MAP[[q]]
    lv  <- if (it %in% rownames(live_tab))
        as.integer(live_tab[it, levs]) else rep(NA_integer_, 5)
    hit <- identical(src, lv)
    ok  <- ok && hit
    cat(sprintf("%-8s %-8s %-22s %-22s %s\n", q, it,
                paste(src, collapse = ","), paste(lv, collapse = ","),
                if (hit) "OK" else "MISMATCH"))
}

# The check is only informative if the 16 source vectors are distinct; state it.
sig <- vapply(names(MAP), function(q) {
    j <- which(codes == q); v <- as.integer(dat[[j]]); v <- v[!is.na(v)]
    paste(as.integer(table(factor(as.character(v), levels = levs))), collapse = ",")
}, character(1))
cat(sprintf("\ndistinct source count-vectors: %d of %d\n", length(unique(sig)), length(sig)))
if (length(unique(sig)) != length(sig)) ok <- FALSE

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
