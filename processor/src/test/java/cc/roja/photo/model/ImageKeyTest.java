package cc.roja.photo.model;

import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ImageKeyTest {

  @Test
  void testParse_Success() {
    String testCase = "/2d249780-7fe9-4c49-aa31-0a30d56afa0f/2020/2020-02-26/2020-02-26T000000_4y5k48k7.jpg";
    ImageKey underTest = new ImageKey();

    underTest.parse(testCase);

    assertEquals(testCase, underTest.getKey());
    assertEquals(testCase, underTest.toString());
    assertEquals(UUID.fromString("2d249780-7fe9-4c49-aa31-0a30d56afa0f"), underTest.getUserId());
    assertEquals("/2020/2020-02-26/2020-02-26T000000_4y5k48k7.jpg", underTest.getFilePath());
    assertEquals("2020-02-26T000000_4y5k48k7.jpg", underTest.getFilename());
  }

  @Test
  void testParse_Failure() {
    String testCase = "foobar";
    ImageKey underTest = new ImageKey();
    assertThrows(IllegalArgumentException.class, () -> underTest.parse(testCase));
  }
}