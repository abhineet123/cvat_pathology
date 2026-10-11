import java.util.zip.GZIPInputStream

import qupath.lib.objects.PathAnnotationObject
import qupath.lib.io.GsonTools
import com.google.gson.reflect.TypeToken

import static groovy.io.FileType.FILES

def json_dir_path = "C:/Datasets/PDL1-2026-Detections/NSCLC-B/cellvit-sam-nucls_super/B3"

new File(json_dir_path).eachFileRecurse(FILES) {
    if(it.name.endsWith('.geojson.gz')) {
        print("\nImporting from ${it}")

//        def json = new File(it).text

        InputStream fileStream = new FileInputStream(it);
        Reader decoder = new InputStreamReader(fileStream, 'ascii');
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


