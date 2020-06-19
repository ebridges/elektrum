package cc.roja.photo.util;

import java.time.temporal.ChronoField;
import java.time.temporal.TemporalAccessor;

import static java.time.temporal.ChronoField.DAY_OF_MONTH;
import static java.time.temporal.ChronoField.HOUR_OF_DAY;
import static java.time.temporal.ChronoField.MINUTE_OF_HOUR;
import static java.time.temporal.ChronoField.MONTH_OF_YEAR;
import static java.time.temporal.ChronoField.SECOND_OF_MINUTE;
import static java.time.temporal.ChronoField.YEAR;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class TestUtils {
  public static void assertTemporalAccessor(TemporalAccessor expected, TemporalAccessor actual) {
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
