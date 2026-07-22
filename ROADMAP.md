# DreamCoder Roadmap

This roadmap is ordered by user value and technical risk. It is not a promise of delivery dates.

## Now — trustworthy first use

- [x] Local-first SQLite and in-process verification defaults
- [x] Generated-artifact path validation and constrained iframe preview
- [x] Generation Run lifecycle module with failure completion tests
- [x] CI for backend lint/tests and frontend production build
- [x] Curated offline example gallery
- [ ] Record a real prompt-to-preview product demo with one supported provider
- [ ] Validate the quickstart on clean Windows, macOS, and Linux environments

## Next — safer, clearer iteration

- [ ] Isolate generated previews on a separate origin or disposable container
- [ ] Centralize provider construction, structured parsing, retry, and timeout behavior in one deep module
- [ ] Stream node-level progress instead of returning logs only after workflow completion
- [ ] Add deterministic browser tests for generated-artifact preview and follow-up generation
- [ ] Publish provider compatibility results with dates and tested model IDs

## Later — evidence before infrastructure

- [ ] Build an evaluation set for gameplay completeness, file validity, and iteration preservation
- [ ] Decide whether vector retrieval improves results before promoting ChromaDB into the default path
- [ ] Add multi-user hosted deployment guidance after preview isolation is independently reviewed
- [ ] Consider packaged local launchers only after the manual quickstart is consistently reproducible

Feedback is welcome through GitHub Issues. Please describe the user problem before proposing a new dependency or infrastructure layer.
