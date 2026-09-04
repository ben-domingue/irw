# verify_cogcontrol_gyurkovics_2019_flanker.R
#
# CLAIM UNDER TEST. Each IRW item code `targ_NN` (NN = 19..34) is one flanker
# stimulus display, and the shipped `item_text` names which arrow display it is
# (e.g. targ_34 = "<-<- -> <-<-"). The IRW code is the raw file's own `targ`
# value ('targ_' + df['targ'] in data/cogcontrol_gyurkovics.py), so nothing can
# go wrong between the raw file and the live table; what CAN go wrong -- and what
# this script tests -- is the decode of `targ` into a stimulus, which the OSF
# readme does not publish ("targ = the identifier of the specific target image").
#
# HOW THE DECODE IS FALSIFIABLE. The raw file carries TWO independent signals per
# trial, and they must agree for every one of the 118 participants:
#   (a) `resp` on correct trials = the key the participant pressed. The paper
#       (Gyurkovics, Stafford & Levita 2020, Method) states the mapping: keys
#       2/4/6/8 on the numeric keypad = down/left/right/up. Psychtoolbox codes
#       those keys 98/100/102/104. -> the TARGET arrow's direction.
#   (b) `code` is a 3-letter feature-repetition string (AAA/ABA/... ) whose
#       letters are that participant's own random assignment of the four
#       directions. Congruent trials (cong==0) have codes XXX, which reveals
#       letter X's direction via (a). Reading those letters back onto the
#       incongruent codes gives flanker-target-flanker directly.
# (a) and (b) are derived from different columns; a wrong decode would show up as
# a disagreement, or as one targ resolving to two different stimuli across
# participants. Both counts must be zero.
#
# Runs offline if osf/flanker_merge.csv is cached beside this script's data dir;
# otherwise downloads it from OSF (2.2 MB), NOT from Redivis -- no export.

ITEMS <- "cogcontrol_gyurkovics_2019_flanker__items.csv"
here  <- dirname(normalizePath(sub("^--file=", "",
          grep("^--file=", commandArgs(FALSE), value = TRUE)[1])))
items <- read.csv(file.path(here, ITEMS), stringsAsFactors = FALSE,
                  encoding = "UTF-8")

src <- file.path(here, "flanker_merge.csv")
if (!file.exists(src)) {
    alt <- "../../.cache/cogcontrol_gyurkovics_2019_flanker/osf/flanker_merge.csv"
    src <- if (file.exists(file.path(here, alt))) file.path(here, alt) else {
        tmp <- tempfile(fileext = ".csv")
        download.file("https://osf.io/download/5ced5c7523fec4001ae6c6a4/",
                      tmp, quiet = TRUE)
        tmp
    }
}
d <- read.csv(src, strip.white = TRUE, stringsAsFactors = FALSE)
names(d) <- trimws(names(d))
d$code <- trimws(d$code)
cat(sprintf("raw trials: %d   participants: %d   distinct targ: %d\n",
            nrow(d), length(unique(d$subid)), length(unique(d$targ))))

KEY <- c("98" = "down", "100" = "left", "102" = "right", "104" = "up")
GLY <- c(up = "↑", down = "↓", left = "←", right = "→")

assign_tbl <- list()          # targ -> set of "target|flanker" strings seen
disagree <- 0L; nsub <- 0L
for (s in sort(unique(d$subid))) {
    x <- d[d$subid == s, ]
    nsub <- nsub + 1L
    letters_map <- c()
    for (t in sort(unique(x$targ[x$cong == 0]))) {
        g <- x[x$targ == t & x$cong == 0, ]
        cd <- unique(g$code); if (length(cd) != 1) stop("multi-code congruent targ")
        dir <- names(sort(table(KEY[as.character(g$resp[g$Acc == 1])]),
                          decreasing = TRUE))[1]
        letters_map[substr(cd, 1, 1)] <- dir
        k <- as.character(t)
        assign_tbl[[k]] <- union(assign_tbl[[k]], paste(dir, dir, sep = "|"))
    }
    for (t in sort(unique(x$targ[x$cong == 1]))) {
        g <- x[x$targ == t & x$cong == 1, ]
        cd <- unique(g$code); if (length(cd) != 1) stop("multi-code incongruent targ")
        tgt_letter <- substr(cd, 2, 2); fl_letter <- substr(cd, 1, 1)
        tgt_code <- letters_map[[tgt_letter]]
        tgt_key  <- names(sort(table(KEY[as.character(g$resp[g$Acc == 1])]),
                               decreasing = TRUE))[1]
        if (!identical(tgt_code, tgt_key)) disagree <- disagree + 1L
        k <- as.character(t)
        assign_tbl[[k]] <- union(assign_tbl[[k]],
                                 paste(tgt_code, letters_map[[fl_letter]], sep = "|"))
    }
}
multi <- sum(vapply(assign_tbl, length, 1L) > 1L)
cat(sprintf("participants decoded: %d\n", nsub))
cat(sprintf("signal (a) vs (b) disagreements on the target direction: %d (must be 0)\n",
            disagree))
cat(sprintf("targ codes resolving to more than one stimulus: %d of %d (must be 0)\n",
            multi, length(assign_tbl)))

cat(sprintf("\n%-9s %-14s %-14s %-9s %-9s %s\n",
            "item", "derived targ", "derived flank", "derived", "shipped", "ok"))
ok <- TRUE
for (t in sort(as.integer(names(assign_tbl)))) {
    parts <- strsplit(assign_tbl[[as.character(t)]][1], "|", fixed = TRUE)[[1]]
    txt <- paste0(strrep(GLY[[parts[2]]], 2), GLY[[parts[1]]],
                  strrep(GLY[[parts[2]]], 2))
    shipped <- unique(items$item_text[items$item == paste0("targ_", t)])
    hit <- length(shipped) == 1 && identical(shipped, txt)
    ok <- ok && hit
    cat(sprintf("%-9s %-14s %-14s %-9s %-9s %s\n", paste0("targ_", t),
                parts[1], parts[2], txt, shipped, if (hit) "yes" else "NO"))
}

# The shipped correct_response is the keypad key for the derived target
# direction (paper: 2/4/6/8 = down/left/right/up). Check it against the raw
# file's own modal correct key, independently of the text comparison above.
KEYNUM <- c(down = "2", left = "4", right = "6", up = "8")
key_ok <- TRUE
for (t in sort(as.integer(names(assign_tbl)))) {
    parts <- strsplit(assign_tbl[[as.character(t)]][1], "|", fixed = TRUE)[[1]]
    shipped <- unique(items$correct_response[items$item == paste0("targ_", t)])
    key_ok <- key_ok && identical(as.character(shipped), unname(KEYNUM[parts[1]]))
}
cat(sprintf("\ncorrect_response matches derived target direction for all %d items: %s\n",
            length(assign_tbl), key_ok))

# Semantic sanity: displays the decode calls congruent must be easier than the
# ones it calls incongruent. This is a consequence of the mapping, not of the
# plumbing -- a permuted decode would blur it.
cong_items <- vapply(sort(as.integer(names(assign_tbl))), function(t) {
    p <- strsplit(assign_tbl[[as.character(t)]][1], "|", fixed = TRUE)[[1]]
    p[1] == p[2] }, TRUE)
ctargs <- sort(as.integer(names(assign_tbl)))[cong_items]
acc_c <- mean(d$Acc[d$targ %in% ctargs]); acc_i <- mean(d$Acc[!d$targ %in% ctargs])
rt_c <- mean(d$RT[d$targ %in% ctargs & d$Acc == 1 & d$RT > 0])
rt_i <- mean(d$RT[!d$targ %in% ctargs & d$Acc == 1 & d$RT > 0])
cat(sprintf("displays decoded as all-same-direction: acc %.4f, RT %.1f ms\n", acc_c, rt_c))
cat(sprintf("displays decoded as odd-one-out       : acc %.4f, RT %.1f ms\n", acc_i, rt_i))
cat(sprintf("flanker effect: %+.1f ms, %+.4f accuracy (expected: slower & less accurate)\n",
            rt_i - rt_c, acc_i - acc_c))
sane <- rt_i > rt_c && acc_i < acc_c

cat("\nWhat this does NOT establish: the arrow GLYPHS are a rendering of stimulus\n",
    "images the deposit does not ship, so the exact arrowhead/length drawn on screen\n",
    "is unverifiable; only the DIRECTIONS are. Instructions text is not published\n",
    "anywhere and is shipped blank.\n", sep = "")

cat(if (ok && key_ok && disagree == 0L && multi == 0L && sane)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
