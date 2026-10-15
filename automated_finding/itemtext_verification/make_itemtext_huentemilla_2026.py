#!/usr/bin/env python3
"""Item text for huentemilla_2026_digital_competence_test (Zenodo 22256717). Spanish stems from the
workbook's Hoja2 sheet, keyed by the printed item number (= column Pk); items 47 and 54 are cut at 255
characters in the deposit and ship as deposited. Behaviour-scored 0/1 test: option_text is left blank
(the deposit records each respondent's chosen option, not the option list). Spanish administration
(Chilean university students); English in the _translated columns is IRW's."""
from _itemtext_writer_c import load_script, row, write

mod = load_script("huentemilla_2026_digital_competence_test")
EN = {
    1: "If you were doing a Google search for the definition of \"digital divide\", what would you type in the search bar to get precise information?",
    2: "When looking for up-to-date, scientifically reliable information on a specific topic in a discipline, you do so through:",
    3: "What type of search is shown in this screenshot of an advanced search?",
    4: "If you need to search for, compare and select digital information, which procedure is the most appropriate?",
    5: "Which of the following digital resources is/are the most appropriate for searching for academic information?",
    6: "What should you do to check that information found on the internet is reliable?",
    7: "What is the best way to organise web pages and share them?",
    8: "Which of these services allow us to store files online?",
    9: "Which mechanism is the most efficient and appropriate for backing up the information (photos, files, videos, etc.) on your phone so that it is accessible on any device?",
    10: "When I browse the Internet and find information I consider relevant to my friends or acquaintances.",
    11: "Which of the following applications would allow you to make video calls to interact with your classmates while they also write a collaborative document?",
    12: "Which of these applications allows you to interact in a chat while working on a collaborative document?",
    13: "Which of the following symbols represents \"share\"?",
    14: "I have found an interesting news item about new environmental protection policies. What is the fastest way to share it with the general public?",
    15: "If you have produced a presentation, assignment, report, document, infographic, etc. and want to share it so that others can see and reuse it, then:",
    16: "You need to create an online survey with many different questions. Which of the following tools is the most advisable?",
    17: "In which web environment do I find the most up-to-date information on the latest events affecting community services (metro, roads, electricity, etc.)?",
    18: "What do you need to be able to download certificates online from the Civil Registry and Identification website?",
    19: "Which of the following applications allows collaborative and simultaneous work?",
    20: "If you are doing collaborative work and need to coordinate, which digital tools would you use:",
    21: "Which tool works as an open virtual space for building and socialising, where you can contribute content and interact with readers?",
    22: "What information should you never show on the internet?",
    23: "What should you do if you want to send an email to several recipients without them knowing who else it was sent to?",
    24: "Is it advisable to make a backup copy of our data?",
    25: "You have to define your signature for the professional emails you send. What would be the most appropriate content?",
    26: "Someone tells me they are concerned about their online privacy and asks me to suggest a web browser that protects their identity on the web. Which web browser should I recommend?",
    27: "You created a profile on several social apps, but you have not used some of them for a long time and are no longer interested in them. What should you do?",
    28: "This digital resource corresponds to:",
    29: "If you want to show another person a procedure using a digital device, which strategy is the best?",
    30: "Which options do I need to activate to get a large, ready-made image about the environment?",
    31: "Which tool is the most appropriate for editing a photograph?",
    32: "Which of the following are criteria for effective presentations?",
    33: "Can I add subtitles to a video on YouTube?",
    34: "When selecting an image from the web that will be used freely, which of the following actions would you take?",
    35: "This symbol on a piece of material refers to:",
    36: "You have downloaded a book from the web that carries the following Creative Commons licence, which means:",
    37: "Which of the following is/are not a programming language?",
    38: "What does the following programming sequence indicate?",
    39: "At the end of the following loop, what is the value of the variable x?",
    40: "To safely remove mobile devices such as phones, cameras or flash drives connected to a computer or PC, it is recommended to:",
    41: "To improve the performance and battery life of your portable devices, it is advisable to.",
    42: "Which of the following updates is/are necessary to keep computers and mobile devices secure and working correctly?",
    43: "If you need to log in to different web services (personal email, social networks, etc.) from someone else's device, it is recommended to:",
    44: "I registered with an email service that requires me to activate two-step verification (2FA). Which of these options has the most common measures for 2FA?",
    45: "When buying online, how do you recognise that the page has a secure connection?",
    46: "In which of the following cases is using a mobile phone least advisable for mental health?",
    47: "Continuous use of devices with bright screens, especially blue light, may damage eyesight. There are several mechanisms to reduce its harmful effect, and a recommended distance from the screen which [text cut off at 255 characters in the deposit]",
    48: "Indicate which option(s) help protect against physical risks from excessive computer use.",
    49: "Technological waste, or devices that stop working or become obsolete, should be:",
    50: "Replacing equipment and/or devices is recommended:",
    51: "What initiative exists for recycling computers?",
    52: "The projector (Datashow) has the following input for connecting a computer. Which cable do I need to connect the computer and the projector successfully?",
    53: "My phone has the following charging port, very similar to the one on my notebook (image). Which cable should I buy to charge my phone?",
    54: "A mouse like the one in the image is having problems with the computer, as the pointer does not move. It was previously used without any problems. The computer and the operating system have not changed since last time. In this context [text cut off at 255 characters in the deposit]",
    55: "To make to-do lists that let the user keep track of what they are doing, have pending or need to complete, which alternative is the best?",
    56: "Which of the following services offer encrypted email?",
    57: "Which of the following concepts is not related to a digital resource?",
    58: "Which instant messaging application is suggested for use in a formal setting to encourage collaboration and teamwork?",
    59: "You need to create an infographic. Which of the following tools is/are the most relevant?",
    60: "Which tool(s) is/are the most appropriate for creating notes with digital multimedia content (text, images, videos, etc.) that are available to the user anywhere and from different devices?",
    61: "Can I obtain certificates for the courses I take online?",
    62: "In the following list, which digital-competence self-assessment tests can you identify?",
    63: "What does Digital Competence mean?",
}


def main():
    stems = mod.stems()
    table = "huentemilla_2026_digital_competence_test"
    rows = []
    for i in range(1, 64):
        c = f"P{i}"
        for r in (0, 1):
            rows.append(row(table, f"{table}_1", c, "Digital competence knowledge test, 63 scored items (pre/post)", "Spanish",
                            r, stems[c], option_text="", item_text_tr=EN[i], option_text_tr=""))
    write(table, rows)


if __name__ == "__main__":
    main()
