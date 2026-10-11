import java.awt.image.BufferedImage
import java.nio.file.Files
import java.util.logging.Logger

import qupath.lib.images.servers.ImageServers
import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.images.servers.openslide.OpenslideServerBuilder
import qupath.lib.images.ImageData
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

def project_path_f = new File(args[0])
if (!project_path_f.isDirectory()){
    logger.severe("invalid project_path: ${project_path_f.path}")
    return
}
def project = Projects.createProject(project_path_f , BufferedImage.class)
def img_root_dir = project_path_f.getParent()
def image_name_to_orig = [:]
def image_names = []

args.eachWithIndex { item, index ->
    if(index == 0){
        return
    }
    def parts = item.split("---")

    def image_name = parts[0]
    def orig_name = parts[1]

    image_names << image_name

    logger.info("adding image: ${image_name} with orig_name: ${orig_name}")

    image_name_to_orig[image_name] = orig_name

    def imagePath = buildFilePath(img_root_dir, image_name)

    def imagePath_f = new File(imagePath)
    if (!imagePath_f.isFile()){
        logger.severe("invalid imagePath: ${imagePath_f.path}")
        return
    }

    def builder = null

    builder = ImageServers.buildServer(imagePath).getBuilder()

    // def image_uri = ImageServerProvider.legacyPathToURI(imagePath)
    // def server_builders = ImageServerProvider.getInstalledImageServerBuilders()
    // for (server_builder in server_builders){
    //     server_builder_name = server_builder.getName()
    //     logger.info("server_builder: ${server_builder_name}")
    //     def support = server_builder.checkImageSupport(image_uri, "")
    //     if (support == null) {
    //         logger.info("not supported")
    //     } else{
    //         builder = support.builders.get(0)
    //         break

    //         // if(server_builder_name == "OpenSlide builder"){
    //         //     builder = support.builders.get(0)
    //         //     break
    //         // }
    //         logger.info("supported")
    //     }
    // }

    // def image_path_as_uri = "file:${imagePath}"
    // def support = ImageServerProvider.getPreferredUriImageSupport(BufferedImage.class, image_path_as_uri, "")
    // if (support == null) {
    //     logger.severe("support is null: ${image_path_as_uri}")
    //     return
    // }
    // def builder = support.builders.get(0)

    // def builder = OpenslideServerBuilder().buildServer(image_uri)

    if (builder == null) {
        logger.severe("builder is null: ${image_path_as_uri}")
        return
    }

    project.addImage(builder)
    project.syncChanges()
}

for (idx, entry in project.getImageList()) {

    def wsi_filename = image_names[idx]
    def old_wsi_filename = entry.getImageName()
    def wsi_name = GeneralTools.stripExtension(wsi_filename)

    orig_name = image_name_to_orig[wsi_filename]

    logger.info("${old_wsi_filename} >> ${wsi_filename} (${orig_name})")
    // logger.info("wsi_name: ${wsi_name}")

    def imageData = entry.readImageData()
    def image_type = null

    if (wsi_name.endsWith("HE")){
        image_type =  ImageData.ImageType.valueOf("BRIGHTFIELD_H_E")
        logger.info("setting ${wsi_name} image type to H&E")
    } else {
        image_type =  ImageData.ImageType.valueOf("BRIGHTFIELD_H_DAB")
        logger.info("setting ${wsi_name} image type to H-DAB")
    }
    imageData.setImageType(image_type)
    entry.saveImageData(imageData)
    entry.setImageName(wsi_filename)
    entry.setDescription("original filename: ${orig_name}")

    project.syncChanges()
}
