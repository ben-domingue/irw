# verify_yang_2023_emotional_eating_ders.R
#
# CLAIM UNDER TEST. data/yang_2023_emotional_eating.py assigns the item codes
# POSITIONALLY: DERS_<i> is the i-th column of the DERS block of the PLOS S1
# Data workbook (the one unprefixed column "13Please read the topic carefully..."
# followed by the 35 columns whose headers start with "@13"). The shipped
# item_text for DERS_<i> (i >= 2) is that column's own header with its "@13,<i> "
# prefix stripped, so the mapping is only right if (a) the positional
# reconstruction reproduces the live table column for column, and (b) each
# header's embedded item number equals its position.
#
# Route: response-frequency matching, per item (Step 5b route 9 applied to the
# item axis). For every item we compare the count of each response level 1..5 in
# the live IRW table against the count in the reconstructed source column --
# 36 x 5 = 180 cells. Because all 36 count-vectors are distinct, a match pins
# EVERY item individually: swapping any two items' text would break two rows.
#
# Secondary, printed but not part of the verdict: keying polarity. The 11
# canonical DERS reverse-keyed (positively worded) items must be the ones whose
# correlation with the sum of the other 25 is near zero/negative if the data are
# stored raw with 5 = "almost always".

suppressMessages({library(irw); library(readxl)})

TABLE <- "yang_2023_emotional_eating_ders"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file?",
                 "type=supplementary&id=10.1371/journal.pone.0280701.s001")

xlsx <- file.path(tempdir(), "yang2023_s1.xlsx")
cached <- ".cache/yang_2023_emotional_eating_ders/s1.xlsx"
if (file.exists(cached)) xlsx <- cached else
    download.file(SI_URL, xlsx, mode = "wb", quiet = TRUE)

raw <- suppressMessages(readxl::read_excel(xlsx))
hdr <- names(raw)
intro <- "13Please read the topic carefully and choose it according to your actual situation"
block <- c(intro, grep("^@13", hdr, value = TRUE))
stopifnot(length(block) == 36)

# (b) header-embedded numbering == position, for the 35 numbered headers
nums <- as.integer(sub("^@13,(\\d+).*$", "\\1", block[-1]))
num_ok <- identical(nums, 2:36)
cat("header numbering: @13,<n> equals its position for",
    sum(nums == 2:36), "of 35 numbered headers (item 1's header is the block's",
    "instruction text, so its position is fixed by elimination)\n\n")

src <- as.data.frame(raw[, block])
names(src) <- paste0("DERS_", 1:36)

d <- irw::irw_fetch(TABLE)
live_tab <- table(factor(d$item, levels = paste0("DERS_", 1:36)),
                  factor(d$resp, levels = 1:5))

src_tab <- t(sapply(names(src), function(cn) {
    v <- suppressWarnings(as.numeric(src[[cn]]))
    sapply(1:5, function(k) sum(v == k, na.rm = TRUE))
}))

cat(sprintf("%-9s %-22s %-22s %s\n", "item", "live counts 1..5", "source counts 1..5", "ok"))
ok <- logical(36)
for (i in 1:36) {
    l <- as.integer(live_tab[i, ]); s <- as.integer(src_tab[i, ])
    ok[i] <- identical(l, s)
    cat(sprintf("%-9s %-22s %-22s %s\n", paste0("DERS_", i),
                paste(l, collapse = ","), paste(s, collapse = ","),
                if (ok[i]) "MATCH" else "MISMATCH"))
}

uniq <- length(unique(apply(src_tab, 1, paste, collapse = ",")))
cat(sprintf("\ncells matched: %d of 180; items matched: %d of 36\n",
            sum(live_tab == src_tab), sum(ok)))
cat(sprintf("distinct count-vectors among the 36 source columns: %d of 36 -- %s\n",
            uniq, if (uniq == 36)
              "no two items share a response distribution, so this route separates every item"
            else "some items are indistinguishable by this route"))

# secondary: polarity
w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
POS <- paste0("DERS_", c(1, 2, 6, 7, 8, 10, 17, 20, 22, 24, 34))
NEG <- setdiff(paste0("DERS_", 1:36), POS)
negsum <- rowSums(w[, NEG], na.rm = TRUE)
rs <- sapply(paste0("DERS_", 1:36), function(cn) {
    tot <- negsum - if (cn %in% NEG) w[[cn]] else 0
    suppressWarnings(cor(w[[cn]], tot, use = "complete.obs"))
})
cat(sprintf("\npolarity (r with sum of the 25 difficulty items):\n  canonical reverse-keyed 11: %.3f to %.3f\n  other 25: %.3f to %.3f\n",
            min(rs[POS]), max(rs[POS]), min(rs[NEG]), max(rs[NEG])))
pol_ok <- max(rs[POS]) < min(rs[NEG])
cat("  separation clean:", pol_ok, "-- confirms the data are stored RAW and that resp 5 is the\n",
    " high-frequency anchor, i.e. the option_text direction shipped.\n")

cat("\nNote: this route does NOT establish the wording of DERS_1 (its source header is the\n",
    "block's instruction text, so its item_text is the canonical Gratz & Roemer item 1,\n",
    "placed by elimination and corroborated only by its reverse-keyed polarity above), and it\n",
    "says nothing about the option labels, which are the canonical DERS anchors rather than\n",
    "the administered Chinese ones.\n", sep = "")

cat(if (all(ok) && num_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
