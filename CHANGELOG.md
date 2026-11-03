# Changelog

All notable changes to this project are listed here. Versions follow semantic versioning.

## [1.4.1] - 2026-11-03

### Fixed
- Removed a Python cache folder (tools/__pycache__) that was committed by mistake, and ignored it from now on.

## [1.4.0] - 2026-11-03

### Added
- Exercise templates page (templates.html): browse, search and filter every exercise from the past plans, edit name, section, photo size and photos (drag to reorder, drop or paste to add), delete with Undo, create new templates, import and export a templates file.
- Templates menu on the Exercise Document page: choosing an exercise adds it, with its photos and size, to the end of its section; a missing section heading is added first.
- Save as PDF (button and Cmd+P): pages laid out like the Word file, with the same page breaks, through the browser's "Save as PDF".
- tools/build.py and tools/extract.py build the templates file from a folder of plans.

## [1.3.0] - 2026-11-01

### Changed
- Shrink documents now saves every file as Word (.docx), whatever the original format.

### Added
- Built-in .odt to .docx conversion: text formatting, headings, bullet and numbered lists, tables (column widths, merged cells, borders), photos at their frame size, SVG and WebP drawn as PNG, text boxes, tabs and line breaks, page breaks, header and footer, page size and margins.
- When an .odt and a .docx in the same list share a name, the converted file is saved as "name (from odt).docx".

## [1.2.0] - 2026-11-01

### Added
- New page "Shrink documents" (batch.html), linked as "Shrink many files": makes many .docx and .odt files smaller, one at a time.
- Each photo is resized to the size it is shown at in the document (200 or 300 dpi); transparent photos stay PNG; photos are only replaced when the result is clearly smaller.
- Progress for the whole batch and for the current file, and a live list of waiting, working, finished and failed files.
- Each finished file is saved right away: into a chosen folder in Chrome and Edge, or downloaded in other browsers. Folders with the originals are refused, so originals are never overwritten.
- Finished files are remembered. After a crash or a closed tab the page continues where it stopped, skips finished files, and skips a file that stopped the page twice.
- Favicon: the rose from the logo, tightly cropped with no background (light in dark browser themes).

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
