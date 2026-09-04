#!/usr/bin/env python3
"""ecps_source.py -- batch_022, issue #1831

The administered instrument for the eight ecps_sahm_2024_* tables, which are
COVIDiSTRESS Global Survey Round II (see provenance.csv for the source
correction).

WHY THIS FILE EXISTS. The two questionnaire workbooks on OSF are
registration-stage documents: they give item wording but their response designs
do not describe what was administered -- information acquisition as a 1-7 slider
where the data run 1-10, agreement scales as 1-6 where the data run 1-7 or 0-6.
`Copy of survey.pdf`, in the Round II project's own Final-Data-Set folder, is
the actual Qualtrics form. It prints every response ladder verbatim, which is
what lets option_text be populated at all.

Two things it settled that the workbooks got wrong:
  - the agreement ladder has a NEUTRAL midpoint the workbooks omitted, so a
    six-anchor list is really seven options;
  - the compliance items are past tense ("Washed your hands regularly"), not
    the imperative the workbooks print.

WHY LITERALS RATHER THAN A PARSER. The Qualtrics print layout interleaves the
question flow and the answer flow across page boundaries, so item order cannot
be read off the extracted text -- page 15 prints two stems, then two ladders,
then items from both blocks mixed. The structure below is therefore written out,
and `verify()` checks every stem, item and ladder label against the sources.
That keeps it re-runnable and self-checking without depending on a layout that
cannot be parsed reliably.

The PDF is authoritative but PARTIAL, which `verify()` accounts for: its print
view renders only one statement per randomised misperception block, and only two
rows of each social-influence norm matrix. 190 strings verify against the PDF
and the remaining 16 against the workbooks, which is why item wording for the
norm blocks follows the workbooks throughout rather than mixing the two -- the
PDF confirms two of eight there, and writes "e.g.," where the workbooks write
"e.g.".

Item ORDER within a block comes from the workbooks, which agree with each other
word for word, except for the secondary stressors, where the administered survey
puts "Receiving inadequate, unclear, or conflicting information" before "Not
having enough support from close others" and the workbooks have them the other
way round. The survey wins: it is the administered form.
"""
import json, os, re, unicodedata

CACHE = ".cache/ecps_sahm_2024"
STUDY = "COVIDiSTRESS Global Survey Round II"

# ---------------------------------------------------------------- ladders
# Positions the form leaves without a verbal label are None, not invented.
AGREE7 = {1: "Strongly disagree", 2: "Disagree", 3: "Slightly disagree",
          4: "Neutral", 5: "Slightly agree", 6: "Agree", 7: "Strongly agree"}
# The _0neutral recode pulls the midpoint out to 0 and leaves the six named
# anchors at 1-6. Established by cross-tabulating each item's _0neutral and
# _midneutral copies in the cleaned file: 32 of 33 give 0->4, 1->1, 2->2, 3->3,
# 4->5, 5->6, 6->7 exactly.
AGREE7_0N = {0: "Neutral", 1: "Strongly disagree", 2: "Disagree",
             3: "Slightly disagree", 4: "Slightly agree", 5: "Agree",
             6: "Strongly agree"}
CHARACT5 = {1: "Not at all characteristic of me", 2: "A little characteristic of me",
            3: "Somewhat characteristic of me", 4: "Very characteristic of me",
            5: "Entirely characteristic of me"}
PSS5 = {0: "Never", 1: "Almost never", 2: "Sometimes", 3: "Fairly often",
        4: "Very often"}
CONCERN5 = {0: "Not at all concerned", 1: "Slightly concerned", 2: "Somewhat concerned",
            3: "Moderately concerned", 4: "Very concerned"}
SLIDER10 = {1: "Not at all", 2: None, 3: None, 4: None, 5: None, 6: None,
            7: None, 8: None, 9: None, 10: "Frequently"}
IMPORTANT7 = {1: "Not important at all", 2: None, 3: None, 4: None, 5: None,
              6: None, 7: "Very important"}
HOWMANY7 = {1: "Nearly nobody", 2: None, 3: None, 4: None, 5: None, 6: None,
            7: "Nearly everybody"}
# The willingness slider labels only its ends and midpoint; the _0neutral
# recode of a 5-point item maps 0->3, 1->1, 2->2, 3->4, 4->5.
WILLING_0N = {0: "Neutral", 1: "Not willing at all", 2: None, 3: None,
              4: "Very willing"}

# The emotions block prints only its ends and midpoint, unlike the identity and
# moral blocks which print all seven labels.
EMO7_0N = {0: "Neutral", 1: "Strongly disagree", 2: None, 3: None, 4: None,
           5: None, 6: "Strongly agree"}
# Trust is a 0-100% slider in ten-point steps, which is the live 0-10 range.
# The form prints "No trust" then 10% through 90%; the top position's label is
# not in the PDF's text layer, so it ships empty rather than inferred as 100%.
TRUST11 = {0: "No trust", 1: "10%", 2: "20%", 3: "30%", 4: "40%", 5: "50%",
           6: "60%", 7: "70%", 8: "80%", 9: "90%", 10: None}

# ------------------------------------------------------------------ blocks
AGREE_STEM = ("We will now present a few statements about the COVID-19 virus and about you. "
              "Please read the statements and indicate to what extent you agree with them.")
DTL_STEM = ("Think about how you deal with things in life. Please indicate the extent to "
            "which you agree with each of the following statements.")

TABLES = {
 "ia": [dict(
    label="Information acquisition", ladder=SLIDER10,
    stem="Over the last two weeks, how much have you used the following sources to get "
         "information about the coronavirus?",
    codes=["information_acquisit_%d" % k for k in range(1, 8)],
    items=["News broadcasters (TV, radio, newspapers)",
           "Government Coronavirus adverts or updates",
           "Social media",
           "Radio or podcasts (not news)",
           "Discussions (in person or messengers) with friends, family or colleagues",
           "Scientific journals or websites",
           "Other, please specify"])],

 "distrust": [
  dict(label="COVID-19 misperceptions", ladder=AGREE7, stem=AGREE_STEM,
       codes=["misperception1_1", "misperception1_2", "misperception2_1",
              "misperception2_2", "misperception3_1", "misperception3_2"],
       items=["A new loss of taste or smell is a symptom of COVID-19",
              "COVID-19 can be spread by people who do not show symptoms",
              "The COVID-19 virus is man-made",
              "COVID-19 is being spread by 5G cell phone technology",
              "Pharmaceutical companies created COVID-19 to profit from the vaccines",
              "COVID-19 is a hoax perpetrated by people who want to take control"]),
  dict(label="Conspiratorial thinking", ladder=AGREE7, stem=AGREE_STEM,
       codes=["conspirational_think_%d" % k for k in range(1, 5)],
       items=["Much of our lives are being controlled by plots hatched in secret places",
              "Even though we live in a democracy, a few people will always run things anyway",
              "The people who really ‘run’ the country are not known to the voter",
              "Big events like wars, recessions, and the outcomes of elections are controlled "
              "by small groups of people who are working in secret against the rest of us"]),
  dict(label="Anti-expert sentiment", ladder=AGREE7, stem=AGREE_STEM,
       codes=["antiexpert_%d" % k for k in range(1, 4)],
       items=["I am more confident in my opinion than other people’s facts",
              "Most of the time I know just as much as experts",
              "Experts really don’t know that much"])],

 "dtl": [
  dict(label="Resilience", ladder=AGREE7, stem=DTL_STEM,
       codes=["resilience_%d" % k for k in range(1, 7)],
       items=["I tend to bounce back quickly after hard times",
              "I have a hard time making it through stressful events",
              "It does not take me long to recover from a stressful event",
              "It is hard for me to snap back when something bad happens",
              "I usually come through difficult times with little trouble",
              "I tend to take a long time to get over set-backs in my life"]),
  dict(label="Intolerance of uncertainty", ladder=CHARACT5,
       stem="Please select the answer that best corresponds with characteristics of you.",
       codes=["uncertainty_%d" % k for k in range(1, 6)],
       items=["I always want to know what the future has in store for me.",
              "I should be able to organize everything in advance.",
              "When it's time to act, uncertainty paralyses me.",
              "I can’t stand being taken by surprise.",
              "Unforeseen events upset me greatly."])],

 "identity": [dict(
    label="Group identification", ladder=AGREE7_0N,
    stem="Most of us belong to groups of various levels. Think about people in your life, "
         "both close to you and people that you have never met. Focus on how close you feel "
         "to/identify with different groups of people. Please indicate to what extent you "
         "agree with the following statements.",
    codes=["identity_%d_0neutral" % k for k in range(1, 5)],
    items=["I identify with my family",
           "I identify with people in my local community",
           "I identify with people of my country",
           "I identify with humanity"])],

 "moral": [dict(
    label="Moral values", ladder=AGREE7_0N,
    stem="Please read the following sentences and indicate your agreement or disagreement",
    codes=["moral.values_%d_0neutral" % k for k in range(1, 12)],
    items=["Compassion for those who are suffering is the most crucial virtue.",
           "When the government makes laws, the number one principle should be ensuring "
           "that everyone is treated fairly.",
           "I am proud of my country’s history.",
           "Respect for authority is something all children need to learn.",
           "People should not do things that are disgusting, even if no one is harmed.",
           "It is better to do good than to do bad.",
           "One of the worst things a person could do is hurt a defenseless animal.",
           "Justice is the most important requirement for a society.",
           "People should be loyal to their family members, even when they have done "
           "something wrong.",
           "Men and women each have different roles to play in society.",
           "I would call some acts wrong on the grounds that they are unnatural"])],

 "sscd": [
  dict(label="Compliance with COVID-19 guidelines", ladder=AGREE7,
       stem="Many countries have issued guidelines for staying safe during the COVID-19 "
            "pandemic. Think about the last month, to what extent do you agree with the "
            "statements about what you did?",
       codes=["compliance_%d" % k for k in range(1, 9)],
       items=["Washed your hands regularly",
              "Wore a face covering in public when indoors (e.g., in a supermarket or cafe)",
              "Wore a face covering in public when outdoors (e.g., in the street or park)",
              "Stayed the recommended distance (for example 2 metres/6 feet) from people "
              "who are not part of your household",
              "Stayed at home unless going out for essential reasons (e.g., buying "
              "essentials, doing essential work, or exercising)",
              "Self-isolated (quarantine) if you suspected that you had been in contact "
              "with the virus",
              "Met with people outside of your household for non-essential reasons",
              "Stayed away from crowded places generally"]),
  dict(label="Social influence: injunctive norms", ladder=IMPORTANT7,
       stem="Now we want you to think about people important to you. How do they rate the "
            "following behaviours…",
       codes=["socialinfluence_nor1_%d" % k for k in range(1, 9)],
       items=["Washing their hands regularly",
              "Wearing a face covering in public when indoors (e.g. in a store or cafe)",
              "Wearing a face covering in public when outdoors (e.g. in the street or park)",
              "Staying at least [2 metres (6 feet)] at all times from people who are not "
              "part of your household",
              "Staying at home at all times unless going out for essential reasons (e.g., "
              "buying essentials, doing essential work, or exercising)",
              "Self-isolating (quarantining) when they suspect to have been in contact "
              "with the virus",
              "Met with people outside of your household for non-essential reasons",
              "Staying away from crowded places generally"]),
  dict(label="Social influence: descriptive norms", ladder=HOWMANY7,
       stem="Once again think about people important to you. How many of them…",
       codes=["socialinfluence_nor2_%d" % k for k in range(1, 9)],
       items=["Wash their hands regularly",
              "Wear a face covering in public when indoors (e.g. in a store or cafe)",
              "Wear a face covering in public when outdoors (e.g. in the street or park)",
              "Stay at least [2 metres (6 feet)] at all times from people who are not part "
              "of their household",
              "Stay at home at all times unless going out for essential reasons (e.g., "
              "buying essentials, doing essential work, or exercising)",
              "Self-isolate (quarantine) when they suspect to have been in contact with "
              "the virus",
              "Met with people outside of their household for non-essential reasons",
              "Stay away from crowded places generally"])],

 "stress": [
  dict(label="Perceived Stress Scale", ladder=PSS5,
       stem="Think about the last month, how often have you...",
       codes=["perceived_stress_sca_%d" % k for k in range(1, 11)],
       items=["been upset because of something that happened unexpectedly?",
              "felt that you were unable to control the important things in your life?",
              "felt nervous and “stressed”?",
              "felt confident about your ability to handle your personal problems?",
              "felt that things were going your way?",
              "found that you could not cope with all the things that you had to do?",
              "been able to control irritations in your life?",
              "felt that you were on top of things?",
              "been angered because of things that were outside of your control?",
              "felt difficulties were piling up so high that you could not overcome them?"]),
  dict(label="Primary stressors", ladder=CONCERN5,
       stem="In the last month, how much have you been concerned about the following:",
       codes=["primary_stressors_%d" % k for k in range(1, 5)],
       items=["Personally catching the coronavirus",
              "People close to me (children, friends, relatives) catching the coronavirus",
              "Not being able to travel",
              "Not being able to meet friends or family"]),
  dict(label="Secondary stressors", ladder=CONCERN5,
       stem="In the last month, how much have you been concerned about the following:",
       codes=["secondary_stressors__%d" % k for k in range(1, 15)],
       items=["Not being able to find a job in the future",
              "Inadequate financial support from the government",
              "Receiving inadequate, unclear, or conflicting information in relation to "
              "the pandemic",
              "Not having enough support from close others (e.g., family, friends)",
              "My relationship/marriage breaking down",
              "Losing my job",
              "Not receiving adequate support from my employer",
              "Being unable to work from home",
              "Sharing a workspace with others",
              "Being unable to study from home",
              "Sharing a workspace with others",
              "My children's education",
              "Not having access to childcare",
              "Coping with the behaviour of other people (children or adults) I am "
              "living with"])],

 "vaccine": [
  dict(label="Vaccine willingness", ladder=WILLING_0N,
       stem="Now we want to ask you a few questions about your thoughts on the COVID-19 "
            "vaccine.",
       codes=["vaccine_0neutral"],
       items=["How willing are you to get the vaccine if one becomes available to you? "
              "(If you have already been offered the vaccine, please think of how wiling "
              "you were before one became available to you)"]),
  dict(label="Vaccine attitudes", ladder=AGREE7_0N,
       stem="Please indicate for the following statements to what extent you agree with them.",
       # The data number these 2,3,4,5,6,9 for six items, so position 1 and two
       # others are absent from the cleaned file. Ascending code order is matched
       # to the survey's printed order -- an order inference, hence PARTIAL.
       codes=["vaccine_attitudes_%d_0neutral" % k for k in (2, 3, 4, 5, 6, 9)],
       items=["Getting vaccines is a good way to protect children from disease",
              "Generally, I do what my doctor recommends about vaccines",
              "New vaccines are recommended only if they are safe",
              "I am concerned about serious side effects of vaccines",
              "Parents should have the right to refuse vaccines required for schools for "
              "any reason",
              "Vaccinations are one of the most significant achievements in improving "
              "public health"])],
 "emotion": [dict(
    label="Emotion regulation (ERQ short form)", ladder=EMO7_0N,
    stem="We would like to ask you some questions about your emotional life, in particular, "
         "how you control (that is, regulate and manage) your emotions. The questions below "
         "involve two distinct aspects of your emotional life. One is your emotional "
         "experience, or what you feel like inside. The other is your emotional expression, "
         "or how you show your emotions in the way you talk, gesture, or behave. Although "
         "some of the following questions may seem similar to one another, they differ in "
         "important ways.",
    codes=["emotions_%d_0neutral" % k for k in range(1, 9)],
    # Administered order, not the workbooks'. The two disagree about where the
    # "negative emotions" item sits -- 4th here, 7th there -- and the data settle
    # it: the ERQ's suppression/reappraisal split falls on 1,2,4,5 against
    # 3,6,7,8 with a within-minus-between correlation gap of 0.268, the maximum
    # of 2000 random 4/4 partitions, where the workbook order gives 0.003.
    items=["I keep my emotions to myself.",
           "When I am feeling positive emotions, I am careful not to express them.",
           "When I’m faced with a stressful situation, I make myself think about it in a way "
           "that helps me stay calm.",
           "When I am feeling negative emotions, I make sure not to express them.",
           "I control my emotions by not expressing them.",
           "When I want to feel more positive emotion, I change the way I’m thinking about "
           "the situation.",
           "I control my emotions by changing the way I think about the situation I’m in.",
           "When I want to feel less negative emotion, I change the way I'm thinking about "
           "the situation."])],

 "support": [dict(
    label="Perceived social support", ladder=AGREE7_0N,
    stem="In your current day to day life, to what degree do you agree with the following?",
    codes=["perceived_support_%d_0neutral" % k for k in range(1, 4)],
    items=["If I am down, I know to whom to go to for support",
           "People would help me if I needed it",
           "I can count on others to meet my needs if things go wrong"])],

 "trust": [dict(
    label="Trust in institutions", ladder=TRUST11,
    stem="Please tell us how much you trust each of the institutions below. Please base your "
         "answer on your general impression.",
    codes=["trust_%d" % k for k in range(1, 8)],
    items=["Parliament/government in the country you live?",
           "Police in the country you live?",
           "Civil service in the country you live?",
           "Health system in the country you live?",
           "The World Health Organisation (WHO)",
           "Government's effort to handle Coronavirus (in the country you live)?",
           "Scientific research community"])],
}

LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}

def norm(s):
    """Fold away what differs between the PDF text layer and a typed literal."""
    for a, b in LIGATURES.items():
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("…", "...").replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9'\"()\[\]/,.?:;% -]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()

def survey_text():
    p = os.path.join(CACHE, "survey_pages.json")
    if os.path.exists(p):
        return norm(" ".join(json.load(open(p, encoding="utf-8"))))
    pdf = os.path.join(CACHE, "survey.pdf")
    if not os.path.exists(pdf):
        return None
    import pypdf
    r = pypdf.PdfReader(pdf)
    return norm(" ".join((pg.extract_text() or "") for pg in r.pages))

def workbook_text():
    """Both registration workbooks, as extracted to blocks.json."""
    p = os.path.join(CACHE, "blocks.json")
    if not os.path.exists(p):
        return None
    b = json.load(open(p, encoding="utf-8"))
    return norm(" ".join(l for v in b.values() for l in v["lines"]))

def verify():
    """Classify every stem, item and ladder label by the source it verifies in.

    The survey PDF is authoritative but partial: its print view renders only
    one statement per randomised misperception block, and only two rows of each
    social-influence norm matrix. Anything it does not carry is checked against
    the questionnaire workbooks instead. A string found in neither source is a
    failure -- that is the case this function exists to catch.
    """
    pdf, wb = survey_text(), workbook_text()
    if pdf is None and wb is None:
        return None
    out = {"pdf": 0, "workbook": 0, "unverified": []}
    for tab, secs in TABLES.items():
        for s in secs:
            strings = ([("stem", s["stem"])]
                       + [("item", i) for i in s["items"]]
                       + [("label", v) for v in s["ladder"].values() if v])
            for kind, val in strings:
                n = norm(val)
                if pdf and n in pdf:
                    out["pdf"] += 1
                elif wb and n in wb:
                    out["workbook"] += 1
                else:
                    out["unverified"].append((tab, s["label"], kind, val[:70]))
    return out

if __name__ == "__main__":
    r = verify()
    if r is None:
        print("neither source cached -- nothing verified")
    else:
        n = sum(len(s["items"]) for v in TABLES.values() for s in v)
        print("tables %d | items %d" % (len(TABLES), n))
        print("strings verified in the survey PDF   : %d" % r["pdf"])
        print("strings verified in the workbooks    : %d" % r["workbook"])
        print("strings verified in neither          : %d" % len(r["unverified"]))
        for x in r["unverified"][:20]:
            print("   UNVERIFIED %-9s %-36s %-5s %s" % x)
