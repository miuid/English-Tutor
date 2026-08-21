# Beta Handbook — English Tutor

Welcome, and thank you for being one of our first beta families. This handbook
is everything you need: what the tutor is, how to install it, what happens to
your child's data, how to tell us what's working (and what isn't), and the
weekly check-in we ask of beta families.

You were invited personally — we're keeping the beta to a small group of
families we know, so please be blunt with feedback. Fast, honest feedback is
exactly why you're here.

---

## 1. The one-pager: what your child is using

**English Tutor** is an after-school writing coach for Australian secondary
students (Year 8–12, QCAA curriculum). It is **not** a chatbot that writes
essays — it is a tutor that teaches your child to write better, one 15-minute
session at a time.

**A daily session looks like this (about 15 minutes):**

1. **Goal** — the tutor sets one small, specific goal for today.
2. **I do** — the tutor demonstrates the skill on a *different* example.
3. **We do** — your child practises together with the tutor.
4. **You do** — your child writes independently (this part matters most).
5. **Feedback** — the tutor gives the 1–2 highest-leverage next steps, never a
   laundry list, and grades the attempt against the QCAA A–E rubric.

**What it will never do:**

- Write your child's essay for them. The coach hands the work back — that's
  the whole point.
- Replace their teacher. It reinforces school; it doesn't compete with it.
- Run all night. Sessions pause automatically at the daily time budget.

**What it covers in this beta:** Year 8–10 analytical, persuasive, and
imaginative writing (QCAA). Senior (Year 11–12) depth is coming later.

**Beta honesty:** this is pre-release software. The tutoring logic is tested,
but you will hit rough edges — odd feedback, a slow response, a confusing
screen. When that happens, we want to hear about it (see §4).

---

## 2. Install guide (no technical background needed)

The app runs **on your own computer** — nothing to sign up for, no account, no
password. It takes about 15 minutes the first time; most of that is a one-time
download. After that, starting it takes seconds.

### The easy way: let us set it up

If you'd rather not touch any of this, just say the word — a 15-minute
call/visit and it's running on your family computer. Skip to §3.

### The DIY way

**Step 1 — Install Docker Desktop (free, one-time).**
Docker is a standard tool that runs the app in a self-contained box, so the
app can't mess with the rest of your computer.

- Windows / Mac: download **Docker Desktop** from
  <https://www.docker.com/products/docker-desktop/> and install it.
- Open Docker Desktop once and leave it running (whale icon in the menu
  bar / system tray).

**Step 2 — Get the project folder.**
You'll receive `english-tutor` as a zip file from us. Unzip it somewhere
permanent (e.g. Documents). Inside it you should see `backend`, `frontend`,
`docker-compose.yml`, and this handbook.

**Step 3 — Add the API key.**
The tutor needs a key to talk to the AI model. You'll receive one from us
(treat it like a password — don't forward it).

- In the `english-tutor` folder, go into `backend`, copy the file
  `.env.example` and rename the copy to `.env`.
- Open `.env` in any text editor (Notepad/TextEdit is fine) and replace the
  `LLM_API_KEY=` line with the key you received:

```ini
LLM_API_KEY=sk-...the key you received...
```

**Step 4 — Start the app.**

- Windows: open the `english-tutor` folder, hold Shift, right-click empty
  space, choose **"Open in Terminal"** (or "Open PowerShell window here").
- Mac: open **Terminal**, type `cd ` (with a space), drag the
  `english-tutor` folder onto the Terminal window, press Enter.

Then run:

```bash
docker compose up -d --build
```

The first run downloads and builds everything — **3–8 minutes**, one time
only. Later starts take seconds.

**Step 5 — Open the app.**
In any browser, go to: <http://localhost/>

If you see the welcome wizard, you're in. (Sanity check:
<http://localhost/health> should show `{"status":"ok"}`.)

**Step 6 — First run (30 seconds).**
The wizard asks you to **create a student profile**: your child's first name,
year level, curriculum (QCAA for Queensland), and optionally the text types
they're working on. Then press **Start today's session** — done.

### Everyday use

| To… | Do this |
|---|---|
| Start a session | Open <http://localhost/> and press **Start today's session** |
| Stop the app | In the project folder: `docker compose down` (data is kept) |
| Start it again later | Make sure Docker Desktop is running, then `docker compose up -d` |
| After we send you an update | `docker compose up -d --build` in the project folder |
| Change profile details | The **Profile** tab in the app |

### Troubleshooting

| Symptom | Fix |
|---|---|
| `docker` is not recognised | Docker Desktop isn't running — start it and wait for the whale icon to settle |
| Error about `.env` missing | The file must be named exactly `.env` inside `backend/` (not `.env.example`, not `.env.txt` — Windows: turn on "File name extensions" to check) |
| Page opens but feedback never arrives / errors | Usually the API key — check the key in `backend/.env` has no extra spaces or quotes, then `docker compose up -d` again |
| Port 80 is already in use | Run `WEB_PORT=8080 docker compose up -d` and use <http://localhost:8080/> instead |
| Anything else | Send us a feedback package (§4) — it exists precisely for this |

### Uninstalling

In the project folder: `docker compose down -v` deletes the app **and all
student data** from your machine. Then delete the folder and (optionally)
Docker Desktop. Nothing was ever installed anywhere else.

---

## 3. Privacy: what happens to your child's data

This is a child's data, so the defaults are minimal retention and easy
deletion.

- **Everything stays on your computer.** Profiles, your child's writing,
  feedback, and scores live in one database file on your machine. There is no
  cloud account, no analytics company, no advertiser.
- **One exception, by design:** to produce feedback, your child's writing is
  sent over an encrypted connection to the AI model provider (currently
  Kimi/Moonshot, via the API key). That's the only data that ever leaves your
  machine. Nothing else is sent anywhere.
- **No login = family device only.** The app trusts whoever is on your
  computer/home network. Don't expose it to the public internet; if siblings
  share a device, each has their own profile.
- **Delete any time.** Deleting a student profile removes their sessions,
  writing, feedback, and scores permanently — no copy is kept elsewhere
  because there is nowhere else.
- **The feedback package contains no writing.** When you report a problem
  (§4), the downloaded file contains usage counts and technical details only —
  no student writing, no tutor responses, no names, no API key. This boundary
  is enforced by automated tests, not just good intentions.

---

## 4. Feedback channel: how to reach us

**Something broken or feedback that looked wrong?**

1. In the app, open the **Profile** tab and click **Report a problem** — this
   downloads a small JSON file (the "feedback package", see §3 for what's in
   it).
2. Email or message that file to Cheng, with one line about what you saw and
   roughly when it happened.

That package lets us diagnose most issues in under 10 minutes without ever
seeing your child's writing.

**Small stuff** (a confusing button, a typo, an idea): just message us
directly. No form, no process — you're a beta family, not a ticket queue.

**We'd especially love to hear:**

- Feedback the tutor gave that was wrong, generic, or unhelpful (with the
  feedback package, we can replay exactly what happened).
- Sessions your child abandoned — where and why.
- Anything your child said about it, good or bad. Quote them verbatim.

---

## 5. Weekly check-in template (5 minutes, once a week)

Once a week during the beta, copy this into a message/email and send it back.
Short answers are perfect — "all fine, nothing to report" is a valid check-in.

```text
Beta check-in — week of: ____/____/______
Family / student (first name + year level): ________________

1. Sessions this week: how many days did your child use the tutor?
   [ ] 0   [ ] 1–2   [ ] 3–4   [ ] 5+

2. The daily loop (goal → I do → we do → you do → feedback):
   Was 15 minutes about right?  [ ] too short  [ ] about right  [ ] too long

3. Best moment this week (a piece of feedback that landed, a skill that
   clicked, anything your child volunteered about it):

4. Worst moment this week (confusing screen, wrong/unhelpful feedback,
   session abandoned — if possible, attach a feedback package from
   Profile → Report a problem):

5. Your child's writing: any change you noticed at school or at home?

6. One thing you'd change first:

7. Keep going next week?  [ ] yes  [ ] yes, but…  [ ] pausing
```

---

*Beta scope note: this handbook describes the current per-family local beta.
Hosted accounts, subscriptions, and multi-school features are future plans,
not things this build has.*
