import qupath.lib.common.GeneralTools
import qupath.lib.images.writers.TileExporter

def imageData = getCurrentImageData()
def server = imageData.getServer()

def name = GeneralTools.getNameWithoutExtension(server.getMetadata().getName())
def pathOutput = buildFilePath(PROJECT_BASE_DIR, 'tiles', name)
mkdirs(pathOutput)

// Check we actually have tissue annotations
println "Annotations: " + getAnnotationObjects().size()

// Output resolution (µm/px) – only works if pixel calibration exists
double requestedPixelSize = 2.0
double pixelSize = server.getPixelCalibration().getAveragedPixelSize()

if (Double.isNaN(pixelSize) || pixelSize <= 0) {
    throw new IllegalArgumentException("Pixel size not calibrated for this image; set requestedPixelSize via downsample directly.")
}

double downsample = requestedPixelSize / pixelSize

new TileExporter(imageData)
    .downsample(downsample)
    .imageExtension('.tif')
    .tileSize(512)
    .annotatedTilesOnly(true)   // requires tissue annotations from the thresholder
    .overlap(0)                 // set to 0 unless you truly need overlap
    .writeTiles(pathOutput)

print 'Done!'
