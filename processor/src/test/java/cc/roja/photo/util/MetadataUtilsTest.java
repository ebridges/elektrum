package cc.roja.photo.util;

import com.drew.lang.Rational;
import com.drew.metadata.Directory;
import com.drew.metadata.Metadata;
import com.sun.tools.javac.util.List;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.time.temporal.TemporalAccessor;
import java.util.Collection;

import static cc.roja.photo.util.MetadataUtils.getDirectory;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class MetadataUtilsTest {

  static class Mocks {
    Directory directory;
    Metadata metadata;
  }

  @Test
  void testResolveInteger() {
    int tag = 999;
    int expectedTagValue = 888;
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getInteger(tag)).thenReturn(expectedTagValue);

    Integer actualTagValue = MetadataUtils.resolveInteger(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertEquals(expectedTagValue, actualTagValue);
  }

  @Test
  void testResolveString() {
    int tag = 999;
    String expectedTagValue = "yuckyuckyuck";
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getString(tag)).thenReturn(expectedTagValue);

    String actualTagValue = MetadataUtils.resolveString(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertEquals(expectedTagValue, actualTagValue);
  }

  @Test
  void testResolveStringWhenNull() {
    int tag = 999;
    String expectedTagValue = "yuckyuckyuck";
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getString(tag)).thenReturn(null);
    when(mock.directory.getDescription(tag)).thenReturn(expectedTagValue);

    String actualTagValue = MetadataUtils.resolveString(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertEquals(expectedTagValue, actualTagValue);
  }

  @Test
  void testResolveStringWhenEmpty() {
    int tag = 999;
    String expectedTagValue = "yuckyuckyuck";
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getString(tag)).thenReturn("");
    when(mock.directory.getDescription(tag)).thenReturn(expectedTagValue);

    String actualTagValue = MetadataUtils.resolveString(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertEquals(expectedTagValue, actualTagValue);
  }

  @Test
  void testResolveDescription() {
    int tag = 999;
    String expectedTagValue = "yuckyuckyuck";
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getDescription(tag)).thenReturn(expectedTagValue);

    String actualTagValue = MetadataUtils.resolveDescription(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertEquals(expectedTagValue, actualTagValue);
  }

  @Test
  void testResolveDate() {
    int tag = 999;
    String tagValue = "2020:02:26 00:00:00";
    LocalDateTime expectedTagValue = LocalDateTime.of(2020, 2, 26, 0, 0, 0);
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getObject(tag)).thenReturn(tagValue);

    TemporalAccessor result = MetadataUtils.resolveDate(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    LocalDateTime actualTagValue = LocalDateTime.from(result);
    assertEquals(expectedTagValue, actualTagValue);
  }

  @Test
  void testResolveDateWhenDirIsNull() {
    int tag = 999;
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.containsTag(tag)).thenReturn(false);
    when(mock.directory.getObject(tag)).thenReturn(null);

    TemporalAccessor result = MetadataUtils.resolveDate(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertNull(result);
  }

  @Test
  void testResolveDateWhenTagIsNull() {
    int tag = 999;
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getObject(tag)).thenReturn(null);

    TemporalAccessor result = MetadataUtils.resolveDate(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertNull(result);
  }

  @Test
  void testResolveRational() {
    int tag = 999;
    Rational expectedTagValue = new Rational(10,10);
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getRational(tag)).thenReturn(expectedTagValue);

    Rational actualTagValue = MetadataUtils.resolveRational(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertEquals(expectedTagValue, actualTagValue);
  }

  @Test
  void testResolveRationalArray() {
    int tag = 999;
    Rational[] expectedTagValue = new Rational[] { new Rational(10,10) };
    Mocks mock = makeMockMetadata(tag);
    when(mock.directory.getRationalArray(tag)).thenReturn(expectedTagValue);

    Rational[] actualTagValue = MetadataUtils.resolveRationalArray(mock.metadata, TagPair.of(mock.directory.getClass(), tag));
    assertEquals(expectedTagValue, actualTagValue);
  }


  @Test
  void testGetDirectoryFound() {
    Mocks mock = makeMockMetadata(0);
    when(mock.metadata.containsDirectoryOfType(mock.directory.getClass()))
        .thenReturn(true);
    doReturn(mock.directory)
        .when(mock.metadata)
        .getFirstDirectoryOfType(mock.directory.getClass());
    Directory actualDirectory = getDirectory(mock.metadata, mock.directory.getClass());
    assertNotNull(actualDirectory);
    assertEquals(mock.directory, actualDirectory);
  }

  @Test
  void testGetDirectoryNotFound() {
    Mocks mock = makeMockMetadata(0);
    when(mock.metadata.containsDirectoryOfType(mock.directory.getClass()))
        .thenReturn(false);
    assertNull(getDirectory(mock.metadata, mock.directory.getClass()));
  }

  private Mocks makeMockMetadata(int tag) {
    Mocks mock = new Mocks();
    mock.metadata = mock(Metadata.class);
    mock.directory = mock(Directory.class);

    Collection<? extends Directory> mockDirectories = List.of(mock.directory);

    when(mock.directory.containsTag(tag)).thenReturn(true);
    doReturn(mockDirectories)
        .when(mock.metadata)
        .getDirectoriesOfType(mock.directory.getClass());

    return mock;
  }


}