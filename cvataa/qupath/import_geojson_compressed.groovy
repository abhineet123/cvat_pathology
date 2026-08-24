import java.util.zip.GZIPInputStream

import qupath.lib.objects.PathAnnotationObject
import qupath.lib.io.GsonTools
import com.google.gson.reflect.TypeToken

import static groovy.io.FileType.FILES

//def json_root_dir = "/data/PDL1-2026-Detections/NSCLC-B/cellpose-dino"
def json_root_dir = '/data/BreastCancerWSIs-Detections/OCTOBER_2024/cellpose-dino'
//def json_dir_path = "/data/PDL1-2026-Detections/TNBC-D/cellvit-sam-nucls_super/D3_HE"
//def json_dir_path = "/data/PDL1-2026-Detections/TNBC-D/cellvit-sam-nucls_super/D9_HE"
//def json_dir_path = "/data/PDL1-2026-Detections/TNBC-D/cellvit-sam-nucls_super/D3"
// def json_dir_path = "/data/PDL1-2026-Detections/TNBC-D/cellvit-sam-nucls_super/D5"
//def json_dir_path = "/data/PDL1-2026-Detections/TNBC-D/cellvit-sam-nucls_super/D9"

def imageData = getCurrentImageData()
def server = imageData.getServer()
def name = GeneralTools.getNameWithoutExtension(server.getMetadata().getName())
def json_dir_path = buildFilePath(json_root_dir,  name)

new File(json_dir_path).eachFileRecurse(FILES) {
    if(it.name.endsWith('.geojson.gz')) {
        print("\nImporting from ${it}")

//        def json = new File(it).text

        InputStream fileStream = new FileInputStream(it);
        InputStream gzipStream = new GZIPInputStream(fileStream);
        Reader decoder = new InputStreamReader(gzipStream, 'ascii');
        BufferedReader json = new BufferedReader(decoder);


        def gson = GsonTools.getInstance(true)

        def type = new TypeToken<List<PathAnnotationObject>>() {}.getType()
        List<PathAnnotationObject> annotations = gson.fromJson(json, type)

        //def type = new com.google.gson.reflect.TypeToken<List<qupath.lib.objects.PathObject>>() {}.getType()
        //def annotations = gson.fromJson(buffered, type)

        //def imageData = getCurrentImageData()
        //def hierarchy = imageData.getHierarchy()
        //hierarchy.addPathObjects(annotations)

        addObjects(annotations)

        print("\tImported ${annotations.size()} annotations successfully!")
    }
}


