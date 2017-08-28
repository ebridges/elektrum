package cc.roja.photo.util;

import static cc.roja.photo.util.TagPair.of;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME_DIGITIZED;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME_ORIGINAL;
import static com.drew.metadata.exif.GpsDirectory.TAG_DATE_STAMP;
import static com.drew.metadata.exif.GpsDirectory.TAG_TIME_STAMP;
import static java.time.temporal.ChronoUnit.HOURS;

import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.Locale;

import org.apache.log4j.Logger;

import com.drew.lang.Rational;
import com.drew.lang.annotations.Nullable;
import com.drew.metadata.Directory;
import com.drew.metadata.Metadata;
import com.drew.metadata.exif.ExifIFD0Directory;
import com.drew.metadata.exif.ExifSubIFDDirectory;
import com.drew.metadata.exif.GpsDirectory;

import cc.roja.photo.MetaDataExtractor;

public class MetadataUtil {
  private static final Logger LOG = Logger.getLogger(MetadataUtil.class);

  // try these tags in this order
  public static final TagPair[] createDateTags = new TagPair[] {
      of(ExifSubIFDDirectory.class, TAG_DATETIME_DIGITIZED),
      of(ExifSubIFDDirectory.class, TAG_DATETIME_ORIGINAL),
      of(ExifIFD0Directory.class, TAG_DATETIME),
  };

  public static Rational resolveRational(Metadata metadata, TagPair... tags) {
    Rational value = null;
    for(TagPair tagPair : tags) {
      LOG.debug("tagPair: "+ tagPair);
      Directory dir = getDirectoryWith(metadata, tagPair.directory, tagPair.tag);
      if(dir != null) {
        value = dir.getRational(tagPair.tag);
        LOG.debug("dir: "+dir.getName()+", rationalValue: "+value);
      }
    }
    return value;
  }

  @SuppressWarnings("WeakerAccess")
  public static Rational[] resolveRationalArray(Metadata metadata, TagPair... tags) {
    Rational[] value = null;
    for(TagPair tagPair : tags) {
      LOG.debug("tagPair: "+ tagPair);
      Directory dir = getDirectoryWith(metadata, tagPair.directory, tagPair.tag);
      if(dir != null) {
        value = dir.getRationalArray(tagPair.tag);
        LOG.debug("dir: "+dir.getName()+", rationalValue: "+ Arrays.toString(value));
      }
    }
    return value;
  }

  public static OffsetDateTime resolveDate(Metadata metadata, TagPair... tags) {
    OffsetDateTime value;
    for(TagPair tagPair : tags) {
      LOG.debug("tagPair: "+ tagPair);
      Directory dir = getDirectoryWith(metadata, tagPair.directory, tagPair.tag);
      if(dir != null) {
        value = ImageDateExtractor.getDate(dir, tagPair.tag);
        LOG.debug("dir: "+dir.getName()+", dateValue: "+value);
        if (value != null) {
          return value;
        }
      }
    }
    return null;
  }

  public static String resolveString(Metadata metadata, TagPair... tags) {
    String value = null;
    for(TagPair tagPair : tags) {
      LOG.debug("tagPair: "+ tagPair);
      Directory dir = getDirectoryWith(metadata, tagPair.directory, tagPair.tag);
      if(dir != null) {
        value = dir.getString(tagPair.tag);
        LOG.debug("dir: "+dir.getName()+", stringValue: "+value);
        if(value == null || value.isEmpty()) {
          value = dir.getDescription(tagPair.tag);
          LOG.debug("dir: "+dir.getName()+", descriptionValue: "+value);
        }
      }
    }
    return value;
  }

  public static Integer resolveInteger(Metadata metadata, TagPair... tags) {
    Integer value = null;
    for(TagPair tagPair : tags) {
      LOG.debug("tagPair: "+ tagPair);
      Directory dir = getDirectoryWith(metadata, tagPair.directory, tagPair.tag);
      if(dir != null) {
        value = dir.getInteger(tagPair.tag);
        LOG.debug("dir: "+dir.getName()+", intValue: "+value);
      }
    }
    return value;
  }

  public static String resolveDescription(Metadata metadata, TagPair... tags) {
    String value = null;
    for(TagPair tagPair : tags) {
      LOG.debug("tagPair: "+ tagPair);
      Directory dir = getDirectoryWith(metadata, tagPair.directory, tagPair.tag);
      if(dir != null) {
        value = dir.getDescription(tagPair.tag);
        LOG.debug("dir: "+dir.getName()+", descriptionValue: "+value);
      }
    }
    return value;
  }

  private static Directory getDirectoryWith(Metadata meta, Class<? extends Directory> dirClass, int tag) {
    for(Directory directory : meta.getDirectoriesOfType(dirClass)) {
      if(directory.containsTag(tag)) {
        return directory;
      }
    }
    return null;
  }

  public static Directory getDirectory(Metadata meta, Class<? extends Directory> dirClass) {
    if(meta.containsDirectoryOfType(dirClass)) {
      return meta.getFirstDirectoryOfType(dirClass);
    } else {
      return null;
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
    String date = resolveString(metadata, of(GpsDirectory.class, TAG_DATE_STAMP));
    Rational[] timeComponents = resolveRationalArray(metadata, of(GpsDirectory.class, TAG_TIME_STAMP));

    if (timeComponents == null || timeComponents.length != 3) {
      return null;
    }

    // Make sure we have the required values
    if (date == null) {
      // use date from CreateDate timestamp
      OffsetDateTime createDate = resolveDate(metadata, createDateTags);
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
