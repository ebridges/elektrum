package cc.roja.photo.util;

import static cc.roja.photo.util.DateUtils.getDateValueFromMetadata;
import static cc.roja.photo.util.TagPair.of;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME_DIGITIZED;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_DATETIME_ORIGINAL;

import java.time.temporal.TemporalAccessor;
import java.util.Arrays;

import org.apache.log4j.Logger;

import com.drew.lang.Rational;
import com.drew.metadata.Directory;
import com.drew.metadata.Metadata;
import com.drew.metadata.exif.ExifIFD0Directory;
import com.drew.metadata.exif.ExifSubIFDDirectory;

public class MetadataUtils {
  private static final Logger LOG = Logger.getLogger(MetadataUtils.class);

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

  public static TemporalAccessor resolveDate(Metadata metadata, TagPair... tags) {
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
}
