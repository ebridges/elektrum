package cc.roja.photo.util;

import com.drew.metadata.Directory;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoField;
import java.time.temporal.TemporalAccessor;

import static cc.roja.photo.util.DateUtils.getDateValueFromMetadata;
import static cc.roja.photo.util.DateUtils.parseDateWithDefaults;
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
