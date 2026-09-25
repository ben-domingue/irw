# verify_znidarsic_2021_org_practices.R -- Step 5b, batch_408.
#
# Claim: item codes OP01..OP25 are POSITIONAL (data/znidarsic_2021_work_family_balance.py,
# df.iloc[:, 27:52] of PLOS S1 Data 10.1371/journal.pone.0245078.s001, sha256 fd8b260d...),
# and item_text is the trimmed column header at that position.
#
# Route (Step 5b route 9 applied to columns / script re-run): the 1..5 response counts of
# every Likert column of S1 Data (0-based cols 9..64: leader, co-worker, practices, WFB,
# UWES blocks) are hard-coded below, computed from the xlsx with the script's own 1..5
# filter (which drops the 55 in col 30 and the 22 in col 38). Each live item's count vector
# must match EXACTLY ONE source column, that column must be the one the script's position
# assigns, and its header must equal the shipped item_text.

suppressMessages(library(irw))
TABLE <- "znidarsic_2021_org_practices"
here <- tryCatch(dirname(normalizePath(sys.frame(1)$ofile)), error = function(e) "itemtables/batch_408")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
if (!file.exists(items_csv)) items_csv <- file.path("itemtables/batch_408", paste0(TABLE, "__items.csv"))

src <- list(   # xlsx 0-based col -> list(header (trimmed), counts at resp 1..5)
  `9` = list("Switched schedules ( hours, overtime hours, vacation ) to accommodate my family responsibilities", c(13,24,63,89,58)),
  `10` = list("Listened to my problems.", c(16,30,76,72,53)),
  `11` = list("Takes into account my efforts to combine work and family", c(10,32,88,63,54)),
  `12` = list("Juggled tasks or duties to accommodate my family responsibilities.", c(17,43,71,71,45)),
  `13` = list("Shared ideas or advice.", c(23,46,63,74,41)),
  `14` = list("Did not held my family responsibilities against me.", c(63,25,46,50,62)),
  `15` = list("Helped me to figure out how to solve a problem.", c(17,35,54,70,71)),
  `16` = list("Was understanding.", c(6,17,68,82,74)),
  `17` = list("Did not showed resentment of my needs as a working parent.", c(31,22,71,55,68)),
  `18` = list("Helped me to switch schedules ( hours, overtime hours, vacation ) to accommodate my family responsibilities", c(11,18,83,89,46)),
  `19` = list("Listened to my problems.", c(9,19,69,97,53)),
  `20` = list("Takes into account my efforts to combine work and family", c(8,25,77,89,48)),
  `21` = list("Juggled tasks or duties to accommodate my family responsibilities.", c(13,37,78,87,32)),
  `22` = list("Shared ideas or advice.", c(13,29,59,90,56)),
  `23` = list("Did not held my family responsibilities against me.", c(56,32,45,62,52)),
  `24` = list("Helped me to figure out how to solve a problem.", c(11,29,63,90,54)),
  `25` = list("Was understanding.", c(7,13,54,100,73)),
  `26` = list("Did not showed resentment of my needs as a working parent.", c(38,34,48,62,65)),
  `27` = list("Flexible working hours.", c(64,35,40,52,56)),
  `28` = list("Flexible arrival / departure time.", c(62,35,36,59,55)),
  `29` = list("Possibility of shortened working time (eg half-time).", c(50,34,51,58,54)),
  `30` = list("Independence in the organization of replacements and on-call time.", c(31,45,52,61,57)),
  `31` = list("Independence in the planning of annual leave.", c(30,32,46,69,70)),
  `32` = list("Flexible working breaks (eg lunch time).", c(22,29,48,66,82)),
  `33` = list("Children's bonus time (extra hours or extra leave for parents on the first day of the school, kindergarten introduction).", c(49,32,50,53,63)),
  `34` = list("Possibility of working at a distance / from home.", c(133,23,40,26,24)),
  `35` = list("Good communication with employees.", c(21,35,65,68,57)),
  `36` = list("Research among employees regarding work-family balance.", c(65,45,80,35,22)),
  `37` = list("A team for the work-family coordination, or an authorized person for issues related to work-family balance.", c(74,42,83,30,18)),
  `38` = list("Informal socializing among employees.", c(30,40,70,60,46)),
  `39` = list("Leadership supporting work-life balance measures and policies.", c(41,45,85,51,25)),
  `40` = list("Leader is educated in the field of work-family balance.", c(72,42,70,43,20)),
  `41` = list("Leadership support and promote the work.family balance.", c(47,40,88,42,30)),
  `42` = list("Help to reintegrate into work after a long absence (for example, holiday leave).", c(36,39,74,59,39)),
  `43` = list("Individual career development plans.", c(47,43,72,56,29)),
  `44` = list("Annual interviews that include the topic of work-family balance.", c(57,49,77,41,23)),
  `45` = list("Giving gifts to newborns or children at Christmas / New Year.", c(37,27,61,48,74)),
  `46` = list("Leisure offer (the company organizes activities that can be used by employees or their family members).", c(51,32,68,41,55)),
  `47` = list("Scholarships for employees' children.", c(107,33,52,30,25)),
  `48` = list("Psychological counseling and help.", c(95,39,59,29,25)),
  `49` = list("Various forms of daily care (for the children of their employees).", c(139,29,41,21,17)),
  `50` = list("Organized holiday care for the children of their employees.", c(137,26,47,22,15)),
  `51` = list("Possibility to bring children to a special situation for a short time to work.", c(117,36,33,35,26)),
  `52` = list("The current relationship between the time I spend on the job and the time I have for my non-formal activities seems good to me.", c(38,49,57,72,31)),
  `53` = list("I have problems with balancing work and non- work activities.", c(35,37,70,60,45)),
  `54` = list("I think that the balance between my work requirements and non-work activities is just right.", c(37,51,64,67,28)),
  `55` = list("Generally speaking, I think my work and private life is balanced..", c(33,41,59,77,37)),
  `56` = list("At my work, I feel bursting with energy", c(9,17,73,103,45)),
  `57` = list("At my job, I feel strong and vigorous", c(3,8,66,98,72)),
  `58` = list("When I get up in the morning, I feel like going to work", c(31,42,80,73,21)),
  `59` = list("I am enthusiastic about my job", c(17,22,101,81,26)),
  `60` = list("I am proud on the work that I do", c(13,16,83,83,52)),
  `61` = list("My job inspires me", c(19,33,95,64,36)),
  `62` = list("I am immersed in my work", c(16,34,83,81,33)),
  `63` = list("I get carried away when I’m working", c(25,31,100,72,19)),
  `64` = list("I feel happy when I am working intensely", c(21,21,63,82,60))
)
expected_col <- setNames(as.character(27:51), sprintf("OP%02d", 1:25))

d <- irw::irw_fetch(TABLE)
it <- read.csv(items_csv, stringsAsFactors = FALSE)
txt <- tapply(it$item_text, it$item, `[`, 1)

ok <- TRUE
cat(sprintf("%-5s %-22s %-10s %-8s %s\n", "item", "live counts 1..5", "matches", "expect", "text==header"))
for (i in names(expected_col)) {
  live <- tabulate(d$resp[d$item == i], 5)
  hits <- names(src)[vapply(src, function(s) identical(as.numeric(s[[2]]), as.numeric(live)), TRUE)]
  tmatch <- identical(txt[[i]], src[[expected_col[[i]]]][[1]])
  good <- length(hits) == 1 && hits == expected_col[[i]] && tmatch
  ok <- ok && good
  cat(sprintf("%-5s %-22s %-10s %-8s %s\n", i, paste(live, collapse = "/"),
              if (length(hits)) paste(hits, collapse = ",") else "none", expected_col[[i]], tmatch))
}
vecs <- vapply(names(expected_col), function(i) paste(tabulate(d$resp[d$item == i], 5), collapse = "/"), "")
cat(sprintf("\ndistinct live count vectors: %d of %d\n", length(unique(vecs)), length(vecs)))
ok <- ok && length(unique(vecs)) == length(vecs)
cat("Each live item's 5-cell count vector matches exactly one of the 56 Likert source columns,\n",
    "and it is the practices column at the script's position; all 25 vectors are distinct, so\n",
    "every item is distinguished from every other.\n",
    "Not established here: the response ANCHORS (1 = completely disagree, 5 = strongly agree)\n",
    "come from the paper's Methods 2.1, not from this check.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
