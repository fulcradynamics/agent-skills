# fulcra-primitives

The short version of how Fulcra actually works, for when you would rather read one page than ten.

Underneath everything else, Fulcra is three ideas. **Events** are timestamped records with data and metadata — the things that happened. **Metrics** are time series values you can read raw or in aggregate — the things that were measured. **Files** are versioned uploads, where each write keeps its predecessor rather than overwriting it.

Almost every other skill is built on those three. Once you can create a data type, write records into it, query a metric over a range, upload a file, and read any of it back, the rest stops looking like a product tour and starts looking like variations on things you already understand.

This is the plain introduction to that: no framing, no workflow, just the CLI, how to authenticate, and what the pieces are.

A good place to start if you prefer learning a system from the bottom rather than the top.
