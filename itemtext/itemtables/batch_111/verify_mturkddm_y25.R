# verify_mturkddm_y25.R
#
# Claim under test: the live item code "N A" is paste(column_7_value,
# column_8_value) of Experiment2.data (task_number == 2) -- N = number of dots,
# A = area flag (1 = summed dot area forced near the mean area of 25 dots,
# 2 = area unrestricted/proportional to numerosity), per the deposit's own
# Experiment2.description codebook -- and resp = 1 means a CORRECT response
# (response_key_ID == 1 for N > 25, == 2 for N < 25), resp = 0 incorrect.
#
# The falsifiable prediction: re-running data/mturk_ddm.R's Experiment-2 task-2
# block over the raw OSF file reproduces, item for item, the live n and the live
# mean accuracy. Any permutation of the 12 codes, or a flipped resp direction,
# breaks it immediately.
#
# Secondary, source-independent check: the paper's Table 5 publishes Pr("large")
# per numerosity, which converts to accuracy and must track the live per-N means.

suppressMessages(library(irw))

TABLE <- "mturkddm_y25"
RAW   <- "https://files.osf.io/v1/resources/za9y8/providers/osfstorage/5fbd7a3aab651800f2b0e5f6"
LOCAL <- ".cache/mturkddm_y25/Experiment2.data"

src <- if (file.exists(LOCAL)) LOCAL else
    tryCatch({
        p <- tempfile(fileext = ".data")
        u <- "https://files.osf.io/v1/resources/za9y8/providers/osfstorage/?meta="
        j <- paste(readLines(url(u), warn = FALSE), collapse = "")
        # crude extraction of the Experiment2.data download link
        m <- regmatches(j, gregexpr('"name": "Experiment2.data".*?"download": "[^"]+"', j))[[1]]
        dl <- sub('.*"download": "([^"]+)".*', "\\1", m)
        if (!length(dl) || !nzchar(dl)) dl <- RAW
        download.file(dl, p, quiet = TRUE); p
    }, error = function(e) NA_character_)

if (is.na(src)) {
    cat("Could not retrieve Experiment2.data from OSF; cannot re-run.\n")
    cat("VERDICT: FAIL\n"); quit(status = 0)
}

x <- read.csv(src, header = TRUE)
x$response_key_ID <- ifelse(x$response_key_ID == 0, NA, x$response_key_ID)
x2 <- x[x$task_number == 2, ]
z  <- ifelse(x2$column_7_value > 25, 1, 2)
x2$resp <- ifelse(x2$response_key_ID == z, 1, 0)
x2$item <- paste(x2$column_7_value, x2$column_8_value)

r   <- aggregate(resp ~ item, x2, function(v) c(n = length(v), m = mean(v)))
raw <- data.frame(item = r$item, n_raw = r$resp[, 1], mean_raw = r$resp[, 2])

d <- irw::irw_fetch(TABLE)
a <- aggregate(resp ~ item, d, function(v) c(n = length(v), m = mean(v)))
live <- data.frame(item = a$item, n_live = a$resp[, 1], mean_live = a$resp[, 2])

m <- merge(raw, live, by = "item")
m <- m[order(as.numeric(sub(" .*", "", m$item)), sub(".* ", "", m$item)), ]

cat(sprintf("%-6s %8s %8s %14s %14s %12s\n",
            "item", "n_raw", "n_live", "mean_raw", "mean_live", "diff"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-6s %8d %8d %14.10f %14.10f %12.2e\n",
                m$item[i], m$n_raw[i], m$n_live[i],
                m$mean_raw[i], m$mean_live[i], m$mean_raw[i] - m$mean_live[i]))

ok_n <- all(m$n_raw == m$n_live) && nrow(m) == 12
worst <- max(abs(m$mean_raw - m$mean_live))
cat(sprintf("\nitems reconciled: %d/12; n identical: %s; largest mean deviation: %.3e\n",
            nrow(m), ok_n, worst))

# Secondary: paper Table 5 (Ratcliff & Hendrickson 2021, Behav Res 53:2302-2325),
# Y25 panel, Pr("large") by numerosity, collapsed over the area variable.
PR_LARGE <- c("10" = 0.102, "15" = 0.157, "20" = 0.359,
              "30" = 0.850, "35" = 0.904, "40" = 0.917)
pub_acc <- ifelse(as.numeric(names(PR_LARGE)) > 25, PR_LARGE, 1 - PR_LARGE)
names(pub_acc) <- names(PR_LARGE)   # ifelse() drops names
Nd <- sub(" .*", "", as.character(d$item))
obs_acc <- tapply(as.numeric(d$resp), Nd, mean, na.rm = TRUE)[names(PR_LARGE)]
cat("\npaper Table 5 vs live, collapsed over the area flag:\n")
cat(sprintf("%-6s %12s %12s %8s\n", "Ndots", "paper_acc", "live_acc", "diff"))
for (i in seq_along(pub_acc))
    cat(sprintf("%-6s %12.3f %12.3f %8.3f\n",
                names(pub_acc)[i], pub_acc[i], obs_acc[i], obs_acc[i] - pub_acc[i]))
cat(sprintf("largest deviation: %.3f (paper reports 92 screened subjects, IRW pools all)\n",
            max(abs(obs_acc - pub_acc))))

cat("\nWhat this does NOT establish: nothing about item_text, which is blank by\n",
    "design (the stimuli are dot arrays with no wording). The area flag digit is\n",
    "pinned only by the exact re-run -- the paper itself reports the area variable\n",
    "had almost no effect, and the live 'N 1' vs 'N 2' means differ by <= 0.022, so\n",
    "no statistical route could separate the two area conditions.\n", sep = "")

cat(if (ok_n && worst < 1e-12) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
