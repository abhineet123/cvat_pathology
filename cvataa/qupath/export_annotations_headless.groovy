import java.awt.image.BufferedImage
import java.nio.file.Files
import java.util.logging.Logger

import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.io.PathIO;

def out_dir_name = "annotations"
def out_ext = ".geojson.gz"
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
def wsi = new File(args[1])
def wsi_name = GeneralTools.stripExtension(wsi.name)

logger.info("wsi_path: ${wsi.path}")
logger.info("wsi_name: ${wsi_name}")


if (project_path.isDirectory()){
    project_path = new File(buildFilePath(project_path.path, project_name))
} else if(!project_path.isFile()){
    logger.severe("invalid project_path: ${project_path}")
    return 1
}

def project_dir = project_path.getParent()
def out_path = null
if (args.size() > 2){
    out_path = args[2]
} else {
    out_path = buildFilePath(project_dir, out_dir_name, wsi_name + out_ext)
}


logger.info("project_path: ${project_path.path}")
logger.info("project_dir: ${project_dir}")

def project = ProjectIO.loadProject(project_path , BufferedImage.class)
def annotations = null
for (entry in project.getImageList()) {
    def qp_filename = entry.getImageName()
    def qp_name = GeneralTools.stripExtension(wsi_filename)

    if (qp_name.toLowerCase() != wsi_name.toLowerCase()){
        continue
    }

    logger.info("exporting annotations to: ${out_path}")

    def imageData = entry.readImageData()
    annotations = imageData.getHierarchy().getAnnotationObjects();
    if (annotations.isEmpty()) {
        logger.severe("No annotations exist for this wsi")
        return 1
    }

    def out_file = new File(out_path)

    PathIO.exportObjectsAsGeoJSON(out_file, annotations, PathIO.GeoJsonExportOptions.FEATURE_COLLECTION);
}

if (annotations == null){
    logger.severe("wsi not found in project")
    return 1
}

return 0



