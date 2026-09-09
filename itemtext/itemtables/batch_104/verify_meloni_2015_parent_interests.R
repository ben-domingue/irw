# Step 5b route 8 (semantic coherence of the response distribution) for
# meloni_2015_parent_interests.
#
# THE CLAIM UNDER TEST. The 25 IRW item codes are the S1 workbook's own column
# names (CHIA<n>_<SET>), so the conceptual SET of each item -- music, religious,
# sport, cultural, social -- is given by the code and is not inferred. Two things
# ARE inferred and are what this script tests:
#   (a) the position <n> WITHIN each set. The S2 File codebook lists the 25
#       statements as one flat roman-numbered list (i)..(xxv) tied to no variable
#       code; the mapping assumes that list runs in code order. It falls into
#       blocks of 3 music / 5 religious / 5 sport / 4 cultural / 8 social, which
#       matches the per-set code counts exactly, so only within-block order is open.
#   (b) the DIRECTION of the response scale. The codebook says only "Scale:
#       Important/Not Important from 1 to 5" and labels no individual point; the
#       shipped option_text puts "Not Important" at 1 and "Important" at 5.
#
# Both are falsifiable, because these are 25 activities Italian parents of 6-11
# year olds would obviously not rate equally. Every prediction below was fixed
# from item CONTENT before looking at the data.
#
# What this does NOT establish: several within-block neighbours have means within
# ~0.05 of each other and no distributional route can separate them (printed at
# the end). Status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "meloni_2015_parent_interests"
d <- irw::irw_fetch(TABLE)
m <- tapply(d$resp, d$item, mean)

TEXT <- c(
  CHIA1_MUSIC    = "learn to sing or play an instrument",
  CHIA2_MUSIC    = "go to a concert",
  CHIA3_MUSIC    = "listen to music",
  CHIA1_RELIG    = "know Jesus or other religious figures",
  CHIA2_RELIG    = "go to church or other places of worship",
  CHIA3_RELIG    = "go to catechism or other places of religious education",
  CHIA4_RELIG    = "pray or meditate",
  CHIA5_RELIG    = "read the Bible or other holy books or stories of saints",
  CHIA1_SPORT    = "usually practice sport, dance, or other physical activities",
  CHIA2_SPORT    = "go to a sporting event",
  CHIA3_SPORT    = "play a competitive sport or participate in a dance exhibition",
  CHIA4_SPORT    = "watch a sport on television or listen to radio programs",
  CHIA5_SPORT    = "attend physical education at school",
  CHIA1_CULTURAL = "go to a museum or attend conferences",
  CHIA2_CULTURAL = "read the newspaper",
  CHIA3_CULTURAL = "read books",
  CHIA4_CULTURAL = "watch cultural and scientific television programs",
  CHIA1_SOCIAL   = "participate in voluntary groups",
  CHIA2_SOCIAL   = "help classmates with their homework",
  CHIA3_SOCIAL   = "join classmates to study or for extra-curricular activities",
  CHIA4_SOCIAL   = "give money to charities",
  CHIA5_SOCIAL   = "give money to a telethon or other social aids",
  CHIA6_SOCIAL   = "give seat up for an elderly person on a bus",
  CHIA7_SOCIAL   = "gather used clothes",
  CHIA8_SOCIAL   = "have a good conduct mark")

cat(sprintf("%-15s %-58s %6s %7s %7s\n", "item", "item_text (shipped)", "mean", "%at1", "%at5"))
for (i in names(TEXT)) {
  x <- d$resp[d$item == i]
  cat(sprintf("%-15s %-58s %6.2f %7.1f %7.1f\n", i, TEXT[[i]], mean(x),
              100 * mean(x == 1), 100 * mean(x == 5)))
}
cat("\n")

blocks <- list(MUSIC = paste0("CHIA", 1:3, "_MUSIC"),
               RELIG = paste0("CHIA", 1:5, "_RELIG"),
               SPORT = paste0("CHIA", 1:5, "_SPORT"),
               CULTURAL = paste0("CHIA", 1:4, "_CULTURAL"),
               SOCIAL = paste0("CHIA", 1:8, "_SOCIAL"))
hi <- function(b) names(which.max(m[blocks[[b]]]))
lo <- function(b) names(which.min(m[blocks[[b]]]))

checks <- list(
  list("MUSIC: 'listen to music' most encouraged, 'go to a concert' least",
       hi("MUSIC") == "CHIA3_MUSIC" && lo("MUSIC") == "CHIA2_MUSIC"),
  list("RELIG: 'know Jesus or other religious figures' most, 'read the Bible...' least",
       hi("RELIG") == "CHIA1_RELIG" && lo("RELIG") == "CHIA5_RELIG"),
  list("SPORT: 'usually practice sport...' most, 'watch a sport on television...' least",
       hi("SPORT") == "CHIA1_SPORT" && lo("SPORT") == "CHIA4_SPORT"),
  list("CULTURAL: 'read books' is the most encouraged of the four cultural items",
       hi("CULTURAL") == "CHIA3_CULTURAL"),
  list("SOCIAL: 'give seat up for an elderly person on a bus' most encouraged",
       hi("SOCIAL") == "CHIA6_SOCIAL"),
  list("SOCIAL: 'give money to charities' least encouraged (a child has no money)",
       lo("SOCIAL") == "CHIA4_SOCIAL"),
  list("whole table: 'read books' is the maximum of all 25 items",
       names(which.max(m)) == "CHIA3_CULTURAL"),
  list("whole table: 'watch a sport on television...' is the minimum of all 25 items",
       names(which.min(m)) == "CHIA4_SPORT"),
  list("'attend physical education at school' > 'go to a sporting event' (school duty vs outing)",
       m[["CHIA5_SPORT"]] > m[["CHIA2_SPORT"]]))

ok <- TRUE
for (c_ in checks) { cat(sprintf("%-4s %s\n", if (c_[[2]]) "OK" else "FAIL", c_[[1]])); ok <- ok && c_[[2]] }

cat(sprintf("\n%d/%d content predictions hold.\n",
            sum(vapply(checks, function(x) x[[2]], TRUE)), length(checks)))

# SCALE DIRECTION. option_text ships "Not Important" at resp 1 and "Important" at
# resp 5. Under the reversed reading, these parents' single most encouraged
# activity would be watching sport on television (mean 1.96) and their least
# encouraged would be reading books (4.46). That is the test, and it is decisive.
dir_ok <- m[["CHIA3_CULTURAL"]] > m[["CHIA4_SPORT"]] &&
          m[["CHIA1_SPORT"]]    > m[["CHIA4_SPORT"]]
cat(sprintf("%-4s DIRECTION: read books (%.2f) and practice sport (%.2f) sit above watch\n",
            if (dir_ok) "OK" else "FAIL", m[["CHIA3_CULTURAL"]], m[["CHIA1_SPORT"]]))
cat(sprintf("     sport on TV (%.2f), so 5 is the 'Important' pole, not 1.\n", m[["CHIA4_SPORT"]]))
ok <- ok && dir_ok

cat("\nNOT ESTABLISHED: CHIA1_CULTURAL (museum, 3.12) vs CHIA2_CULTURAL (newspaper,\n")
cat("3.15) and CHIA5_SOCIAL (telethon, 3.05) vs CHIA7_SOCIAL (used clothes, 3.00)\n")
cat("are mutually indistinguishable by any distributional route; their order rests\n")
cat("on the codebook's list order alone. Hence PARTIAL, not VERIFIED.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
