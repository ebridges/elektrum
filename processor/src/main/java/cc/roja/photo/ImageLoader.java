package cc.roja.photo;

import static java.lang.System.getenv;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import org.apache.log4j.Logger;

import cc.roja.photo.util.FilenameUtils;

@SuppressWarnings("WeakerAccess")
public class ImageLoader {
  private static final Logger LOG = Logger.getLogger(ImageLoader.class);

  public static File load(String imageKey) throws IOException {
    if(getenv("BUCKET_NAME") != null) {
      return loadFromS3(imageKey);
    } else if(getenv("IMAGE_ROOT") != null) {
      return loadFromFilesystem(imageKey);
    } else {
      throw new IllegalArgumentException("environment not configured correctly.");
    }
  }

  private static File loadFromFilesystem(String imageKey) {
    String parentPath = getenv("IMAGE_ROOT");
    File imagePath = new File(parentPath, imageKey);
    LOG.info("imagePath: "+imagePath);
    return imagePath;
  }

  private static File loadFromS3(String imageKey) throws IOException {
    // download from S3 & store in temp location
    String bucket = getenv("BUCKET_NAME");
    String extension = FilenameUtils.getExtension(imageKey);
    Path tempfile = Files.createTempFile(bucket, extension);
    // @todo write data from S3 to local tempfile.
    return tempfile.toFile();
  }
}
