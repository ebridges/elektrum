package cc.roja.photo.util;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.*;

class FilenameUtilsTest {

  @ParameterizedTest
  @CsvSource({
      "foo.txt, txt",
      "a/b/c.jpg, jpg",
      "foo.jpeg, jpeg",
      "a/b.txt/c,''",
      "a/b/c,''",
  })
  void testGetExtension(String testCase, String extension) {
    String expectedExtension = extension == null ? "" : extension;
    String actualExtension = FilenameUtils.getExtension(testCase);
    assertEquals(expectedExtension, actualExtension);
  }

  @Test
  void testGetExtension_NullFilename() {
    assertNull(FilenameUtils.getExtension(null));
  }
}