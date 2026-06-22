# Download

## Clone the repository

```bash
git clone https://github.com/0xThiagoAmaral/deadlock-open-assets.git
cd deadlock-open-assets
```

## CDN (no clone)

Use [jsDelivr](https://www.jsdelivr.com/) for any file:

```
https://cdn.jsdelivr.net/gh/0xThiagoAmaral/deadlock-open-assets@main/manifests/heroes.json
https://cdn.jsdelivr.net/gh/0xThiagoAmaral/deadlock-open-assets@main/images/deadlock/heroes_circle/abrams.png
```

Pin to a release tag for stability:

```
https://cdn.jsdelivr.net/gh/0xThiagoAmaral/deadlock-open-assets@v1.0.0/manifests/hub.json
```

## Large assets (GitHub Releases)

Some folders are too large for comfortable git browsing. Download from **Releases**:

| Package | Contents |
|---------|----------|
| `deadlock-particles-*.tar.gz` | 9,463 decompiled .vpcf files |
| `deadlock-images-*.tar.gz` | Full PNG bundle (optional) |

Generate locally:

```powershell
python tools/package_release.py
```

## Extract yourself

If you own Deadlock on Steam:

```powershell
pip install -r requirements.txt
python tools/extract_deadlock_assets.py --tier complete
python tools/build_community_hub.py --sync-remote
```

Or double-click `UmblockExtractor.bat`.

## Git LFS

PNG images may use Git LFS. Install [Git LFS](https://git-lfs.com/) before cloning if images appear as pointer files.

```bash
git lfs install
git clone https://github.com/0xThiagoAmaral/deadlock-open-assets.git
```
