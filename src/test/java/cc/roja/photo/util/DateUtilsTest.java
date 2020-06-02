package cc.roja.photo.util;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.time.LocalDateTime;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.TemporalAccessor;
import java.util.TimeZone;

import static cc.roja.photo.util.DateUtils.parseDateWithDefaults;
import static cc.roja.photo.util.DateUtils.stripTimeZone;
import static org.junit.jupiter.api.Assertions.assertEquals;

class DateUtilsTest {

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
    TestUtils.assertTemporalAccessor(expected, actual);
  }
}
