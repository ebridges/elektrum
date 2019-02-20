package cc.roja.photo.util;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;

import java.time.LocalDate;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;

import static cc.roja.photo.util.DateUtil.parseDate;
import static java.time.format.DateTimeFormatter.ofPattern;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

class DateUtilTest {

  @ParameterizedTest
  @CsvSource({"20200226T123456, yyyyMMdd'T'HHmmss",
      "2020-02-26T123456, yyyy-MM-dd'T'HHmmss",
      "2020-02-26, yyyy-MM-dd",
      "20200226, yyyyMMdd"})
  void parseDateYMD_success(String testCase, String pattern) {
    DateTimeFormatter format = ofPattern(pattern);
    LocalDate expected = LocalDate.parse(testCase, format);
    LocalDate actual = parseDate(testCase);
    assertNotNull(actual);
    assertEquals(expected, actual);
  }

  @ParameterizedTest
  @CsvSource({"202002, yyyyMM",
      "2020-02, yyyy-MM"})
  void parseDateYM_success(String testCase, String pattern) {
    DateTimeFormatter format = ofPattern(pattern);
    YearMonth yyyyMM = YearMonth.parse(testCase, format);
    LocalDate expected = LocalDate.of(yyyyMM.getYear(), yyyyMM.getMonth(), 1);
    LocalDate actual = parseDate(testCase);
    assertNotNull(actual);
    assertEquals(expected, actual);
  }

  @ParameterizedTest
  @ValueSource(strings = { "February 26, 2020", "20181342T357520" })
  void parseDate_failure(String testCase) {
    LocalDate actual = parseDate(testCase);
    assertNull(actual);
  }
}
