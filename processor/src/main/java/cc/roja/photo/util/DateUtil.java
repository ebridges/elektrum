package cc.roja.photo.util;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.YearMonth;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;

import org.apache.log4j.Logger;

public class DateUtil {
  private static final Logger LOG = Logger.getLogger(DateUtil.class);

  public static ZoneOffset determineTimeZoneOffset(OffsetDateTime localTime, OffsetDateTime utcTime) {
    if(utcTime == null) {
      return null;
    }

    OffsetDateTime ceilingUtc = utcTime.truncatedTo(ChronoUnit.HOURS).plusHours(1);
    OffsetDateTime ceilingLocal = localTime.truncatedTo(ChronoUnit.HOURS).plusHours(1);

    int offsetHours = (int)ChronoUnit.HOURS.between(ceilingUtc, ceilingLocal);

    return ZoneOffset.ofHours(offsetHours);
  }

  public static LocalDate parseDate(String date) {
    String[] yymmddFormats = new String[]{"yyyyMMdd'T'HHmmss", "yyyy-MM-dd'T'HHmmss", "yyyy-MM-dd", "yyyyMMdd"};
    for (String format : yymmddFormats) {
      DateTimeFormatter formatter = DateTimeFormatter.ofPattern(format);
      try {
        return LocalDate.parse(date, formatter);
      } catch(DateTimeParseException ignored) {
        // pass
      }
    }

    String[] yymmFormats = new String[]{"yyyyMM", "yyyy-MM"};
    for (String format : yymmFormats) {
      DateTimeFormatter formatter = DateTimeFormatter.ofPattern(format);
      try {
        YearMonth yyyyMM = YearMonth.parse(date, formatter);
        return LocalDate.of(yyyyMM.getYear(), yyyyMM.getMonth(), 1);
      } catch(DateTimeParseException ignored) {
        // This is expected when the format does not match input
        LOG.debug("exception: "+ignored.getMessage(), ignored);
      }
    }

    return null;
  }
}
