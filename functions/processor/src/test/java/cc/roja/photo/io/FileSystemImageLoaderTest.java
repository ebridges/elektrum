package cc.roja.photo.io;

import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

class FileSystemImageLoaderTest {
  private final static String IMAGE_ROOT = "abcd";

  @Test
  void testLoad() throws IOException {
    String imageKey = "efgh";
    File expectedFile = new File(IMAGE_ROOT, imageKey);
    FileSystemImageLoader underTest = spy(new FileSystemImageLoader());
    when(underTest.getImageRoot()).thenReturn(IMAGE_ROOT);
    File actualFile = underTest.load(imageKey);
    assertEquals(expectedFile, actualFile);
  }

  @Test
  void testLoad_MissingEnvVar() throws IOException {
    String imageKey = "efgh";
    File expectedFile = new File(imageKey);
    FileSystemImageLoader underTest = spy(new FileSystemImageLoader());
    when(underTest.getImageRoot()).thenReturn(null);
    File actualFile = underTest.load(imageKey);
    assertEquals(expectedFile, actualFile);
  }

  @Test
  void testLoad_Null() {
    FileSystemImageLoader underTest = new FileSystemImageLoader();
    assertThrows(IOException.class, () -> underTest.load(null));
  }

  @Test
  void testLoad_Empty() {
    FileSystemImageLoader underTest = new FileSystemImageLoader();
    assertThrows(IOException.class, () -> underTest.load(""));
  }
}
