# verify_kern_2021_connectedness.R
#
# CLAIM UNDER TEST: item_text for C1..C9 is tied to those exact codes by the study's
# own Supplementary Material 1 (Gan et al. 2022, Front. Psychol. 13:827517, CC BY 4.0;
# supplementary file Table_2.DOCX), which prints a Labels x Measurement items table
# using the very codes the live IRW data uses. data/kern_2021_positive_edu.py melts the
# figshare workbook (files/28626591) by column NAME, so live item == workbook header.
#
# CHECK 1 (the mapping): re-download the supplement, parse the C rows, and require that
#   the text shipped for each code equals the text printed against that code.
#   This is what breaks if C3 and C5 were swapped.
# CHECK 2 (the name link): re-download the figshare workbook and require that each
#   live item's 350 responses equal, respondent by respondent, the workbook column of
#   the same name -- and differ from every other C column (so the check separates
#   every item from every other).
# CHECK 3 (option direction, 1 = Strongly disagree): in the raw workbook the C total
#   must correlate positively with the SHS total, whose anchors run 'Not a very happy
#   person'(1) .. 'A very happy person'(7) (same supplement), as the paper reports
#   (Fornell-Larcker latent r = 0.210).
# CORROBORATION ONLY: paper Table 2 PLS outer loadings vs live one-factor loadings.

suppressMessages(library(irw))
TABLE <- "kern_2021_connectedness"
ITEMS <- paste0("C", 1:9)

args <- commandArgs(FALSE)
here <- dirname(sub("^--file=", "", args[grep("^--file=", args)][1]))
ship <- read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
shipped <- tapply(ship$item_text, ship$item, function(x) unique(x)[1])[ITEMS]
cache <- file.path(here, "..", "..", ".cache", TABLE)
norm <- function(s) trimws(gsub("\\s+", " ", gsub("[\u2018\u2019\u201c\u201d]", "'", s)))

## ---- 1. supplement label match ---------------------------------------------
get_supp <- function() {
    f <- file.path(cache, "supp", "Table_2.DOCX")
    if (!file.exists(f)) {
        z <- tempfile(fileext = ".zip")
        ok <- tryCatch({ download.file(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8931502/supplementaryFiles",
            z, quiet = TRUE, mode = "wb"); TRUE }, error = function(e) FALSE)
        if (!ok) return(NULL)
        unzip(z, files = "Table_2.DOCX", exdir = tempdir(), overwrite = TRUE)
        f <- file.path(tempdir(), "Table_2.DOCX")
    }
    xml <- tryCatch(paste(readLines(unz(f, "word/document.xml"), warn = FALSE), collapse = ""),
                    error = function(e) NULL)
    if (is.null(xml)) return(NULL)
    xml <- gsub("</w:p>", " ", xml); xml <- gsub("</w:tc>", "\t", xml); xml <- gsub("</w:tr>", "\n", xml)
    unlist(strsplit(gsub("<[^>]+>", "", xml), "\n"))
}
lines <- get_supp()
ok1 <- FALSE
if (is.null(lines)) cat("!! supplement unavailable -- check 1 could not run\n") else {
    hits <- sapply(ITEMS, function(code) {
        row <- lines[grepl(paste0("^\\s*", code, "\\s*\t"), lines)]
        supp <- if (length(row)) norm(sub("\t.*$", "", sub(paste0("^\\s*", code, "\\s*\t"), "", row[1]))) else "<none>"
        m <- identical(supp, norm(shipped[[code]]))
        cat(sprintf("%-3s %-5s %s\n", code, if (m) "OK" else "MISM", substr(supp, 1, 90)))
        m
    })
    ok1 <- all(hits)
    cat(sprintf("check 1: supplement label-to-text match %d/%d\n\n", sum(hits), length(ITEMS)))
}

## ---- 2. live item == workbook column of the same name ----------------------
wbf <- file.path(cache, "supp.xlsx")
if (!file.exists(wbf)) {
    wbf <- tempfile(fileext = ".xlsx")
    tryCatch(download.file("https://ndownloader.figshare.com/files/28626591", wbf, quiet = TRUE, mode = "wb"),
             error = function(e) NULL)
}
raw <- tryCatch(as.data.frame(readxl::read_excel(wbf, sheet = 1)), error = function(e) NULL)
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w)); w <- w[order(w$id), ]
ok2 <- FALSE; ok3 <- FALSE
if (is.null(raw)) cat("!! workbook unavailable -- checks 2/3 could not run\n") else {
    # id = row index + 1 in the processing script
    agree <- outer(ITEMS, ITEMS, Vectorize(function(a, b) mean(w[[a]] == raw[[b]])))
    dimnames(agree) <- list(live = ITEMS, workbook = ITEMS)
    cat("check 2: share of 350 respondents where live item (row) == workbook column (col)\n")
    print(round(agree, 3))
    offdiag_max <- max(agree[row(agree) != col(agree)])
    ok2 <- all(diag(agree) == 1) && offdiag_max < 1
    cat(sprintf("diagonal all 1: %s ; max off-diagonal agreement %.3f (must be < 1)\n\n",
                all(diag(agree) == 1), offdiag_max))
    r <- cor(rowSums(raw[, ITEMS]), rowSums(raw[, paste0("SHS", 1:3)]))
    ok3 <- r > 0
    cat(sprintf("check 3: raw C total vs SHS total r = %+.3f (paper latent r = +0.210); positive => 1 = Strongly disagree\n\n", r))
}

## ---- corroboration: loadings -------------------------------------------------
PUB <- c(0.702, 0.724, 0.779, 0.816, 0.802, 0.709, 0.706, 0.778, 0.721)
fa <- factanal(na.omit(as.matrix(w[, ITEMS])), factors = 1)
obs <- fa$loadings[ITEMS, 1]
cat("corroboration: paper PLS loadings vs live one-factor loadings\n")
for (i in seq_along(ITEMS)) cat(sprintf("%-3s %6.3f %6.3f\n", ITEMS[i], PUB[i], obs[i]))
cat(sprintf("Spearman rho = %.2f (corroboration only; loadings are too close to separate items)\n",
            cor(PUB, obs, method = "spearman")))
cat("Note: every item is separated from every other by check 1 (label match) plus check 2\n",
    "(exact per-respondent identity with the same-named workbook column); the loadings do not.\n", sep = "")

cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
