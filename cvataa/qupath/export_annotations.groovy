// Run this once per image in QuPath to export annotations as GeoJSON
import qupath.lib.io.GsonTools

def imageData = getCurrentImageData()
def server    = imageData.getServer()
def name      = GeneralTools.getNameWithoutExtension(server.getMetadata().getName())

def outPath = buildFilePath(PROJECT_BASE_DIR, "annotations", name + "_annotations.geojson")
mkdirs(buildFilePath(PROJECT_BASE_DIR, "annotations"))

def annotations = imageData.getHierarchy().getAnnotationObjects()
def gson = GsonTools.getInstance(true)

new File(outPath).text = gson.toJson(annotations)
println "Saved ${annotations.size()} annotations to: ${outPath}"