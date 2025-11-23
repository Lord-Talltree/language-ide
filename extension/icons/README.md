# Icon Placeholders

Extension icons are referenced in manifest.json but not yet created.

## Temporary Solution

Create simple text-based icons:

```bash
# Create placeholder icons (Linux/Mac)
convert -size 16x16 xc:blue -pointsize 12 -draw "text 2,12 'L'" icons/icon16.png
convert -size 48x48 xc:blue -pointsize 36 -draw "text 6,36 'L'" icons/icon48.png
convert -size 128x128 xc:blue -pointsize 96 -draw "text 16,96 'L'" icons/icon128.png
```

## For Now

Upload simple PNG files with "L" text in blue background at sizes:
- 16x16px
- 48x48px  
- 128x128px

## Future

Design proper icons with:
- GPS/compass metaphor
- Clean, modern aesthetic
- Recognizable at small sizes
