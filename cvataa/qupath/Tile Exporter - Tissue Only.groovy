import qupath.lib.common.GeneralTools
import qupath.lib.regions.RegionRequest
import org.locationtech.jts.geom.Envelope
import org.locationtech.jts.geom.GeometryFactory
import org.locationtech.jts.geom.Coordinate

// ---------------- SETTINGS ----------------
String classifierName = "IHC_Pixel_Classifier"
double requestedPixelSize = 1.5
int tileSizePx = 1024
int overlapPx = 0

double minTileTissueFraction = 0.40   // 30% threshold

double minAreaPixels = 1e6
double minHoleAreaPixels = 1e6

// Sampling grid for fast tissue fraction estimate
int samplesX = 10
int samplesY = 10
// ------------------------------------------

// Get image
def imageData = getCurrentImageData()
def server = imageData.getServer()
def imageName = server.getMetadata().getName()
def upper = imageName.toUpperCase()

//if (!upper.endsWith("HE") &&
//    !upper.endsWith("HE.SVS") &&
//    !upper.endsWith("HE.TIF") &&
//    !upper.endsWith("HE.TIFF") &&
//    !upper.endsWith("HE.NDPI")) {
//
//    println "Skipping (not HE): " + imageName
//    return
//}

println "Processing HE slide: " + imageName

// Clear old annotations
clearAnnotations()

// Create tissue annotations
createAnnotationsFromPixelClassifier(classifierName, minAreaPixels, minHoleAreaPixels)

def annotations = getAnnotationObjects()
if (annotations.isEmpty()) {
    println "No tissue detected. Skipping."
    return
}

// ---- Build tissue union geometry ----
def tissueGeom = annotations
    .collect { it.getROI().getGeometry() }
    .inject(null) { acc, g -> acc == null ? g : acc.union(g) }

if (tissueGeom == null || tissueGeom.isEmpty()) {
    println "Empty tissue geometry."
    return
}

// Output folder
def base = GeneralTools.getNameWithoutExtension(imageName)
def pathOutput = buildFilePath(PROJECT_BASE_DIR, "tiles", base)
mkdirs(pathOutput)

// Compute downsample (guard calibration)
double pixelSize = server.getPixelCalibration().getAveragedPixelSize()
if (Double.isNaN(pixelSize) || pixelSize <= 0) {
    throw new IllegalArgumentException("Pixel size not calibrated for " + imageName + ". Cannot compute downsample from requestedPixelSize.")
}
double downsample = requestedPixelSize / pixelSize

// Tile dimensions in FULL resolution coordinates
double tileW = tileSizePx * downsample
double tileH = tileSizePx * downsample
double stepX = (tileSizePx - overlapPx) * downsample
double stepY = (tileSizePx - overlapPx) * downsample

int fullW = server.getWidth()
int fullH = server.getHeight()

def gf = new GeometryFactory()
def tissueEnv = tissueGeom.getEnvelopeInternal()  // cheap prefilter

int exported = 0
int skipped = 0

for (double y = 0; y + tileH <= fullH; y += stepY) {
    for (double x = 0; x + tileW <= fullW; x += stepX) {

        // Fast envelope reject (cheaper than polygon ops)
        def rectEnv = new Envelope(x, x + tileW, y, y + tileH)
        if (!tissueEnv.intersects(rectEnv)) {
            skipped++
            continue
        }

        // Still do a quick intersects check
        def rect = gf.toGeometry(rectEnv)
        if (!rect.intersects(tissueGeom)) {
            skipped++
            continue
        }

        // ---- FAST tissue fraction estimate by sampling points ----
        int inside = 0
        int total = samplesX * samplesY

        double dx = tileW / samplesX
        double dy = tileH / samplesY

        for (int iy = 0; iy < samplesY; iy++) {
            double py = y + (iy + 0.5) * dy
            for (int ix = 0; ix < samplesX; ix++) {
                double px = x + (ix + 0.5) * dx
                def pt = gf.createPoint(new Coordinate(px, py))
                if (tissueGeom.contains(pt))
                    inside++
            }
        }

        double frac = inside / (double) total

        if (frac < minTileTissueFraction) {
            skipped++
            continue
        }

        // Export this tile
        def request = RegionRequest.createInstance(server.getPath(), downsample, (int)x, (int)y, (int)tileW, (int)tileH)
        def filename = String.format("x_%d_y_%d.tif", (int)x, (int)y)
        def outPath = buildFilePath(pathOutput, filename)

        writeImageRegion(server, request, outPath)
        exported++
    }
}

println "Export complete."
println "Exported tiles: " + exported
println "Skipped tiles: " + skipped
