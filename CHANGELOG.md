# Changelog

All notable changes to this project are listed here. Versions follow semantic versioning.

## [1.1.0] - 2026-11-01

### Changed
- The app is now called "Shantal Yoga Exercise Document" (was "Photos to Word").
- Everything in the document is centered: logo, title, section headings, exercise names and photo rows, both on the page and in the Word file.
- A new document starts with only the title; everything below it is added by the user. An empty page shows a short hint.
- "New document" is now a clear button next to "Open Word file" in a new File card.
- Exercise controls (photo size, Add photos) float in a small menu above the line, so they never cover the centered name.

### Removed
- The Shortcuts card. The shortcuts still work.

## [1.0.0] - 2026-11-01

First public release of Photos to Word for Shantal Yoga session plans.

### Added
- Edit directly on an A4 page that looks like the finished Word document: title, section headings and exercises with rows of photos.
- The Shantal Yoga logo is always placed at the top right, rebuilt as a transparent PNG from the original document.
- Download as a small .docx file. Every photo is resized to the size it takes up on the page (150 or 300 dpi) and saved as JPG.
- Photos in an exercise are arranged in balanced rows that fill the page width, with Small, Medium and Large sizes.
- Approximate Word page breaks are shown on the page, and the panel shows the page count.
- When an exercise misses the bottom of a page by a little, its photos shrink (down to 60%) so the page is filled instead of leaving a gap.
- Open an existing .docx, both files made here and older session plans, to keep editing it.
- Outline panel, document stats, estimated file size, keyboard shortcuts, drag and drop, paste with Cmd+V, and Undo after deleting.
- Work is saved automatically in the browser (IndexedDB). Works offline; JSZip is bundled in vendor/.
- Light and dark theme, mobile layout and reduced motion support.
