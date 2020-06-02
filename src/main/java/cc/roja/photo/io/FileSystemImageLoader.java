package cc.roja.photo.io;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.io.IOException;

import static java.lang.System.getenv;

class FileSystemImageLoader implements ImageLoader {
  private static final Logger LOG = LogManager.getLogger(FileSystemImageLoader.class);

  @Override
  public File load(String imageKey) throws IOException {
    if(imageKey == null || imageKey.isEmpty()) {
      throw new IOException("imageKey cannot be empty or null.");
    }
    String parentPath = getImageRoot();
    File imagePath = new File(parentPath, imageKey);
    LOG.info("imagePath: "+imagePath);
    return imagePath;
  }

  public String getImageRoot() {
    return getenv(ImageLoaderFactory.ENV_IMAGE_ROOT);
  }
}
