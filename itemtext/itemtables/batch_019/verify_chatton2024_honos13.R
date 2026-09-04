# verify_chatton2024_honos13.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM: item honos_NN carries the text of item NN in Table 1 of Chatton et al.
# (2023) Addict Sci Clin Pract, doi:10.1186/s13722-023-00416-8.
#
# The mapping chain is a NUMBER match, not an order inference:
#   paper Table 1 "NN. <item name>"  <->  deposit column HonosE<NN>/HonosS<NN>
#   <->  IRW code honos_NN, because data/chatton2024_honos13.py strips the
#   "HonosE"/"HonosS" prefix and zero-pads the remaining integer.
# This script re-establishes the falsifiable half of that chain: the severity
# profile the paper publishes for item NN must be the profile the deposit's
# column NN actually has. Fetches the public figshare deposit (no IRW export).

suppressWarnings(suppressMessages({
  ok <- requireNamespace("readxl", quietly = TRUE)
}))
if (!ok) stop("needs the readxl package")

TABLE <- "chatton2024_honos13"
URL   <- "https://ndownloader.figshare.com/files/48461233"  # 10.6084/m9.figshare.26631202.v1

# Paper Table 1 "Distribution of HoNOS-13": response rate (%) at scores 0..4,
# items 1..13 in the order the table prints them.
PUB <- matrix(c(
  68.9,15.2,10.6, 3.8, 1.6,
  82.1, 9.2, 5.3, 2.8, 0.6,
  12.0,12.0,19.7,33.5,22.8,
  72.9,14.7, 8.5, 3.4, 0.6,
  62.7,16.5,13.8, 5.9, 1.2,
  77.1, 8.9, 6.9, 4.6, 2.5,
  18.5,23.8,37.6,15.6, 4.5,
  27.8,18.3,37.2,13.5, 3.3,
  31.3,31.5,26.5, 8.5, 2.2,
  38.7,24.9,24.4, 9.3, 2.7,
  37.6,22.8,22.4,11.5, 5.6,
  20.8,24.6,35.3,15.7, 3.7,
  60.3,12.9,14.6, 7.5, 4.7), nrow = 13, byrow = TRUE)
pub_mean <- as.vector(PUB %*% (0:4)) / 100

# Item names as printed in Table 1 -- what the shipped CSV must carry.
PUB_TEXT <- c(
 "Overactive, aggressive, disruptive or agitated behaviour",
 "Non-accidental self-injury",
 "Problem drinking or drug taking",
 "Cognitive problems",
 "Physical illness or disability problems",
 "Problems with hallucinations and delusions",
 "Problems with depressed mood",
 "Other mental and behavioural problems",
 "Problems with relationships",
 "Problems with activities of daily living",
 "Problems with living conditions",
 "Problems with occupation and activities",
 "Problems with psychotropic medication compliance")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
x <- as.data.frame(readxl::read_excel(tmp))

# --- 1. the shipped CSV must place PUB_TEXT[n] on honos_<n> ---
csvp <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                  paste0(TABLE, "__items.csv"))
if (!file.exists(csvp)) csvp <- paste0("itemtables/batch_019/", TABLE, "__items.csv")
it <- read.csv(csvp, stringsAsFactors = FALSE)
shipped <- tapply(it$item_text, it$item, function(z) unique(z)[1])[sprintf("honos_%02d", 1:13)]
text_ok <- all(shipped == PUB_TEXT)
cat("shipped item_text == Table 1 name, item by item: ", text_ok, "\n\n", sep = "")

# --- 2. deposit column NN must have the severity profile the paper gives item NN ---
obs_mean <- sapply(1:13, function(n) mean(x[[paste0("HonosE", n)]], na.rm = TRUE))
rho <- suppressWarnings(cor(pub_mean, obs_mean, method = "spearman"))

cat(sprintf("%-6s %-52s %9s %9s %6s %6s\n",
            "item", "Table 1 name", "pub mean", "obs mean", "p.rank", "o.rank"))
pr <- rank(pub_mean); orr <- rank(obs_mean)
for (n in 1:13)
  cat(sprintf("%-6s %-52s %9.2f %9.2f %6.0f %6.0f\n",
              sprintf("honos_%02d", n), substr(PUB_TEXT[n], 1, 52),
              pub_mean[n], obs_mean[n], pr[n], orr[n]))

cat(sprintf("\nSpearman(paper Table 1 item means, deposit HonosE column means), n=13: %.4f\n", rho))
cat(sprintf("most severe item -- paper: %d, deposit column: %d (expected 3, 'Problem drinking or drug taking')\n",
            which.max(pub_mean), which.max(obs_mean)))
cat(sprintf("three least severe -- paper: %s, deposit: %s (expected 2, 4, 6)\n",
            paste(sort(order(pub_mean)[1:3]), collapse = ","),
            paste(sort(order(obs_mean)[1:3]), collapse = ",")))
cat(sprintf("max |rank difference| under the identity mapping: %.0f\n", max(abs(pr - orr))))

extremes_ok <- which.max(obs_mean) == 3 &&
               identical(sort(order(obs_mean)[1:3]), sort(order(pub_mean)[1:3]))

cat("\nNote: the deposit's absolute severity runs above Table 1 (Table 1's exact\n",
    "analysis subset is not identified in the paper), so this route is matched on\n",
    "rank/profile rather than on levels; it corroborates the numbering match that\n",
    "carries the mapping. Separately, HonosE1 and HonosS1 are byte-identical across\n",
    "all 609 deposit rows -- a defect in the response data, not in the item text.\n", sep = "")

pass <- text_ok && !is.na(rho) && rho >= 0.90 && extremes_ok && max(abs(pr - orr)) <= 2
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
