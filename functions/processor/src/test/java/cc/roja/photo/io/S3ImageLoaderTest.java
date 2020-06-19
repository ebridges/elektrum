package cc.roja.photo.io;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.DisabledIfEnvironmentVariable;
import software.amazon.awssdk.core.ResponseInputStream;
import software.amazon.awssdk.http.AbortableInputStream;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import static cc.roja.photo.io.ImageLoaderFactory.ENV_BUCKET_NAME;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.isA;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

class S3ImageLoaderTest {
  private final static String BUCKET_NAME = "cc.roja.photo.io";


  @Test
  void testLoad() throws Exception {
    String imageKey = "S3ImageLoaderTest_testLoad.txt";
    InputStream inputStream = getClass().getResourceAsStream(objectName(imageKey));
    GetObjectRequest mockRequest = mock(GetObjectRequest.class);
    when(mockRequest.bucket()).thenReturn(BUCKET_NAME);
    when(mockRequest.key()).thenReturn(imageKey);

    ResponseInputStream<GetObjectResponse> mockResponse = new ResponseInputStream<>(GetObjectResponse.builder().build(), AbortableInputStream.create(inputStream));

    S3Client mockClient = mock(S3Client.class);
    when(mockClient.getObject(mockRequest)).thenReturn(mockResponse);

    S3ImageLoader underTest = spy(S3ImageLoader.class);
    doReturn(mockClient).when(underTest).buildS3Client(isA(Region.class));
    doReturn(mockRequest).when(underTest).buildRequest(isA(String.class));

    File actual = underTest.load(imageKey);
    File expected = new File("src/test/resources", objectName(imageKey));
    assertNotNull(actual);
    assertTrue(actual.exists());
    assertThat(actual)
        .hasSameContentAs(expected);
  }

  @Test
  // disabled when running integration tests, as the env var is necessary for that
  @DisabledIfEnvironmentVariable(named = ENV_BUCKET_NAME, matches = ".*integration.*")
  void testLoad_MissingEnvVar() {
    S3ImageLoader underTest = spy(new S3ImageLoader());
    assertThrows(IllegalStateException.class, () -> underTest.load("abcd"));
  }

  @Test
  void testLoad_ImageKeyNull() {
    S3ImageLoader underTest = new S3ImageLoader();
    assertThrows(IOException.class, () -> underTest.load(null));
  }

  @Test
  void testLoad_ImageKeyEmpty() {
    S3ImageLoader underTest = new S3ImageLoader();
    assertThrows(IOException.class, () -> underTest.load(""));
  }

  private String objectName(String key) {
    return "/" + BUCKET_NAME + "/" + key;
  }
}
