---
format: 1920x1080
duration: 83.1s
message: "Slush has 2,989 attendees and you are one person. Grabbit finds the startups backed by the investors you trust, shows the source of every fact, and alerts you when one of them moves."
arc: The door → Grabbit → It watches
audience: Junction 2026 judges and peer reviewers
---

The presenter speaks in every filmed frame. The times of the spoken words are in the script of
each scene file. Frames 4 to 7 and frame 9 are screen recordings of the public app (one take,
cut into assets/captures/, then cut fast by assets/captures/recut.sh into assets/captures/fast/).

Voiceover over the captures: the final voice is the presenter's own recording, one file for each line
(`voiceover to record` below). Until it exists a stand-in plays: the old ElevenLabs takes (voice Lara) at
1.1x speed, in assets/vo/fit/ (`stand-in` below).

Sound: the presenter and the voiceover sit at -16.5 LUFS. The music bed plays under the whole film: 0.16
under the presenter, 0.24 under the voiceover, 0.5 in the gaps, 0.6 on the end card. The bed
(assets/music/bed.mp3) is a stand-in: it is flat, and the film needs a track that builds to 25.3 s, drops
there, and lifts again at 63.7 s. Effects (assets/sfx/, ElevenLabs): a riser into an impact on the cut into
the app (25.3 s), a whoosh on each zoom-through (51.1, 55.9, 63.7 s), a softer impact on the mark (78.8 s).

## Frame 1: At the door (0-10.5s)

- act: Act 1: The door
- status: built
- src: compositions/s01.html
- footage: assets/footage/shot-1-door.mp4
- duration: 10.5s
- poster: 9.6s
- spoken: "Slush 2026. In just one week, more than 3,000 startups will cross these doors, and you only have two days to find the right one."
- reads: the Slush logo and 2026 (0.4-4.4s); the counter rolls to 3,000+ (4.8-10.5s); "2 days" (8.4-10.5s)
- overlay: assets/overlays/count.webm (remotion/src/Count.tsx), 4.7-10.5s

## Frame 2: Tabs (10.5-19.1s)

- act: Act 1: The door
- status: built
- overlay: assets/overlays/pile.webm (remotion/src/Pile.tsx), 13.1-20.1s, no scene file
- footage: assets/footage/shot-2-tabs.mp4
- duration: 8.6s
- poster: 8.4s
- spoken: "So you will do what everyone does: open one tab per business. But the door is open and you're still searching."
- reads: 12 windows pile up on the right while the count runs to 47 tabs (2.7-6.6s); "0 decisions." (7.1-8.6s)

## Frame 3: Skip the data (19.1-25.3s)

- act: Act 2: Grabbit
- status: built
- src: compositions/s03.html
- footage: assets/footage/shot-3-meet.mp4
- duration: 6.2s
- poster: 5.5s
- spoken: "But there's a way where you can skip the data. Meet Grabbit."
- reads: the speed lines take the pile away (0.2-0.8s); "Skip the data." (1.8-4.4s); the phone shows the app and the Grabbit lockup lands (4.6-5.8s); the frame zooms through the phone screen into the app (5.8-6.2s)

## Frame 4: Thesis (25.3-32.1s)

- act: Act 2: Grabbit
- status: built
- src: compositions/s05.html
- capture: assets/captures/fast/s05.mp4
- duration: 6.8s
- voiceover to record: "Type your thesis. One vague line is enough." at 25.6s, 3.0s at most
- stand-in: "Tell Grabbit what you want. A vague thesis is enough." at 25.6s
- reads: the typed thesis, after the punch-in (0.5-2.2s); the agent reads it (2.4-3.8s); its answer and three questions arrive (3.9-6.8s)

## Frame 5: It asks (32.1-38.6s)

- act: Act 2: Grabbit
- status: built
- src: compositions/s06.html
- capture: assets/captures/fast/s06.mp4, the same take as frame 4 with no cut between them
- duration: 6.5s
- voiceover to record: "Grabbit asks back, with real numbers from Cala's graph." at 28.9s (in frame 4, when the questions arrive), 4.8s at most; "Name the investors you trust." at 34.0s, 2.2s at most
- stand-in: "Grabbit does not only answer. It asks, and each question has real numbers from Cala's graph." at 28.9s; "Then name the investors you trust." at 34.0s
- reads: the three questions and their numbers (0-1.4s); the three answers, the last one names both investors (1.4-3.6s); the answers go (4s); the report card (5s)

## Frame 6: Shortlist (38.6-45.1s)

- act: Act 2: Grabbit
- status: built
- src: compositions/s07.html
- capture: assets/captures/fast/s07.mp4
- duration: 6.5s
- voiceover to record: "Your Slush shortlist. Who led each round. Which investors you trust joined. Every fact shows its source." at 38.8s, 6.2s at most
- stand-in: "Here is your Slush shortlist. Who led each round. Which of your trusted investors joined. Each fact shows its source." at 38.8s
- reads: the report opens (0-1.5s); the frame moves to the report and it scrolls to one startup (1.5-3.9s); the path to the trusted lead investor and the co-invest signal with its trust badge (3.9-6.5s)

## Frame 7: It rewrites itself (45.1-51.1s)

- act: Act 2: Grabbit
- status: built
- src: compositions/s08.html
- capture: assets/captures/fast/s08.mp4
- duration: 6s
- voiceover to record: "Too long? Say so. Grabbit rewrites its own instructions." at 45.5s, 5.2s at most
- stand-in: "Too long? Say so." at 45.85s; "The agent rewrites its own instructions, and the report changes in front of you." at 47.3s
- reads: "Shorter, co-investors first" goes (0.5s); the agent rewrites (1-2.2s); the report shows its change marks: 67% shorter, 3 startups removed (2.4-6s)
- not shown: a source opening. A source link opens a new browser tab, which the capture window cannot show

## Frame 8: Away (51.1-55.9s)

- act: Act 3: It watches
- status: built
- src: compositions/s09.html
- footage: assets/footage/shot-5-away.mp4
- duration: 4.8s
- poster: 3.3s
- spoken: "So, while I am away, it is ready to notify if anything changes."
- reads: "You: away." (0.7s); "Grabbit: on watch." (1.7s); the footage arrives from the app screen (0-0.5s); a notification beside the presenter (2.4-4.4s); the frame zooms through into the alert (4.4-4.8s)

## Frame 9: The alert (55.9-63.7s)

- act: Act 3: It watches
- status: built
- src: compositions/s10.html
- capture: assets/captures/fast/s10.mp4
- duration: 7.8s
- voiceover to record: "A startup on your list raises a seed. You know why it matters before the others read the news." at 56.3s, 6.8s at most
- stand-in: "A startup on your shortlist announces a seed round, led by an investor you trust." at 56.3s; "You know why it matters before the others read the news." at 60.5s
- reads: the in-app alert with its Simulated event label, after the punch-in (0.6-2.7s); the alert opens in the chat with why it matters (3.9-7.8s)
- note: the capture shows the in-app alert, not the desktop notification of the operating system

## Frame 10: The closing (63.7-77.9s)

- act: Act 3: It watches
- status: built
- src: compositions/s11.html
- footage: assets/footage/shot-4-closing.mp4
- duration: 14.2s
- poster: 13.7s
- spoken: "So, compared to other investors, while them search for information, you spend your time deciding which opportunity is the best for you. And remember, with Grabbit, you skip the data and focus on what matters."
- reads: "Other investors: Searching" (0.5-9s) against "You: Deciding" (5.6-9s); the frame moves the presenter right (9.4-10s); "Skip the data. Focus on what matters." (11-14.2s)

## Frame 11: End card (77.9-83.1s)

- act: Act 3: It watches
- status: built
- overlay: assets/overlays/endcard.webm (remotion/src/EndCard.tsx), no scene file
- duration: 5.2s
- poster: 2.2s
- reads: the speed lines bring the card in and become the bars of the mark (0-0.9s); the lockup, "Built on Cala", the demo button and the domain grabbit.cloud hold (2.5-5.2s)
