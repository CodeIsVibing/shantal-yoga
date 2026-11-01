# Shantal Yoga Exercise Document

A page for building Shantal Yoga session plans as Word documents. You edit directly on a page that looks like the finished document. Photos are resized to the size they take up in the document, so the .docx stays small. Everything runs in the browser and photos never leave your computer.

## How to use
1. Type the document title.
2. Under each section heading, type the exercises. Enter adds a new line.
3. Add photos to an exercise: the "Add photos" button, drag and drop, or ⌘V.
4. Pick the photo quality and click **Download Word file** (or press ⌘S).

Your work is saved in the browser automatically. "Start a new document" clears the page, and "Undo" brings it back.

To change an existing file, click **Open Word file** (or press ⌘O, or drop the .docx onto the page). It works with files made here and with older session plans. Gray bands on the page show where Word will start a new page. They are approximate.

## Shrink many files
Open **Shrink many files** (or `batch.html`) to make a whole set of Word (.docx) and OpenDocument (.odt) files smaller.

1. Add files or a whole folder (or drop them onto the page).
2. Pick the photo quality and, in Chrome or Edge, an empty folder for the finished files. Other browsers download each file as soon as it is finished.
3. Press **Start**. Files are handled one at a time, with progress for the whole batch and for the current file.

Photos are resized to the size they are shown at in the document, at 200 or 300 dpi. The originals are never changed. Finished files are remembered, so after a crash or a closed tab the page continues where it stopped and skips what is already done.

## Run locally
Open `index.html` by double-clicking it. No internet connection needed.

## GitHub Pages
1. Create a repository and add all files (including `vendor/`).
2. Settings → Pages → Source: "Deploy from a branch", branch `main`, folder `/ (root)`.
3. The page is live at https://codeisvibing.github.io/shantal-yoga/.
