# verify_stoyel_2021_pos_affect.R -- Step 5b mapping check (copied from references/verify_template.R)
#
# Code derivation is POSITIONAL: data/stoyel_2021_disordered_eating.py renames the POSAF<k>.<wave>
# columns of the PLOS S1 workbook, sorted by integer k within each wave, to item_{i+1}. So the claim
# being shipped is item_k <-> header "POSAF<k>.<w>: In the past week, I have felt... <adjective>".
#
# This script re-runs that derivation over the raw workbook and compares every (id, wave, item)
# response against the live IRW table. It then checks that the route separates every item from every
# other: for each pair of items (a, b), assigning a's source column to b must break the match. If the
# response vectors of two source columns were identical, the route could not tell those items apart,
# and the verdict would be FAIL.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "stoyel_2021_pos_affect"
URL <- "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0257577.s001&type=supplementary"
TEXT <- c("Interested", "Excited", "Strong", "Enthusiastic", "Proud",
          "Alert", "Inspired", "Determined", "Attentive", "Active")   # shipped item_text for item_1..item_10

tf <- tempfile(fileext = ".xlsx")
download.file(URL, tf, mode = "wb", quiet = TRUE)
raw <- as.data.frame(read_excel(tf, sheet = "alldata_subjectlevel_NO ID"))
raw$.id <- seq_len(nrow(raw))                                   # script: id = row index + 1

live <- as.data.frame(irw::irw_fetch(TABLE))
live$key <- paste(live$id, live$wave, live$item)
lv <- setNames(live$resp, live$key)

ok_text <- TRUE
rebuilt <- list()
for (w in 1:3) {
    cols <- grep(sprintf("^POSAF[0-9]+\\.%d\\s*:", w), names(raw), value = TRUE)
    k <- as.integer(sub(sprintf("^POSAF([0-9]+)\\.%d.*", w), "\\1", cols))
    cols <- cols[order(k)]
    for (i in seq_along(cols)) {
        hdr_adj <- sub("^.*I have felt\\.\\.\\. ", "", cols[i])
        if (hdr_adj != TEXT[i]) { ok_text <- FALSE
            cat(sprintf("TEXT MISMATCH wave %d item_%d: header '%s' vs shipped '%s'\n", w, i, hdr_adj, TEXT[i])) }
        v <- suppressWarnings(as.numeric(raw[[cols[i]]]))
        rebuilt[[length(rebuilt) + 1]] <- data.frame(id = raw$.id, wave = w, item = paste0("item_", i),
                                                     src = cols[i], resp = v)
    }
}
rb <- do.call(rbind, rebuilt)
rb <- rb[!is.na(rb$resp) & rb$resp >= 1 & rb$resp <= 5 & rb$resp == round(rb$resp), ]
rb$key <- paste(rb$id, rb$wave, rb$item)

cat(sprintf("header diff (shipped item_text vs workbook header at each position, 3 waves): %s\n",
            if (ok_text) "30/30 match" else "MISMATCH"))
cat(sprintf("rows: rebuilt %d, live %d\n", nrow(rb), nrow(live)))
same_keys <- setequal(rb$key, live$key)
agree <- sum(lv[rb$key] == rb$resp, na.rm = TRUE)
cat(sprintf("(id,wave,item) keys identical: %s; responses agreeing: %d of %d\n", same_keys, agree, nrow(rb)))

cat("\nper item (all waves): n_live  mean_live  mean_rebuilt\n")
for (i in 1:10) {
    it <- paste0("item_", i)
    cat(sprintf("  %-8s %-11s %6d  %.4f  %.4f\n", it, TEXT[i], sum(live$item == it),
                mean(live$resp[live$item == it]), mean(rb$resp[rb$item == it])))
}

# Does the route distinguish every item from every other? Swap each pair of source columns and count
# how many live responses the swapped assignment would still reproduce.
cat("\npairwise swap test (min over pairs of mismatching cells if item a's text were given to item b):\n")
min_mis <- Inf; worst <- ""
for (a in 1:9) for (b in (a + 1):10) {
    ra <- rb[rb$item == paste0("item_", a), ]; rbb <- rb[rb$item == paste0("item_", b), ]
    ka <- paste(ra$id, ra$wave, paste0("item_", b)); kb <- paste(rbb$id, rbb$wave, paste0("item_", a))
    mis <- sum(lv[ka] != ra$resp, na.rm = TRUE) + sum(lv[kb] != rbb$resp, na.rm = TRUE)
    if (mis < min_mis) { min_mis <- mis; worst <- sprintf("item_%d<->item_%d", a, b) }
}
cat(sprintf("  closest pair %s: %d mismatching cells under a swap\n", worst, min_mis))

pass <- ok_text && same_keys && agree == nrow(rb) && nrow(rb) == nrow(live) && min_mis > 0
cat("Note: this proves the code<->source-column tie (and so item_text, which is that column's own header).\n",
    "It does not speak to the unlabeled midpoints 2-4, whose option_text is left blank.\n", sep = "")
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
