## build_gilbert_meta_107.R
## Source: Cohen, Abubakar, Perlman (2023) "Pathways to Choice: A Bundled
## Intervention against Child Marriage", CEGA Working Paper WPS-230
## (escholarship.org/uc/item/33j1k1k4), Appendix B "Empowerment beliefs index"
## (cached: itemtext/.cache/gilbert_meta_107/paper_raw.txt, lines 1748-1768)

items <- data.frame(
  item = c("soneduc","dghthome","sonparent","sonfirst","womanfcshome",
           "manpltcs","needhus","relyson","agreehus","fatherchoose"),
  item_text = c(
    "It is important that sons have more education than daughters.",
    "Daughters should be sent to school only if they are not needed to help at home.",
    "The most important reason that sons should be more educated than daughters is so that they can better look after their parents when they are older.",
    "If there is a limited amount of money to pay for tutoring, it should be spent on sons first.",
    "A woman should take good care of her own children and not worry about other people's affairs.",
    "Woman should leave politics to the men.",
    "A woman has to have a husband or sons or some other male kinsman to protect her.",
    "The only thing a woman can really rely on in her old age is her sons.",
    "A good woman never questions her husband's opinions, even if she is not sure she agrees with them.",
    "When it is a question of children's health, it is best to do whatever the father wants."
  ),
  stringsAsFactors = FALSE
)

table <- "gilbert_meta_107"
section_id <- "gilbert_meta_107_empowerment_beliefs"
instrument <- "Empowerment Beliefs Index (gender-attitude agree/disagree statements), Pathways to Choice endline/baseline survey (Cohen, Abubakar & Perlman 2023)"

out <- do.call(rbind, lapply(seq_len(nrow(items)), function(i) {
  data.frame(
    table = table,
    section_id = section_id,
    item = items$item[i],
    instrument = instrument,
    instructions = NA_character_,
    section_prompt = NA_character_,
    item_text = items$item_text[i],
    correct_response = NA_character_,
    option_text = NA_character_,
    resp = c(0L, 1L),
    stringsAsFactors = FALSE
  )
}))

saveRDS(out, "/home/ben/Dropbox/projects/irw/src/itemtext/skill_test/sessionB_batch/candidate_gilbert_meta_107.rds")
str(out)
print(out)
