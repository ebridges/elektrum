package cc.roja.photo.io;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.S3Object;
import org.junit.Rule;
import org.junit.contrib.java.lang.system.EnvironmentVariables;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import static cc.roja.photo.io.ImageLoaderFactory.ENV_BUCKET_NAME;
import static java.lang.System.getenv;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class S3ImageLoaderTest {
  private final static String BUCKET_NAME = "cc.roja.photo.io";

  @Rule
  private final EnvironmentVariables environmentVariables = new EnvironmentVariables();

  @BeforeEach
  void setEnvironmentVariables() {
    environmentVariables.set(ENV_BUCKET_NAME, BUCKET_NAME);
    environmentVariables.set("AWS_REGION", "foobar");
  }

  @Test
  void testLoad() throws IOException {
    String imageKey = "S3ImageLoaderTest_testLoad.txt";
    InputStream inputStream = getClass().getResourceAsStream(objectName(imageKey));

    AmazonS3 mockClient = buildMockS3Client(inputStream, imageKey);

    S3ImageLoader underTest = new S3ImageLoader(mockClient);
    File actual = underTest.load(imageKey);
    File expected = new File("src/test/resources", objectName(imageKey));
    assertNotNull(actual);
    assertTrue(actual.exists());
    assertThat(actual)
        .hasSameContentAs(expected);
  }

  @Test
  void testLoad_MissingEnvVar() {
    environmentVariables.clear(ENV_BUCKET_NAME);
    S3ImageLoader underTest = new S3ImageLoader();
    assertThrows(IOException.class, () -> underTest.load("abcd"));
  }

  @Test
  void testLoad_Null() {
    S3ImageLoader underTest = new S3ImageLoader();
    assertThrows(IOException.class, () -> underTest.load(null));
  }

  @Test
  void testLoad_Empty() {
    S3ImageLoader underTest = new S3ImageLoader();
    assertThrows(IOException.class, () -> underTest.load(""));
  }

  private AmazonS3 buildMockS3Client(InputStream inputStream, String imageKey) {
    AmazonS3 mockClient = mock(AmazonS3.class);
    S3Object fakeObject = new S3Object();
    fakeObject.setObjectContent(inputStream);
    String bucket = getenv(ImageLoaderFactory.ENV_BUCKET_NAME);
    when(mockClient.getObject(bucket, imageKey))
        .thenReturn(fakeObject);
    return mockClient;
  }

  private String objectName(String key) {
    return "/" + BUCKET_NAME + "/" + key;
  }
}
