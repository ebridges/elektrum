package cc.roja.photo.metadata;

import com.drew.lang.Rational;
import com.drew.metadata.Directory;
import com.drew.metadata.Metadata;
import org.assertj.core.util.Lists;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.temporal.TemporalAccessor;
import java.util.Collection;
import java.util.Optional;
import java.util.TimeZone;

import static cc.roja.photo.metadata.MetadataUtils.getDateValueFromMetadata;
import static cc.roja.photo.metadata.MetadataUtils.getDirectory;
import static cc.roja.photo.util.DateUtils.parseDateWithDefaults;
import static cc.roja.photo.util.TestUtils.assertTemporalAccessor;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
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
    assertNotNull(result);
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

    Collection<? extends Directory> mockDirectories = Lists.list(mock.directory);

    when(mock.directory.containsTag(tag)).thenReturn(true);
    doReturn(mockDirectories)
        .when(mock.metadata)
        .getDirectoriesOfType(mock.directory.getClass());

    return mock;
  }

  @ParameterizedTest
  @CsvSource({
      "2020:02:26 12:34:56, yyyy:MM:dd HH:mm:ss",
      "2020:02:26 12:34, yyyy:MM:dd HH:mm",
      "2020-02-26 12:34:56, yyyy-MM-dd HH:mm:ss",
      "2020-02-26 12:34, yyyy-MM-dd HH:mm",
      "2020.02.26 12:34:56, yyyy.MM.dd HH:mm:ss",
      "2020.02.26 12:34, yyyy.MM.dd HH:mm",
      "2020-02-26T12:34:56, yyyy-MM-dd'T'HH:mm:ss",
      "2020-02-26T12:34, yyyy-MM-dd'T'HH:mm",
      "2020-02-26, yyyy-MM-dd",
      "2020-02, yyyy-MM",
      "20200226, yyyyMMdd",
      "2020, yyyy",
  })
  void getDateValueFromMetadata_Success(String testCase, String pattern) {
    int tagType = 999;
    Directory mockDirectory = mock(Directory.class);
    when(mockDirectory.getObject(tagType)).thenReturn(testCase);
    TemporalAccessor actual = getDateValueFromMetadata(mockDirectory, tagType);
    TemporalAccessor expected = parseDateWithDefaults(testCase, pattern);
    assertTemporalAccessor(expected, actual);
  }

  @ParameterizedTest
  @CsvSource({
      "2020:02:26 12:34:56Z, yyyy:MM:dd HH:mm:ssVV, GMT",
      "2020-02-26T12:34:56Z, yyyy-MM-dd'T'HH:mm:ssVV, GMT",
      "2020:02:26 12:34:56+05:00, yyyy:MM:dd HH:mm:ssVV, GMT+05:00",
      "2020-02-26T12:34:56+05:00, yyyy-MM-dd'T'HH:mm:ssVV, GMT+05:00",
      "2020:02:26 12:34:56-05:00, yyyy:MM:dd HH:mm:ssVV, GMT-05:00",
      "2020-02-26T12:34:56-05:00, yyyy-MM-dd'T'HH:mm:ssVV, GMT-05:00",
  })
  void getDateValueFromMetadata_WithTZSuccess(String testCase, String pattern, String timeZone) {
    int tagType = 999;
    TimeZone tz = TimeZone.getTimeZone(timeZone);
    Directory mockDirectory = mock(Directory.class);
    when(mockDirectory.getObject(tagType)).thenReturn(testCase);
    TemporalAccessor actual = getDateValueFromMetadata(mockDirectory, tagType);
    TemporalAccessor expected = parseDateWithDefaults(testCase, pattern, Optional.of(tz));
    assertTemporalAccessor(expected, actual);
    ZonedDateTime expectedWithZone = ZonedDateTime.from(expected);
    assert actual != null;
    ZonedDateTime actualWithZone = ZonedDateTime.from(actual);
    assertEquals(expectedWithZone.getOffset(), actualWithZone.getOffset());
  }

  @Test
  void getDateValueFromMetadata_TagTypeNotFound() {
    int tagType = 0;
    Directory mockDirectory = mock(Directory.class);
    when(mockDirectory.getObject(tagType)).thenReturn(null);
    TemporalAccessor result = getDateValueFromMetadata(mockDirectory, tagType);
    assertNull(result);
  }

  @Test()
  void getDateValueFromMetadata_DirectoryIsNull() {
    //noinspection ConstantConditions
    assertThrows(NullPointerException.class, () -> getDateValueFromMetadata(null, 0));
  }
}
