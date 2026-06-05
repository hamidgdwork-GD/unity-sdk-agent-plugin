# Contributing

New SDK integrations should be added as self-contained packs under:

```text
core/integrations/<integration-id>/
```

## Required Files

Each integration should include:

- `README.md`
- `recipe.md`
- `recipe.yaml`
- `templates/`

## Recipe Checklist

Document:

- package names and versions
- supported Unity versions if known
- required project settings
- generated files
- validation checks
- manual steps
- known limitations

## Validation First

Every integration should include validation before full automation. A validator lets AI agents inspect existing projects safely before they start changing files.

