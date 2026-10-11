import qupath.lib.common.GeneralTools
import qupath.lib.regions.RegionRequest
import org.locationtech.jts.geom.Envelope
import org.locationtech.jts.geom.GeometryFactory

// ---------------- SETTINGS ----------------
String classifierName = "tissue mask"
double requestedPixelSize = 1
int tileSizePx = 512
int overlapPx = 0

double minTileTissueFraction = 0.10   // 50% threshold

double minAreaPixels = 1e6
double minHoleAreaPixels = 1e6
// ------------------------------------------

// Get image
def imageData = getCurrentImageData()
def server = imageData.getServer()
def imageName = server.getMetadata().getName()

println "Processing: " + imageName

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

// Compute downsample
double pixelSize = server.getPixelCalibration().getAveragedPixelSize()
double downsample = requestedPixelSize / pixelSize

// Tile dimensions in FULL resolution
double tileW = tileSizePx * downsample
double tileH = tileSizePx * downsample
double stepX = (tileSizePx - overlapPx) * downsample
double stepY = (tileSizePx - overlapPx) * downsample

int fullW = server.getWidth()
int fullH = server.getHeight()

def gf = new GeometryFactory()

int exported = 0
int skipped = 0

for (double y = 0; y + tileH <= fullH; y += stepY) {
    for (double x = 0; x + tileW <= fullW; x += stepX) {

        def rect = gf.toGeometry(new Envelope(x, x + tileW, y, y + tileH))

        if (!rect.intersects(tissueGeom)) {
            skipped++
            continue
        }

        double interArea = rect.intersection(tissueGeom).getArea()
        double tileArea = rect.getArea()
        double frac = interArea / tileArea

        if (frac < minTileTissueFraction) {
            skipped++
            continue
        }

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
