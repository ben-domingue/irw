# Step 5b evidence for dpt_noncog__interpersonal_reactivity.
#
# mapping_basis is data_labels (the Harvard Dataverse xlsx carries the item text in
# its own row 4 and the original IRI item number in row 2), so this table is exempt.
# This script exists anyway because the exemption covers only the FILE's tie of column
# -> text; it does not cover data/dpt_noncognitive_traits.py's tie of source column
# Q15_k -> IRW code iri_N, which is a positional/dictionary rename. That step is what
# is checked here.
#
# Claim: live item iri_N was produced from the xlsx column whose row 2 reads
# IR_Index_N -- i.e. the column whose row-4 wording this table ships.
# Falsifiable prediction: the per-item x per-resp response frequency profile of each
# live item must reproduce that source column's own frequency profile CELL FOR CELL.
# Any permutation of the 15 columns breaks it, because the 15 profiles are distinct.
#
# The source file (85 KB, CC0) is fetched live from Dataverse so this is self-contained.

suppressMessages(library(irw))

TABLE <- "dpt_noncog__interpersonal_reactivity"
URL   <- "https://dataverse.harvard.edu/api/access/datafile/3234209"

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")

raw <- suppressMessages(readxl::read_excel(tmp, col_names = FALSE))
raw <- as.data.frame(raw)
cols <- 16:30                                   # the Q15_* block
labs <- gsub("^IR_Index_", "iri_", as.character(unlist(raw[2, cols])))

src <- do.call(rbind, lapply(seq_along(cols), function(j) {
    v <- suppressWarnings(as.integer(unlist(raw[5:302, cols[j]])))
    v <- v[!is.na(v)]
    data.frame(item = labs[j], resp = as.integer(names(table(v))),
               n_src = as.integer(table(v)), stringsAsFactors = FALSE)
}))

d <- irw::irw_fetch(TABLE)
lv <- as.data.frame(table(item = d$item, resp = d$resp), stringsAsFactors = FALSE)
lv <- lv[lv$Freq > 0, ]
names(lv)[3] <- "n_live"
lv$resp <- as.integer(lv$resp)

m <- merge(src, lv, by = c("item", "resp"), all = TRUE)
m$n_src[is.na(m$n_src)] <- 0L
m$n_live[is.na(m$n_live)] <- 0L
m <- m[order(m$item, m$resp), ]

cat(sprintf("%-8s %5s %8s %8s\n", "item", "resp", "source", "live"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-8s %5d %8d %8d%s\n", m$item[i], m$resp[i], m$n_src[i], m$n_live[i],
                if (m$n_src[i] != m$n_live[i]) "   <-- MISMATCH" else ""))

bad <- sum(m$n_src != m$n_live)
cat(sprintf("\ncells compared: %d   mismatched: %d\n", nrow(m), bad))
cat("Note: this pins every item code to its source column, and therefore to the\n",
    "row-4 wording shipped for it. It does NOT independently check the option\n",
    "anchors: 'does not describe me well' = 1 and 'describes me very well' = 5 come\n",
    "from the paper's Methods (which states 0-4; the deposit stores 1-5) and from\n",
    "item content, not from these counts.\n", sep = "")

cat(if (bad == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
