package cc.roja.photo.metadata;

import cc.roja.photo.model.ImageInfo;
import cc.roja.photo.model.ImageKey;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;

import static javafx.scene.input.KeyCode.Z;
import static org.junit.jupiter.api.Assertions.*;

class MetaDataExtractorTest {

  @Test
  void testExtractMetadata() throws IOException {
    String imageIdentifier = "/2d249780-7fe9-4c49-aa31-0a30d56afa0f/2019/2019-02-24/2019-02-24T205115_4y5k48k7.jpg";
    ImageKey imageKey = new ImageKey();
    imageKey.parse(imageIdentifier);

    ImageInfo expected = new ImageInfo(imageKey.getFilePath());
    expected.setFileSize(3954388);
    expected.setCreateDate(LocalDateTime.parse("2019-02-24T20:51:15"));
    expected.setCameraMake("Google");
    expected.setCameraModel("Pixel 3");
    expected.setAperture("f/1.8");
    expected.setShutterSpeedNumerator(66683L);
    expected.setShutterSpeedDenominator(1000000L);
    expected.setIsoSpeed(1514);
    expected.setGpsLon(-73.9626138888889);
    expected.setGpsLat(40.718075);
    expected.setGpsAlt(0.0);
    expected.setGpsDatetime(OffsetDateTime.parse("2019-02-25T01:51:08Z"));
    expected.setImageWidth(4032);
    expected.setImageHeight(3024);
    expected.setFocalLengthNumerator(4440L);
    expected.setFocalLengthDenominator(1000L);

    File file = new File("src/test/resources/cc.roja.photo.metadata/testExtractMetadata/20190224T205115.jpg");

    MetaDataExtractor underTest = new MetaDataExtractor();
    ImageInfo actual = underTest.extract(imageKey, file);
    assertEquals(expected, actual);
  }

  @Test
  void testExtractMetadata_CreateDateFromFilename() throws IOException {
    File file = new File("src/test/resources/cc.roja.photo.metadata/testExtractMetadata_CreateDateFromFilename/20190224T205115.jpg");
    ImageKey imageKey = new ImageKey();

    MetaDataExtractor underTest = new MetaDataExtractor();
    ImageInfo actual = underTest.extract(imageKey, file);

    LocalDateTime expectedCreateDate = LocalDateTime.parse("2019-02-24T20:51:15");
    LocalDateTime actualCreateDate = actual.getCreateDate();

    assertEquals(expectedCreateDate, actualCreateDate);
  }

  @Test
  void testExtractMetadata_NotFound() {
    ImageKey imageKey = new ImageKey();
    File file = new File("/not/found");
    MetaDataExtractor underTest = new MetaDataExtractor();
    assertThrows(IOException.class, () -> { underTest.extract(imageKey, file); });
  }
}