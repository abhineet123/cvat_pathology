import qupath.lib.common.GeneralTools
import qupath.lib.objects.PathObjects
import qupath.lib.objects.classes.PathClassFactory
import qupath.lib.regions.ImagePlane
import qupath.lib.roi.GeometryTools
import qupath.lib.roi.ROIs
import qupath.lib.regions.RegionRequest

import java.awt.image.BufferedImage

// ---------------- SETTINGS ----------------
String pixelClassifierName = "Tissue Mask"

double requestedPixelSize = 1.5      // µm/px (requires calibration)
int tileSizePx = 512
int overlapPx = 0
String imageExt = ".png"

// Pixel-classifier -> annotation cleanup
double minArea = 1e6
double minHoleArea = 1e6

// Tissue coverage threshold (0.30 = 30%)
double minTissueFraction = 0.30
// -----------------------------------------

def imageData = getCurrentImageData()
def server = imageData.getServer()
def imageName = server.getMetadata().getName()
println "Processing: " + imageName

// 1) Manual annotations
def manualAnns = getAnnotationObjects()
println "Manual annotations found: " + manualAnns.size()
if (manualAnns.isEmpty()) {
    println "No annotations found - skipping."
    return
}

// Union manual geometries
def manualGeom = manualAnns.collect { it.getROI().getGeometry() }
        .inject(null) { acc, g -> acc == null ? g : acc.union(g) }

if (manualGeom == null || manualGeom.isEmpty()) {
    println "Manual ROI geometry empty - skipping."
    return
}

// Convert union geometry -> ROI (supported in your QuPath)
def plane = ImagePlane.getDefaultPlane()
def unionROI = GeometryTools.geometryToROI(manualGeom, plane)

// TEMP annotation so we can select ONE object
def unionClass = PathClassFactory.getPathClass("TEMP_MANUAL_UNION")
def unionAnn = PathObjects.createAnnotationObject(unionROI, unionClass)
addObject(unionAnn)

// 2) Run pixel classifier within selected union annotation
def before = new HashSet(getAnnotationObjects())

setSelectedObject(unionAnn)
createAnnotationsFromPixelClassifier(pixelClassifierName, minArea, minHoleArea)
clearSelectedObjects(true)

// Remove TEMP union annotation
removeObject(unionAnn, true)

// Find newly created annotations from classifier
def after = getAnnotationObjects()
def classifierAnns = after.findAll { !before.contains(it) }

println "Classifier annotations created: " + classifierAnns.size()
if (classifierAnns.isEmpty()) {
    println "Classifier produced no objects - skipping."
    return
}

// Union classifier mask geometry
def maskGeom = classifierAnns.collect { it.getROI().getGeometry() }
        .inject(null) { acc, g -> acc == null ? g : acc.union(g) }

if (maskGeom == null || maskGeom.isEmpty()) {
    println "Classifier mask geometry empty - cleanup + skipping."
    classifierAnns.each { removeObject(it, true) }
    return
}

// Cleanup raw classifier annotations (recommended)
classifierAnns.each { removeObject(it, true) }

// Add ONE mask annotation (optional, for visualization)
def maskROI = GeometryTools.geometryToROI(maskGeom, plane)
def maskClass = PathClassFactory.getPathClass("IHC_Mask_For_Tiling")
def maskAnn = PathObjects.createAnnotationObject(maskROI, maskClass)
addObject(maskAnn)

println "Mask annotation added for tiling."

// Output folder
def base = GeneralTools.getNameWithoutExtension(imageName)
def pathOutput = buildFilePath(PROJECT_BASE_DIR, "tiles", base)
mkdirs(pathOutput)

// Calibration -> downsample
double pixelSize = server.getPixelCalibration().getAveragedPixelSize()
if (Double.isNaN(pixelSize) || pixelSize <= 0) {
    throw new IllegalArgumentException("Pixel size not calibrated for " + imageName)
}
double downsample = requestedPixelSize / pixelSize
println "Pixel size (um/px): " + pixelSize + " | Requested (um/px): " + requestedPixelSize + " | Downsample: " + downsample

// Tile size in full-res pixels (RegionRequest uses full-res coords)
int tileSizeFull = Math.max(1, Math.round(tileSizePx * downsample) as int)
int stride = Math.max(1, tileSizeFull - overlapPx)

println "Tile size (export px): ${tileSizePx} | Tile size (full-res px): ${tileSizeFull} | Stride: ${stride}"
println "Min tissue fraction: ${minTissueFraction}"

// Limit scan to mask bounds
def env = maskGeom.getEnvelopeInternal()
int minX = Math.floor(env.getMinX()) as int
int minY = Math.floor(env.getMinY()) as int
int maxX = Math.ceil(env.getMaxX()) as int
int maxY = Math.ceil(env.getMaxY()) as int

int tested = 0
int kept = 0

for (int y = minY; y <= maxY - tileSizeFull; y += stride) {
    for (int x = minX; x <= maxX - tileSizeFull; x += stride) {

        tested++

        // Build tile rectangle geometry in full-res coords
        def tileROI = ROIs.createRectangleROI(x, y, tileSizeFull, tileSizeFull, plane)
        def tileGeom = tileROI.getGeometry()

        // Compute tissue fraction
        def inter = tileGeom.intersection(maskGeom)
        if (inter == null || inter.isEmpty())
            continue

        double frac = inter.getArea() / tileGeom.getArea()
        if (frac < minTissueFraction)
            continue

        // Read region at requested downsample (so output is ~tileSizePx)
        def req = RegionRequest.createInstance(server.getPath(), downsample, x, y, tileSizeFull, tileSizeFull)
        BufferedImage img = server.readRegion(req)

        // Save using QuPath built-in writer (works across versions)
        String outName = String.format("%s_x%d_y%d_t%.2f%s", base, x, y, frac, imageExt)
        def outPath = buildFilePath(pathOutput, outName)
        writeImage(img, outPath)

        kept++
    }
}

println "Done! Tested tiles: ${tested} | Kept tiles (>= ${minTissueFraction}): ${kept}"
println "Exported to: " + pathOutput