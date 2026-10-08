# fulcra-dashboard

Turn your own data into something you can actually look at.

Fulcra holds the real-world data you have collected — sleep, movement, listening, whatever you have connected. Useful, but a data store is not a view. This skill builds the view: it scaffolds a dashboard from a clean template, fills it with the data you actually have, and then reshapes it around what you want to see — a chart you asked for, a comparison nobody anticipated, a layout that suits how you read.

Then it gets themed, which is more of the point than it sounds. The agent asks what vibe you want — minimalist dark, cyberpunk, a retro diner, a cosy bakery — rewrites the titles and labels to match, generates original artwork for the header, and animates it.

It runs locally against your own store, and it asks first: permission to pull your data, and permission to load the third-party charting libraries it draws with.

The output is deliberately lightweight: HTML, Alpine.js, plain CSS, with a small Python backend to serve it. No build step, and no framework to keep up with.

When you want to share something, there is a separate export path that produces a specific previewable directory — and before anything is deployed you are told exactly which files are about to become public and asked to confirm. Publishing is a deliberate act, and the rest of your data stays where it was.
