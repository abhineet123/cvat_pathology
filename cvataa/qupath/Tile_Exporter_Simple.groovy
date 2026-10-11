import qupath.lib.common.GeneralTools
import qupath.lib.images.writers.TileExporter

// ---------------- SETTINGS ----------------
int tileSizePx = 256
int overlapPx = 0
String imageExt = ".png"
// -----------------------------------------

def imageData = getCurrentImageData()
def server = imageData.getServer()
def imageName = server.getMetadata().getName()

// 🚫 Skip H&E images
if (imageName.toUpperCase().contains("HE")) {
    println "Skipping H&E image: " + imageName
    return
}
println "Processing: " + imageName

def anns = getAnnotationObjects()
println "Annotations found: " + anns.size()
if (anns.isEmpty()) {
    println "No annotations found - skipping."
    return
}

// Output folder
def base = GeneralTools.getNameWithoutExtension(imageName)
def pathOutput = buildFilePath(PROJECT_BASE_DIR, "256", base)
mkdirs(pathOutput)

// ✅ 100% native resolution (no resampling)
double downsample = 1.0

new TileExporter(imageData)
        .downsample(downsample)
        .imageExtension(imageExt)
        .tileSize(tileSizePx)
        .overlap(overlapPx)
        .annotatedTilesOnly(true)
        .writeTiles(pathOutput)

println "Export complete @ native resolution."
println "Done! Exported to: " + pathOutput