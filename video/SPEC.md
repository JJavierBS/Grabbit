GOAL:    A judge understands in 1:56 that Grabbit gives a lone angel a sourced Slush
         shortlist and watches it, and wants to open the demo.
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps. HyperFrames is the master. The fast graphics are
         Remotion clips: source in remotion/src, `npm run render` there writes transparent
         WebM to assets/overlays/, and index.html mounts each one as a muted video.
TIME:    115.5 s x 30 = 3465 frames (hard limit 120 s). The presenter speaks in every filmed
         shot: the presenter's voice is the clock, and each graphic lands on its word. The ElevenLabs
         voice is only over the app captures.
LOOK:    Ground #f7f7fa flat, no texture. Ink #14151c. One accent, violet #6139f8: one
         phrase per designed shot, the logo's speed lines, the end card.
         Display: Hanken Grotesk 800, 150-430 px, tracking -0.035 to -0.045em, left aligned
         at x = 96. Body: Hanken Grotesk 500-700, 28 px minimum. Wordmark: Outfit 800.
         Medium: the angel's desktop. Browser windows are white, 2 px #e3e3ec line,
         22 px radius, shadow 0 30 px 70 px at 14%. The product is always a real capture.
OBJECTS: The presenter at Messukeskus, the Slush venue, filmed hand-held on an iPhone 16 Pro
         (4K, 30 fps, Apple Log). The proxies in assets/footage/ are Rec.709; the look is the
         data-color-grading on each video in index.html: a startup showcase grade, preset
         clean-studio at 0.8, contrast 0.2, whites 0.14, blacks -0.14, vibrance 0.3, and an
         exposure for each shot (0.16-0.18 in daylight, 0.28 for the dusk closing). No wheels:
         a warm highlight tint turns the white sign and the white jumper pink. The presenter faces the camera in every shot.
         Plates: ground colour, 2 px #e3e3ec line, 22 px radius, shadow 0 30 px 70 px at 14%.
         All text over footage sits on a plate beside the presenter, never over the presenter, and
         stays in screen space (the camera moves, so nothing is pinned to the ground).
         Browser windows (title bar, three grey dots, truncated tab titles). The speed lines
         (the two violet bars of the logo): they take the tabs away (s03) and bring the end
         card in (s12). Third-party marks: the Slush logo appears once, in the s01 title.
MOTION:  Ease by role: a plate arrives on expo.out in 18 frames; a move is power2.inOut,
         15 frames; an exit is a blur-out on the spot, power2.in, 6 frames; camera punch-in
         power3.inOut 15 frames, then hold.
         Three entrances, not one: the rise (40 px, scale 0.96), the wipe from an edge
         (clip-path, the answer plates "2 days" and "You: Deciding"), the whip from the left
         (140 px, 10 px blur that clears as it lands: the lockup and the notification).
         Text never moves while it is read. It arrives in place: letters 1.5 frames apart,
         words 2-3 frames apart, 6 px blur to 0 in 4 frames.
         Remotion clips: real motion blur on every fast mover (180 degree shutter, 16-32
         samples) and closed-form springs with a damping ratio of 0.68-0.88, one for each
         object. Numbers roll as odometer columns, they do not swap. In the end card the two
         speed lines brake and become the two bars of the mark.
         Footage to app screen: zoom-through, 12 frames. The footage pushes in (power3.in),
         blurs and its exposure rises to the ground colour; the window grows in from 0.75 and
         18 px blur (expo.out, 15 frames). App screen to footage: the inverse, the window
         recedes to 0.8 and the footage arrives oversized and settles. Both sides of a cut move
         in the same direction. Footage to footage stays a hard cut.
SHOTS:   s01    0-315     footage 1, the entrance, wide: "Slush 2026", counter to 3,000+, "2 days"
         s02  315-573     footage 2, medium: 12 windows pile up on the right, "47 tabs. 0 decisions."
                          No scene file: the clip pile.webm, frames 393-603, crosses the cut
         s03  573-759     footage 3, medium: the speed lines take the pile away, "Skip the data.",
                          the presenter shows the app on the phone, the Grabbit lockup lands
         s05  759-1239    app capture (placeholder): thesis and two reference investors
         s06 1239-1719    app capture (placeholder): the question and its numbers
         s07 1719-2019    app capture (placeholder): the report opens, trust badges
         s08 2019-2319    app capture (placeholder): the correction and the change marks
         s09 2319-2463    footage 5, the presenter walks away: "You: away." "Grabbit: on watch.", a notification
         s10 2463-2883    app capture (placeholder): the alert with "Simulated event"; why it matters
         s11 2883-3309    footage 4, the closing: "Other investors: Searching" against "You: Deciding",
                          then "Skip the data. Focus on what matters."
         s12 3309-3465    the speed lines bring the end card in; "Built on Cala"; demo link
                          No scene file: the clip endcard.webm. The counter of s01 is count.webm
         Not mounted: cap.html and s04.html (the cap and into-the-screen shots are not in the cut).
BANNED:  dark ground; glow; gradients; invented app UI; real product names on the tabs of
         shot 2; the logo before shot 3 except inside the tab; text over a dimmed capture;
         a screen line that repeats the spoken sentence word for word; everything centred
         (only the end card is centred).
QA:      6 s the number readable beside the presenter; 18.9 s 47 tabs drawn, no plate over
         the face; 24.6 s the phone screen and the lockup both readable; 80.6 s the
         notification readable; 104 s the two plates clear of the head; 112.5 s lockup 30%
         of the frame width, link readable.
