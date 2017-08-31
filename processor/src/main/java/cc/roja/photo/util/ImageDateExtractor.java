package cc.roja.photo.util;

import static cc.roja.photo.util.TagPair.of;
import static com.drew.metadata.exif.GpsDirectory.TAG_DATE_STAMP;
import static com.drew.metadata.exif.GpsDirectory.TAG_TIME_STAMP;
import static java.time.temporal.ChronoUnit.HOURS;

import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Locale;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.log4j.Logger;

import com.drew.lang.Rational;
import com.drew.lang.annotations.Nullable;
import com.drew.metadata.Directory;
import com.drew.metadata.Metadata;
import com.drew.metadata.StringValue;
import com.drew.metadata.exif.GpsDirectory;

public class ImageDateExtractor {
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
  @SuppressWarnings("SameParameterValue")
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

  /**
   * Copied from com.drew.metadata.exif.GpsDirectory#getGpsDate()
   *
   * Parses the date stamp tag and the time stamp tag to obtain a single Date object representing the
   * date and time when this image was captured.
   *
   * @return A Date object representing when this image was captured, if possible, otherwise null
   */
  @Nullable
  public static OffsetDateTime getGpsDate(Metadata metadata) {
    String date = MetadataUtil.resolveString(metadata, of(GpsDirectory.class, TAG_DATE_STAMP));
    Rational[] timeComponents = MetadataUtil.resolveRationalArray(metadata, of(GpsDirectory.class, TAG_TIME_STAMP));

    if (timeComponents == null || timeComponents.length != 3) {
      return null;
    }

    // Make sure we have the required values
    if (date == null) {
      // use date from CreateDate timestamp
      OffsetDateTime createDate = MetadataUtil.resolveDate(metadata, MetadataUtil.createDateTags);
      if(createDate != null) {
        LocalTime localTime =  createDate.toLocalTime();
        LocalTime utcTime = LocalTime.of(timeComponents[0].intValue(), timeComponents[1].intValue(), timeComponents[2].intValue());

        long hoursBetween = HOURS.between(localTime, utcTime);

        // if the difference between the UTC hour obtained from TAG_TIME_STAMP and the hour of the createDate
        // is greater than 18, then we move the day of the month up or down one day.
        //
        // Why "18"?  because ZoneOffset throws an exception if the difference in hours
        // between two dates is greater than 18 hours.

        if(hoursBetween > 18) {
          createDate = createDate.minusDays(1);
        } else if (hoursBetween < -18) {
          createDate = createDate.plusDays(1);
        }

        date = createDate.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
      } else {
        return null;
      }
    }

    String dateTime = String.format(Locale.US, "%s %02d:%02d:%02.3f",
        date,
        timeComponents[0].intValue(),
        timeComponents[1].intValue(),
        timeComponents[2].doubleValue()
    );

    try {
      DateTimeFormatter pattern = DateTimeFormatter
          .ofPattern("yyyy:MM:dd HH:mm:s.SSS")
          .withZone(ZoneOffset.UTC);

      ZonedDateTime zdt = ZonedDateTime.parse(dateTime, pattern);
      return zdt.toOffsetDateTime();

    } catch (DateTimeParseException e) {
      LOG.info("unable to parse GPS timestamp: "+e.getMessage());
      return null;
    }
  }
}
