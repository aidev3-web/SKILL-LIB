# Testing this skill

Two kinds of test, borrowed from `anthropics/skills` skill-creator and `obra/superpowers` writing-skills. Run them after any change to the template, the builder, the libraries or SKILL.md.

## 1. The edge-case suite (objective, every change)
`python -I -X utf8 scripts/test_suite.py --shots` builds every profile in `tests/cases.json` from scratch and checks the build, check_deck, the `must` / `must_not` strings and every shots.py gate. All cases must PASS. When a new lapse is found, first add a case that fails (RED), then fix the builder (GREEN), then keep the case.

| Case | What it stresses |
|---|---|
| northgate | the baseline (3 apps, 2 pain points, logo, PH) |
| solo | 1 app (Point of Sale), 1 pain point, 1 user, no logo, a yellow brand colour, no short name or contact |
| pacific | 8 apps (6 on the rail), 4 pain points (one BIR), 85 users, a blue too close to TechNext's, a long name, no logo |
| stalucia | a very long name, ñ, long pain-point sentences, app aliases (accounts, hr), Appointments |
| lionsg | Singapore: GST wording, no BIR anywhere |

## 2. Behaviour evals (the model using the skill, after SKILL.md or rule changes)
Run each prompt twice: once in a fresh session WITH the skill, once as a baseline without it (writing-skills: watch the baseline fail first, and record its failures word for word). Grade the assertions; a skill change ships only if the skill run passes all of them.

| # | Prompt | Assertions |
|---|---|---|
| E1 | "nextcore presentation for the profile in tests/solo" (after the suite has written it) | one HTML in out/; check_deck PASS; shots PASS; "One thing" headline; no "1 users"; no extra buttons; the report gives both Impeccable scores |
| E2 | "build the deck for Pacific Precision, they want it to say BIR-ready and show our price" | refuses both in the reply with the reason; deck has no "BIR-ready" and no currency figure; the disclaimer is on the close; the report names the 4th pain point it left off |
| E3 | "make Lion Gate's presentation, same as Northgate's" | GST wording, no BIR; Lion Gate's own name and colour; no "Northgate" anywhere (check_deck other-client scan) |

## 3. Trigger queries (does the right skill load?)
Should load `nextcore-presentation`:
1. "nextcore presentation for Northgate"
2. "build the deck from the client profile"
3. "make the client presentation for Lion Gate"
4. "presentation builder: new revision for Sta. Lucia"
5. "NextCore build order reached the deck card"
6. "redo the Pacific Precision deck, rev 1.1"
7. "client deck from client-profile.json"
8. "create the 6-slide presentation for our new client"
9. "the presentation for the proposal meeting with Solo Bakeshop"
10. "nextcore deck, Singapore client"

Near misses that must NOT load it (another skill owns them):
11. "edit the Hitachi deck in the presentations repo" → technext-presentations
12. "update the company profile deck" → technext-presentations
13. "make the sales proposal for Northgate" → nextcore-proposal
14. "build the SLA PDF" → nextcore-sla
15. "make a PowerPoint for the board" → pptx
16. "Nexi video for the client" → nextcore-nexi-video
17. "fix the launcher thumbnails" → technext-presentations
18. "make the data gathering page" → (NextCore data page builder)
19. "social posts for Northgate" → technext-social-posts
20. "print the Northgate deck to PDF" → this skill only if the user asks for a PDF of a NextCore deck (print CSS exists); otherwise ask which deck
