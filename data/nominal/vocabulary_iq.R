##Nominal companion of vocabulary_iq: the Vocabulary IQ Test (openpsychometrics.org,
##July 2017 - March 2018). Each of the 45 questions lists five words and asks for the
##two with the same meaning. The source records the pair as a 5-bit code (word k
##contributes 2^(k-1); e.g. 24 = words 4 and 5), which data/vocabulary_iq.R scores
##0/1 against the codebook key. Here `text` is the pair actually chosen, as the two
##words ("large+big"), so wrong answers keep which pair was picked.
##A handful of answers selected one word, or three; those are joined the same way.
##
##`text` codes: the two words joined by "+"; "don't know" where the source has -1
##(the respondent chose "don't know"); empty where the source has 0 (no response).
##The core table scores both -1 and 0 as missing; the distinction survives only here.
##Items 46-75 (s1-s30, the optional 1-5 personality survey) are carried with an
##empty `text`, so id/item/resp match the core table row for row.
library(dplyr); library(tidyr); library(readr); library(stringr)

zip <- tempfile(fileext = ".zip")
download.file("https://openpsychometrics.org/_rawdata/VIQT_data.zip", zip, mode = "wb", quiet = TRUE)
csv <- grep("VIQT_data\\.csv$", unzip(zip, list = TRUE)$Name, value = TRUE)
raw <- read_delim(unz(zip, csv), show_col_types = FALSE)
names(raw) <- tolower(names(raw))

## The five words of each question, in order (codebook.txt).
words <- strsplit(c(
 "tiny faded new large big","shovel spade needle oak club","walk rob juggle steal discover",
 "finish embellish cap squeak talk","recall flex efface remember divest","implore fancy recant beg answer",
 "deal claim plea recoup sale","mindful negligent neurotic lax delectable","quash evade enumerate assist defeat",
 "entrapment partner fool companion mirror","junk squeeze trash punch crack","trivial crude presidential flow minor",
 "prattle siren couch chatter good","above slow over pierce what","assail designate arcane capitulate specify",
 "succeed drop squeal spit fall","fly soar drink peer hop","disburse perplex muster convene feign",
 "cistern crimp bastion leeway pleat","solder beguile distant reveal seduce","dowager matron spank fiend sire",
 "worldly solo inverted drunk alone","protracted standard normal florid unbalanced","admissible barbaric lackluster drab spiffy",
 "related intrinsic alien steadfast pertinent","facile annoying clicker obnoxious counter","capricious incipient galling nascent chromatic",
 "noted subsidiary culinary illustrious begrudge","breach harmony vehement rupture acquiesce","influence power cauterize bizarre regular",
 "silence rage anger victory love","sector mean light harsh predator","house carnival yeast economy domicile",
 "depression despondency forswear hysteria integrity","memorandum catalogue bourgeois trigger note","fulminant doohickey ligature epistle letter",
 "titanic equestrian niggardly promiscuous gargantuan","stanchion strumpet pole pale forstall","yearn reject hanker despair indolence",
 "introduce terminate shatter bifurcate fork","omen opulence harbinger mystic demand","hightail report abscond perturb surmise",
 "fugacious vapid fractious querulous extemporaneous","cardinal pilot full trial inkling","fixed rotund stagnant permanent shifty"), " ")
stopifnot(length(words) == 45, all(lengths(words) == 5))

pair <- function(q, code) {
  mapply(function(q, k) {
    if (is.na(k) || k == 0) return(NA_character_)
    if (k == -1) return("don't know")
    paste(words[[q]][bitwAnd(k, 2^(0:4)) > 0], collapse = "+")
  }, q, code, USE.NAMES = FALSE)
}

## Same id and item numbering as data/vocabulary_iq.R: id = row number, items in
## column order q1-q45 then s1-s30 -> 1-75.
qs <- paste0("q", 1:45)
text <- raw |>
  mutate(id = row_number()) |>
  select(id, all_of(qs)) |>
  pivot_longer(-id, names_to = "q", values_to = "code") |>
  mutate(item = as.integer(sub("q", "", q)),
         text = pair(item, code)) |>
  select(id, item, text)
## Nearly all answers are a pair, but the source also holds 917 single-word and one
## three-word selection (all scored wrong in core); `text` keeps what was selected.
stopifnot(all(lengths(strsplit(na.omit(text$text[text$text != "don't know"]), "+", fixed = TRUE)) %in% 1:3))

core <- irw::irw_fetch("vocabulary_iq")
nom <- core |> left_join(text, by = c("id", "item"))
stopifnot(nrow(nom) == nrow(core), nrow(core) == 12173 * 75)
## every scored vocabulary answer has a pair, and resp = 1 exactly where it is the keyed pair
chk <- nom |> filter(item <= 45, !is.na(resp))
stopifnot(!any(is.na(chk$text)))

write.csv(nom, "vocabulary_iq_nom.csv", row.names = FALSE, na = "")
