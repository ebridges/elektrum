package cc.roja.photo.io;

import cc.roja.photo.util.FilenameUtils;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.S3Object;
import org.apache.log4j.Logger;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

import static java.lang.System.getenv;

class S3ImageLoader implements ImageLoader {
  private static final Logger LOG = Logger.getLogger(S3ImageLoader.class);
  @Override
  public File load(String imageKey) throws IOException {
    // download from S3 & store in temp location
    String bucket = getenv(ImageLoaderFactory.ENV_BUCKET_NAME);
    String extension = FilenameUtils.getExtension(imageKey);
    Path tempfile = Files.createTempFile(bucket, extension);

    String prefixedKey = "photos/pictures" + imageKey;

    AmazonS3 s3Client = AmazonS3ClientBuilder.defaultClient();
    S3Object object = s3Client.getObject(bucket, prefixedKey);
    try (InputStream in = object.getObjectContent()) {
      Files.copy(in, tempfile, StandardCopyOption.REPLACE_EXISTING);
    }

    LOG.info("downloaded key: "+prefixedKey + " to " + tempfile);

    return tempfile.toFile();
  }
}
