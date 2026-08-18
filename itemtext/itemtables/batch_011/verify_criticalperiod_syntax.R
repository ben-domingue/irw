# verify_criticalperiod_syntax.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item code `q<i>_<j>` is question i, option j of the "Which English?"
# quiz, where j indexes the options in the order Hartshorne, Tenenbaum & Pinker
# (2018) print them in their Supplementary Information "Materials" section
# (a=1, b=2, ... h=8). The shipped item_text is that option's sentence.
#
# WHY THIS IS FALSIFIABLE ----------------------------------------------------
# The same SI's "Scoring" section gives, for each of the 95 critical items,
# whether the keyed answer is Correct or Incorrect (Top/Bottom for the six
# picture items). The live IRW `resp` is scored accuracy (0/1) against exactly
# that key. So the SI's raw per-option endorsement data (OSF pyb8s
# `compiled.csv`, 680,333 respondents, one 0/1 column per option) lets us
# recompute each item's accuracy under OUR letter->index mapping and compare it
# with the live per-item mean. If the mapping assigned the wrong option, the
# keyed class flips and the recomputed accuracy lands near 1-p instead of p.
#
# NOTE ON SAMPLES: the live table pools 1,131,401 respondents (Chen &
# Hartshorne 2021) while compiled.csv holds HTP 2018's 680,333, so a small
# positive offset is expected throughout; order and class, not the third
# decimal, are the signal.
#
# WHAT IT DOES NOT ESTABLISH: within a question, two options that share the
# same keyed class and whose accuracies differ by less than the between-sample
# offset are not separated by their own numbers. See the printout.

suppressMessages(library(data.table))

TABLE   <- "criticalperiod_syntax"
CACHE   <- file.path(".cache", TABLE)
RAWFILE <- file.path(CACHE, "compiled.csv")
RAWURL  <- "https://osf.io/download/gw8fx/"   # OSF pyb8s -> compiled.csv (351 MB)

dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)
if (!file.exists(RAWFILE) || file.size(RAWFILE) < 351000000) {
    cat("downloading", RAWURL, "(351 MB, cached afterwards) ...\n")
    utils::download.file(RAWURL, RAWFILE, mode = "wb", quiet = TRUE)
}

## --- answer key, transcribed from HTP 2018 SI "Scoring" (pp. 58-60) ---------
KEY <- c(
"1. Bottom","2. Bottom","3. Top","5. Bottom","6. Bottom","7. Top",
"9a. Incorrect","9d. Incorrect","10b. Incorrect","10c. Incorrect",
"11c. Incorrect","11d. Incorrect","12a. Incorrect","12b. Incorrect","12d. Correct",
"13c. Incorrect","13d. Incorrect","14c. Incorrect","14d. Incorrect",
"15a. Incorrect","15b. Incorrect","15c. Correct","16c. Incorrect","16d. Incorrect",
"17a. Incorrect","17c. Incorrect","17d. Correct","18b. Incorrect","18c. Correct",
"18d. Incorrect","19a. Correct","19b. Incorrect","19c. Incorrect","19d. Incorrect",
"20a. Incorrect","20b. Incorrect","20c. Incorrect","20d. Correct",
"21a. Incorrect","21b. Correct","21c. Incorrect","21d. Incorrect",
"22a. Correct","22b. Incorrect","22c. Incorrect","22d. Incorrect",
"23c. Incorrect","23d. Incorrect","24a. Incorrect","24b. Incorrect","24c. Incorrect",
"24d. Correct","25a. Incorrect","25b. Incorrect","25c. Incorrect","25d. Correct",
"26a. Correct","26b. Incorrect","26c. Incorrect","26d. Incorrect",
"27a. Incorrect","27b. Correct","27c. Incorrect","27d. Incorrect",
"28a. Incorrect","28b. Incorrect","29a. Incorrect","29b. Incorrect","29c. Correct",
"29d. Incorrect","30a. Incorrect","30b. Correct","30c. Incorrect","30d. Incorrect",
"31a. Incorrect","31d. Incorrect","32e. Correct","32f. Incorrect","32h. Correct",
"33d. Correct","33e. Incorrect","33f. Correct","33g. Incorrect",
"34a. Correct","34b. Incorrect","34c. Incorrect","34d. Incorrect","34f. Correct",
"34h. Incorrect","35a. Incorrect","35b. Incorrect","35d. Correct","35e. Incorrect",
"35g. Incorrect","35h. Incorrect")

key <- data.table(raw = KEY)
key[, qn  := sub("^([0-9]+)([a-h]?)\\..*$", "\\1", raw)]
key[, let := sub("^([0-9]+)([a-h]?)\\..*$", "\\2", raw)]
key[, ans := sub("^[0-9]+[a-h]?\\. ", "", raw)]
key[, idx := match(let, letters)]
## Question 10 is printed a, b, c, c -- its FOURTH option carries a duplicated
## "c." label, so the key's "10c" is option 4 ("What old are you?"). Note that
## "How old are you?" (option 3) is grammatical in every dialect and so cannot
## be the entry keyed Incorrect.
key[qn == "10" & let == "c", idx := 4L]
key[, item := ifelse(let == "", paste0("q", qn), paste0("q", qn, "_", idx))]
stopifnot(nrow(key) == 95, !anyDuplicated(key$item))

## --- live per-item means ----------------------------------------------------
## irw::irw_fetch() on this table pulls 107,483,095 rows, so the live side is
## taken as a Redivis aggregate; the hard-coded fallback is that same query's
## output (2026-08-18) so the script still runs offline.
LIVE_FALLBACK <- c(
q1=0.964154176989414, q10_2=0.996484005228916, q10_4=0.997523424497591,
q11_3=0.953137746917318, q11_4=0.726734376229118, q12_1=0.927348482103162,
q12_2=0.981522908323397, q12_4=0.899589977382024, q13_3=0.803458720648117,
q13_4=0.992994526255502, q14_3=0.981534398502387, q14_4=0.98359025668176,
q15_1=0.980409244821244, q15_2=0.993960585150623, q15_3=0.967164603884918,
q16_3=0.991562673181304, q16_4=0.987794778332351, q17_1=0.984467929584648,
q17_3=0.977402353365429, q17_4=0.974161239030194, q18_2=0.974853301349389,
q18_3=0.781629148286063, q18_4=0.963335722701324, q19_1=0.822720679935761,
q19_2=0.899178982518135, q19_3=0.841097895441139, q19_4=0.988271178830495,
q2=0.748977595034829, q20_1=0.92661576222754, q20_2=0.955040697330125,
q20_3=0.923519600919568, q20_4=0.956109283976238, q21_1=0.994633202551527,
q21_2=0.985228049117864, q21_3=0.97884304503885, q21_4=0.988844803920096,
q22_1=0.907234481850378, q22_2=0.833989010085726, q22_3=0.830532233929438,
q22_4=0.965749544149245, q23_3=0.949498011757104, q23_4=0.899338961164079,
q24_1=0.867368863912971, q24_2=0.967718784056227, q24_3=0.879102104382089,
q24_4=0.832287579735213, q25_1=0.980530333630605, q25_2=0.747110882878838,
q25_3=0.99681014954026, q25_4=0.875734598077958, q26_1=0.975320863248309,
q26_2=0.972458924819759, q26_3=0.997723176840041, q26_4=0.968742293846302,
q27_1=0.985507348853324, q27_2=0.921037722257626, q27_3=0.954064915975857,
q27_4=0.876454060054746, q28_1=0.985510000433091, q28_2=0.968435594453249,
q29_1=0.820829219701945, q29_2=0.87464921809332, q29_3=0.843454265994109,
q29_4=0.976589202236872, q3=0.879565246981398, q30_1=0.836540713681533,
q30_2=0.902848768915708, q30_3=0.938723759303731, q30_4=0.96540837421922,
q31_1=0.902543837242498, q31_4=0.989648232589507, q32_5=0.868634551321768,
q32_6=0.978630034797565, q32_8=0.921918930600203, q33_4=0.865130046729674,
q33_5=0.778768093717436, q33_6=0.910705399765424, q33_7=0.859087096440607,
q34_1=0.741737898410908, q34_2=0.9083587516716, q34_3=0.882253948865168,
q34_4=0.728539218190545, q34_6=0.785973319804384, q34_8=0.959226657922346,
q35_1=0.866148253360215, q35_2=0.901343555467956, q35_4=0.876449640755135,
q35_5=0.935070766244682, q35_7=0.978715769210032, q35_8=0.788296103680304,
q5=0.900831800572917, q6=0.975755722330101, q7=0.95560459996058,
q9_1=0.96491429652263, q9_4=0.897507603404982)

live <- tryCatch({
    suppressMessages(library(redivis))
    q <- redivis$query(paste(
        "SELECT item, AVG(resp) AS mean_resp FROM",
        "`datapages.item_response_warehouse:as2e.criticalperiod_syntax`",
        "GROUP BY item"))
    r <- as.data.frame(q$to_data_frame())
    setNames(as.numeric(r$mean_resp), r$item)
}, error = function(e) {
    cat("(redivis unavailable:", conditionMessage(e), "-- using cached live means)\n")
    LIVE_FALLBACK
})
stopifnot(setequal(names(live), key$item))

## --- recompute accuracy from the raw per-option endorsements ----------------
natdial <- c("Australia","Canada","Ebonics","England","New Zealand","Ireland",
             "Northern Ireland","Scotland","Singapore","South Africa",
             "United States","Wales","India")
cmp <- fread(RAWFILE, select = c("type", key$item))
cat("raw respondents:", nrow(cmp), "\n\n")

res <- rbindlist(lapply(seq_len(nrow(key)), function(i) {
    it <- key$item[i]; a <- key$ans[i]
    v   <- suppressWarnings(as.numeric(cmp[[it]]))
    nat <- v[cmp$type %in% natdial]
    ## for the six picture items the SI key is Top/Bottom and the raw 0/1
    ## coding is undocumented, so the keyed value is the modal native response
    target <- if (a %in% c("Correct", "Incorrect")) as.integer(a == "Correct")
              else as.integer(mean(nat, na.rm = TRUE) > 0.5)
    data.table(item = it, keyed = a,
               acc = mean(v == target, na.rm = TRUE),
               live = live[[it]])
}))
res[, diff := acc - live]
res[, flip := abs((1 - acc) - live)]   # what the wrong-class reading would cost

cat(sprintf("%-7s %-10s %8s %8s %8s %10s\n",
            "item", "SI key", "recomp", "live", "diff", "if flipped"))
for (i in order(-abs(res$diff)))
    cat(sprintf("%-7s %-10s %8.4f %8.4f %8.4f %10.4f\n", res$item[i], res$keyed[i],
                res$acc[i], res$live[i], res$diff[i], res$flip[i]))

cat(sprintf("\n95 items | cor(recomputed, live) = %.4f | mean|diff| = %.4f | max|diff| = %.4f\n",
            cor(res$acc, res$live), mean(abs(res$diff)), max(abs(res$diff))))
cat(sprintf("smallest cost of reading any single item's key the other way: %.4f\n",
            min(res$flip)))

set.seed(1)
nullcor <- replicate(2000, cor(res$acc, sample(res$live)))
cat(sprintf("permutation null for cor: mean %.3f, max of 2000 draws %.3f\n",
            mean(nullcor), max(nullcor)))

## --- within-question ordering (immune to the between-sample offset) ---------
res[, qn := sub("_.*$", "", item)]
pairs <- rbindlist(lapply(split(res, res$qn), function(g) {
    if (nrow(g) < 2) return(NULL)
    cb <- t(utils::combn(nrow(g), 2))
    data.table(a = g$item[cb[, 1]], b = g$item[cb[, 2]],
               d_acc = g$acc[cb[, 1]] - g$acc[cb[, 2]],
               d_live = g$live[cb[, 1]] - g$live[cb[, 2]],
               same_class = g$keyed[cb[, 1]] == g$keyed[cb[, 2]])
}))
pairs[, ok := sign(d_acc) == sign(d_live)]
cat(sprintf("\nwithin-question option pairs concordant in order: %d / %d\n",
            sum(pairs$ok), nrow(pairs)))
cat("discordant pairs (all near-ties):\n")
print(pairs[ok == FALSE, .(a, b, d_acc = round(d_acc, 4),
                           d_live = round(d_live, 4), same_class)])
unres <- pairs[ok == FALSE & same_class == TRUE]
cat(sprintf("\nof those, %d pair(s) also share the keyed class, so their own numbers\n",
            nrow(unres)),
    "do NOT separate them: ",
    paste(unres$a, unres$b, sep = "/", collapse = ", "), "\n",
    "Those rest on the single global letter->index convention, which the other\n",
    "113 orderings and all 95 class assignments validate -- not on item-specific\n",
    "evidence. That is why this table is recorded PARTIAL, not VERIFIED.\n", sep = "")

pass <- max(abs(res$diff)) < 0.15 &&
        min(res$flip) > 0.40 &&   # observed worst-case 0.486, vs max|diff| 0.079
        cor(res$acc, res$live) > 0.9 &&
        sum(pairs$ok) >= 110
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
