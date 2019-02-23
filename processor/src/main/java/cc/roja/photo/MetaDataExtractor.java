package cc.roja.photo;

import static cc.roja.photo.util.MetadataUtils.getDirectory;
import static cc.roja.photo.util.MetadataUtils.resolveDescription;
import static cc.roja.photo.util.MetadataUtils.resolveInteger;
import static cc.roja.photo.util.MetadataUtils.resolveRational;
import static cc.roja.photo.util.MetadataUtils.resolveString;
import static cc.roja.photo.util.TagPair.of;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_APERTURE;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_ARTIST;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_EXIF_IMAGE_HEIGHT;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_EXIF_IMAGE_WIDTH;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_EXPOSURE_TIME;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_FOCAL_LENGTH;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_ISO_EQUIVALENT;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_MAKE;
import static com.drew.metadata.exif.ExifDirectoryBase.TAG_MODEL;
import static com.drew.metadata.exif.GpsDirectory.TAG_ALTITUDE;
import static com.drew.metadata.exif.GpsDirectory.TAG_DATE_STAMP;
import static com.drew.metadata.exif.GpsDirectory.TAG_TIME_STAMP;
import static com.drew.metadata.file.FileSystemDirectory.TAG_FILE_NAME;
import static java.time.temporal.ChronoUnit.HOURS;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.TemporalAccessor;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import cc.roja.photo.util.DateUtils;
import com.drew.lang.annotations.Nullable;
import org.apache.log4j.Logger;

import com.drew.imaging.ImageMetadataReader;
import com.drew.imaging.ImageProcessingException;
import com.drew.lang.GeoLocation;
import com.drew.lang.Rational;
import com.drew.metadata.Metadata;
import com.drew.metadata.exif.ExifIFD0Directory;
import com.drew.metadata.exif.ExifSubIFDDirectory;
import com.drew.metadata.exif.GpsDirectory;
import com.drew.metadata.file.FileSystemDirectory;

import cc.roja.photo.util.MetadataUtils;

@SuppressWarnings("WeakerAccess")
public class MetaDataExtractor {
  private static final Logger LOG = Logger.getLogger(MetaDataExtractor.class);

  public void extract(File image, ImageInfo imageInfo) throws IOException {
    Metadata metadataReader;
    try {
      metadataReader = ImageMetadataReader.readMetadata(image);
    } catch (ImageProcessingException e) {
      throw new IOException(e);
    }

    imageInfo.setFileSize(image.length());

    setGpsInfo(metadataReader, imageInfo); // should be done first to get GPSTime
    setExifInfo(metadataReader, imageInfo);

    if(LOG.isInfoEnabled()) {
      LOG.info(imageInfo.toString());
    }
  }

  private static void setExifInfo(Metadata metadata, ImageInfo meta) {
    LocalDateTime createDate = deduceCreateDate(metadata);
    meta.setCreateDate(createDate);
    LOG.debug("createDate: "+createDate);

    String artist = resolveString(metadata, of(ExifIFD0Directory.class, TAG_ARTIST));
    LOG.debug("artist: "+artist);
    meta.setArtist(artist);

    String cameraMake = resolveString(metadata, of(ExifIFD0Directory.class, TAG_MAKE));
    LOG.debug("cameraMake: "+cameraMake);
    meta.setCameraMake(cameraMake);

    String cameraModel = resolveString(metadata, of(ExifIFD0Directory.class, TAG_MODEL));
    LOG.debug("cameraModel: "+cameraModel);
    meta.setCameraModel(cameraModel);

    Rational focalLength = resolveRational(metadata, of(ExifSubIFDDirectory.class, TAG_FOCAL_LENGTH));
    LOG.debug("focalLength: "+focalLength);
    if(focalLength != null) {
      meta.setFocalLength(Math.round(focalLength.floatValue()));
    }

    String apertureDescription = resolveDescription(metadata, of(ExifSubIFDDirectory.class, TAG_APERTURE));
    LOG.debug("aperture: "+apertureDescription);
    meta.setAperture(apertureDescription);

    Integer isoSpeed = resolveInteger(metadata, of(ExifSubIFDDirectory.class, TAG_ISO_EQUIVALENT));
    LOG.debug("isoSpeed: "+isoSpeed);
    meta.setIsoSpeed( isoSpeed );

    Rational shutterSpeed = resolveRational(metadata, of(ExifSubIFDDirectory.class, TAG_EXPOSURE_TIME));
    LOG.debug("shutterSpeed: "+shutterSpeed);
    if (shutterSpeed != null) {
      meta.setShutterSpeedNumerator(shutterSpeed.getNumerator());
      meta.setShutterSpeedDenominator(shutterSpeed.getDenominator());
    }

    Integer imageHeight = resolveInteger(metadata, of(ExifSubIFDDirectory.class, TAG_EXIF_IMAGE_HEIGHT));
    LOG.debug("imageHeight: "+imageHeight);
    meta.setImageHeight(imageHeight);

    Integer imageWidth = resolveInteger(metadata, of(ExifSubIFDDirectory.class, TAG_EXIF_IMAGE_WIDTH));
    LOG.debug("imageWidth: "+imageWidth);
    meta.setImageWidth(imageWidth);
  }

  private static LocalDateTime deduceCreateDate(Metadata metadata) {
    TemporalAccessor createDate = MetadataUtils.resolveDate(metadata, MetadataUtils.createDateTags);

    if(createDate == null) {
      createDate = deduceCreateDateFromFilename(metadata);
    }

    return DateUtils.stripTimeZone(createDate);
  }

  private static LocalDateTime deduceCreateDateFromFilename(Metadata metadata) {
    String filename = resolveString(metadata, of(FileSystemDirectory.class, TAG_FILE_NAME));
    if(filename == null || filename.isEmpty()) {
      return null;
    }
    // if the filename starts with this parameter, we can extract from there:
    //    20141118T110523
    //    @todo add more patterns...
    //    @todo consolidate date parsing logic with DateUtils
    
    String regex = "^(?<date>[0-9]{4}[0-9]{2}[0-9]{2}T[0-9]{2}[0-9]{2}[0-9]{2})";
    Pattern pattern = Pattern.compile(regex);
    Matcher matcher = pattern.matcher(filename);
    boolean success = matcher.find();

    if(!success) {
      return null;
    }

    String date = matcher.group("date");
    DateTimeFormatter format = DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss");
    LocalDateTime createDate = LocalDateTime.parse(date, format);
    return createDate;
  }

  private static void setGpsInfo(Metadata metadata, ImageInfo meta) {
    GpsDirectory dir = (GpsDirectory) getDirectory(metadata, GpsDirectory.class);
    if(dir == null) {
      return;
    }

    Rational altitude = resolveRational(metadata, of(GpsDirectory.class, TAG_ALTITUDE));
    LOG.debug("altitude: "+altitude);
    if(altitude != null) {
      meta.setGpsAlt(altitude.doubleValue());
    }

    OffsetDateTime gpsTime = getGpsDate(metadata);
    LOG.debug("gpsTime: "+gpsTime);
    meta.setGpsDatetime( gpsTime );

    GeoLocation loc = dir.getGeoLocation();
    if (loc == null) {
      return;
    }
    LOG.debug("gpsLocation: "+loc.toDMSString());
    meta.setGpsLat( loc.getLatitude() );
    meta.setGpsLon( loc.getLongitude() );
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
  private static OffsetDateTime getGpsDate(Metadata metadata) {
    String date = MetadataUtils.resolveString(metadata, of(GpsDirectory.class, TAG_DATE_STAMP));
    Rational[] timeComponents = MetadataUtils.resolveRationalArray(metadata, of(GpsDirectory.class, TAG_TIME_STAMP));

    if (timeComponents == null || timeComponents.length != 3) {
      return null;
    }

    // Make sure we have the required values
    if (date == null) {
      // use date from CreateDate timestamp
      TemporalAccessor ta = MetadataUtils.resolveDate(metadata, MetadataUtils.createDateTags);

      if(ta != null) {
        LocalDateTime createDate = DateUtils.stripTimeZone(ta);
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
