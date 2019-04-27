package cc.roja.photo.io;

import cc.roja.photo.util.FilenameUtils;
import software.amazon.awssdk.core.ResponseInputStream;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.core.sync.ResponseTransformer;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static java.lang.System.getenv;
import static java.nio.file.StandardCopyOption.REPLACE_EXISTING;
import static cc.roja.photo.io.ImageLoaderFactory.ENV_BUCKET_NAME;

class S3ImageLoader implements ImageLoader {
  private static final Logger LOG = LogManager.getLogger(S3ImageLoader.class);
  private static final Region DEFAULT_REGION = Region.US_EAST_1;

  @Override
  public File load(String imageKey) throws IOException {
    if(imageKey == null || imageKey.isEmpty()) {
      throw new IOException("imageKey cannot be empty or null.");
    }

    // download from S3 & store in temp location
    String extension = FilenameUtils.getExtension(imageKey);
    Path temppath = Files.createTempFile(S3ImageLoader.class.getSimpleName(), '.'+extension);
    File tempfile = temppath.toFile();
    tempfile.deleteOnExit();

    S3Client s3Client = buildS3Client(DEFAULT_REGION);

    s3Client.getObject(
        buildRequest(imageKey),
        ResponseTransformer.toFile(tempfile)
    );

    GetObjectRequest getObjectRequest = buildRequest(imageKey);
    ResponseInputStream<GetObjectResponse> response = s3Client.getObject(getObjectRequest);
    Files.copy(response, temppath, REPLACE_EXISTING);

    LOG.info("downloaded key: "+imageKey + " to " + tempfile);

    return tempfile;
  }

  S3Client buildS3Client(Region region) {
    return S3Client.builder().region(region).build();
  }

  GetObjectRequest buildRequest(String key) {
    String bucket = getBucketName();
    return GetObjectRequest.builder()
        .bucket(bucket)
        .key(key)
        .build();
  }

  String getBucketName() {
    String bucket = getenv(ENV_BUCKET_NAME);
    if(bucket == null || bucket.isEmpty()) {
      throw new IllegalStateException("bucket name not configured under env var ["+ENV_BUCKET_NAME+"]");
    }
    return bucket;
  }
}
