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
  private String imageKey;

  public ImageLoader(String imageKey) {
    this.imageKey = imageKey;
  }

  public File load() throws IOException {
    if(getenv("BUCKET_NAME") != null) {
      return loadFromS3();
    } else if(getenv("IMAGE_ROOT") != null) {
      return loadFromFilesystem();
    } else {
      throw new IllegalArgumentException("environment not configured correctly.");
    }
  }

  private File loadFromFilesystem() {
    String parentPath = getenv("IMAGE_ROOT");
    File imagePath = new File(parentPath, this.imageKey);
    LOG.info("imagePath: "+imagePath);
    return imagePath;
  }

  private File loadFromS3() throws IOException {
    // download from S3 & store in temp location
    String bucket = getenv("BUCKET_NAME");
    String extension = FilenameUtils.getExtension(imageKey);
    Path tempfile = Files.createTempFile(bucket, extension);
    // @todo write data from S3 to local tempfile.
    return tempfile.toFile();
  }
}
