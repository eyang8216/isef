# Experimental Data Directory

This directory stores experimental validation data.

## Structure

```
experimental_data/
├── metadata/              # Trial metadata JSON files
├── frozen_predictions/    # Preregistered predictions (SHA-256 hashed)
├── images/                # Raw camera images/videos (not tracked in git)
└── profiles/              # Extracted profile coordinates
```

## Workflow

1. **Before experiment**: Create metadata file in `metadata/`
2. **Run matched simulation**: Generate frozen prediction in `frozen_predictions/`
3. **Conduct experiment**: Save images/videos to `images/` (local only, too large for git)
4. **Process images**: Extract profiles to `profiles/`
5. **Compare**: Simulation vs experimental profiles

## Note

Raw image files are excluded from git tracking due to size. Keep local backups and document image locations in metadata files.
