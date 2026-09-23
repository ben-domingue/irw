# verify_magiccats_ozono_2020.R -- Step 5b check for the resp<->option_text axis.
#
# The item axis needs no check: data/magiccats_ozono_2020.py melts the OSF
# 'participants data.csv' with item = source column header (pattern 1), and
# item_text is that header verbatim. What carried inference is resp: the paper
# (Ozono et al. 2021, BRM, PMC7880926) and the deposit's 'description of data.pdf'
# describe the scales as 1 (not at all)..10 (very much) and 1 not at all /
# 2 a little bit / 3 frequently, but the participant file (and so the live table)
# stores 0..9 and 0..2. The shipped anchors assume stored = described - 1.
#
# Two things would break that assumption: (a) a range that is not 10 / 3
# consecutive levels starting at 0 (then it is not a shift), (b) a reversed
# direction (0 = very much). (b) is tested against the SAME respondents'
# per-trick 'Interest in the trick' ratings in 'rating data.csv', which the
# deposit stores on the described 1..10 scale (1 = not at all): general interest
# must correlate POSITIVELY with mean per-trick interest; and the 'performing'
# item must floor at 0 in an MTurk sample (not at all) with performers rating
# general interest higher.
#
# Does NOT establish: that the administered interest points 2..9 carried labels
# (none are published; option_text is blank there), nor the literal on-screen
# question wording (never published; item_text is the deposit's column label).

suppressMessages(library(irw))
TABLE <- "magiccats_ozono_2020"
I1 <- "How interested in the magic tricks"
I2 <- "Performing magic tricks by themselves"

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)

tf <- tempfile(fileext = ".csv")
download.file("https://osf.io/download/kgh6e/", tf, quiet = TRUE, mode = "wb")
r <- read.csv(tf, check.names = FALSE, fileEncoding = "UTF-8-BOM")

ok <- TRUE
lv1 <- sort(unique(d$resp[d$item == I1])); lv2 <- sort(unique(d$resp[d$item == I2]))
cat("live levels, interest:  ", lv1, "\n")
cat("live levels, performing:", lv2, "\n")
cat("rating-file levels, 'Interest in the trick':", sort(unique(r[["Interest in the trick"]])), "\n")
if (!identical(as.numeric(lv1), as.numeric(0:9)) || !identical(as.numeric(lv2), as.numeric(0:2))) ok <- FALSE

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
m <- aggregate(r[["Interest in the trick"]], list(id = r[["Participant ID"]]), mean)
x <- merge(w, m, by = "id")
rho <- cor(x[[I1]], x$x, method = "spearman", use = "complete.obs")
cat(sprintf("\nn = %d; Spearman(general interest, mean per-trick interest 1..10) = %+.3f\n", nrow(x), rho))
if (!(rho > 0.2)) ok <- FALSE

tab <- table(d$resp[d$item == I2])
cat("performing counts by stored level:", paste(names(tab), tab, sep = "=", collapse = "  "), "\n")
p0 <- as.numeric(tab["0"]) / sum(tab)
cat(sprintf("share at 0 = %.3f (expect majority = 'not at all' in MTurk sample)\n", p0))
if (!(p0 > 0.5)) ok <- FALSE
g <- tapply(x[[I1]], x[[I2]], mean)
cat("mean general interest by performing level:", paste(names(g), round(g, 2), sep = "=", collapse = "  "), "\n")
if (!(g["0"] < g["1"] && g["1"] < g["2"])) ok <- FALSE

cat("\nNot established: labels for interest points 1..8 (unpublished) and the on-screen wording.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
