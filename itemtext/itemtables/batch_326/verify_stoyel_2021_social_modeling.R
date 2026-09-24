# verify_stoyel_2021_social_modeling.R -- Step 5b mapping check (copied from references/verify_template.R)
#
# Code derivation is POSITIONAL: data/stoyel_2021_disordered_eating.py renames the MBEH<k>.<wave>
# columns of the PLOS S1 workbook (doi:10.1371/journal.pone.0257577.s001), sorted by integer k within
# each wave, to item_{i+1}. MBEH k runs contiguously 1..7, so the shipped claim is
# item_k <-> header "MBEH<k>.1: <item text>". Only wave 1 carries data (waves 2-3 columns are empty).
#
# The script re-runs that derivation over the raw workbook, diffs the shipped item_text against the
# header at each position, compares every (id, item) response against the live IRW table, and runs a
# pairwise swap test: giving item a's source column to item b must break the match, for every pair.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "stoyel_2021_social_modeling"
URL <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0257577.s001&type=supplementary"
TEXT <- c("My friends diet or use weight control behaviours",
          "My teammates diet or use weight control behaviours",
          "People in my family diet or use weight control behaviours",
          "Do you feel that your sport encourages dieting or use of weight control behaviours",
          "My coach encourages me to use weight/shape controls or dieting",
          "Significant others in my life encourage me to diet or use weight/shape control behaviour",
          "Others outside my sport may see my diet as extreme, but it is accepted within my sport")

tf <- tempfile(fileext = ".xlsx")
download.file(URL, tf, mode = "wb", quiet = TRUE)
raw <- as.data.frame(read_excel(tf, sheet = "alldata_subjectlevel_NO ID"))
raw$.id <- seq_len(nrow(raw))                                   # script: id = row index + 1

live <- as.data.frame(irw::irw_fetch(TABLE))
live$key <- paste(live$id, live$wave, live$item)
lv <- setNames(live$resp, live$key)

n_text_ok <- 0; rebuilt <- list()
for (w in 1:3) {
    cols <- grep(sprintf("^MBEH[0-9]+\\.%d\\s*:", w), names(raw), value = TRUE)
    k <- as.integer(sub(sprintf("^MBEH([0-9]+)\\.%d.*", w), "\\1", cols))
    cols <- cols[order(k)]
    for (i in seq_along(cols)) {
        hdr <- sub("^MBEH[0-9]+\\.[0-9]:\\s*", "", cols[i])
        if (hdr == TEXT[i]) n_text_ok <- n_text_ok + 1 else
            cat(sprintf("TEXT MISMATCH wave %d item_%d: header '%s' vs shipped '%s'\n", w, i, hdr, TEXT[i]))
        v <- suppressWarnings(as.numeric(raw[[cols[i]]]))
        rebuilt[[length(rebuilt) + 1]] <- data.frame(id = raw$.id, wave = w, item = paste0("item_", i), resp = v)
    }
}
rb <- do.call(rbind, rebuilt)
rb <- rb[!is.na(rb$resp) & rb$resp >= 1 & rb$resp <= 5 & rb$resp == round(rb$resp), ]
rb$key <- paste(rb$id, rb$wave, rb$item)

cat(sprintf("header diff (shipped item_text vs workbook header at each position, 3 waves): %d/21\n", n_text_ok))
cat(sprintf("rows: rebuilt %d, live %d\n", nrow(rb), nrow(live)))
same_keys <- setequal(rb$key, live$key)
agree <- sum(lv[rb$key] == rb$resp, na.rm = TRUE)
cat(sprintf("(id,wave,item) keys identical: %s; responses agreeing: %d of %d\n", same_keys, agree, nrow(rb)))

cat("\nper item: n_live  mean_live  mean_rebuilt\n")
for (i in 1:7) {
    it <- paste0("item_", i)
    cat(sprintf("  %-7s %5d  %.4f  %.4f  %s\n", it, sum(live$item == it),
                mean(live$resp[live$item == it]), mean(rb$resp[rb$item == it]), substr(TEXT[i], 1, 50)))
}

cat("\npairwise swap test (mismatching cells if item a's source column were given to item b):\n")
min_mis <- Inf; worst <- ""
for (a in 1:6) for (b in (a + 1):7) {
    ra <- rb[rb$item == paste0("item_", a), ]; rbb <- rb[rb$item == paste0("item_", b), ]
    ka <- paste(ra$id, ra$wave, paste0("item_", b)); kb <- paste(rbb$id, rbb$wave, paste0("item_", a))
    mis <- sum(lv[ka] != ra$resp, na.rm = TRUE) + sum(lv[kb] != rbb$resp, na.rm = TRUE)
    if (mis < min_mis) { min_mis <- mis; worst <- sprintf("item_%d<->item_%d", a, b) }
}
cat(sprintf("  closest pair %s: %d mismatching cells under a swap\n", worst, min_mis))

pass <- n_text_ok == 21 && same_keys && agree == nrow(rb) && nrow(rb) == nrow(live) && min_mis > 0
cat("Note: this proves the code<->source-column tie (and so item_text, which is that column's own header).\n",
    "It says nothing about response anchors: none are published for this block, and option_text is blank.\n", sep = "")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
