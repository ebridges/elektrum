package cc.roja.photo.metadata;

import static cc.roja.photo.metadata.TagPair.of;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME_DIGITIZED;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME_ORIGINAL;

import java.time.format.DateTimeParseException;
import java.time.temporal.TemporalAccessor;
import java.util.Arrays;
import java.util.Optional;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import cc.roja.photo.util.DateUtils;
import com.drew.metadata.StringValue;
import org.apache.log4j.Logger;

import com.drew.lang.Rational;
import com.drew.metadata.Directory;
import com.drew.metadata.Metadata;
import com.drew.metadata.exif.ExifIFD0Directory;
import com.drew.metadata.exif.ExifSubIFDDirectory;

class MetadataUtils {
  private static final Logger LOG = Logger.getLogger(MetadataUtils.class);

  // try these tags in this order
  static final TagPair[] createDateTags = new TagPair[] {
      of(ExifSubIFDDirectory.class, TAG_DATETIME_DIGITIZED),
      of(ExifSubIFDDirectory.class, TAG_DATETIME_ORIGINAL),
      of(ExifIFD0Directory.class, TAG_DATETIME),
  };

  static Rational resolveRational(Metadata metadata, TagPair... tags) {
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

  static Rational[] resolveRationalArray(Metadata metadata, TagPair... tags) {
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

  static TemporalAccessor resolveDate(Metadata metadata, TagPair... tags) {
    TemporalAccessor value;
    for(TagPair tagPair : tags) {
      LOG.debug("tagPair: "+ tagPair);
      Directory dir = getDirectoryWith(metadata, tagPair.directory, tagPair.tag);
      if(dir != null) {
        value = getDateValueFromMetadata(dir, tagPair.tag);
        LOG.debug("dir: "+dir.getName()+", dateValue: "+value);
        if (value != null) {
          return value;
        }
      }
    }
    return null;
  }

  static String resolveString(Metadata metadata, TagPair... tags) {
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

  static Integer resolveInteger(Metadata metadata, TagPair... tags) {
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

  static String resolveDescription(Metadata metadata, TagPair... tags) {
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

  static Directory getDirectory(Metadata meta, Class<? extends Directory> dirClass) {
    if(meta.containsDirectoryOfType(dirClass)) {
      return meta.getFirstDirectoryOfType(dirClass);
    } else {
      return null;
    }
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
      String[] datePatterns = {
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
          "yyyy"};

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
          date = DateUtils.parseDateWithDefaults(dateString, datePattern, Optional.ofNullable(timeZone));
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
