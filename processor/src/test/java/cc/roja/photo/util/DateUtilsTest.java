package cc.roja.photo.util;

import com.drew.metadata.Directory;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoField;
import java.time.temporal.TemporalAccessor;
import java.util.Optional;
import java.util.TimeZone;

import static cc.roja.photo.util.DateUtils.getDateValueFromMetadata;
import static cc.roja.photo.util.DateUtils.parseDateWithDefaults;
import static cc.roja.photo.util.DateUtils.stripTimeZone;
import static java.time.temporal.ChronoField.DAY_OF_MONTH;
import static java.time.temporal.ChronoField.HOUR_OF_DAY;
import static java.time.temporal.ChronoField.MINUTE_OF_HOUR;
import static java.time.temporal.ChronoField.MONTH_OF_YEAR;
import static java.time.temporal.ChronoField.SECOND_OF_MINUTE;
import static java.time.temporal.ChronoField.YEAR;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DateUtilsTest {

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
    assertThrows(NullPointerException.class, () -> {getDateValueFromMetadata(null, 0);});
  }

  @ParameterizedTest
  @CsvSource({
      "20200226T123456, yyyyMMdd'T'HHmmss",
      "2020-02-26T123456, yyyy-MM-dd'T'HHmmss",
      "2020-02-26, yyyy-MM-dd",
      "20200226, yyyyMMdd",
      "202002, yyyyMM",
      "2020-02, yyyy-MM",
      "2020, yyyy"
  })
  void testParseDateWithDefaults(String testCase, String pattern) {
    TemporalAccessor underTest = parseDateWithDefaults(testCase, pattern);
    DateTimeFormatter dtf = DateTimeFormatter.ofPattern(pattern);
    String actual = dtf.format(underTest);
    assertEquals(testCase, actual);
  }

  @Test
  void testStripTimeZone() {
    LocalDateTime expected = LocalDateTime.of(2020, 2, 26, 0, 0, 0);
    ZonedDateTime zonedDateTime = ZonedDateTime.of(expected, TimeZone.getTimeZone("America/New_York").toZoneId());
    LocalDateTime actual = stripTimeZone(zonedDateTime);
    assertTemporalAccessor(expected, actual);
  }

  private void assertTemporalAccessor(TemporalAccessor expected, TemporalAccessor actual) {
    assertNotNull(expected);
    assertNotNull(actual);
    ChronoField[] testFields = {
        YEAR,
        MONTH_OF_YEAR,
        DAY_OF_MONTH,
        HOUR_OF_DAY,
        MINUTE_OF_HOUR,
        SECOND_OF_MINUTE,
    };
    for(ChronoField field : testFields) {
      assertEquals(expected.get(field), actual.get(field));
    }
  }
}
