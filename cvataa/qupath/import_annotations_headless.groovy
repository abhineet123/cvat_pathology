import java.awt.image.BufferedImage
import java.nio.file.Files
import java.util.logging.Logger

import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.io.PathIO;

def wsi_ext = "svs"
def dets_dir = "detections"
def project_name = "project.qpproj"

System.setProperty("java.util.logging.SimpleFormatter.format",
 '%1$tY-%1$tm-%1$td %1$tH:%1$tM:%1$tS %4$-6s %5$s%6$s%n');
Logger logger = Logger.getLogger("")
if (args.size() < 1){
    logger.severe("project_path must be provided")
    return
}
def project_path = new File(args[0])

if (args.size() < 2){
    logger.severe("wsi_path must be provided")
    return
}
def dst_wsi = new File(args[1])
def dst_wsi_name = dst_wsi.name

logger.info("dst_wsi_path: ${dst_wsi.path}")
logger.info("dst_wsi_name: ${dst_wsi_name}")


if (project_path.isDirectory()){
    project_path = new File(buildFilePath(project_path.path, project_name))
} else if(!project_path.isFile()){
    logger.severe("invalid project_path: ${project_path}")
    return
}

def project_dir = project_path.getParent()

def json_root_dir = buildFilePath(project_dir, dets_dir)

logger.info("project_path: ${project_path.path}")
logger.info("project_dir: ${project_dir}")
logger.info("json_root_dir: ${json_root_dir}")

def project = ProjectIO.loadProject(project_path , BufferedImage.class)

for (entry in project.getImageList()) {
    """Get a path to the data for this image entry,
    or null if this entry is not stored on the local file system."""
    // def wsi_path = entry.getEntryPath()

    def wsi_filename = entry.getImageName()
    def wsi_name = GeneralTools.stripExtension(wsi_filename)

    // logger.info("wsi_filename: ${wsi_filename}")
    // logger.info("wsi_name: ${wsi_name}")

    if (wsi_filename.toLowerCase() != dst_wsi_name.toLowerCase()){
        continue
    }

    def uris = entry.getURIs()
    def replacements = new HashMap<URI, URI>()

    uris.each{
        def path = it.getPath()
        logger.info("path: ${path}")

        name = new File(path).name
        if (name == dst_wsi_name){
            path = dst_wsi.path
        }
        def newUri = new URI(it.getScheme(),
                            it.getUserInfo(),
                            it.getHost(),
                            it.getPort(),
                            path,
                            it.getQuery(),
                            it.getFragment()
                            )
        replacements.put( it, newUri )
    }
    replacements.each{ k, v ->
        println "    Original: $k"
        println "    -----> Modified: $v"

    }
    entry.updateURIs( replacements )
    project.syncChanges()

    logger.info("\n")
    def imageData = entry.readImageData()
    // def server = imageData.getServer()

    // if ((args.size() > 1) && !(name.endsWith(args[1]))){
    //     logger.info("skipping: ${name} since it does not end with ${args[1]}")
    //     continue
    // }

    def json_path = buildFilePath(json_root_dir, wsi_name + ".geojson.gz")
    def json_file = new File(json_path)
    if (!json_file.isFile()) {
        logger.severe("json_file not found: ${json_file}")
        return
    }
    logger.info("loading detections from: ${json_path}")
    List<PathObject> objects = PathIO.readObjects(json_file);

    logger.info("importing ${objects.size()} detections...")
    imageData.getHierarchy().addObjects(objects);

    entry.saveImageData(imageData);
    project.syncChanges()
}
