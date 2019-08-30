package cc.roja.photo.model;

import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ImageKeyTest {

  @Test
  void testParse_Success() {
    String testCase = "2d249780-7fe9-4c49-aa31-0a30d56afa0f/b7556920-7009-11e9-b91d-320017981ea0.jpg";
    ImageKey underTest = ImageKey.parse(testCase);

    assertEquals(testCase, underTest.getKey());
    assertEquals(testCase, underTest.toString());
    assertEquals(UUID.fromString("2d249780-7fe9-4c49-aa31-0a30d56afa0f"), underTest.getUserId());
    assertEquals(UUID.fromString("b7556920-7009-11e9-b91d-320017981ea0"), underTest.getImageId());
    assertEquals("b7556920-7009-11e9-b91d-320017981ea0.jpg", underTest.getFilename());
  }

  @Test
  void testParse_Failure() {
    String testCase = "foobar";
    assertThrows(IllegalArgumentException.class, () -> ImageKey.parse(testCase));
  }
}