# Showcase Website Setup Guide

## Overview

Build a portfolio website for the Data Journalism course (SS-2026, Hertie School) that showcases student projects. Hosted as a GitHub Page under the `data-journalism-26` organization.

## Step 1: Create the repo

Go to https://github.com/orgs/data-journalism-26 and create a new repo called `showcase` (public, with a README). Clone it locally.

## Step 2: Add the data

Copy `projects.json` from this folder into the repo root. This file contains metadata for all projects (title, authors, URL, category, editor's pick status, thumbnail filename, blurb).

## Step 3: Add thumbnails

Create a `thumbnails/` folder in the repo. Add student portrait photos named to match the `thumbnail` field in `projects.json` (e.g., `elenadreyer.jpg`, `giorgio.jpg`). For students without thumbnails, the site should show a placeholder or initials.

## Step 4: Enable GitHub Pages

In the repo settings, enable GitHub Pages from the `main` branch, root folder.

## Step 5: Use Claude Code to build the site

Open Claude Code in the cloned repo directory and send the following prompts in sequence.

---

### Prompt 1: Initial build

```
Read projects.json. Build a single-page website (index.html + style.css + app.js) that showcases these student data journalism projects. Requirements:

Design:
- Modern news magazine aesthetic (think The Pudding meets NYT interactive). Dark header, clean white content area, good typography (Inter or similar from Google Fonts).
- NO frameworks, NO build step. Plain HTML/CSS/JS that works as a static GitHub Page.
- Responsive (works on mobile).

Structure:
- Hero section: "Data Journalism Portfolio - Hertie School SS 2026" with a short intro paragraph about the course.
- "Editor's Picks" section at the top featuring projects where editors_pick is true. These get large cards with thumbnail, title, subtitle, blurb, and a "Read the story" link.
- Below that, projects grouped by category. Use these category labels:
  - "conflict" -> "Conflict & Security"
  - "migration" -> "Migration"
  - "energy" -> "Energy & Infrastructure"
  - "transport" -> "Transport & Aviation"
  - "public-opinion" -> "Public Opinion & Polling"
  - "domestic-politics" -> "Domestic Politics"
  - "climate" -> "Climate & Environment"
  - "economics" -> "Economics & Trade"
  - "urban" -> "Urban & Local"
  - "culture" -> "Culture & Media"
  - "press-freedom" -> "Press Freedom"
  - "investigation" -> "Investigations"
  - "history" -> "History"
  - "education" -> "Education"
  - "inequality" -> "Inequality"
- Each project card shows: thumbnail (or initials fallback), title, subtitle, author names, assignment badge (Final Project / Data Bit 1 / Data Bit 2), and links to the live piece and GitHub repo.
- Cards link to the project URL. If url is null, link to the repo instead.
- Footer with course info: "GRAD-E1493: Data Journalism, taught by Prof. Simon Munzert, Hertie School, Berlin. Spring 2026."

Thumbnails are in the thumbnails/ folder. If thumbnail is null, generate a colored circle with the author's initials.

Load projects.json via fetch() and render everything client-side so the page is easy to maintain (just update the JSON to add projects).
```

### Prompt 2: Polish and refine

```
Improve the design:
1. Add a subtle filter/search bar above the category sections that lets users filter by category or search by title/author.
2. Editor's picks should have a gold accent or badge. Use a horizontal scroll or 2-column grid for picks.
3. Add smooth scroll-to-section when clicking category names in a sticky nav bar.
4. Add a count badge next to each category name showing how many projects it contains.
5. Hover effects on cards: subtle shadow lift, thumbnail slight zoom.
6. Make the assignment badges visually distinct: "Final Project" in a dark badge, "Data Bit 1/2/3" in lighter shades.
```

### Prompt 3: Add course context

```
Add an "About" section between the hero and the editor's picks with this text:

"This portfolio showcases work from the Data Journalism course at the Hertie School in Berlin (Spring 2026). Students produced three data bits - short, focused data journalism pieces - and a final project over the course of the semester. The projects span investigative data work, interactive visualizations, and explanatory journalism. All code is open source."

Also add a small "About the course" expandable section in the footer that links to the course syllabus at https://github.com/data-journalism-26 and mentions the topics covered: web scraping, survey analysis, maps and geodata, data visualization, and interactive graphics.
```

### Prompt 4: Final checks

```
Review the site for:
1. All project URLs resolve (no broken links for null URLs - those should link to repo).
2. Mobile layout works (cards stack, hero text is readable, filter bar doesn't break).
3. Categories: Make sure every category features at least 2 articles. Reduce overall number of categories. One category should be on Berlin (e.g. for the firefighter and the may 1st pieces), another one on geographic deep dives into America ("Oh, America"), featuring food deserts, the native Americans piece, the data centers piece and others who focus on the US
4. The page loads fast (no heavy dependencies, images are lazy-loaded).
5. For each category, feature one piece more prominently and the others as smaller thumbnails. Also, consider using two 
6. Add an Open Graph meta tag so the page previews nicely when shared on social media. Title: "The Hertie Times". Description: "Student projects from the Data Journalism course at the Hertie School, Berlin."
7. Author names (e.g., Daniel Boppert, not Thiele)
8. Use author thumbnails. I added a few in the thumbnails folder. Assign them randomly.
9. Use of colors and other design features. Make the Title more colorful with background colors. Also, try to integrate a unique style. I like low-poly and areal designs with a reduced but aestethic color palette.
10. Add a column to the right, similar to how opinion pieces are catered on nytimes or washington post. Use those to promote selected data bits.
```

---

## Step 6: Deploy

```bash
git add .
git commit -m "Launch showcase site"
git push
```

The site will be live at `https://data-journalism-26.github.io/showcase/`.

## Maintenance

To add or update projects, edit `projects.json` and push. The site renders from the JSON dynamically, so no HTML changes needed.

To add thumbnails, drop images in `thumbnails/` with filenames matching the `thumbnail` field in the JSON.
