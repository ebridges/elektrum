package cc.roja.photo.io;

import org.apache.log4j.Logger;

import java.io.File;
import java.io.IOException;

import static java.lang.System.getenv;

class FileSystemImageLoader implements ImageLoader {
  private static final Logger LOG = Logger.getLogger(FileSystemImageLoader.class);

  @SuppressWarnings("RedundantThrows")
  @Override
  public File load(String imageKey) throws IOException {
    if(imageKey == null || imageKey.isEmpty()) {
      throw new IOException("imageKey cannot be empty or null.");
    }
    String parentPath = getenv(ImageLoaderFactory.ENV_IMAGE_ROOT);
    File imagePath = new File(parentPath, imageKey);
    LOG.info("imagePath: "+imagePath);
    return imagePath;
  }
}
