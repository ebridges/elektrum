package cc.roja.photo.io;

import static java.lang.System.getenv;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

import org.apache.log4j.Logger;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.S3Object;

import cc.roja.photo.util.FilenameUtils;

@SuppressWarnings("WeakerAccess")
public class ImageLoaderFactory {
  private static final Logger LOG = Logger.getLogger(ImageLoaderFactory.class);

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
