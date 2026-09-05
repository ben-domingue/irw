# verify_enkavi_2019_navon.R -- Step 5b re-runnable mapping evidence.
#
# CLAIM UNDER TEST: each live item code `<condition>_<global_shape>_<local_shape>`
# denotes the Navon stimulus with that global letter made of that local letter, with
# `condition` naming the ATTENDED level, and correct_response = the attended letter.
#
# Route: deterministic re-run of the processing script's item construction over the
# study's own raw trial files (core model section 3), plus the raw file's own
# correct_response key. Two falsifiable predictions:
#   (a) per-item trial counts recomputed from the raw files reproduce the live
#       per-item n EXACTLY, item by item. The 12 counts are all distinct, so the
#       count vector identifies every item uniquely -- a permutation of any two
#       item codes breaks it.
#   (b) the raw file's own `correct_response` key code (72 = "H" key, 83 = "S" key;
#       expfactory local_global_letter/experiment.js: choices = [72, 83]) is
#       unanimous within each item and equals the key for the GLOBAL letter on
#       global_* items and the LOCAL letter on local_* items -- i.e. it confirms
#       which level `condition` names, which is what the shipped item_text asserts.
#
# Live data is read with irw_table_sets() (server-side aggregate, no export).

suppressMessages(library(irw))

TABLE <- "enkavi_2019_navon"
RAW <- c("https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data/Complete_02-16-2019/Individual_Measures/local_global_letter.csv.gz",
         "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data/Retest_02-16-2019/Individual_Measures/local_global_letter.csv.gz")

read_raw <- function(u) {
    tf <- tempfile(fileext = ".csv.gz")
    utils::download.file(u, tf, quiet = TRUE)
    d <- read.csv(gzfile(tf), stringsAsFactors = FALSE)
    unlink(tf)
    d
}

raw <- do.call(rbind, lapply(RAW, function(u)
    read_raw(u)[, c("worker_id","exp_stage","condition","global_shape","local_shape",
                    "correct","correct_response")]))

# Same cleaning as data/enkavi_2019_conflict_tasks.py::_clean
d <- raw[raw$exp_stage == "test", ]
d$resp <- suppressWarnings(as.numeric(d$correct))
d$resp[!d$resp %in% c(0, 1)] <- NA
d <- d[!is.na(d$resp) & !is.na(d$worker_id) & d$worker_id != "", ]
d$item <- paste(d$condition, d$global_shape, d$local_shape, sep = "_")

raw_n <- table(d$item)

live <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(live$per_item)
live_n <- setNames(as.numeric(pi$n), pi$item)

items <- sort(union(names(raw_n), names(live_n)))

# (b) predicted key from the shipped reading of the code
attended <- ifelse(startsWith(items, "global_"),
                   toupper(sub("^[a-z]+_([a-z])_([a-z])$", "\\1", items)),
                   toupper(sub("^[a-z]+_([a-z])_([a-z])$", "\\2", items)))
pred_key <- ifelse(attended == "H", 72, 83)

cat(sprintf("%-12s %8s %8s %6s   %9s %9s %6s\n",
            "item", "raw n", "live n", "diff", "pred key", "raw key", "pure"))
ok_n <- TRUE; ok_k <- TRUE
for (i in seq_along(items)) {
    it <- items[i]
    rn <- if (!is.na(raw_n[it])) as.numeric(raw_n[it]) else NA
    ln <- if (it %in% names(live_n)) live_n[[it]] else NA
    kt <- table(d$correct_response[d$item == it])
    rk <- as.numeric(names(kt)[which.max(kt)])
    pure <- max(kt) / sum(kt)
    cat(sprintf("%-12s %8s %8s %6s   %9d %9d %5.1f%%\n",
                it, rn, ln, rn - ln, pred_key[i], rk, 100 * pure))
    if (is.na(rn) || is.na(ln) || rn != ln) ok_n <- FALSE
    if (rk != pred_key[i] || pure < 1) ok_k <- FALSE
}

cat(sprintf("\ndistinct live per-item n: %d of %d -- %s\n",
            length(unique(live_n)), length(live_n),
            if (length(unique(live_n)) == length(live_n))
                "count vector identifies every item uniquely" else
                "NOT unique; counts alone cannot separate the tied items"))
cat("item counts reproduce exactly: ", ok_n, "\n", sep = "")
cat("correct_response key matches the attended-level reading, unanimously: ", ok_k, "\n", sep = "")

cat("\nNote: this establishes the item<->stimulus mapping and which level `condition`\n",
    "names. It does NOT establish the wording of `instructions` (transcribed from\n",
    "expfactory-experiments/local_global_letter/experiment.js, not testable here), nor\n",
    "the option_text labels for resp 0/1, which are accuracy codes, not options anyone read.\n", sep = "")

cat(if (ok_n && ok_k) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
