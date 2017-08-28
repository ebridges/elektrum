package cc.roja.photo.util;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.log4j.Logger;

import com.drew.lang.annotations.Nullable;
import com.drew.metadata.Directory;
import com.drew.metadata.StringValue;

class ImageDateExtractor {
  private static final Logger LOG = Logger.getLogger(ImageDateExtractor.class);

  static OffsetDateTime getDate(Directory dir, int tagType) {
    return getDate(dir, tagType, null, null);
  }

  /**
   * Copied from com.drew.metadata.Directory#getDate(int, java.lang.String, java.util.TimeZone) in order to parse to an
   * OffsetDateTime rather than java.util.Date.
   *
   * @param dir Directory
   * @param tagType int
   * @param subsecond String
   * @param timeZone TimeZone
   * @return java.util.Date
   */
  private static OffsetDateTime getDate(Directory dir, int tagType, @Nullable String subsecond,
      @Nullable TimeZone timeZone) {
    Object o = dir.getObject(tagType);

    if(o == null) {
      return null;
    }

    OffsetDateTime date = null;

    if ((o instanceof String) || (o instanceof StringValue)) {
      // This seems to cover all known Exif and Xmp date strings
      // Note that "    :  :     :  :  " is a valid date string according to the Exif spec (which means 'unknown date'): http://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html
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

      // if the date string has subsecond information, it supersedes the subsecond parameter
      Pattern subsecondPattern = Pattern.compile("(\\d\\d:\\d\\d:\\d\\d)(\\.\\d+)");
      Matcher subsecondMatcher = subsecondPattern.matcher(dateString);
      if (subsecondMatcher.find()) {
        subsecond = subsecondMatcher.group(2).substring(1);
        dateString = subsecondMatcher.replaceAll("$1");
      }

      // if the date string has time zone information, it supersedes the timeZone parameter
      Pattern timeZonePattern = Pattern.compile("(Z|[+-]\\d\\d:\\d\\d)$");
      Matcher timeZoneMatcher = timeZonePattern.matcher(dateString);
      if (timeZoneMatcher.find()) {
        timeZone = TimeZone.getTimeZone("GMT" + timeZoneMatcher.group().replaceAll("Z", ""));
        dateString = timeZoneMatcher.replaceAll("");
      }

      for (String datePattern : datePatterns) {
        try {
          DateTimeFormatter pattern = DateTimeFormatter.ofPattern(datePattern);
          if(timeZone != null) {
            pattern = pattern.withZone(timeZone.toZoneId());
          } else {
            pattern = pattern.withZone(ZoneOffset.UTC);
          }

          ZonedDateTime zdt = ZonedDateTime.parse(dateString, pattern);
          date = zdt.toOffsetDateTime();

          break;
        } catch (DateTimeParseException ex) {
          // simply try the next pattern
          LOG.debug("Exception: "+ex.getMessage()+" parsedString: "+ex.getParsedString());
        }
      }
    }

    if (date == null)
      return null;

    if (subsecond == null)
      return date;

    try {
      int millisecond = (int) (Double.parseDouble("." + subsecond) * 1000);
      if (millisecond >= 0 && millisecond < 1000) {
        return date.plusSeconds(millisecond);
      }
      return date;
    } catch (NumberFormatException e) {
      return date;
    }
  }
}
