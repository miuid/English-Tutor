# QCE Senior Instrument Modelling — English (General)

**Ticket:** ISS-024 · **Status:** modelled framework only — no senior content depth beyond this note and the seed rows.

## Source

| | |
|---|---|
| Document | English 2025 v1.3 — General senior syllabus (January 2026) |
| Publisher | © State of Queensland (QCAA) 2026 |
| Licence | CC-BY 4.0 (syllabus front matter); attribution: © State of Queensland (QCAA) 2026, www.qcaa.qld.edu.au/copyright |
| Official URL | https://www.qcaa.qld.edu.au/downloads/senior-qce/syllabuses/snr_english_25_syll.pdf |
| Archived copy | `research/official/english-2025-v1.3-syllabus.md` (full extracted text, retrieved 2026-08-21) |
| Currency | For implementation with students completing the course in 2026 or beyond (QCAA syllabus page) |

All page references below are to this syllabus. Per Q-001 (answered 2026-08-21), senior framework
claims cite this official document directly; derived descriptors from earlier research files are not
used for senior rows.

## Course structure (syllabus "Course structure" p. 6; "Units" pp. 17–32)

| Unit | Title | Phase | Reporting |
|---|---|---|---|
| 1 | Perspectives and texts | Year 11 formative | S/U (NR) to QCAA |
| 2 | Texts and culture | Year 11 formative | S/U (NR) to QCAA |
| 3 | Textual connections | Year 12 summative (studied as a pair with Unit 4) | contributes to subject result |
| 4 | Close study of literary texts | Year 12 summative | contributes to subject result |

Units 1–2 precede Units 3–4; Units 3–4 are studied as a pair (p. 6). In Units 1–2 schools develop
2–4 assessments and report S/U; in Units 3–4 schools develop three assessments using the syllabus
specifications and conditions ("Designing a course of study", p. 7).

## Summative assessment instruments (syllabus "Assessment" pp. 33–48)

Each instrument contributes 25% to the subject result out of 100.

| Instrument | Technique | Mode & response requirement | Key conditions | ISMG criteria (marks) |
|---|---|---|---|---|
| IA1 | Spoken persuasive response | Spoken (live or recorded), up to 8 minutes | 4 weeks notification; individual; open access to resources | Knowledge application (8), Organisation and development (8), Textual features (9) |
| IA2 | Written response for a public audience | Written, up to 1500 words | 5 weeks notification; individual; open access to resources; two connected texts, ≥1 from the prescribed text list | Knowledge application (9), Organisation and development (8), Textual features (8) |
| IA3 | Examination — extended response (imaginative) | Written; 15 min planning + 120 min working | Supervised; no notes or springboard text; task provided 1 week prior | Knowledge application (9), Organisation and development (8), Textual features (8) |
| EA | Examination — extended response (analytical essay) | Written; 15 min planning + 120 min working | Unseen question on a literary text from the EA section of the prescribed text list; relates to Unit 4; developed and marked by the QCAA, common to all schools | Marked by QCAA (25) |

Note the technique mix: **IA1 is a persuasive spoken task, IA3 is the imaginative examination, and the
analytical written instruments are IA2 and the EA.** The senior "analytical essay" depth therefore
lives in IA2 and EA, not IA1 (recorded in Q-005 for ISS-025 scoping).

## ISMG structure (syllabus "Instrument-specific marking guide", pp. 36–38, 40–42, 45–47)

- Each internal instrument is marked with an ISMG of the same three criteria: **Knowledge
  application**, **Organisation and development**, **Textual features**.
- Each criterion lists performance-level descriptors with mark ranges, keyed by a qualifier ladder:
  *discerning → effective → suitable/appropriate → superficial/inconsistent → fragmented → does not
  match (0)*.
- Schools mark each instrument by criterion and report a **provisional mark by criterion** to the
  QCAA; the QCAA confirms the results ("Determining and reporting results", p. 16).

## Reporting standards and A–E (syllabus "Reporting", pp. 15–16)

- Reporting standards are summary statements of typical performance at A–E, organised under the same
  three headings (application of knowledge; organisation and development; textual features) with the
  same qualifier ladder: A *discerning*, B *effective*, C *suitable*, D *superficial/inconsistent*,
  E *fragmented*.
- Units 1–2: unit judgment A–E is made using the reporting standards, but reported to QCAA only as
  S/U/NR.
- Units 3–4: confirmed IA marks (IA1 + IA2 + IA3, 25 each) combine with the EA result (25) into a
  **subject result as a mark out of 100 and as an A–E**, determined by the QCAA ("Determining and
  reporting results", p. 16).

## curriculum_outcome mapping (backend/app/seed.py)

| Row | code | year_level | text_type | strand |
|---|---|---|---|---|
| Units 1–4 | QCAA-Y11-U1, QCAA-Y11-U2, QCAA-Y12-U3, QCAA-Y12-U4 | 11 / 11 / 12 / 12 | `framework` | Course structure |
| IA1 | QCAA-Y12-IA1 | 12 | persuasive | Summative assessment |
| IA2 | QCAA-Y12-IA2 | 12 | analytical | Summative assessment |
| IA3 | QCAA-Y12-IA3 | 12 | imaginative | Summative assessment |
| EA | QCAA-Y12-EA | 12 | analytical | Summative assessment |

Descriptors record framework facts only (technique, weight, response requirement, conditions, ISMG
criteria with mark allocations) with a page-level citation. `framework` marks course-structure rows
that span text types. Year 8–10 rows are untouched.

## ISMG → A–E mapping strategy for the product

1. **Criterion alignment.** Senior feedback uses the three official ISMG criterion names
   (Knowledge application, Organisation and development, Textual features) so per-criterion scores
   line up 1:1 with the school's provisional marks.
2. **Qualifier ladder.** Internal five-level judgments reuse the official qualifier vocabulary
   (fragmented → superficial → suitable → effective → discerning). This ladder is identical in the
   ISMG descriptors and the A–E reporting standards, so it bridges instrument-level marks and
   subject-level A–E without inventing our own scale.
3. **Marks, then grade.** A senior attempt can carry per-criterion marks inside the official ranges
   (e.g. IA1 Knowledge application 0–8). Summing an instrument's criteria yields its mark out of 25;
   summing IA1+IA2+IA3+EA yields a provisional /100.
4. **A–E is always provisional.** Only the QCAA determines the official subject result A–E after
   confirmation (p. 16). The product may show a *provisional* band from the qualifier ladder for
   coaching purposes and must never present it as an official result.
5. **Units 1–2 stay formative.** No mark semantics for Year 11 rows; S/U reporting is a school
   decision outside product scope.

## Boundaries (acceptance criterion 3)

- Framework rows + this note only. No senior reference packs, rubrics, or task content are authored
  here; senior content depth waits for ISS-025 (IA1 framework/handoff per Q-005) and a real senior
  user.
- The prescribed text list is referenced as an external QCAA resource, not imported.
