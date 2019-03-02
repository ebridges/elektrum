package cc.roja.photo.io;

import static java.lang.System.getenv;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@SuppressWarnings("WeakerAccess")
public class ImageLoaderFactory {
  private static final Logger LOG = LogManager.getLogger(ImageLoaderFactory.class);

  static final String ENV_BUCKET_NAME = "BUCKET_NAME";
  static final String ENV_IMAGE_ROOT = "IMAGE_ROOT";

  public static ImageLoader getLoader() {
    if(getenv(ENV_BUCKET_NAME) != null) {
      LOG.info("Loading from S3 bucket named: " + getenv(ENV_BUCKET_NAME));
      return new S3ImageLoader();
    } else if(getenv(ENV_IMAGE_ROOT) != null) {
      LOG.info("Loading from filesystem location named: " + getenv(ENV_IMAGE_ROOT));
      return new FileSystemImageLoader();
    } else {
      throw new IllegalArgumentException("environment not configured correctly.");
    }
  }
}
