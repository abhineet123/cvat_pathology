import java.awt.image.BufferedImage
import java.nio.file.Files
import java.util.logging.Logger

import qupath.lib.images.servers.ImageServerProvider
import qupath.lib.io.PathIO;
import qupath.lib.images.ImageData

import java.text.SimpleDateFormat

def project_name = "project.qpproj"

System.setProperty("java.util.logging.SimpleFormatter.format",
 '%1$tY-%1$tm-%1$td %1$tH:%1$tM:%1$tS %4$-6s %5$s%6$s%n');
Logger logger = Logger.getLogger("")
if (args.size() < 1){
    logger.severe("project_path must be provided")
    return 1
}
def project_path = new File(args[0])

if (args.size() < 2){
    logger.severe("shared_root must be provided")
    return 1
}
def shared_root = args[1]

if (args.size() < 3){
    logger.severe("local_root must be provided")
    return 1
}
def local_root = args[2]

logger.info("shared_root: ${shared_root}")
logger.info("local_root: ${local_root}")


def rename_local_file(src_path, dst_path, shared_root, local_root){

    def local_src_path = src_path.replace(shared_root, local_root)
    def local_dst_path = dst_path.replace(shared_root, local_root)

    def src_file = new File(local_src_path)
    def dst_file = new File(local_dst_path)

    logger.info("rename:\n\t${src_file.path}\n\t${dst_file.path}\n")

    src_file.renameTo(dst_file)

}

def rename_file(src_path, dst_path){
    def src_file = new File(src_path)
    def dst_file = new File(dst_path)

    logger.info("rename:\n\t${src_file.path}\n\t${dst_file.path}")

    src_file.renameTo(dst_file)

}
def rename_file_to_temp(file_path){

    def timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date())

    def wsi_file = new File(file_path)
    def wsi_dir = wsi_file.parent
    def wsi_name = GeneralTools.stripExtension(wsi_file.name)
    def wsi_ext = wsi_file.extension

    def temp_path = "${file_path}-${timestamp}"

    def src_file = new File(file_path)
    def temp_file = new File(temp_path)

    logger.info("rename:\n\t${src_file.path}\n\t${temp_file.path}")

    src_file.renameTo(temp_file)

    return temp_path
}
def sync_uri(project, entry, dst_path){
    def uri = entry.getURIs()[0]
    def replacements = new HashMap<URI, URI>()
    def image_type = null
    def src_path = uri.getPath()
    if (src_path == dst_path){
        return
    }

    def description = entry.getDescription()

    logger.info("updating uri:\n\t${src_path}\n\t${dst_path}")

    def src_name = GeneralTools.stripExtension(new File(src_path).name)
    def dst_name = GeneralTools.stripExtension(new File(dst_path).name)

    def timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date())

    description = "${description}\n${timestamp} :: image URI changed from:\n${src_path}\nto\n${dst_path}"

    if(src_name.endsWith("-HE")){
        """old image was added as H&E and needs to be changed to H-DAB"""
        image_type =  ImageData.ImageType.valueOf("BRIGHTFIELD_H_DAB")
        logger.info("changing image type to H-DAB")
        description = "${description}\n${timestamp} :: image type changed from H&E to H-DAB"

    } else if (dst_name.endsWith("-HE")){
        """old image was added as H-DAB and needs to be changed to H&E"""
        image_type =  ImageData.ImageType.valueOf("BRIGHTFIELD_H_E")
        logger.info("changing image type to H&E")
        description = "${description}\n${timestamp} :: image type changed from H-DAB to H&E"
    }
    def newUri = new URI(uri.getScheme(),
                        uri.getUserInfo(),
                        uri.getHost(),
                        uri.getPort(),
                        dst_path,
                        uri.getQuery(),
                        uri.getFragment()
                        )
    replacements.put(uri, newUri)
    entry.updateURIs(replacements)
    if(image_type){
        def imageData = entry.readImageData()
        imageData.setImageType(image_type)
        entry.saveImageData(imageData);
    }
    entry.setDescription(description)
    project.syncChanges()
}

def swapFileNames(src_path, dst_path){
    def dst_file = new File(dst_path)
    def src_file = new File(src_path)

    if (!src_file.exists()){
        logger.error("nonexistent src_path: ${src_path}")
        return
    }

    def temp_path = null
    if (dst_file.exists()){
        def timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date())

        temp_path = "${dst_path}-${timestamp}"

        def temp_file = new File(temp_path)

        logger.info("rename: ${dst_file.name} >> ${temp_file.name}")
        dst_file.renameTo(temp_file)

    }
    dst_file = new File(dst_path)
    logger.info("rename: ${src_file.name} >> ${dst_file.name}")
    src_file.renameTo(dst_file)

    if(temp_path){
        src_file = new File(src_path)
        def temp_file = new File(temp_path)
        logger.info("rename: ${temp_file.name} >> ${src_file.name}")
        temp_file.renameTo(src_file)
    }
}

def swapURIs(project, path1, path2){
    for (entry in project.getImageList()) {
        def uris = entry.getURIs()
        def replacements = new HashMap<URI, URI>()

        def src_path = null
        def dst_path = null

        uris.each{
            def path = it.getPath()
            if (path == path1){
                src_path = path1
                dst_path = path2

            } else if (path == path2){
                src_path = path2
                dst_path = path1

            }
            if (src_path && dst_path){
                logger.info("updating uri:\n\t${src_path}\n\t${dst_path}\n")

                def description = entry.getDescription()

                path = dst_path

                def src_name = GeneralTools.stripExtension(new File(src_path).name)
                def dst_name = GeneralTools.stripExtension(new File(dst_path).name)

                def timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date())

                description = "${description}\n${timestamp} :: image name changed from ${src_name} to ${dst_name}"

                def image_type = null
                if(src_name.endsWith("-HE")){
                    """old image was added as H&E and needs to be changed to H-DAB"""
                    image_type =  ImageData.ImageType.valueOf("BRIGHTFIELD_H_DAB")
                    logger.info("changing image type to H-DAB")
                    description = "${description}\n${timestamp} :: image type changed from H&E to H-DAB"

                } else if (dst_name.endsWith("-HE")){
                    """old image was added as H-DAB and needs to be changed to H&E"""
                    image_type =  ImageData.ImageType.valueOf("BRIGHTFIELD_H_E")
                    logger.info("changing image type to H&E")
                    description = "${description}\n${timestamp} :: image type changed from H-DAB to H&E"
                }
                if(image_type){
                    def imageData = entry.readImageData()
                    imageData.setImageType(image_type)
                    entry.saveImageData(imageData);
                }
                entry.setDescription(description)
                project.syncChanges()
            }
            // def newUri = new URI(it.getScheme(),
            //                     it.getUserInfo(),
            //                     it.getHost(),
            //                     it.getPort(),
            //                     path,
            //                     it.getQuery(),
            //                     it.getFragment()
            //                     )
            // replacements.put( it, newUri )
        }

        if (src_path && dst_path){
            // replacements.each{ k, v ->
            //     println "    Original: $k"
            //     println "    -----> Modified: $v"
            // }
            // entry.updateURIs(replacements)
            project.syncChanges()
        }
    }
}


if (project_path.isDirectory()){
    project_path = new File(buildFilePath(project_path.path, project_name))
} else if(!project_path.isFile()){
    logger.severe("invalid project_path: ${project_path}")
    return
}

def project_dir = project_path.getParent()

logger.info("project_path: ${project_path.path}")
logger.info("project_dir: ${project_dir}")

def project = ProjectIO.loadProject(project_path , BufferedImage.class)

// def wsi_path_to_qp_name = [:]
// def wsi_path_to_entry = [:]
def qp_name_to_entry = [:]
def qp_name_to_temp_path = [:]
def qp_name_to_dst_path = [:]

def found_mismatch = false

for (entry in project.getImageList()) {
    logger.info("\n")
    def qp_img_filename = entry.getImageName()
    def qp_name = GeneralTools.stripExtension(qp_img_filename)

    def imageData = entry.readImageData()
    def server = imageData.getServer()

    def uri = server.getBuilder().getURIs()[0]
    def wsi_path = java.nio.file.Paths.get(uri).toString()

    def wsi_file = new File(wsi_path)
    def wsi_dir = wsi_file.parent
    def wsi_name = GeneralTools.stripExtension(wsi_file.name)
    def wsi_ext = wsi_file.extension
    def dst_path = buildFilePath(wsi_dir, "${qp_name}.${wsi_ext}")

    temp_path = rename_file_to_temp(wsi_path)
    rename_local_file(wsi_path, temp_path, shared_root, local_root)

    if (qp_name != wsi_name){
        logger.info("found_mismatch: ${qp_name} >> ${wsi_name}")
        logger.info("wsi_path: ${wsi_path}")
        logger.info("wsi_ext: ${wsi_ext}")
        logger.info("temp_path: ${temp_path}")

        found_mismatch = true
    }

    // wsi_path_to_qp_name[temp_path] = qp_name
    // wsi_path_to_entry[temp_path] = entry

    qp_name_to_entry[qp_name] = entry
    qp_name_to_dst_path[qp_name] = dst_path
    qp_name_to_temp_path[qp_name] = temp_path
}

if(!found_mismatch){
    return 0
}

qp_name_to_entry.each { qp_name, entry ->
    temp_path = qp_name_to_temp_path[qp_name]
    dst_path = qp_name_to_dst_path[qp_name]
    entry = qp_name_to_entry[qp_name]

    rename_file(temp_path, dst_path)
    sync_uri(project, entry, dst_path)

    rename_local_file(temp_path, dst_path, shared_root, local_root)

    // swapURIs(project, wsi_file.path, dst_wsi_file.path)

}

return 0
