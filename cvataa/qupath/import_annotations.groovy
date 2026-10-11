import qupath.lib.objects.PathObject
import qupath.lib.io.GsonTools
import com.google.gson.reflect.TypeToken
import com.google.gson.JsonParser
import static groovy.io.FileType.FILES

def file_ext = "svs"

def json_root_dir = '/mnt/NAS/NASIF/Nasif-3rd-batch/tiles_multiclass_regions'

def imageData = getCurrentImageData()
def server = imageData.getServer()

//def name = GeneralTools.getNameWithoutExtension(server.getMetadata().getName())

def wsi_path = server.getPath()
print "wsi file path: ${wsi_path}"

def names = wsi_path.split("[^A-Za-z0-9_ ]")
def ext_idx = names.findIndexOf {it==file_ext}
print "wsi file name: ${names}"
print "ext_idx: ${ext_idx}"

def name = names[ext_idx-1]
print "name: ${name}"

//def existingAnn = getAnnotationObjects()
//if (!existingAnn.isEmpty()) {
//    print "Skipping ${name}: ${existingAnn.size()} annotations already present."
//    return
//}

def json_dir_path = buildFilePath(json_root_dir, name)
def dir = new File(json_dir_path)
if (!dir.isDirectory()) {
    print "Directory not found: ${json_dir_path}"
    return
}

print "Looking for geojson files in ${json_dir_path}"


def gson = GsonTools.getInstance(true)
def type = new TypeToken<List<PathObject>>() {}.getType()

int total = 0
dir.eachFileRecurse(FILES) { file ->
    if (file.name.endsWith('.geojson')) {
        print "\nImporting from ${file}"
        file.withReader('UTF-8') { reader ->
            def element = JsonParser.parseReader(reader)
            // Unwrap FeatureCollection -> features array; bare array passes through
            def featuresEl = element.isJsonObject() ? element.getAsJsonObject().get('features') : element
            List<PathObject> objects = gson.fromJson(featuresEl, type)
            addObjects(objects)
            total += objects.size()
            print "\tImported ${objects.size()} objects"
        }
    }
}
resolveHierarchy()
fireHierarchyUpdate()

def entry = getProjectEntry()
if (entry != null) {
    entry.saveImageData(imageData)
    print "\nSaved ${total} objects to project entry: ${name}"
} else {
    print "\nNo project entry found — data NOT saved."
}