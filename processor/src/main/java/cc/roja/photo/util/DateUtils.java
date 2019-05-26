package cc.roja.photo.util;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.temporal.TemporalAccessor;
import java.util.TimeZone;

import static java.time.temporal.ChronoField.DAY_OF_MONTH;
import static java.time.temporal.ChronoField.HOUR_OF_DAY;
import static java.time.temporal.ChronoField.MILLI_OF_SECOND;
import static java.time.temporal.ChronoField.MINUTE_OF_HOUR;
import static java.time.temporal.ChronoField.MONTH_OF_YEAR;
import static java.time.temporal.ChronoField.SECOND_OF_MINUTE;
import static java.time.temporal.ChronoField.YEAR;

public class DateUtils {

  public static LocalDateTime stripTimeZone(TemporalAccessor temporalAccessor) {
    if(temporalAccessor == null){
      return null;
    }

    return LocalDateTime.of(
        temporalAccessor.get(YEAR),
        temporalAccessor.get(MONTH_OF_YEAR),
        temporalAccessor.get(DAY_OF_MONTH),
        temporalAccessor.get(HOUR_OF_DAY),
        temporalAccessor.get(MINUTE_OF_HOUR),
        temporalAccessor.get(SECOND_OF_MINUTE),
        0
    );
  }

  public static TemporalAccessor parseDateWithDefaults(String dateString, String pattern) {
    return parseDateWithDefaults(dateString, pattern, null);
  }

  public static TemporalAccessor parseDateWithDefaults(String dateString, String pattern, TimeZone timeZone) {
    DateTimeFormatter formatter = new DateTimeFormatterBuilder().appendPattern(pattern)
        .parseDefaulting(MONTH_OF_YEAR, 1)
        .parseDefaulting(DAY_OF_MONTH, 1)
        .parseDefaulting(HOUR_OF_DAY, 0)
        .parseDefaulting(MINUTE_OF_HOUR, 0)
        .parseDefaulting(SECOND_OF_MINUTE, 0)
        .parseDefaulting(MILLI_OF_SECOND, 0)
        .toFormatter();

    if(timeZone != null) {
      formatter = formatter.withZone(timeZone.toZoneId());
    }

    return formatter.parse(dateString);
  }

}
