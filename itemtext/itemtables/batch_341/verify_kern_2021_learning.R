# verify_kern_2021_learning.R
#
# CLAIM UNDER TEST: item_text for L1..L12 is tied to those exact codes by the study's
# own Supplementary Material 1 (Gan et al. 2022, Front. Psychol. 13:827517, CC BY 4.0;
# supplementary file Table_2.DOCX), whose "Life skills" block prints L1..L12 beside
# their statements. data/kern_2021_positive_edu.py melts the figshare workbook
# (files/28626591) by column NAME, so live item == workbook header.
#
# CHECK 1 (the mapping): re-read the supplement, parse the L rows, and require that
#   the text shipped for each code equals the text printed against that code
#   (one disclosed correction: L5's source "l am" -> shipped "I am").
# CHECK 2 (the name link): each live item's 350 responses must equal, respondent by
#   respondent, the workbook column of the same name -- and differ from every other
#   L column (max off-diagonal agreement < 1), so every item is separated.
# CHECK 3 (option direction, 1 = Strongly disagree): raw L total must correlate
#   positively with the SHS total (paper Table 3 latent r = 0.231).
# CORROBORATION ONLY: paper Table 1 T3 M(SD) for L11 2.92 (0.50) and L12 2.96 (0.54);
#   paper Table 2 PLS loadings vs live one-factor loadings.

suppressMessages(library(irw))
TABLE <- "kern_2021_learning"
ITEMS <- paste0("L", 1:12)

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
        supp_c <- sub("^l am ", "I am ", supp)   # disclosed typo correction (L5)
        m <- identical(supp_c, norm(shipped[[code]]))
        cat(sprintf("%-4s %-5s %s%s\n", code, if (m) "OK" else "MISM", substr(supp, 1, 90),
                    if (supp_c != supp) "  [l->I corrected]" else ""))
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
raw <- tryCatch(suppressMessages(as.data.frame(readxl::read_excel(wbf, sheet = 1))), error = function(e) NULL)
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
    ok2 <- nrow(w) == nrow(raw) && all(diag(agree) == 1) && offdiag_max < 1
    cat(sprintf("diagonal all 1: %s ; max off-diagonal agreement %.3f (must be < 1)\n\n",
                all(diag(agree) == 1), offdiag_max))
    r <- cor(rowSums(raw[, ITEMS]), rowSums(raw[, paste0("SHS", 1:3)]))
    ok3 <- r > 0
    cat(sprintf("check 3: raw L total vs SHS total r = %+.3f (paper latent r = +0.231); positive => 1 = Strongly disagree\n\n", r))
}

## ---- corroboration -------------------------------------------------------------
cat("corroboration: paper Table 1 T3 M (SD) vs live\n")
for (x in list(c("L11", 2.92, 0.50), c("L12", 2.96, 0.54)))
    cat(sprintf("%-4s paper %s (%s)  live %.2f (%.2f)\n", x[1], x[2], x[3],
                mean(w[[x[1]]]), sd(w[[x[1]]])))
PUB <- c(0.727, 0.716, 0.783, 0.814, 0.797, 0.770, 0.753, 0.769, 0.751, 0.781, 0.803, 0.785)
fa <- factanal(na.omit(as.matrix(w[, ITEMS])), factors = 1)
obs <- fa$loadings[ITEMS, 1]
cat("paper PLS loadings vs live one-factor loadings\n")
for (i in seq_along(ITEMS)) cat(sprintf("%-4s %6.3f %6.3f\n", ITEMS[i], PUB[i], obs[i]))
cat(sprintf("Spearman rho = %.2f (corroboration only; loadings are too close to separate items)\n",
            cor(PUB, obs, method = "spearman")))
cat("Note: every item is separated from every other by check 1 (label match) plus check 2\n",
    "(exact per-respondent identity with the same-named workbook column); the M/SD and loadings do not.\n", sep = "")

cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
