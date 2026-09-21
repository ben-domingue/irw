# verify_hoai_2026_cognitive_presence.R
#
# CLAIM under test: item codes CP1..CP4 in the live IRW table carry the four
# Cognitive Presence statements in the order the deposit's codebook assigns them,
# and the Vietnamese wording shipped in item_text is the same four statements.
#
# What would break if CP2 and CP3 were swapped:
#   (a) the codebook's VARIABLE->LABEL rows (explicit code labels) would no longer
#       reproduce the shipped item_text_translated;
#   (b) the distinctive-content crosswalk below would mis-assign the Vietnamese
#       stem to the wrong English statement.
#
# Route: explicit code labels in the deposit codebook (codebook.docx, Mendeley
# tdsspksw83) + a content crosswalk pinning each Vietnamese stem to its English twin.

suppressMessages({library(xml2); library(irw); library(stringi)})

TABLE <- "hoai_2026_cognitive_presence"
BASE  <- "https://data.mendeley.com/public-api/datasets/tdsspksw83"
ITEMS <- paste0("CP", 1:4)

# ---- fetch the deposit's own files -------------------------------------------
tmp <- tempfile("hoai"); dir.create(tmp)
meta <- jsonlite::fromJSON(BASE, simplifyVector = FALSE)
get_file <- function(name) {
    hit <- Filter(function(f) f$filename == name, meta$files)
    stopifnot(length(hit) == 1)
    p <- file.path(tmp, gsub(" ", "_", name))
    utils::download.file(hit[[1]]$content_details$download_url, p, quiet = TRUE, mode = "wb")
    p
}

docx_tables <- function(path) {
    d <- file.path(tmp, paste0(basename(path), "_x")); dir.create(d, showWarnings = FALSE)
    utils::unzip(path, files = "word/document.xml", exdir = d)
    x <- xml2::read_xml(file.path(d, "word", "document.xml"))
    lapply(xml2::xml_find_all(x, ".//w:tbl"), function(tbl)
        lapply(xml2::xml_find_all(tbl, "./w:tr"), function(tr)
            vapply(xml2::xml_find_all(tr, "./w:tc"),
                   function(tc) trimws(paste(xml2::xml_text(xml2::xml_find_all(tc, ".//w:t")), collapse = "")),
                   character(1))))
}
norm <- function(s) stringi::stri_trans_nfc(trimws(gsub("[[:space:]]+", " ", s)))

# ---- codebook: VARIABLE -> LABEL ---------------------------------------------
cb_tbl <- docx_tables(get_file("codebook.docx"))[[2]]
cb <- setNames(vapply(cb_tbl, function(r) norm(r[3]), character(1)),
               vapply(cb_tbl, function(r) norm(r[1]), character(1)))

# ---- questionnaire blocks (EN and VN): construct blocks in document order ----
# Merged construct-header rows come back as a single cell; item rows have 6.
q_blocks <- function(path) {
    rs <- docx_tables(path)[[1]]; blocks <- list(); cur <- NULL
    for (r in rs) {
        if (length(r) == 1L) { if (!is.null(cur)) blocks[[length(blocks) + 1L]] <- cur; cur <- character(0); next }
        if (!is.null(cur) && nzchar(r[1])) cur <- c(cur, norm(r[1]))
    }
    if (!is.null(cur)) blocks[[length(blocks) + 1L]] <- cur
    blocks
}
enb <- q_blocks(get_file("Questionaire_EN.docx"))
vnb <- q_blocks(get_file("Questionaire_VN.docx"))
cat(sprintf("questionnaire blocks: EN %s | VN %s  (CP is block 3)\n",
            paste(lengths(enb), collapse = "-"), paste(lengths(vnb), collapse = "-")))
ok0 <- identical(lengths(enb), lengths(vnb)) && identical(lengths(enb), c(5L, 4L, 4L, 5L, 4L, 4L, 4L))
en <- enb[[3]]
vn <- vnb[[3]]

# ---- shipped table ------------------------------------------------------------
ship <- read.csv(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(), value = TRUE)[1])),
                           paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE, encoding = "UTF-8")
ship <- unique(ship[, c("item", "item_text", "item_text_translated")])
rownames(ship) <- ship$item

# ---- check 1: live item set ---------------------------------------------------
live <- sort(as.character(irw::irw_table_sets(TABLE)$item))
cat("live item set:", paste(live, collapse = ", "), "\n\n")

# ---- check 2: codebook label == shipped English, per code ---------------------
cat("codebook LABEL vs shipped item_text_translated\n")
ok1 <- TRUE
for (i in seq_along(ITEMS)) {
    a <- cb[[ITEMS[i]]]; b <- norm(ship[ITEMS[i], "item_text_translated"])
    m <- identical(a, b); ok1 <- ok1 && m
    cat(sprintf("  %-4s %-5s codebook: %s\n", ITEMS[i], if (m) "MATCH" else "DIFF", a))
    if (!m) cat(sprintf("       shipped : %s\n", b))
}

# ---- check 3: codebook order == EN questionnaire CP block order ---------------
cat(sprintf("\ncodebook CP1..CP4 == EN questionnaire CP block rows 1..4: %d/%d\n",
            sum(vapply(seq_along(ITEMS), function(i) identical(cb[[ITEMS[i]]], en[i]), logical(1))),
            length(ITEMS)))
ok2 <- all(vapply(seq_along(ITEMS), function(i) identical(cb[[ITEMS[i]]], en[i]), logical(1)))

# ---- check 4: Vietnamese stem pinned to its English twin by distinctive content
# Each pair below appears in exactly one of the four statements, so a swap of any
# two items breaks at least two rows of this table.
key <- list(CP1 = c("nội dung môn học", "course content"),
            CP2 = c("giải quyết các vấn đề", "solutions to problems"),
            CP3 = c("tình huống thực tế", "real-life situations"),
            CP4 = c("học liệu số", "digital resources"))
cat("\ndistinctive-content crosswalk (VN phrase / EN phrase: rows hit, must be 1 and the same item)\n")
ok3 <- TRUE
for (code in ITEMS) {
    hv <- ITEMS[grepl(key[[code]][1], vn, fixed = TRUE)]
    he <- ITEMS[grepl(key[[code]][2], vapply(ITEMS, function(k) cb[[k]], character(1)), fixed = TRUE)]
    sv <- ITEMS[grepl(key[[code]][1], norm(ship[ITEMS, "item_text"]), fixed = TRUE)]
    good <- identical(hv, code) && identical(he, code) && identical(sv, code)
    ok3 <- ok3 && good
    cat(sprintf("  %-4s VN questionnaire -> %-12s codebook EN -> %-12s shipped item_text -> %-12s %s\n",
                code, paste(hv, collapse = "/"), paste(he, collapse = "/"),
                paste(sv, collapse = "/"), if (good) "ok" else "MISMATCH"))
}

# ---- check 5: shipped Vietnamese == VN questionnaire block, in order ----------
ok4 <- all(vapply(seq_along(ITEMS), function(i)
    identical(norm(ship[ITEMS[i], "item_text"]), vn[i]), logical(1)))
cat(sprintf("\nshipped item_text == VN questionnaire CP block rows 1..4: %d/%d\n",
            sum(vapply(seq_along(ITEMS), function(i)
                identical(norm(ship[ITEMS[i], "item_text"]), vn[i]), logical(1))), length(ITEMS)))

cat("\nNote: this route pins every one of the four items individually -- the codebook\n",
    "names the code beside its statement, and the crosswalk phrases are unique to one\n",
    "statement each, so no permutation of CP1..CP4 survives. It does NOT check the\n",
    "resp<->option_text direction, which rests on the codebook's stated coding\n",
    "(1 = Strongly disagree ... 5 = Strongly agree) and is not testable from the data.\n", sep = "")

cat(if (ok0 && ok1 && ok2 && ok3 && ok4 && identical(live, ITEMS)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
