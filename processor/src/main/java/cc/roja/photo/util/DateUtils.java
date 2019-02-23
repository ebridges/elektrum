package cc.roja.photo.util;

import com.drew.metadata.Directory;
import com.drew.metadata.StringValue;
import org.apache.log4j.Logger;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.time.format.DateTimeParseException;
import java.time.temporal.TemporalAccessor;
import java.util.Optional;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static java.time.temporal.ChronoField.DAY_OF_MONTH;
import static java.time.temporal.ChronoField.HOUR_OF_DAY;
import static java.time.temporal.ChronoField.MILLI_OF_SECOND;
import static java.time.temporal.ChronoField.MINUTE_OF_HOUR;
import static java.time.temporal.ChronoField.MONTH_OF_YEAR;
import static java.time.temporal.ChronoField.SECOND_OF_MINUTE;
import static java.time.temporal.ChronoField.YEAR;

public class DateUtils {
  private static final Logger LOG = Logger.getLogger(DateUtils.class);

  public static LocalDateTime stripTimeZone(TemporalAccessor temporalAccessor) {
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

  static TemporalAccessor parseDateWithDefaults(String dateString, String pattern) {
    return parseDateWithDefaults(dateString, pattern, Optional.empty());
  }

  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  static TemporalAccessor parseDateWithDefaults(String dateString, String pattern, Optional<TimeZone> timeZone) {
    DateTimeFormatter formatter = new DateTimeFormatterBuilder().appendPattern(pattern)
        .parseDefaulting(MONTH_OF_YEAR, 1)
        .parseDefaulting(DAY_OF_MONTH, 1)
        .parseDefaulting(HOUR_OF_DAY, 0)
        .parseDefaulting(MINUTE_OF_HOUR, 0)
        .parseDefaulting(SECOND_OF_MINUTE, 0)
        .parseDefaulting(MILLI_OF_SECOND, 0)
        .toFormatter();

    if(timeZone.isPresent()) {
      formatter = formatter.withZone(timeZone.get().toZoneId());
    }

    return formatter.parse(dateString);
  }

  /**
   * Copied from com.drew.metadata.Directory#getDate(int, java.lang.String, java.util.TimeZone) in order to parse to a
   * TemporalAccessor rather than java.util.Date.
   *
   * Changes from drewnoakes implementation:
   * ============================================
   * - parse tag value into a TemporalAcessor rather than a java.util.Date
   * - subsecond param is skipped for our purposes.
   * - timeZone param is now handled internally.
   *
   * @param dir Directory
   * @param tagType int
   * @param String subsecond
   * @param TimeZone timeZone
   * @return TemporalAccessor
   */
  @SuppressWarnings({"SameParameterValue", "JavadocReference"})
  static TemporalAccessor getDateValueFromMetadata(Directory dir, int tagType) {
    Object o = dir.getObject(tagType);

    if(o == null) {
      return null;
    }

    TemporalAccessor date = null;

    if ((o instanceof String) || (o instanceof StringValue)) {
      // This seems to cover all known Exif and Xmp date strings
      // Note that "    :  :     :  :  " is a valid date string according to the Exif spec (which means 'unknown
      // date'): http://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html
      String datePatterns[] = {
          "yyyy:MM:dd HH:mm:ss",
          "yyyy:MM:dd HH:mm",
          "yyyy-MM-dd HH:mm:ss",
          "yyyy-MM-dd HH:mm",
          "yyyy.MM.dd HH:mm:ss",
          "yyyy.MM.dd HH:mm",
          "yyyy-MM-dd'T'HH:mm:ss",
          "yyyy-MM-dd'T'HH:mm",
          "yyyy-MM-dd",
          "yyyy-MM",
          "yyyyMMdd", // as used in IPTC data
          "yyyy" };

      String dateString = o.toString();

      // see if we can extract timezone information from the time portion of the tag value
      TimeZone timeZone = null;
      Pattern timeZonePattern = Pattern.compile("(Z|[+-]\\d\\d:\\d\\d)$");
      Matcher timeZoneMatcher = timeZonePattern.matcher(dateString);
      if (timeZoneMatcher.find()) {
        timeZone = TimeZone.getTimeZone("GMT" + timeZoneMatcher.group().replaceAll("Z", ""));
        dateString = timeZoneMatcher.replaceAll("");
      }

      for (String datePattern : datePatterns) {
        //noinspection CatchMayIgnoreException
        try {
          date = parseDateWithDefaults(dateString, datePattern, Optional.ofNullable(timeZone));
          break;
        } catch (DateTimeParseException ignored) {
          // simply try the next pattern
          LOG.debug("Exception: "+ignored.getMessage()+" parsedString: "+ignored.getParsedString());
        }
      }
    }

    return date;
  }
}
