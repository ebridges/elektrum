package cc.roja.photo.io;

import org.junit.Rule;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import org.junit.contrib.java.lang.system.EnvironmentVariables;

import java.io.File;
import java.io.IOException;

import static cc.roja.photo.io.ImageLoaderFactory.ENV_IMAGE_ROOT;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class FileSystemImageLoaderTest {
  private final static String IMAGE_ROOT = "abcd";

  @Rule
  private final EnvironmentVariables environmentVariables = new EnvironmentVariables();

  @BeforeEach
  void setEnvironmentVariables() {
    environmentVariables.set(ENV_IMAGE_ROOT, IMAGE_ROOT);
  }

  @Test
  void testLoad() throws IOException {
    String imageKey = "efgh";
    File expectedFile = new File(IMAGE_ROOT, imageKey);
    FileSystemImageLoader underTest = new FileSystemImageLoader();
    File actualFile = underTest.load(imageKey);
    assertEquals(expectedFile, actualFile);
  }

  @Test
  void testLoad_MissingEnvVar() throws IOException {
    environmentVariables.clear(ENV_IMAGE_ROOT);
    String imageKey = "efgh";
    File expectedFile = new File(imageKey);
    FileSystemImageLoader underTest = new FileSystemImageLoader();
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
