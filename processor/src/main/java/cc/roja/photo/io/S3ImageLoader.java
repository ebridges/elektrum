package cc.roja.photo.io;

import cc.roja.photo.util.FilenameUtils;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.S3Object;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

import static cc.roja.photo.io.ImageLoaderFactory.ENV_BUCKET_NAME;
import static java.lang.System.getenv;

class S3ImageLoader implements ImageLoader {
  private static final Logger LOG = LogManager.getLogger(S3ImageLoader.class);

  private AmazonS3 s3Client;

  S3ImageLoader() {
    this(AmazonS3ClientBuilder.defaultClient());
  }

  // For testing
  S3ImageLoader(AmazonS3 s3Client) {
    this.s3Client = s3Client;
  }

  @Override
  public File load(String imageKey) throws IOException {
    if(imageKey == null || imageKey.isEmpty()) {
      throw new IOException("imageKey cannot be empty or null.");
    }

    // download from S3 & store in temp location
    String bucket = getenv(ENV_BUCKET_NAME);
    if(bucket == null || bucket.isEmpty()) {
      throw new IOException("bucket name not configured under env var ["+ENV_BUCKET_NAME+"]");
    }
    String extension = FilenameUtils.getExtension(imageKey);
    Path tempfile = Files.createTempFile(bucket, extension);

    S3Object object = s3Client.getObject(bucket, imageKey);
    try (InputStream in = object.getObjectContent()) {
      Files.copy(in, tempfile, StandardCopyOption.REPLACE_EXISTING);
    }

    LOG.info("downloaded key: "+imageKey + " to " + tempfile);

    return tempfile.toFile();
  }
}
