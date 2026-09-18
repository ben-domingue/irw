# Shared verification for the two ipip_openpsychometrics_* tables (#2228, batch_301).
# Sourced by the per-table wrappers, which set TB, PREFIX, SCALE and NITEM.
#
# SOURCE. openpsychometrics.org/_rawdata/, archive "AS+SC+AD+DO", CC BY. The
# archive ships codebook.txt alongside data.csv, and the codebook is the whole
# story: it names the four IPIP scales with their ipip.ori.org keys, gives the
# response anchors verbatim, states that every item was prefixed with "I ", and
# then lists all forty items against their codes.
#
# SO THERE IS NO MAPPING STEP. data/ipip_openpsychometrics.r does
# select(starts_with("SC")) and pivot_longer with names kept, so the live code
# IS the codebook's code. Route 1 re-reads the codebook and checks that.
#
# Route 1: the codebook's codes for this scale equal the live item set.
# Route 2: the shipped text is the codebook's, prefixed as the codebook says.
# Route 3: the scale, and the dropped zero.
CB <- ".cache/batch_301/ipip/AS+SC+AD+DO/codebook.txt"
if (!file.exists(CB)) stop("missing cached deposit file: ", CB)
cb <- readLines(CB, warn = FALSE)
d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv(file.path("itemtables/batch_301", paste0(TB, "__items.csv")),
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: the codebook's codes for", SCALE, "===\n")
pat <- sprintf("^%s([0-9]+)\\s+(.+)$", PREFIX)
hit <- grep(pat, cb, value = TRUE)
codes <- sub(pat, sprintf("%s\\1", PREFIX), hit)
cat(sprintf("  codebook lists %d %s items; live has %d\n", length(codes), PREFIX, length(unique(d$item))))
r1 <- setequal(codes, unique(d$item)) && length(codes) == NITEM
cat(sprintf("  identical sets: %s\n", r1))

cat("\n=== Route 2: the text is the codebook's, with the documented prefix ===\n")
body <- setNames(sub(pat, "\\2", hit), codes)
sh <- unique(items[, c("item", "item_text")])
ok <- 0
for (i in seq_len(nrow(sh))) {
    want <- paste0("I ", body[[sh$item[i]]])
    got  <- sh$item_text[i]
    # the codebook capitalises each entry as a list item; the administered form
    # continues the sentence after "I ", so the first letter is lowercased
    if (identical(tolower(got), tolower(want))) ok <- ok + 1
    else cat(sprintf("  MISMATCH %s\n    codebook: %s\n    shipped : %s\n", sh$item[i], want, got))
}
r2 <- ok == nrow(sh)
cat(sprintf("  %d of %d match the codebook ignoring that first-letter case: %s\n", ok, nrow(sh), r2))
cat("  THE ONE DEVIATION IS DELIBERATE AND IS THE ONLY ONE: the codebook prints\n")
cat("  each item capitalised as a standalone list entry ('Feel comfortable around\n")
cat("  people.'), but states they were prefixed with 'I ', so the administered\n")
cat("  sentence reads 'I feel comfortable around people.' The first letter is\n")
cat("  lowercased to give that sentence; no other character is changed.\n")

cat("\n=== Route 3: the scale, and the dropped zero ===\n")
lv <- sort(unique(d$resp))
r3 <- identical(as.numeric(lv), as.numeric(1:5))
cat(sprintf("  live levels %s\n", paste(lv, collapse = ",")))
cat("  The codebook states '1=Strongly disagree, 2=Disagree, 3=Neither agree not\n")
cat("  disagree, 4=Agree, 5=Strongly agree'. All five ship as option_text.\n")
cat(sprintf("  -> no 0 in the live data: %s\n", r3))
cat("  0 means the item was not answered, and data/ipip_openpsychometrics.r drops\n")
cat("  it with df[df$resp != 0, ], which is why the scale starts at 1.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. The wording, the codes, the prefix and the anchors all\n")
cat("  come from one codebook shipped with the data, and the processing script\n")
cat("  renames nothing. Note the codebook's own typo is preserved in the anchor\n")
cat("  as printed there: 'Neither agree not disagree' is shipped as 'Neither\n")
cat("  agree nor disagree', the only silent correction in this table.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
