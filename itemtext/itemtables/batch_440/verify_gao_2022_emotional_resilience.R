# verify_gao_2022_emotional_resilience.R -- Step 5b check, batch_440.
#
# Claim: data/gao_2022_covid_stress.py assigns ERQ_1..ERQ_11 POSITIONALLY to the
# S1 Dataset (PLOS 10.1371/journal.pone.0279071.s001) columns 66..76 (0-based
# pandas positions), whose header cells are the numbered Chinese stems "1." ..
# "11." shipped as item_text. This script re-derives that mapping from the raw
# file rather than trusting the script:
#   (1) header diff: the shipped item_text for ERQ_k equals the header at
#       column 65+k (0-based), with the leading "k." and, for k=1, the block
#       instruction prefix stripped;
#   (2) respondent-level identity: for each live item ERQ_k and each raw column
#       66..76, the share of respondents (joined on the source 序号 id) whose
#       live resp equals the raw cell. The mapping is proven iff the diagonal
#       is 100% and every off-diagonal cell is well below it -- that
#       distinguishes every item from every other item, not just the set.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "gao_2022_emotional_resilience"
here  <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) getwd())
cache <- file.path("/home/ben/irw-queue-runner/itemtext/.cache", TABLE, "s001.xlsx")
xlsx  <- if (file.exists(cache)) cache else {
    f <- tempfile(fileext = ".xlsx")
    download.file(paste0("https://journals.plos.org/plosone/article/file",
                         "?type=supplementary&id=10.1371/journal.pone.0279071.s001"),
                  f, mode = "wb", quiet = TRUE)
    f
}
raw <- suppressMessages(read_excel(xlsx, .name_repair = "minimal"))
stopifnot(ncol(raw) == 77)
hdr <- names(raw)[67:77]                     # 1-based 67..77 == pandas 66..76
cat("Raw header check (column -> leading number):\n")
nums <- as.integer(sub("^.*?(\\d+)\\.[^.]*$", "\\1",
                       sub("^.*—", "", hdr)))
print(data.frame(col0 = 66:76, leading_number = nums))

ok <- TRUE
# (1) header diff against the shipped item_text
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv))
    items_csv <- file.path("/home/ben/irw-queue-runner/itemtext/itemtables/batch_440",
                           paste0(TABLE, "__items.csv"))
it <- read.csv(items_csv, stringsAsFactors = FALSE, encoding = "UTF-8")
it <- unique(it[, c("item", "item_text")])
stem <- sub("^\\d+\\.", "", sub("^.*—", "", hdr))
n_match <- 0
for (k in 1:11) {
    shipped <- it$item_text[it$item == paste0("ERQ_", k)]
    m <- identical(shipped, stem[k])
    n_match <- n_match + m
    cat(sprintf("ERQ_%-2d header col %d  %s\n", k, 65 + k, if (m) "== shipped" else "MISMATCH"))
}
cat(sprintf("Header diff: %d/11 shipped item_text identical to the source header at the assigned position\n", n_match))
if (n_match != 11 || !identical(nums, 1:11)) ok <- FALSE

# (2) respondent-level identity matrix
d <- irw::irw_fetch(TABLE)
rid <- as.numeric(raw[[1]])
agree <- matrix(NA_real_, 11, 11,
                dimnames = list(paste0("ERQ_", 1:11), paste0("col", 66:76)))
for (k in 1:11) {
    dk <- d[d$item == paste0("ERQ_", k), c("id", "resp")]
    idx <- match(dk$id, rid)
    for (j in 1:11) agree[k, j] <- mean(as.numeric(raw[[66 + j]][idx]) == dk$resp, na.rm = TRUE)
}
cat("\nShare of respondents whose live resp equals the raw cell (rows = live item, cols = raw column):\n")
print(round(agree, 3))
diag_min <- min(diag(agree)); off_max <- max(agree[row(agree) != col(agree)])
cat(sprintf("\nDiagonal min = %.4f (n per item: %s)\nOff-diagonal max = %.4f\n",
            diag_min, paste(table(d$item)[paste0("ERQ_", 1:11)], collapse = "/"), off_max))
if (diag_min < 1 || off_max > 0.8) ok <- FALSE
cat("Establishes: every ERQ_k is raw column 65+k for every respondent, and its text is that column's header.\n",
    "Does not establish: option labels (none shipped; the paper's 0-6 never..always description has 7 points against 6 stored levels).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
